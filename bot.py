import random
from rules import Rules
from stockfish import Stockfish
import chess
import os
import time

class ChessBot:
    def __init__(self, elo=1500):
        self.elo = elo
        
        # Stockfish'i başlat
        try:
            stockfish_path = "stockfish/stockfish-windows-x86-64.exe"  # Windows için
            # stockfish_path = "stockfish/stockfish-ubuntu-x86-64"     # Linux için
            # stockfish_path = "stockfish/stockfish-macos-x86-64"      # MacOS için
            
            self.engine = Stockfish(path=stockfish_path)
            
            # ELO'ya göre motor ayarları
            if elo < 800:
                # Düşük ELO ayarları aynı kalabilir
                self.engine.set_skill_level(0)
                self.engine.set_elo_rating(800)
            elif elo < 1500:
                # Orta ELO ayarları aynı kalabilir
                self.engine.set_skill_level(5)
                self.engine.set_elo_rating(1500)
            elif elo < 2000:
                self.engine.set_skill_level(10)
                self.engine.set_elo_rating(2000)
            elif elo < 2500:
                self.engine.set_skill_level(15)
                self.engine.set_elo_rating(2500)
            else:  # 2500+
                # Tam güç ayarları
                self.engine.set_skill_level(20)  # Maksimum beceri
                self.engine.set_elo_rating(3000)
                self.engine.update_engine_parameters({
                    "Hash": 2048,          # 2GB hash tablosu
                    "Threads": 4,          # 4 thread kullan
                    "MultiPV": 1,          # Sadece en iyi hamleye odaklan
                    "Minimum Thinking Time": 3000,  # 3 saniye minimum düşünme
                    "Move Overhead": 1000,  # Network gecikmesi için buffer
                    "Slow Mover": 400,      # Çok daha dikkatli düşün
                    "UCI_LimitStrength": False,  # Güç sınırlaması yok
                    "UCI_AnalyseMode": True,
                    "Use NNUE": True       # Neural network kullan
                })
                
        except Exception as e:
            print(f"Stockfish başlatılamadı: {e}")
            self.engine = None
    
    def convert_to_fen(self, positions):
        """Pozisyonları FEN formatına çevir"""
        board = [['' for _ in range(8)] for _ in range(8)]
        
        piece_map = {
            'W_PAWN': 'P', 'W_KNIGHT': 'N', 'W_BISHOP': 'B',
            'W_ROOK': 'R', 'W_QUEEN': 'Q', 'W_KING': 'K',
            'pawn': 'p', 'knight': 'n', 'bishop': 'b',
            'rook': 'r', 'queen': 'q', 'king': 'k'
        }
        
        # Pozisyonları diziye yerleştir
        for pos, piece in positions.items():
            if piece:
                col = ord(pos[0]) - ord('a')
                row = 8 - int(pos[1])
                board[row][col] = piece_map.get(piece, '')
        
        # FEN stringi oluştur
        fen_parts = []
        for row in board:
            empty = 0
            row_str = ''
            for cell in row:
                if cell == '':
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += cell
            if empty > 0:
                row_str += str(empty)
            fen_parts.append(row_str)
        
        return '/'.join(fen_parts)
    
    def get_move(self, positions, turn):
        """Stockfish'ten en iyi hamleyi al"""
        if not self.engine:
            return self.get_random_move(positions, turn)
        
        try:
            # Pozisyonları FEN formatına çevir
            fen = self.convert_to_fen(positions)
            # Sırayı ekle
            fen += ' w ' if turn == 'WHITE' else ' b '
            # Diğer FEN bilgilerini ekle (rok hakları ve geçerken alma)
            fen += 'KQkq - 0 1'
            
            # Pozisyonu motora ayarla
            self.engine.set_fen_position(fen)
            
            # Yüksek ELO'da daha uzun düşün
            if self.elo >= 2500:
                # En iyi hamleyi bul
                best_move = self.engine.get_best_move_time(5000)  # 5 saniye düşün
                
                # Hamle değerlendirmesini al
                evaluation = self.engine.get_evaluation()
                print(f"Hamle değerlendirmesi: {evaluation}")
                
                if best_move:
                    from_pos = best_move[:2]
                    to_pos = best_move[2:4]
                    piece = positions.get(from_pos)
                    return (from_pos, to_pos, piece)
            else:
                # Normal ELO için standart düşünme
                best_move = self.engine.get_best_move_time(1000)
                if best_move:
                    from_pos = best_move[:2]
                    to_pos = best_move[2:4]
                    piece = positions.get(from_pos)
                    return (from_pos, to_pos, piece)
            
        except Exception as e:
            print(f"Stockfish hatası: {e}")
            return self.get_random_move(positions, turn)
    
    def get_random_move(self, positions, turn):
        """Yedek olarak rastgele hamle"""
        possible_moves = []
        for start_pos, piece in positions.items():
            if piece and (not piece.startswith('W_')):
                for end_pos in positions.keys():
                    if Rules.is_valid_move(piece, start_pos, end_pos, positions):
                        temp_positions = positions.copy()
                        temp_positions[end_pos] = piece
                        temp_positions[start_pos] = None
                        if not Rules.is_check(temp_positions, turn):
                            possible_moves.append((start_pos, end_pos, piece))
        
        return random.choice(possible_moves) if possible_moves else None 