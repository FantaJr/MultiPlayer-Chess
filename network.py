import socket
import pickle
import threading
import time
import select
import random

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
            # Önce localhost'u dene, hata verirse tüm arayüzleri dene
            try:
                self.socket.bind(('127.0.0.1', port))
                self.local_ip = '127.0.0.1'
                print("Hosting on localhost")
            except:
                self.socket.bind(('0.0.0.0', port))
                hostname = socket.gethostname()
                self.local_ip = socket.gethostbyname(hostname)
                print(f"Hosting on {self.local_ip}")
            
            self.socket.listen(1)
            self.socket.setblocking(False)
            
            self.room_name = room_name
            self.room_password = room_password
            self.players.append("Host (You)")
            
            # Periyodik olarak odayı yayınla
            self.broadcasting = True
            threading.Thread(target=self.periodic_broadcast, daemon=True).start()
            
            # Bağlantı bekleme thread'i
            threading.Thread(target=self.wait_for_connection, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False

    def wait_for_connection(self):
        try:
            while not self.connected:
                try:
                    client_socket, addr = self.socket.accept()
                    
                    # Şifre kontrolü
                    password = client_socket.recv(1024).decode()
                    if password == self.room_password:
                        client_socket.send("OK".encode())
                        self.opponent = client_socket
                        self.connected = True
                        self.players.append(f"Guest ({addr[0]})")
                        print("Guest connected successfully")  # Debug için
                        threading.Thread(target=self.listen_for_moves, daemon=True).start()
                    else:
                        client_socket.send("WRONG_PASSWORD".encode())
                        client_socket.close()
                except BlockingIOError:
                    time.sleep(0.1)
                
        except Exception as e:
            print(f"Bağlantı bekleme hatası: {e}")

    def join_game(self, host_ip, room_password, room_name=None, port=5555):
        try:
            # Yeni bir soket oluştur
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            
            print(f"Connecting to {host_ip}:{port}")  # Debug için
            # Host'a bağlan
            self.socket.connect((host_ip, port))
            
            # Şifre kontrolü
            self.socket.send(room_password.encode())
            response = self.socket.recv(1024).decode()
            
            if response != "OK":
                print("Yanlış şifre!")
                self.socket.close()
                self.socket = None
                return False
            
            print("Connected successfully")  # Debug için
            # Bağlantı başarılı
            self.socket.settimeout(None)
            self.socket.setblocking(False)
            self.opponent = self.socket
            self.connected = True
            self.room_name = room_name
            self.players = ["Host", "You (Guest)"]
            
            # Dinleme thread'ini başlat
            threading.Thread(target=self.listen_for_moves, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            return False
    
    def send_move(self, move_data):
        if not self.connected:
            return False
        try:
            # Hamle verisini pickle ile serialize et
            data = pickle.dumps(move_data)
            self.opponent.send(data)
            return True
        except:
            return False
            
    def listen_for_moves(self):
        while self.connected and self.socket and self.opponent:
            try:
                ready = select.select([self.opponent], [], [], 0.1)
                if ready[0]:
                    data = self.opponent.recv(4096)
                    if not data:
                        print("Connection closed")
                        break
                    
                    try:
                        decoded_data = pickle.loads(data)
                        if isinstance(decoded_data, dict):
                            if decoded_data.get('type') == 'START_GAME':
                                print("Received START_GAME signal with color info")
                                self.plays_white = not decoded_data.get('host_is_white')
                                self.game_started = True
                                continue
                            
                            # Normal hamle verisi
                            print(f"Received move: {decoded_data}")
                            if hasattr(self, 'move_callback'):
                                self.move_callback(
                                    decoded_data['from'],
                                    decoded_data['to'],
                                    decoded_data['piece'],
                                    decoded_data['is_white_move']
                                )
                                print("Move processed")
                    except Exception as e:
                        print(f"Error processing data: {e}")
                        continue
                
            except Exception as e:
                if not isinstance(e, BlockingIOError):
                    print(f"Listen error: {e}")
                    break
            
            time.sleep(0.01)
        
        print("Connection ended")
        self.connected = False

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
            try:
                self.broadcast_room()
            except Exception as e:
                print(f"Periyodik yayın hatası: {e}")
            time.sleep(1)  # Her saniye yayınla

    def broadcast_room(self):
        try:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            room_info = {
                "name": self.room_name,
                "players": self.players,
                "password_protected": bool(self.room_password),
                "host_ip": self.local_ip
            }
            
            data = pickle.dumps(room_info)
            
            try:
                # Hem localhost hem de network broadcast
                broadcast_socket.sendto(data, ('127.0.0.1', 5555))
                broadcast_socket.sendto(data, ('255.255.255.255', 5555))
            finally:
                broadcast_socket.close()
        except Exception as e:
            print(f"Yayın hatası: {e}")

    def get_active_rooms(self):
        rooms = []
        listen_socket = None
        try:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.settimeout(1.0)
            
            # Hem localhost hem de tüm arayüzlerden dinle
            try:
                listen_socket.bind(('', 5555))
            except:
                listen_socket.bind(('127.0.0.1', 5555))
            
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            try:
                # Hem localhost hem de network'e broadcast yap
                broadcast_socket.sendto("LIST_ROOMS".encode(), ('127.0.0.1', 5555))
                broadcast_socket.sendto("LIST_ROOMS".encode(), ('255.255.255.255', 5555))
                
                start_time = time.time()
                while time.time() - start_time < 2:
                    try:
                        data, addr = listen_socket.recvfrom(8192)
                        try:
                            room_info = pickle.loads(data)
                            if isinstance(room_info, dict) and room_info.get("name"):
                                # Aynı odayı tekrar ekleme
                                if not any(r.get("name") == room_info["name"] for r in rooms):
                                    rooms.append(room_info)
                        except:
                            continue
                    except socket.timeout:
                        continue
                
            finally:
                broadcast_socket.close()
                
        except Exception as e:
            print(f"Oda listesi alınamadı: {e}")
        finally:
            if listen_socket:
                listen_socket.close()
        
        self.active_rooms = rooms
        return rooms

    def handle_broadcast_request(self):
        if self.is_host:
            try:
                # Oda bilgilerini hazırla ve yayınla
                self.broadcast_room()
            except Exception as e:
                print(f"Broadcast yanıt hatası: {e}") 

    def send_game_start(self):
        if self.connected and not self.game_started:
            try:
                print("Sending game start signal")
                self.plays_white = random.choice([True, False])  # Host için rastgele renk seç
                # Renk bilgisini de gönder
                start_data = {
                    'type': 'START_GAME',
                    'host_is_white': self.plays_white
                }
                self.opponent.send(pickle.dumps(start_data))
                self.game_started = True
                return True
            except Exception as e:
                print(f"Game start signal error: {e}")
                return False
        return False

    def set_start_game_callback(self, callback):
        self.start_game_callback = callback 