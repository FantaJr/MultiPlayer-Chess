import pygame as pg
from squares import Squares
from network import ChessNetwork
import tkinter as tk
from tkinter import messagebox, simpledialog
import time
from bot import ChessBot

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

def show_create_room_screen(screen):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    input_boxes = {
        'room_name': pg.Rect(250, 300, 300, 50),
        'password': pg.Rect(250, 400, 300, 50)
    }
    
    input_texts = {
        'room_name': '',
        'password': ''
    }
    
    active_box = None
    create_button = pg.Rect(300, 500, 200, 50)
    back_button = pg.Rect(50, 750, 200, 50)
    
    running = True
    while running:
        screen.fill((50, 50, 50))
        
        # Başlık
        title = font.render("Create Room", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 200))
        screen.blit(title, title_rect)
        
        # Input kutuları
        for box_name, box in input_boxes.items():
            color = (100, 100, 100) if box_name == active_box else (70, 70, 70)
            pg.draw.rect(screen, color, box, border_radius=10)
            
            # Placeholder text
            if not input_texts[box_name]:
                placeholder = "Room Name" if box_name == 'room_name' else "Password"
                text = small_font.render(placeholder, True, (150, 150, 150))
            else:
                text = small_font.render(input_texts[box_name], True, (255, 255, 255))
            
            text_rect = text.get_rect(center=box.center)
            screen.blit(text, text_rect)
        
        # Butonlar
        mouse_pos = pg.mouse.get_pos()
        
        # Create button
        create_color = (100, 100, 100) if create_button.collidepoint(mouse_pos) else (70, 70, 70)
        pg.draw.rect(screen, create_color, create_button, border_radius=10)
        create_text = small_font.render("Create", True, (255, 255, 255))
        create_rect = create_text.get_rect(center=create_button.center)
        screen.blit(create_text, create_rect)
        
        # Back button
        back_color = (100, 100, 100) if back_button.collidepoint(mouse_pos) else (70, 70, 70)
        pg.draw.rect(screen, back_color, back_button, border_radius=10)
        back_text = small_font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Input box tıklamaları
                    for box_name, box in input_boxes.items():
                        if box.collidepoint(event.pos):
                            active_box = box_name
                            break
                    else:
                        active_box = None
                    
                    # Create button
                    if create_button.collidepoint(event.pos):
                        if input_texts['room_name'] and input_texts['password']:
                            return input_texts['room_name'], input_texts['password']
                    
                    # Back button
                    if back_button.collidepoint(event.pos):
                        return None
            elif event.type == pg.KEYDOWN:
                if active_box:
                    if event.key == pg.K_RETURN:
                        active_box = None
                    elif event.key == pg.K_BACKSPACE:
                        input_texts[active_box] = input_texts[active_box][:-1]
                    else:
                        input_texts[active_box] += event.unicode
        
        pg.display.flip()
        pg.time.delay(50)

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
    
    if network.is_host:
        print("Host is sending start signal")
        network.start_game()
    
    running = True
    dots = 0
    last_update = time.time()
    start_time = time.time()
    
    while running:  # Timeout'u kaldırdık, host başlatana kadar bekle
        if network.game_started:  # Oyun başladı mı kontrolü
            print("Game is starting...")
            pg.time.delay(500)
            return True
        
        current_time = time.time()
        if current_time - last_update >= 0.5:
            dots = (dots + 1) % 4
            last_update = current_time
        
        screen.fill((50, 50, 50))
        
        # Loading ekranı
        title = font.render("Loading", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 300))
        screen.blit(title, title_rect)
        
        dots_text = "." * dots
        dots_surface = font.render(dots_text, True, (255, 255, 255))
        dots_rect = dots_surface.get_rect(midleft=(title_rect.right + 10, title_rect.centery))
        screen.blit(dots_surface, dots_rect)
        
        status = "Starting game..." if network.is_host else "Waiting for host to start the game"
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
    
    ready = False
    ready_button = pg.Rect(300, 500, 200, 50)
    
    def start_game_callback():
        nonlocal ready
        ready = True
    
    network.set_start_game_callback(start_game_callback)
    
    running = True
    while running:
        # Host oyunu başlattıysa lobby'den çık
        if not network.is_host and network.game_started:
            print("Host started the game, leaving lobby...")
            return False
            
        screen.fill((50, 50, 50))
        
        # Başlık
        title = font.render("Lobby", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 100))
        screen.blit(title, title_rect)
        
        # Oda bilgileri
        room_info = f"Room: {network.room_name}"
        room_text = small_font.render(room_info, True, (255, 255, 255))
        room_rect = room_text.get_rect(center=(400, 200))
        screen.blit(room_text, room_rect)
        
        # Oyuncu listesi
        y_offset = 300
        for player in network.players:
            player_text = small_font.render(player, True, (255, 255, 255))
            player_rect = player_text.get_rect(center=(400, y_offset))
            screen.blit(player_text, player_rect)
            y_offset += 50
        
        # Hazır butonu (sadece host için)
        if network.is_host:
            mouse_pos = pg.mouse.get_pos()
            button_color = (100, 100, 100) if ready else (70, 70, 70)
            if ready_button.collidepoint(mouse_pos):
                button_color = (120, 120, 120) if ready else (90, 90, 90)
            
            pg.draw.rect(screen, button_color, ready_button, border_radius=10)
            ready_text = small_font.render("Start Game" if not ready else "Starting...", True, (255, 255, 255))
            text_rect = ready_text.get_rect(center=ready_button.center)
            screen.blit(ready_text, text_rect)
        else:
            # Misafir için bekleme mesajı
            status = "Waiting for host to start the game..."
            status_text = small_font.render(status, True, (200, 200, 200))
            status_rect = status_text.get_rect(center=(400, 500))
            screen.blit(status_text, status_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                network.disconnect()
                return False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and network.is_host:  # Sol tıklama ve host ise
                    if ready_button.collidepoint(event.pos) and not ready:
                        ready = True
                        print("Host is starting the game...")
                        network.start_game()
                        return False
        
        pg.display.flip()
        pg.time.delay(50)
    
    return False

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
                
                # IP adresini göster
                ip_text = small_font.render(f"IP: {room['host_ip']}", True, (200, 200, 200))
                screen.blit(ip_text, (300, y_offset + 40))
                
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

def show_password_screen(screen):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    input_box = pg.Rect(250, 300, 300, 50)
    input_text = ''
    active = True
    
    submit_button = pg.Rect(300, 400, 200, 50)
    back_button = pg.Rect(50, 750, 200, 50)
    
    running = True
    while running:
        screen.fill((50, 50, 50))
        
        # Başlık
        title = font.render("Enter Password", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 200))
        screen.blit(title, title_rect)
        
        # Input kutusu
        color = (100, 100, 100) if active else (70, 70, 70)
        pg.draw.rect(screen, color, input_box, border_radius=10)
        
        # Şifreyi yıldızlarla göster
        display_text = '*' * len(input_text) if input_text else "Password"
        text_surface = small_font.render(display_text, True, 
                                       (255, 255, 255) if input_text else (150, 150, 150))
        text_rect = text_surface.get_rect(center=input_box.center)
        screen.blit(text_surface, text_rect)
        
        # Butonlar
        mouse_pos = pg.mouse.get_pos()
        
        # Submit button
        submit_color = (100, 100, 100) if submit_button.collidepoint(mouse_pos) else (70, 70, 70)
        pg.draw.rect(screen, submit_color, submit_button, border_radius=10)
        submit_text = small_font.render("Submit", True, (255, 255, 255))
        submit_rect = submit_text.get_rect(center=submit_button.center)
        screen.blit(submit_text, submit_rect)
        
        # Back button
        back_color = (100, 100, 100) if back_button.collidepoint(mouse_pos) else (70, 70, 70)
        pg.draw.rect(screen, back_color, back_button, border_radius=10)
        back_text = small_font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if submit_button.collidepoint(event.pos):
                        if input_text:
                            return input_text
                    elif back_button.collidepoint(event.pos):
                        return None
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    if input_text:
                        return input_text
                elif event.key == pg.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        
        pg.display.flip()
        pg.time.delay(50)

def show_difficulty_selection(screen):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    buttons = {
        "EASY": pg.Rect(250, 250, 300, 60),
        "MEDIUM": pg.Rect(250, 350, 300, 60),
        "HARD": pg.Rect(250, 450, 300, 60)
    }
    
    running = True
    while running:
        screen.fill((50, 50, 50))
        
        title = font.render("Select Difficulty", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 150))
        screen.blit(title, title_rect)
        
        mouse_pos = pg.mouse.get_pos()
        
        for text, rect in buttons.items():
            color = (100, 100, 100) if rect.collidepoint(mouse_pos) else (70, 70, 70)
            pg.draw.rect(screen, color, rect, border_radius=10)
            
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.MOUSEBUTTONDOWN:
                for difficulty, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return difficulty
        
        pg.display.flip()

def show_elo_selection(screen):
    font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 36)
    
    # Slider özellikleri
    slider_rect = pg.Rect(250, 300, 400, 10)
    slider_button_radius = 15
    slider_pos = 250  # Başlangıç pozisyonu
    dragging = False
    
    # ELO aralığı
    min_elo = 400
    max_elo = 3000
    current_elo = 1500  # Başlangıç ELO'su
    
    # Start butonu
    start_button = pg.Rect(350, 500, 200, 50)
    
    running = True
    while running:
        screen.fill((50, 50, 50))
        
        # Başlık
        title = font.render("Select Bot ELO", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 150))
        screen.blit(title, title_rect)
        
        # Mevcut ELO'yu göster
        elo_text = font.render(f"ELO: {current_elo}", True, (255, 255, 255))
        elo_rect = elo_text.get_rect(center=(400, 250))
        screen.blit(elo_text, elo_rect)
        
        # Slider'ı çiz
        pg.draw.rect(screen, (100, 100, 100), slider_rect)
        
        # Slider düğmesini çiz
        button_pos = (slider_pos, slider_rect.centery)
        pg.draw.circle(screen, (200, 200, 200), button_pos, slider_button_radius)
        
        # Start butonunu çiz
        mouse_pos = pg.mouse.get_pos()
        button_color = (100, 100, 100) if start_button.collidepoint(mouse_pos) else (70, 70, 70)
        pg.draw.rect(screen, button_color, start_button, border_radius=10)
        
        start_text = small_font.render("Start Game", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_rect)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
                
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Slider düğmesi tıklaması
                    button_rect = pg.Rect(slider_pos - slider_button_radius,
                                        slider_rect.centery - slider_button_radius,
                                        slider_button_radius * 2,
                                        slider_button_radius * 2)
                    if button_rect.collidepoint(event.pos):
                        dragging = True
                    
                    # Start butonu tıklaması
                    elif start_button.collidepoint(event.pos):
                        return current_elo
            
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            
            elif event.type == pg.MOUSEMOTION:
                if dragging:
                    slider_pos = max(slider_rect.left,
                                   min(event.pos[0], slider_rect.right))
                    # ELO'yu hesapla
                    elo_range = max_elo - min_elo
                    slider_range = slider_rect.width
                    current_elo = min_elo + int((slider_pos - slider_rect.left) 
                                              * elo_range / slider_range)
                    current_elo = (current_elo // 50) * 50  # 50'lik adımlarla yuvarla
        
        pg.display.flip()

def start_game():
    pg.init()
    # Ekranı 900 pixel genişliğe çıkaralım
    screen = pg.display.set_mode((900, 850))
    pg.display.set_caption("Chess")
    
    while True:
        game_mode = show_main_menu(screen)
        if game_mode is None:
            break
            
        network = None
        try:
            if game_mode == "Multiplayer":
                while True:
                    result = show_rooms_list(screen)
                    if result is None:
                        break
                    elif result == "back":
                        break
                    elif result == "create":
                        room_name, room_password = show_create_room_screen(screen)
                        if room_name and room_password:
                            network = ChessNetwork(is_host=True)
                            if network.host_game(room_name, room_password):
                                if show_lobby(network, screen):
                                    continue
                                if network.game_started:  # Oyun başladıysa
                                    squares = Squares(screen, network)
                                    run_game(screen, squares, network)
                                break
                    elif isinstance(result, tuple) and result[0] == "join":
                        room = result[1]
                        password = show_password_screen(screen)
                        if not password:
                            continue
                        
                        network = ChessNetwork(is_host=False)
                        if network.join_game(host_ip=room["host_ip"], 
                                          room_password=password or "",
                                          room_name=room["name"]):
                            if show_lobby(network, screen):
                                continue
                            if network.game_started:  # Oyun başladıysa
                                squares = Squares(screen, network)
                                run_game(screen, squares, network)
                            break
            elif game_mode == "Singleplayer":
                elo = show_elo_selection(screen)
                if elo:
                    bot = ChessBot(elo=elo)
                    squares = Squares(screen, bot=bot)
                    run_game(screen, squares, None)
            else:  # Singleplayer
                squares = Squares(screen)
                run_game(screen, squares, None)
                
        finally:
            if network:
                network.disconnect()

    pg.quit()

def run_game(screen, squares, network):
    """Oyun döngüsünü çalıştır"""
    clock = pg.time.Clock()
    running = True
    game_ended = False
    menu_button = None
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tuş
                    if game_ended and menu_button and menu_button.collidepoint(event.pos):
                        return  # Ana menüye dön
                    elif not game_ended:
                        if squares.selected_piece:
                            squares.movePiece(event.pos[0], event.pos[1])
                        else:
                            squares.selectPiece(event.pos[0], event.pos[1])
        
        # Ekranı güncelle
        screen.fill((0, 0, 0))
        squares.drawBoard()
        
        # Oyun sonu kontrolü
        if not game_ended:
            menu_button = squares.show_game_end_screen()
            if menu_button:
                game_ended = True
        elif game_ended:
            menu_button = squares.show_game_end_screen()
        
        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    start_game()
