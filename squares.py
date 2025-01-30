import pygame as pg
from rules import is_valid_move, is_check, Rules

class Squares:
    def __init__(self, root, network=None):
        self.root = root
        self.network = network
        # Eğer ağ bağlantısı varsa ve misafir oyuncuysak tahtayı ters çevir
        self.board_flipped = network and not network.is_host
        
        # Pozisyonları başlat
        self.positions = self.initialize_positions()
        self.font = pg.font.Font(None, 36)
        self.selected_piece = None
        self.selected_piece_pos = None
        self.move_history = []
        self.turn = 'WHITE'
        # Olası hamleleri tutmak için yeni liste
        self.possible_moves = []
        
        # Network varsa hamle callback'ini ayarla
        if network:
            network.set_move_callback(self.handle_opponent_move)

    def initialize_positions(self):
        if not self.board_flipped:
            return {
                "a1": "W_ROOK", "a2": "W_PAWN", "a3": None, "a4": None, "a5": None, "a6": None, "a7": "pawn", "a8": "rook",
                "b1": "W_KNIGHT", "b2": "W_PAWN", "b3": None, "b4": None, "b5": None, "b6": None, "b7": "pawn", "b8": "knight",
                "c1": "W_BISHOP", "c2": "W_PAWN", "c3": None, "c4": None, "c5": None, "c6": None, "c7": "pawn", "c8": "bishop",
                "d1": "W_QUEEN", "d2": "W_PAWN", "d3": None, "d4": None, "d5": None, "d6": None, "d7": "pawn", "d8": "queen",
                "e1": "W_KING", "e2": "W_PAWN", "e3": None, "e4": None, "e5": None, "e6": None, "e7": "pawn", "e8": "king",
                "f1": "W_BISHOP", "f2": "W_PAWN", "f3": None, "f4": None, "f5": None, "f6": None, "f7": "pawn", "f8": "bishop",
                "g1": "W_KNIGHT", "g2": "W_PAWN", "g3": None, "g4": None, "g5": None, "g6": None, "g7": "pawn", "g8": "knight",
                "h1": "W_ROOK", "h2": "W_PAWN", "h3": None, "h4": None, "h5": None, "h6": None, "h7": "pawn", "h8": "rook"
            }
        else:
            # Tahtayı ters çevir
            return {
                "a8": "W_ROOK", "a7": "W_PAWN", "a6": None, "a5": None, "a4": None, "a3": None, "a2": "pawn", "a1": "rook",
                "b8": "W_KNIGHT", "b7": "W_PAWN", "b6": None, "b5": None, "b4": None, "b3": None, "b2": "pawn", "b1": "knight",
                "c8": "W_BISHOP", "c7": "W_PAWN", "c6": None, "c5": None, "c4": None, "c3": None, "c2": "pawn", "c1": "bishop",
                "d8": "W_QUEEN", "d7": "W_PAWN", "d6": None, "d5": None, "d4": None, "d3": None, "d2": "pawn", "d1": "queen",
                "e8": "W_KING", "e7": "W_PAWN", "e6": None, "e5": None, "e4": None, "e3": None, "e2": "pawn", "e1": "king",
                "f8": "W_BISHOP", "f7": "W_PAWN", "f6": None, "f5": None, "f4": None, "f3": None, "f2": "pawn", "f1": "bishop",
                "g8": "W_KNIGHT", "g7": "W_PAWN", "g6": None, "g5": None, "g4": None, "g3": None, "g2": "pawn", "g1": "knight",
                "h8": "W_ROOK", "h7": "W_PAWN", "h6": None, "h5": None, "h4": None, "h3": None, "h2": "pawn", "h1": "rook"
            }

    def drawBoard(self):
        square_size = 100
        for row in range(8):
            for col in range(8):
                # Eğer tahta ters çevrilmişse koordinatları ters hesapla
                actual_row = 7 - row if self.board_flipped else row
                actual_col = 7 - col if self.board_flipped else col
                
                color = (255, 255, 255) if (actual_row + actual_col) % 2 == 0 else (0, 0, 0)
                pg.draw.rect(self.root, color, (col * square_size, row * square_size, square_size, square_size))

                # Olası hamleleri göster
                pos = f"{chr(actual_col + ord('a'))}{8 - actual_row}"
                if pos in self.possible_moves:
                    # Yarı saydam yeşil daire çiz
                    surface = pg.Surface((square_size, square_size), pg.SRCALPHA)
                    pg.draw.circle(surface, (0, 255, 0, 128), (square_size//2, square_size//2), 15)
                    self.root.blit(surface, (col * square_size, row * square_size))

                # Taşları çiz
                piece = self.positions.get(pos)
                if piece and (pos != self.selected_piece_pos):
                    piece_color = (255, 0, 0) if piece.isupper() else (0, 0, 255)
                    png = pg.image.load(f'assets/{piece}.png')
                    png = pg.transform.scale(png, (100, 100))
                    self.root.blit(png, (col * square_size, row * square_size))

        # Seçili taşı fareyle birlikte çiz
        if self.selected_piece:
            mouse_x, mouse_y = pg.mouse.get_pos()
            self.root.blit(pg.image.load(f'assets/{self.selected_piece}.png'), (mouse_x - 50, mouse_y - 50))

        # Sırayı gösteren metni çiz (artık altta)
        turn_text = f"Turn: {self.turn}"
        text_surface = self.font.render(turn_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 825))  # Ortalanmış pozisyon
        self.root.blit(text_surface, text_rect)

    def get_possible_moves(self, piece, start_pos):
        possible_moves = []
        for row in range(8):
            for col in range(8):
                end_pos = f"{chr(col + ord('a'))}{8 - row}"
                # Normal hamle kontrolü
                if Rules.is_valid_move(piece, start_pos, end_pos, self.positions):
                    # Hamlenin şah durumuna neden olup olmadığını kontrol et
                    if not Rules.will_move_cause_check(piece, start_pos, end_pos, self.positions, self.turn):
                        possible_moves.append(end_pos)
        return possible_moves

    def selectPiece(self, x, y):
        file = chr(x // 100 + ord('a'))
        rank = str(8 - y // 100)
        position = file + rank
        
        # Eğer zaten seçili bir taş varsa, önce onu temizle
        if self.selected_piece:
            self.selected_piece = None
            self.selected_piece_pos = None
            self.possible_moves = []  # Olası hamleleri temizle
            return
        
        self.selected_piece_pos = position
        self.selected_piece = self.positions.get(self.selected_piece_pos)

        # Sadece geçerli oyuncunun taşını seçebilmesi için kontrol
        if self.selected_piece and (
                (self.turn == 'WHITE' and self.selected_piece.islower()) or
                (self.turn == 'BLACK' and self.selected_piece.isupper())):
            self.selected_piece = None
            self.selected_piece_pos = None
            self.possible_moves = []
        else:
            # Seçilen taşın gidebileceği yerleri hesapla
            if self.selected_piece:
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

    def movePiece(self, x, y):
        if not self.selected_piece:
            return

        # Mouse koordinatlarını tahta koordinatlarına çevir
        file = chr(x // 100 + ord('a'))
        rank = str(8 - y // 100)
        target_pos = file + rank
        
        # Eğer aynı kareye tıklandıysa, seçimi iptal et
        if target_pos == self.selected_piece_pos:
            self.selected_piece = None
            self.selected_piece_pos = None
            return

        if not (ord('a') <= ord(file) <= ord('h') and 1 <= int(rank) <= 8):
            self.selected_piece = None
            self.selected_piece_pos = None
            return

        # Şah durumunda özel kontrol
        if self.is_in_check():
            if not self.is_valid_check_move(x, y):
                self.selected_piece = None
                self.selected_piece_pos = None
                return
        else:
            # Normal hamle kontrolü
            if not Rules.is_valid_move(self.positions[self.selected_piece_pos], 
                                     self.selected_piece_pos, 
                                     target_pos, 
                                     self.positions):
                self.selected_piece = None
                self.selected_piece_pos = None
                return
            
            # Hamlenin kendi şahımızı tehlikeye atıp atmadığını kontrol et
            if Rules.will_move_cause_check(self.positions[self.selected_piece_pos],
                                         self.selected_piece_pos,
                                         target_pos,
                                         self.positions,
                                         self.turn):
                self.selected_piece = None
                self.selected_piece_pos = None
                return

        # Hamleyi yap
        self.positions[target_pos] = self.positions[self.selected_piece_pos]
        self.positions[self.selected_piece_pos] = None
        
        # Eğer network bağlantısı varsa hamleyi gönder
        if self.network and self.network.connected:
            move_data = {
                'from': self.selected_piece_pos,
                'to': target_pos,
                'piece': self.positions[target_pos]
            }
            self.network.send_move(move_data)
        
        # Hamleyi geçmişe kaydet
        self.move_history.append((self.selected_piece_pos, target_pos))
        
        self.selected_piece = None
        self.selected_piece_pos = None
        self.possible_moves = []  # Hamleden sonra noktaları temizle
        self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'

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

    def handle_opponent_move(self, from_pos, to_pos, piece):
        # Rakibin hamlesini işle
        self.positions[from_pos] = None
        self.positions[to_pos] = piece
        self.turn = 'WHITE' if self.turn == 'BLACK' else 'BLACK'
        self.move_history.append((from_pos, to_pos))
