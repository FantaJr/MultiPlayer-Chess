import pygame as pg
from rules import is_valid_move, is_check, Rules

class Squares:
    def __init__(self, root, network=None, bot=None):
        self.root = root
        self.network = network
        self.bot = bot  # Bot nesnesini ekle
        
        # Eğer ağ bağlantısı varsa ve beyaz değilsek tahtayı ters çevir
        self.is_white = network.plays_white if network else True
        self.board_flipped = network and not self.is_white if network else False
        
        # Pozisyonları başlat
        self.positions = self.initialize_positions()
        self.font = pg.font.Font(None, 36)
        self.selected_piece = None
        self.selected_piece_pos = None
        self.move_history = []
        
        # Beyaz her zaman başlar
        self.turn = 'WHITE'
        
        # Olası hamleleri tutmak için tuple (normal hamleler, rook hamleleri)
        self.possible_moves = ([], [])
        
        # Yenilen taşları tutmak için listeler
        self.captured_white_pieces = []
        self.captured_black_pieces = []
        
        # Network varsa hamle callback'ini ayarla
        if network:
            network.set_move_callback(self.handle_opponent_move)

    def initialize_positions(self):
        # Tahtanın gerçek durumu - değişmez pozisyonlar
        positions = {
            "a1": "W_ROOK", "b1": "W_KNIGHT", "c1": "W_BISHOP", "d1": "W_QUEEN",
            "e1": "W_KING", "f1": "W_BISHOP", "g1": "W_KNIGHT", "h1": "W_ROOK",
            "a2": "W_PAWN", "b2": "W_PAWN", "c2": "W_PAWN", "d2": "W_PAWN",
            "e2": "W_PAWN", "f2": "W_PAWN", "g2": "W_PAWN", "h2": "W_PAWN",
            
            "a7": "pawn", "b7": "pawn", "c7": "pawn", "d7": "pawn",
            "e7": "pawn", "f7": "pawn", "g7": "pawn", "h7": "pawn",
            "a8": "rook", "b8": "knight", "c8": "bishop", "d8": "queen",
            "e8": "king", "f8": "bishop", "g8": "knight", "h8": "rook"
        }
        
        # Boş kareleri ekle
        for rank in range(3, 7):
            for file in 'abcdefgh':
                positions[f"{file}{rank}"] = None
        
        return positions

    def drawBoard(self):
        square_size = 100
        
        # Tahta yüzeyini oluştur
        board_surface = pg.Surface((800, 800))
        
        # Tahtayı çiz
        for row in range(8):
            for col in range(8):
                # Kare rengini belirle
                color = (255, 255, 255) if (row + col) % 2 == 0 else (0, 0, 0)
                pg.draw.rect(board_surface, color, (col * square_size, row * square_size, square_size, square_size))

                # Pozisyonu hesapla
                file = chr(col + ord('a'))
                rank = str(8 - row)
                pos = file + rank

                # Olası hamleleri göster
                if pos in self.possible_moves[0]:  # Normal hamleler
                    surface = pg.Surface((square_size, square_size), pg.SRCALPHA)
                    pg.draw.circle(surface, (0, 255, 0, 128), (square_size//2, square_size//2), 15)
                    board_surface.blit(surface, (col * square_size, row * square_size))
                elif pos in self.possible_moves[1]:  # Rook hamleleri
                    surface = pg.Surface((square_size, square_size), pg.SRCALPHA)
                    pg.draw.circle(surface, (255, 100, 100, 128), (square_size//2, square_size//2), 15)
                    board_surface.blit(surface, (col * square_size, row * square_size))

                # Taşları çiz
                piece = self.positions.get(pos)
                if piece and (pos != self.selected_piece_pos):
                    png = pg.image.load(f'assets/{piece}.png')
                    png = pg.transform.scale(png, (100, 100))
                    if self.board_flipped:
                        png = pg.transform.rotate(png, 180)
                    board_surface.blit(png, (col * square_size, row * square_size))

        # Siyah oyuncu için tahtayı 180 derece döndür
        if self.board_flipped:
            board_surface = pg.transform.rotate(board_surface, 180)

        # Tahtayı ekrana çiz
        self.root.blit(board_surface, (0, 0))

        # Seçili taşı fareyle birlikte çiz (her zaman düz)
        if self.selected_piece:
            mouse_x, mouse_y = pg.mouse.get_pos()
            png = pg.image.load(f'assets/{self.selected_piece}.png')
            png = pg.transform.scale(png, (100, 100))
            self.root.blit(png, (mouse_x - 50, mouse_y - 50))

        # Sıra göstergesi
        turn_text = "Your turn" if ((self.turn == 'WHITE' and self.is_white) or 
                                   (self.turn == 'BLACK' and not self.is_white)) else "Opponent's turn"
        text_surface = self.font.render(turn_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 825))
        self.root.blit(text_surface, text_rect)

        # Yenilen taşları çiz
        piece_size = 40  # Yenilen taşların boyutu
        x_offset = 810  # Sağ taraftaki başlangıç pozisyonu
        
        # Başlıkları çiz
        title_font = pg.font.Font(None, 30)
        white_title = title_font.render("Captured White Pieces", True, (255, 255, 255))
        black_title = title_font.render("Captured Black Pieces", True, (255, 255, 255))
        self.root.blit(white_title, (x_offset, 20))
        self.root.blit(black_title, (x_offset, 420))
        
        # Beyaz taşları çiz
        for i, piece in enumerate(self.captured_white_pieces):
            y_pos = 60 + (i // 2) * (piece_size + 5)  # Her satırda 2 taş
            x_pos = x_offset + (i % 2) * (piece_size + 5)
            
            png = pg.image.load(f'assets/{piece}.png')
            png = pg.transform.scale(png, (piece_size, piece_size))
            if self.board_flipped:  # Siyah oyuncu için taşları çevir
                png = pg.transform.rotate(png, 180)
            self.root.blit(png, (x_pos, y_pos))
        
        # Siyah taşları çiz
        for i, piece in enumerate(self.captured_black_pieces):
            y_pos = 460 + (i // 2) * (piece_size + 5)  # Her satırda 2 taş
            x_pos = x_offset + (i % 2) * (piece_size + 5)
            
            png = pg.image.load(f'assets/{piece}.png')
            png = pg.transform.scale(png, (piece_size, piece_size))
            if self.board_flipped:  # Siyah oyuncu için taşları çevir
                png = pg.transform.rotate(png, 180)
            self.root.blit(png, (x_pos, y_pos))

    def convert_mouse_position(self, x, y):
        """Mouse koordinatlarını tahta koordinatlarına çevirir"""
        col = x // 100
        row = y // 100
        
        if self.board_flipped:
            # Siyah için koordinatları ters çevir
            file = chr((7 - col) + ord('a'))
            rank = str(row + 1)
        else:
            file = chr(col + ord('a'))
            rank = str(8 - row)
        
        return file + rank

    def get_possible_moves(self, piece, start_pos):
        possible_moves = []
        castle_moves = []

        # Şah durumunu kontrol et
        is_in_check = Rules.is_check(self.positions, self.turn)

        # Normal hamleleri kontrol et
        for row in range(8):
            for col in range(8):
                end_pos = f"{chr(col + ord('a'))}{8 - row}"
                
                # Hamlenin geçerli olup olmadığını kontrol et
                if Rules.is_valid_move(piece, start_pos, end_pos, self.positions):
                    # Hamlenin şah durumunu çözüp çözmediğini kontrol et
                    temp_positions = self.positions.copy()
                    temp_positions[end_pos] = piece
                    temp_positions[start_pos] = None
                    
                    if not Rules.is_check(temp_positions, self.turn):
                        possible_moves.append(end_pos)

        # Eğer şah durumu yoksa ve şah ilk pozisyonundaysa rook kontrolü yap
        if not is_in_check and piece.endswith('KING'):
            king_pos = 'e1' if self.is_white else 'e8'
            if start_pos == king_pos:
                # Sağa rook kontrolü
                right_rook_pos = 'h1' if self.is_white else 'h8'
                if self.can_castle(king_pos, right_rook_pos):
                    castle_moves.append('g1' if self.is_white else 'g8')
                
                # Sola rook kontrolü
                left_rook_pos = 'a1' if self.is_white else 'a8'
                if self.can_castle(king_pos, left_rook_pos):
                    castle_moves.append('c1' if self.is_white else 'c8')

        return possible_moves, castle_moves

    def selectPiece(self, x, y):
        # Sıra kontrolü - sadece network varsa kontrol et
        if self.network and ((self.turn == 'WHITE' and not self.is_white) or 
                            (self.turn == 'BLACK' and self.is_white)):
            return

        position = self.convert_mouse_position(x, y)

        if self.selected_piece:
            self.selected_piece = None
            self.selected_piece_pos = None
            self.possible_moves = ([], [])
            return

        self.selected_piece_pos = position
        self.selected_piece = self.positions.get(self.selected_piece_pos)

        if self.selected_piece:
            # Singleplayer'da sıra kontrolü
            if not self.network:
                is_white_piece = self.selected_piece.startswith('W_')
                if (is_white_piece and self.turn == 'BLACK') or (not is_white_piece and self.turn == 'WHITE'):
                    self.selected_piece = None
                    self.selected_piece_pos = None
                    self.possible_moves = ([], [])
                    return
            else:
                # Multiplayer sıra kontrolü
                is_white_piece = self.selected_piece.startswith('W_')
                if (is_white_piece != self.is_white):
                    self.selected_piece = None
                    self.selected_piece_pos = None
                    self.possible_moves = ([], [])
                    return
                
            self.possible_moves = self.get_possible_moves(self.selected_piece, self.selected_piece_pos)

    def is_in_check(self):
        return Rules.is_check(self.positions, self.turn)

    def is_valid_check_move(self, x, y):
        if not self.selected_piece:
            return False
        
        file = chr(x // 100 + ord('a'))
        rank = str(8 - y // 100)
        target_pos = file + rank
        
        # Hamlenin kural olarak geçerli olup olmadığını kontrol et
        if not is_valid_move(self.selected_piece, self.selected_piece_pos, target_pos, self.positions):
            return False
        
        # Hamlenin şah durumunu kurtarıp kurtarmadığını kontrol et
        temp_positions = self.positions.copy()
        temp_positions[target_pos] = self.selected_piece
        temp_positions[self.selected_piece_pos] = None
        
        # Şah durumu devam ediyor mu kontrol et
        still_in_check = Rules.is_check(temp_positions, self.turn)
        
        return not still_in_check

    def can_castle(self, king_pos, rook_pos):
        """Rook atma kontrolü"""
        # Şah ve kale ilk pozisyonlarında mı kontrol et
        if self.is_white:
            if king_pos != 'e1' or (rook_pos != 'a1' and rook_pos != 'h1'):
                return False
            # Şah ve kaleler doğru pozisyonlarda mı
            if (rook_pos == 'a1' and self.positions.get('a1') != 'W_ROOK') or \
               (rook_pos == 'h1' and self.positions.get('h1') != 'W_ROOK') or \
               self.positions.get('e1') != 'W_KING':
                return False
        else:
            if king_pos != 'e8' or (rook_pos != 'a8' and rook_pos != 'h8'):
                return False
            # Şah ve kaleler doğru pozisyonlarda mı
            if (rook_pos == 'a8' and self.positions.get('a8') != 'rook') or \
               (rook_pos == 'h8' and self.positions.get('h8') != 'rook') or \
               self.positions.get('e8') != 'king':
                return False
        
        # Şah ve kale arasında taş var mı kontrol et
        king_col = ord(king_pos[0]) - ord('a')
        rook_col = ord(rook_pos[0]) - ord('a')
        row = king_pos[1]
        
        # Sağa mı sola mı rook yapılacak
        direction = 1 if rook_col > king_col else -1
        
        # Aradaki kareleri kontrol et
        for col in range(king_col + direction, rook_col, direction):
            pos = f"{chr(col + ord('a'))}{row}"
            if self.positions[pos] is not None:
                return False
        
        # Şahın geçeceği karelerin tehdit altında olup olmadığını kontrol et
        if direction == 1:  # Sağa rook
            check_squares = [f"f{row}", f"g{row}"]
        else:  # Sola rook
            check_squares = [f"c{row}", f"d{row}"]
        
        temp_positions = self.positions.copy()
        for square in check_squares:
            temp_positions[king_pos] = None
            temp_positions[square] = 'W_KING' if self.is_white else 'king'
            if Rules.is_check(temp_positions, self.turn):
                return False
            temp_positions[square] = None
        temp_positions[king_pos] = 'W_KING' if self.is_white else 'king'
        
        return True

    def movePiece(self, x, y):
        # Sıra kontrolü - sadece network varsa kontrol et
        if self.network:
            is_my_turn = (self.turn == 'WHITE' and self.is_white) or (self.turn == 'BLACK' and not self.is_white)
            if not is_my_turn:
                print(f"Not your turn! Current turn: {self.turn}, You are: {'white' if self.is_white else 'black'}")
                return

        if not self.selected_piece:
            return

        target_pos = self.convert_mouse_position(x, y)
        print(f"Moving to: {target_pos}")

        # Eğer aynı kareye tıklandıysa, seçimi iptal et
        if target_pos == self.selected_piece_pos:
            self.selected_piece = None
            self.selected_piece_pos = None
            self.possible_moves = ([], [])
            return

        # Eğer hedef pozisyon olası hamleler içinde değilse, hamleyi iptal et
        if target_pos not in self.possible_moves[0] and target_pos not in self.possible_moves[1]:
            self.selected_piece = None
            self.selected_piece_pos = None
            self.possible_moves = ([], [])
            return

        # Hamleyi yap
        moving_piece = self.positions[self.selected_piece_pos]
        captured_piece = self.positions.get(target_pos)

        if captured_piece:
            if captured_piece.startswith('W_'):
                self.captured_white_pieces.append(captured_piece)
            else:
                self.captured_black_pieces.append(captured_piece)

        self.positions[target_pos] = moving_piece
        self.positions[self.selected_piece_pos] = None
        
        # Sırayı değiştir
        self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'

        # Network varsa hamleyi gönder
        if self.network and self.network.connected:
            move_data = {
                'from': self.selected_piece_pos,
                'to': target_pos,
                'piece': moving_piece,
                'is_white_move': self.is_white,
                'captured_piece': captured_piece if captured_piece else None
            }
            self.network.send_move(move_data)

        # Seçimi temizle
        self.selected_piece = None
        self.selected_piece_pos = None
        self.possible_moves = ([], [])

        # Hamle yapıldıktan sonra, eğer bot varsa ve sıra siyahtaysa
        if not self.network and self.bot and self.turn == 'BLACK':
            # Kısa bir gecikme ekle
            pg.time.delay(500)
            # Bot hamlesi
            bot_move = self.bot.get_move(self.positions, self.turn)
            if bot_move:
                start_pos, end_pos, piece = bot_move
                # Bot hamlesini uygula
                captured_piece = self.positions.get(end_pos)
                if captured_piece:
                    if captured_piece.startswith('W_'):
                        self.captured_white_pieces.append(captured_piece)
                    else:
                        self.captured_black_pieces.append(captured_piece)
                
                self.positions[end_pos] = piece
                self.positions[start_pos] = None
                self.turn = 'WHITE'

    def undoMove(self):
        if not self.move_history:
            return

        # Hamle geçmişinden son hamleyi al
        old_pos, new_pos = self.move_history.pop()
        
        # Taşı eski konumuna geri al
        self.positions[old_pos] = self.positions[new_pos]
        self.positions[new_pos] = None
        
        # Sırayı değiştir
        self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'

    def handle_opponent_move(self, from_pos, to_pos, piece, is_white_move, move_data=None):
        print(f"Handling opponent move: {from_pos} -> {to_pos}")
        try:
            # Yenilen taş varsa kaydet
            captured_piece = self.positions.get(to_pos)
            if captured_piece:
                if is_white_move:
                    self.captured_black_pieces.append(captured_piece)
                else:
                    self.captured_white_pieces.append(captured_piece)

            # Normal hamle
            self.positions[from_pos] = None
            self.positions[to_pos] = piece
            
            # Sırayı değiştir
            old_turn = self.turn
            self.turn = 'WHITE' if self.turn == 'BLACK' else 'BLACK'
            print(f"Turn changed from {old_turn} to {self.turn}")
        except Exception as e:
            print(f"Error handling opponent move: {e}")

    def check_game_end(self):
        """Oyunun bitip bitmediğini kontrol et"""
        # Şah mat kontrolü
        if Rules.is_check(self.positions, self.turn):
            # Kurtuluş hamlesi var mı kontrol et
            for start_pos, piece in self.positions.items():
                if piece:
                    is_white_piece = piece.startswith('W_')
                    if (self.turn == 'WHITE' and is_white_piece) or (self.turn == 'BLACK' and not is_white_piece):
                        for end_pos in self.positions.keys():
                            if Rules.is_valid_move(piece, start_pos, end_pos, self.positions):
                                # Hamleyi dene
                                temp_positions = self.positions.copy()
                                temp_positions[end_pos] = piece
                                temp_positions[start_pos] = None
                                if not Rules.is_check(temp_positions, self.turn):
                                    return None  # Kurtuluş hamlesi var
        
            # Kurtuluş hamlesi yoksa şah mat
            winner = "Black" if self.turn == 'WHITE' else "White"
            return {'type': 'checkmate', 'winner': winner}
        
        # Pat kontrolü (şahta değil ama legal hamle yok)
        has_legal_move = False
        for start_pos, piece in self.positions.items():
            if piece:
                is_white_piece = piece.startswith('W_')
                if (self.turn == 'WHITE' and is_white_piece) or (self.turn == 'BLACK' and not is_white_piece):
                    for end_pos in self.positions.keys():
                        if Rules.is_valid_move(piece, start_pos, end_pos, self.positions):
                            temp_positions = self.positions.copy()
                            temp_positions[end_pos] = piece
                            temp_positions[start_pos] = None
                            if not Rules.is_check(temp_positions, self.turn):
                                has_legal_move = True
                                break
            if has_legal_move:
                break
        
        if not has_legal_move:
            return {'type': 'stalemate'}
        
        return None

    def show_game_end_screen(self):
        """Oyun sonu ekranını göster"""
        result = self.check_game_end()
        if result:
            # Yarı saydam siyah overlay
            overlay = pg.Surface((900, 850))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.root.blit(overlay, (0, 0))
            
            # Sonuç mesajı
            if result['type'] == 'checkmate':
                text = f"{result['winner']} Wins!"
            else:  # stalemate
                text = "Draw - Stalemate!"
            
            # Mesajı göster
            font = pg.font.Font(None, 74)
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(450, 400))
            self.root.blit(text_surface, text_rect)
            
            # Main Menu butonu
            menu_button = pg.Rect(350, 500, 200, 50)
            pg.draw.rect(self.root, (70, 70, 70), menu_button, border_radius=10)
            
            small_font = pg.font.Font(None, 36)
            menu_text = small_font.render("Main Menu", True, (255, 255, 255))
            menu_rect = menu_text.get_rect(center=menu_button.center)
            self.root.blit(menu_text, menu_rect)
            
            return menu_button  # Buton koordinatlarını döndür
        
        return None
