import random
from rules import Rules

class ChessBot:
    def __init__(self, difficulty='EASY'):
        self.difficulty = difficulty  # EASY, MEDIUM, HARD
        
    def get_move(self, positions, turn):
        if self.difficulty == 'EASY':
            return self.get_random_move(positions, turn)
        elif self.difficulty == 'MEDIUM':
            return self.get_smart_move(positions, turn)
        else:  # HARD
            return self.get_best_move(positions, turn)
    
    def get_random_move(self, positions, turn):
        """Rastgele geçerli bir hamle seç"""
        possible_moves = []
        
        # Tüm siyah taşları bul
        for start_pos, piece in positions.items():
            if piece and (not piece.startswith('W_')):  # Siyah taşlar
                # Bu taşın yapabileceği tüm hamleleri bul
                for end_pos in positions.keys():
                    if Rules.is_valid_move(piece, start_pos, end_pos, positions):
                        # Hamle şah durumuna yol açıyor mu kontrol et
                        temp_positions = positions.copy()
                        temp_positions[end_pos] = piece
                        temp_positions[start_pos] = None
                        
                        if not Rules.is_check(temp_positions, turn):
                            possible_moves.append((start_pos, end_pos, piece))
        
        if possible_moves:
            return random.choice(possible_moves)
        return None
    
    def get_smart_move(self, positions, turn):
        """Biraz daha akıllı hamleler yap"""
        possible_moves = []
        capture_moves = []  # Taş yeme hamleleri
        
        for start_pos, piece in positions.items():
            if piece and (not piece.startswith('W_')):
                for end_pos in positions.keys():
                    if Rules.is_valid_move(piece, start_pos, end_pos, positions):
                        temp_positions = positions.copy()
                        temp_positions[end_pos] = piece
                        temp_positions[start_pos] = None
                        
                        if not Rules.is_check(temp_positions, turn):
                            # Eğer hedefte rakip taş varsa, capture_moves'a ekle
                            if positions.get(end_pos) and positions.get(end_pos).startswith('W_'):
                                capture_moves.append((start_pos, end_pos, piece))
                            else:
                                possible_moves.append((start_pos, end_pos, piece))
        
        # Önce yeme hamlelerini tercih et
        if capture_moves:
            return random.choice(capture_moves)
        elif possible_moves:
            return random.choice(possible_moves)
        return None
    
    def get_best_move(self, positions, turn):
        """En iyi hamleyi bul (basit değerlendirme ile)"""
        best_move = None
        best_score = float('-inf')
        
        piece_values = {
            'PAWN': 1, 'pawn': -1,
            'KNIGHT': 3, 'knight': -3,
            'BISHOP': 3, 'bishop': -3,
            'ROOK': 5, 'rook': -5,
            'QUEEN': 9, 'queen': -9,
            'KING': 100, 'king': -100
        }
        
        for start_pos, piece in positions.items():
            if piece and (not piece.startswith('W_')):
                for end_pos in positions.keys():
                    if Rules.is_valid_move(piece, start_pos, end_pos, positions):
                        temp_positions = positions.copy()
                        captured_piece = temp_positions.get(end_pos)
                        temp_positions[end_pos] = piece
                        temp_positions[start_pos] = None
                        
                        if not Rules.is_check(temp_positions, turn):
                            # Pozisyonu değerlendir
                            score = 0
                            # Eğer bir taş yeniyorsa, değerini ekle
                            if captured_piece:
                                score += piece_values.get(captured_piece.replace('W_', ''), 0)
                            
                            # Merkez kontrolü
                            if end_pos in ['d4', 'd5', 'e4', 'e5']:
                                score += 0.5
                                
                            if score > best_score:
                                best_score = score
                                best_move = (start_pos, end_pos, piece)
        
        return best_move or self.get_smart_move(positions, turn) 