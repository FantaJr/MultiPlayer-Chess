import pygame as pg
from squares import Squares
from network import ChessNetwork
import tkinter as tk
from tkinter import messagebox, simpledialog
import time

def show_main_menu(screen):
    # Ana menüyü pygame penceresinde göster
    font = pg.font.Font(None, 50)
    
    buttons = {
        "Singleplayer": pg.Rect(250, 300, 300, 60),
        "Multiplayer": pg.Rect(250, 400, 300, 60)
    }
    
    running = True
    while running:
        screen.fill((50, 50, 50))  # Koyu gri arkaplan
        
        # Başlık
        title = font.render("Chess Game", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 200))
        screen.blit(title, title_rect)
        
        mouse_pos = pg.mouse.get_pos()
        
        for text, rect in buttons.items():
            # Buton üzerinde mouse varsa rengi değiştir
            color = (100, 100, 100) if rect.collidepoint(mouse_pos) else (70, 70, 70)
            pg.draw.rect(screen, color, rect, border_radius=10)
            
            # Buton metni
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for text, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            return text
        
        pg.display.flip()

def show_multiplayer_options():
    root = tk.Tk()
    root.withdraw()
    
    options = ["Oda Kur", "Odaya Katıl"]
    option_window = tk.Toplevel(root)
    option_window.title("Multiplayer Options")
    option_window.geometry("300x150")
    option_window.resizable(False, False)
    
    selected_option = [None]
    
    def select_option(option):
        selected_option[0] = option
        option_window.destroy()
        root.quit()
    
    tk.Label(option_window, text="Multiplayer Seçeneği", font=('Arial', 14)).pack(pady=10)
    
    for option in options:
        tk.Button(option_window, text=option, width=20,
                 command=lambda o=option: select_option(o)).pack(pady=5)
    
    option_window.protocol("WM_DELETE_WINDOW", lambda: select_option(None))
    
    root.mainloop()
    return selected_option[0]

def show_create_room_dialog():
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("Oda Oluştur")
    dialog.geometry("300x200")
    dialog.resizable(False, False)
    
    room_info = {'name': None, 'password': None}
    
    tk.Label(dialog, text="Oda Adı:", font=('Arial', 12)).pack(pady=5)
    name_entry = tk.Entry(dialog, width=30)
    name_entry.pack(pady=5)
    
    tk.Label(dialog, text="Şifre:", font=('Arial', 12)).pack(pady=5)
    pass_entry = tk.Entry(dialog, width=30, show="*")
    pass_entry.pack(pady=5)
    
    def confirm():
        room_info['name'] = name_entry.get()
        room_info['password'] = pass_entry.get()
        if room_info['name'] and room_info['password']:
            dialog.destroy()
            root.quit()
    
    tk.Button(dialog, text="Oda Kur", width=20, command=confirm).pack(pady=20)
    
    dialog.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    
    return room_info['name'], room_info['password']

def show_join_room_dialog():
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("Odaya Katıl")
    dialog.geometry("300x250")
    dialog.resizable(False, False)
    
    room_info = {'name': None, 'password': None}
    
    tk.Label(dialog, text="Oda Adı:", font=('Arial', 12)).pack(pady=5)
    name_entry = tk.Entry(dialog, width=30)
    name_entry.pack(pady=5)
    
    tk.Label(dialog, text="Şifre:", font=('Arial', 12)).pack(pady=5)
    pass_entry = tk.Entry(dialog, width=30, show="*")
    pass_entry.pack(pady=5)
    
    def confirm():
        room_info['name'] = name_entry.get()
        room_info['password'] = pass_entry.get()
        if room_info['name'] and room_info['password']:
            dialog.destroy()
            root.quit()
    
    tk.Button(dialog, text="Katıl", width=20, command=confirm).pack(pady=20)
    
    dialog.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    
    return room_info['name'], room_info['password']

def show_loading_screen(screen, network):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    game_started = [False]  # Thread'den değiştirebilmek için liste kullanıyoruz
    
    def on_game_start():
        game_started[0] = True
    
    network.set_start_game_callback(on_game_start)
    
    # Host ise oyunu başlat
    if network.is_host:
        network.send_game_start()
    
    running = True
    dots = 0
    last_update = time.time()
    
    while running:
        if game_started[0]:
            return True  # Oyunu başlat
            
        current_time = time.time()
        if current_time - last_update >= 0.5:  # Her 0.5 saniyede bir noktaları güncelle
            dots = (dots + 1) % 4
            last_update = current_time
        
        screen.fill((50, 50, 50))
        
        # Başlık
        title = font.render("Loading", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 300))
        screen.blit(title, title_rect)
        
        # Animasyonlu noktalar
        dots_text = "." * dots
        dots_surface = font.render(dots_text, True, (255, 255, 255))
        dots_rect = dots_surface.get_rect(midleft=(title_rect.right + 10, title_rect.centery))
        screen.blit(dots_surface, dots_rect)
        
        # Bekleme mesajı
        if network.is_host:
            status = "Waiting for guest to connect"
        else:
            status = "Waiting for host to start the game"
        
        status_text = small_font.render(status, True, (200, 200, 200))
        status_rect = status_text.get_rect(center=(400, 400))
        screen.blit(status_text, status_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                network.disconnect()
                return False
        
        pg.display.flip()
        pg.time.delay(50)
    
    return False

def show_lobby(network, screen):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    # Butonlar - her frame'de yeniden oluşturmak yerine sabit tut
    buttons = {
        "Back": pg.Rect(50, 750, 200, 50)
    }
    
    # Host için Start Game butonu
    if network.is_host:
        buttons["Start Game"] = pg.Rect(550, 750, 200, 50)
    else:
        buttons["Waiting..."] = pg.Rect(550, 750, 200, 50)
    
    # Oyuncu kartları için dikdörtgenler
    player_cards = [
        pg.Rect(250, 250, 300, 100),  # Host
        pg.Rect(250, 400, 300, 100)   # Guest
    ]
    
    running = True
    while running:
        # Her frame'de bağlantı durumunu kontrol et
        if not network.connected and not network.is_host:
            return True  # Misafir oyuncu için bağlantı koptuğunda ana menüye dön
            
        screen.fill((50, 50, 50))
        
        # Başlık ve Oda Bilgileri
        title = font.render("Lobby", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 100))
        screen.blit(title, title_rect)
        
        room_info = small_font.render(f"Room: {network.room_name}", True, (255, 255, 255))
        screen.blit(room_info, (50, 170))
        
        if network.is_host:
            ip_info = small_font.render(f"IP: {network.local_ip}", True, (200, 200, 200))
            screen.blit(ip_info, (50, 200))
            
            # Host için bekleme mesajı
            if not network.connected:
                waiting_text = small_font.render("Waiting for player to join...", True, (255, 200, 0))
                screen.blit(waiting_text, (50, 230))
        
        # Oyuncu Kartları
        for i, card_rect in enumerate(player_cards):
            color = (70, 70, 70)
            pg.draw.rect(screen, color, card_rect, border_radius=10)
            
            if i < len(network.players):
                player_text = small_font.render(network.players[i], True, (255, 255, 255))
                status_text = small_font.render("Ready ✓", True, (0, 255, 0))
            else:
                player_text = small_font.render("Waiting for player...", True, (150, 150, 150))
                status_text = small_font.render("Not Connected", True, (255, 150, 0))
            
            text_rect = player_text.get_rect(midleft=(card_rect.x + 20, card_rect.centery - 15))
            status_rect = status_text.get_rect(midleft=(card_rect.x + 20, card_rect.centery + 15))
            screen.blit(player_text, text_rect)
            screen.blit(status_text, status_rect)
        
        # Butonlar
        mouse_pos = pg.mouse.get_pos()
        for text, rect in buttons.items():
            # Start Game butonu için özel durum
            if text == "Start Game" and network.is_host:
                # İki oyuncu da hazırsa butonu aktif göster
                color = (100, 200, 100) if network.connected else (100, 100, 100)
                if rect.collidepoint(mouse_pos) and network.connected:
                    color = (120, 220, 120)
            else:
                color = (100, 100, 100) if rect.collidepoint(mouse_pos) else (70, 70, 70)
            
            pg.draw.rect(screen, color, rect, border_radius=10)
            text_surface = small_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        
        # Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                network.disconnect()
                return False
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if buttons["Back"].collidepoint(event.pos):
                        network.disconnect()
                        return True
                    elif network.is_host and "Start Game" in buttons:
                        if buttons["Start Game"].collidepoint(event.pos):
                            if network.connected:
                                if show_loading_screen(screen, network):  # Loading ekranını göster
                                    return False  # Oyunu başlat
                                return True  # Loading iptal edildi, ana menüye dön
        
        pg.display.flip()
        pg.time.delay(50)

def show_rooms_list(screen):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    buttons = {
        "Back": pg.Rect(50, 750, 200, 50),
        "Create Room": pg.Rect(550, 750, 200, 50),
        "Refresh": pg.Rect(300, 750, 200, 50)
    }
    
    # Ağ işlemleri için network nesnesi - parametre vermeden oluştur
    network = ChessNetwork()  # Varsayılan olarak is_host=False
    active_rooms = []
    selected_room = None
    
    # İlk oda listesini al
    active_rooms = network.get_active_rooms()
    last_refresh = time.time()
    
    running = True
    while running:
        # Her 2 saniyede bir otomatik yenile
        if time.time() - last_refresh > 2:
            active_rooms = network.get_active_rooms()
            last_refresh = time.time()
        
        screen.fill((50, 50, 50))
        
        # Başlık
        title = font.render("Available Rooms", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 50))
        screen.blit(title, title_rect)
        
        # Oda listesi alanı
        room_list_rect = pg.Rect(50, 100, 700, 600)
        pg.draw.rect(screen, (70, 70, 70), room_list_rect, border_radius=10)
        
        if not active_rooms:
            # Oda yoksa mesaj göster
            no_rooms_text = small_font.render("No active rooms found", True, (150, 150, 150))
            text_rect = no_rooms_text.get_rect(center=(400, 400))
            screen.blit(no_rooms_text, text_rect)
        else:
            # Odaları listele
            y_offset = 120
            for room in active_rooms:
                room_rect = pg.Rect(60, y_offset, 680, 80)
                color = (100, 100, 100) if room == selected_room else (80, 80, 80)
                pg.draw.rect(screen, color, room_rect, border_radius=5)
                
                # Oda bilgileri
                name_text = small_font.render(room["name"], True, (255, 255, 255))
                screen.blit(name_text, (80, y_offset + 10))
                
                players_text = small_font.render(f"Players: {len(room['players'])}/2", True, (200, 200, 200))
                screen.blit(players_text, (80, y_offset + 40))
                
                lock_text = "🔒" if room["password_protected"] else "🔓"
                lock_surface = small_font.render(lock_text, True, (255, 255, 0) if room["password_protected"] else (100, 100, 100))
                screen.blit(lock_surface, (650, y_offset + 25))
                
                y_offset += 100
        
        # Butonlar
        mouse_pos = pg.mouse.get_pos()
        for text, rect in buttons.items():
            color = (100, 100, 100) if rect.collidepoint(mouse_pos) else (70, 70, 70)
            pg.draw.rect(screen, color, rect, border_radius=10)
            
            text_surface = small_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        
        # Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Buton tıklamaları
                    if buttons["Back"].collidepoint(event.pos):
                        return "back"
                    elif buttons["Create Room"].collidepoint(event.pos):
                        return "create"
                    elif buttons["Refresh"].collidepoint(event.pos):
                        active_rooms = network.get_active_rooms()
                    
                    # Oda seçimi
                    y_offset = 120
                    for room in active_rooms:
                        room_rect = pg.Rect(60, y_offset, 680, 80)
                        if room_rect.collidepoint(event.pos):
                            selected_room = room
                            return ("join", room)
                        y_offset += 100
        
        pg.display.flip()

def show_password_dialog():
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("Oda Şifresi")
    dialog.geometry("300x150")
    dialog.resizable(False, False)
    
    password = [None]  # Liste içinde değer kullanarak nonlocal kullanmaktan kaçınıyoruz
    
    tk.Label(dialog, text="Oda Şifresi:", font=('Arial', 12)).pack(pady=10)
    
    pass_entry = tk.Entry(dialog, width=30, show="*")
    pass_entry.pack(pady=5)
    
    def confirm():
        if pass_entry.get():
            password[0] = pass_entry.get()
            dialog.destroy()
            root.quit()
    
    tk.Button(dialog, text="Giriş", width=20, command=confirm).pack(pady=20)
    
    dialog.protocol("WM_DELETE_WINDOW", lambda: [setattr(root, 'quit', lambda: None), dialog.destroy()])
    
    root.mainloop()
    return password[0]

def start_game():
    pg.init()
    screen = pg.display.set_mode((800, 850))
    pg.display.set_caption("Chess")
    
    while True:  # Ana menüye dönüş için sonsuz döngü
        # Ana menüyü göster
        game_mode = show_main_menu(screen)
        if game_mode is None:  # Pencere kapatıldıysa
            break
            
        network = None
        if game_mode == "Multiplayer":
            while True:
                result = show_rooms_list(screen)
                if result is None:  # Pencere kapatıldı
                    break
                elif result == "back":
                    break
                elif result == "create":
                    room_name, room_password = show_create_room_dialog()
                    if room_name and room_password:
                        network = ChessNetwork(is_host=True)  # Host için is_host=True
                        if network.host_game(room_name, room_password):
                            if show_lobby(network, screen):
                                continue
                            break
                elif isinstance(result, tuple) and result[0] == "join":
                    room = result[1]
                    password = None
                    if room["password_protected"]:
                        password = show_password_dialog()
                        if not password:
                            continue
                    
                    network = ChessNetwork(is_host=False)  # Misafir için is_host=False
                    if network.join_game(host_ip=room["host_ip"], 
                                        room_password=password or "",
                                        room_name=room["name"]):  # Oda adını da gönder
                        if show_lobby(network, screen):
                            continue
                        break
        
        # Oyunu başlat
        clock = pg.time.Clock()
        squares = Squares(screen, network)
        
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Sol tuş
                        if squares.selected_piece:
                            # Şah durumunu kontrol et
                            if squares.is_in_check():
                                # Sadece şahı kurtaracak hamlelere izin ver
                                if squares.is_valid_check_move(event.pos[0], event.pos[1]):
                                    squares.movePiece(event.pos[0], event.pos[1])
                                squares.selected_piece = None
                            else:
                                squares.movePiece(event.pos[0], event.pos[1])
                        else:
                            squares.selectPiece(event.pos[0], event.pos[1])
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_u:  # Geri alma tuşu
                        squares.undoMove()

            screen.fill((0, 0, 0))
            squares.drawBoard()
            pg.display.flip()
            clock.tick(144)

        if network:
            network.socket.close()

    pg.quit()

if __name__ == "__main__":
    start_game()
