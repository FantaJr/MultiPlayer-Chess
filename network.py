import socket
import pickle
import threading
import time
import select
import random
import struct

class ChessNetwork:
    def __init__(self, is_host=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_host = is_host
        self.connected = False
        self.opponent = None
        self.room_name = None
        self.room_password = None
        self.players = []  # Odadaki oyuncular
        self.local_ip = None
        self.active_rooms = []
        self.broadcasting = False
        self.game_started = False
        self.plays_white = None  # Oyuncunun rengi
        
    def host_game(self, room_name, room_password, port=5555):
        try:
            # SO_REUSEADDR ekle
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', port))
            self.socket.listen(1)
            self.socket.setblocking(False)
            
            hostname = socket.gethostname()
            self.local_ip = socket.gethostbyname(hostname)
            print(f"Hosting on {self.local_ip}:{port}")
            
            self.room_name = room_name
            self.room_password = room_password
            self.players.append("Host (You)")
            
            # Periyodik olarak odayı yayınla
            self.broadcasting = True
            threading.Thread(target=self.periodic_broadcast, daemon=True).start()
            
            # Bağlantı bekleme thread'i
            threading.Thread(target=self.wait_for_connection, daemon=True).start()
            
            # Hamle dinleme thread'ini başlat
            threading.Thread(target=self.listen_for_moves, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"Error hosting game: {e}")
            return False

    def wait_for_connection(self):
        try:
            while not self.connected:
                try:
                    client_socket, addr = self.socket.accept()
                    print(f"Connection from: {addr}")
                    
                    try:
                        auth_data = pickle.loads(client_socket.recv(1024))
                        if isinstance(auth_data, dict):
                            client_password = auth_data.get('password')
                            client_room = auth_data.get('room_name')
                            
                            if client_room == self.room_name and client_password == self.room_password:
                                response = {'status': 'accepted'}
                                client_socket.send(pickle.dumps(response))
                                
                                self.opponent = client_socket
                                self.connected = True
                                self.players.append(f"Guest ({addr[0]})")
                                print("Guest connected successfully")
                                
                                # Dinleme thread'ini yeniden başlat
                                threading.Thread(target=self.listen_for_moves, daemon=True).start()
                                break
                            else:
                                response = {
                                    'status': 'rejected',
                                    'message': 'Invalid password or room name'
                                }
                                client_socket.send(pickle.dumps(response))
                                client_socket.close()
                    except Exception as e:
                        print(f"Auth error: {e}")
                        client_socket.close()
                        
                except BlockingIOError:
                    time.sleep(0.1)
                    continue
                
        except Exception as e:
            print(f"Wait for connection error: {e}")
            self.handle_connection_error()

    def join_game(self, host_ip, room_password, room_name):
        try:
            print(f"Trying to connect to {host_ip}:5555")
            self.socket.settimeout(5)  # 5 saniye timeout
            self.socket.connect((host_ip, 5555))
            self.socket.settimeout(None)
            
            # Oda şifresini ve ismini gönder
            auth_data = {
                'password': room_password,
                'room_name': room_name
            }
            self.socket.send(pickle.dumps(auth_data))
            
            # Yanıt bekle
            try:
                response = pickle.loads(self.socket.recv(1024))
                if isinstance(response, dict) and response.get('status') == 'accepted':
                    self.connected = True
                    self.opponent = self.socket
                    self.room_name = room_name
                    self.room_password = room_password
                    
                    # Bağlantı dinleme thread'ini başlat
                    threading.Thread(target=self.listen_for_moves, daemon=True).start()
                    return True
                else:
                    print(f"Connection rejected: {response.get('message', 'Unknown reason')}")
                    self.socket.close()
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    return False
            except (pickle.UnpicklingError, EOFError) as e:
                print(f"Response deserialization error: {e}")
                self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                return False
            
        except Exception as e:
            print(f"Connection error: {e}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return False
    
    def send_move(self, move_data):
        """Hamle verilerini gönder"""
        try:
            if self.opponent and self.connected:
                print(f"Sending move: {move_data}")
                serialized_data = pickle.dumps(move_data)
                self.opponent.sendall(serialized_data)  # sendall kullanıyoruz
                return True
        except Exception as e:
            print(f"Error sending move: {e}")
            return False

    def listen_for_moves(self):
        """Hamleleri dinle"""
        while True:  # Sonsuz döngü
            if not (self.connected and self.socket and self.opponent):
                time.sleep(0.1)
                continue
            
            try:
                ready = select.select([self.opponent], [], [], 0.1)
                if ready[0]:
                    data = self.opponent.recv(4096)
                    if not data:
                        print("Connection closed")
                        continue
                    
                    decoded_data = pickle.loads(data)
                    print(f"Received: {decoded_data}")
                    
                    if isinstance(decoded_data, dict):
                        if decoded_data.get('type') == 'START_GAME':
                            print("Received START_GAME signal")
                            self.plays_white = not decoded_data.get('host_is_white')
                            self.game_started = True
                            if hasattr(self, 'start_game_callback'):
                                self.start_game_callback()
                        else:
                            if hasattr(self, 'move_callback'):
                                self.move_callback(
                                    decoded_data['from'],
                                    decoded_data['to'],
                                    decoded_data['piece'],
                                    decoded_data['is_white_move'],
                                    decoded_data
                                )
                                print(f"Move processed: {decoded_data['from']} -> {decoded_data['to']}")
                
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(0.1)
                continue
            
            time.sleep(0.01)

    def handle_move(self, move_data):
        try:
            from_pos = move_data.get('from')
            to_pos = move_data.get('to')
            piece = move_data.get('piece')
            
            if all([from_pos, to_pos, piece]):
                print(f"Hamle alındı: {from_pos} -> {to_pos}")
                if hasattr(self, 'move_callback'):
                    try:
                        self.move_callback(from_pos, to_pos, piece)
                        print(f"Move callback executed: {from_pos} -> {to_pos}")
                    except Exception as e:
                        print(f"Error in move callback: {e}")
        except Exception as e:
            print(f"Hamle işleme hatası: {e}")

    def set_move_callback(self, callback):
        self.move_callback = callback

    def close_room(self):
        if self.is_host and self.connected:
            try:
                self.opponent.send("CLOSE_ROOM".encode())
                self.disconnect()
            except:
                pass
                
    def leave_room(self):
        if not self.is_host and self.connected:
            try:
                self.opponent.send("LEAVE_ROOM".encode())
                self.disconnect()
            except:
                pass
                
    def disconnect(self):
        self.broadcasting = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        if self.opponent and self.opponent != self.socket:
            try:
                self.opponent.close()
            except:
                pass
            self.opponent = None
        self.players.clear()

    def periodic_broadcast(self):
        while self.broadcasting:
            self.broadcast_room()
            time.sleep(1)  # Her saniye broadcast yap

    def broadcast_room(self):
        try:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            room_info = {
                'name': self.room_name,
                'password_protected': bool(self.room_password),
                'players': self.players,
                'host_ip': self.local_ip
            }
            
            data = pickle.dumps(room_info)
            # Hamachi broadcast adresi
            broadcast_socket.sendto(data, ('25.255.255.255', 5556))  # Hamachi için
            broadcast_socket.sendto(data, ('255.255.255.255', 5556)) # Normal ağ için
            broadcast_socket.close()
        except Exception as e:
            print(f"Broadcast error: {e}")

    def get_active_rooms(self):
        rooms = []
        listen_socket = None
        try:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.settimeout(1)  # 1 saniye timeout
            listen_socket.bind(('', 5556))
            
            start_time = time.time()
            while time.time() - start_time < 2:  # 2 saniye dinle
                try:
                    data, addr = listen_socket.recvfrom(1024)
                    room_info = pickle.loads(data)
                    # Aynı odayı tekrar ekleme
                    if not any(r['host_ip'] == room_info['host_ip'] for r in rooms):
                        rooms.append(room_info)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Room discovery error: {e}")
                
        except Exception as e:
            print(f"Error getting rooms: {e}")
        finally:
            if listen_socket:
                listen_socket.close()
        
        return rooms

    def handle_broadcast_request(self):
        if self.is_host:
            try:
                # Oda bilgilerini hazırla ve yayınla
                self.broadcast_room()
            except Exception as e:
                print(f"Broadcast yanıt hatası: {e}") 

    def start_game(self):
        if self.connected and self.is_host:
            try:
                print("Starting game as host...")
                self.plays_white = random.choice([True, False])
                start_data = {
                    'type': 'START_GAME',
                    'host_is_white': self.plays_white
                }
                print(f"Sending start data: {start_data}")
                
                # Start game sinyalini gönder
                if self.send_move(start_data):
                    self.game_started = True
                    if hasattr(self, 'start_game_callback'):
                        self.start_game_callback()
                    print("Game started successfully")
                    return True
                else:
                    print("Failed to send start game signal")
                    return False
            except Exception as e:
                print(f"Error starting game: {e}")
                return False
        return False

    def send_data(self, data):
        """Güvenli veri gönderme fonksiyonu"""
        try:
            if self.opponent and self.connected:
                serialized_data = pickle.dumps(data)
                # Önce veri boyutunu gönder
                size = len(serialized_data)
                self.opponent.send(struct.pack('!I', size))
                # Sonra veriyi gönder
                self.opponent.send(serialized_data)
                return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def receive_data(self):
        """Güvenli veri alma fonksiyonu"""
        try:
            # Önce veri boyutunu al
            size_data = self.opponent.recv(4)
            if not size_data:
                return None
            size = struct.unpack('!I', size_data)[0]
            
            # Veriyi parça parça al
            data = b''
            while len(data) < size:
                chunk = self.opponent.recv(min(size - len(data), 4096))
                if not chunk:
                    return None
                data += chunk
            
            return pickle.loads(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None

    def handle_connection_error(self):
        """Bağlantı hatalarını yönet"""
        print("Handling connection error...")
        try:
            if self.opponent:
                self.opponent.close()
            if self.socket:
                self.socket.close()
        except:
            pass
        
        self.connected = False
        self.game_started = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connection reset")

    def set_start_game_callback(self, callback):
        self.start_game_callback = callback 

    def send_game_start(self):
        """Oyunu başlatma sinyali gönder"""
        print("Host is starting the game...")
        return self.start_game() 