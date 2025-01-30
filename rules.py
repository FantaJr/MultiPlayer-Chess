def is_check(white_turn, positions):
    king_pos = None
    king_color = 'WHITE' if white_turn else 'BLACK'

    # Şahın pozisyonunu bulalım
    for pos, piece in positions.items():
        if piece and ((piece == 'KING' and white_turn and piece.isupper()) or (piece == 'king' and not white_turn and piece.islower())):
            king_pos = pos
            break

    if not king_pos:
        return False

    opponent_color = 'BLACK' if white_turn else 'WHITE'
    # Karşı takımın tüm taşlarını kontrol edelim
    for pos, piece in positions.items():
        if piece and ((piece.isupper() and not white_turn) or (piece.islower() and white_turn)):  # Karşı takımın taşı
            if is_valid_move(piece, pos, king_pos, positions):
                return True

    return False

def is_checkmate(king_color, positions):
    # Mat durumu kontrolü
    for pos, current_piece in positions.items():
        if current_piece and ((king_color == 'WHITE' and current_piece.isupper()) or (king_color == 'BLACK' and current_piece.islower())):
            for new_pos in positions.keys():
                if is_valid_move(current_piece, pos, new_pos, positions):
                    old_piece = positions[new_pos]
                    positions[new_pos] = current_piece
                    positions[pos] = None
                    if not is_check(king_color == 'WHITE', positions):
                        positions[new_pos] = old_piece
                        positions[pos] = current_piece
                        return False
                    positions[new_pos] = old_piece
                    positions[pos] = current_piece
    print("checkmate")
    return True

def is_starting_move(piece, start_pos, end_pos, positions):
    start_col, start_row = ord(start_pos[0]), int(start_pos[1])
    end_col, end_row = ord(end_pos[0]), int(end_pos[1])
    
    if piece.isupper():
        # Beyaz piyonlar
        if start_row == 2 and end_row == 4 and positions.get(chr(start_col) + '3') is None and positions.get(end_pos) is None:
            return True
        elif start_row + 1 == end_row and positions.get(end_pos) is None:
            return True
    else:
        # Siyah piyonlar
        if start_row == 7 and end_row == 5 and positions.get(chr(start_col) + '6') is None and positions.get(end_pos) is None:
            return True
        elif start_row - 1 == end_row and positions.get(end_pos) is None:
            return True
    
    return False

def is_valid_move(piece, start_pos, end_pos, positions):
    if start_pos == end_pos:
        return False

    start_col, start_row = ord(start_pos[0]), int(start_pos[1])
    end_col, end_row = ord(end_pos[0]), int(end_pos[1])
    if piece.upper() == 'W_PAWN':
        direction = 1
        # Piyonun düz hareketi
        if start_col == end_col and end_row - start_row == direction and positions.get(end_pos) is None:
            return True
        # Piyonun başlangıç hareketi
        if start_col == end_col and end_row - start_row == 2 * direction and (start_row == 2 or start_row == 7) and positions.get(end_pos) is None:
            return is_starting_move(piece, start_pos, end_pos, positions)
        # Piyonun çapraz yeme hareketi
        if abs(start_col - end_col) == 1 and end_row - start_row == direction and positions.get(end_pos) is not None:
            return True

    elif piece.lower() == 'pawn':
        direction = -1
        # Piyonun düz hareketi
        if start_col == end_col and end_row - start_row == direction and positions.get(end_pos) is None:
            return True
        # Piyonun başlangıç hareketi
        if start_col == end_col and end_row - start_row == 2 * direction and (start_row == 2 or start_row == 7) and positions.get(end_pos) is None:
            return is_starting_move(piece, start_pos, end_pos, positions)
        # Piyonun çapraz yeme hareketi
        if abs(start_col - end_col) == 1 and end_row - start_row == direction and positions.get(end_pos) is not None:
            return True
    elif piece.lower() == 'rook' or piece.upper() == 'W_ROOK':
        if start_col == end_col or start_row == end_row:
            if is_path_clear(start_pos, end_pos, positions):
                return True
    elif piece.lower() == 'knight' or piece.upper() == 'W_KNIGHT':
        if (abs(start_col - end_col), abs(start_row - end_row)) in [(1, 2), (2, 1)]:
            return True
    elif piece.lower() == 'bishop' or piece.upper() == 'W_BISHOP':
        if abs(start_col - end_col) == abs(start_row - end_row):
            if is_path_clear(start_pos, end_pos, positions):
                return True
    elif piece.lower() == 'queen' or piece.upper() == 'W_QUEEN':
        if start_col == end_col or start_row == end_row or abs(start_col - end_col) == abs(start_row - end_row):
            if is_path_clear(start_pos, end_pos, positions):
                return True
    elif piece.lower() == 'king' or piece.upper() == 'W_KING':
        if max(abs(start_col - end_col), abs(start_row - end_row)) == 1:
            return True

    return False

def is_path_clear(start_pos, end_pos, positions):
    start_col, start_row = ord(start_pos[0]), int(start_pos[1])
    end_col, end_row = ord(end_pos[0]), int(end_pos[1])

    step_col = 0 if start_col == end_col else 1 if end_col > start_col else -1
    step_row = 0 if start_row == end_row else 1 if end_row > start_row else -1

    col, row = start_col + step_col, start_row + step_row
    while col != end_col or row != end_row:
        if positions.get(chr(col) + str(row)) is not None:
            return False
        col += step_col
        row += step_row

    return True

class Rules:
    @staticmethod
    def is_valid_move(piece, start_pos, end_pos, positions):
        # String olarak gelen piece'i kontrol et
        piece_type = piece.replace('W_', '').lower() if piece.startswith('W_') else piece.lower()
        
        # Hedef karede kendi taşımız varsa hareket edemeyiz
        target_piece = positions.get(end_pos)
        if target_piece:
            # Eğer hedef karede kendi rengimizden bir taş varsa geçersiz hamle
            if (piece.isupper() and target_piece.isupper()) or \
               (piece.islower() and target_piece.islower()):
                return False
        
        if piece_type == "pawn":
            return Rules._is_valid_pawn_move(piece, start_pos, end_pos, positions)
        elif piece_type == "rook":
            return Rules._is_valid_rook_move(piece, start_pos, end_pos, positions)
        elif piece_type == "knight":
            return Rules._is_valid_knight_move(piece, start_pos, end_pos, positions)
        elif piece_type == "bishop":
            return Rules._is_valid_bishop_move(piece, start_pos, end_pos, positions)
        elif piece_type == "queen":
            return Rules._is_valid_queen_move(piece, start_pos, end_pos, positions)
        elif piece_type == "king":
            return Rules._is_valid_king_move(piece, start_pos, end_pos, positions)
        return False

    @staticmethod
    def is_check(positions, turn):
        king_pos = None
        # Şahın pozisyonunu bulalım
        king_piece = 'W_KING' if turn == 'WHITE' else 'king'
        
        for pos, piece in positions.items():
            if piece == king_piece:
                king_pos = pos
                break
        
        if not king_pos:
            return False
        
        # Rakip taşların şahı tehdit edip etmediğini kontrol et
        for pos, piece in positions.items():
            if piece:  # Eğer kare boş değilse
                # Eğer rakip taşsa (beyaz sırasında siyah taşları, siyah sırasında beyaz taşları kontrol et)
                if (turn == 'WHITE' and piece.islower()) or (turn == 'BLACK' and piece.isupper()):
                    if is_valid_move(piece, pos, king_pos, positions):
                        return True
        
        return False

    @staticmethod
    def is_checkmate(board, color):
        if not Rules.is_check(board, color):
            return False

        # Tüm olası hamleleri kontrol et
        for y in range(8):
            for x in range(8):
                piece = board[y][x]
                if piece and piece.color == color:
                    # Her taşın tüm olası hamlelerini kontrol et
                    for end_y in range(8):
                        for end_x in range(8):
                            if Rules.is_valid_move(piece, (x, y), (end_x, end_y), board):
                                # Hamleyi geçici olarak yap
                                temp_piece = board[end_y][end_x]
                                board[end_y][end_x] = piece
                                board[y][x] = None

                                # Hala şah durumu var mı kontrol et
                                still_in_check = Rules.is_check(board, color)

                                # Hamleyi geri al
                                board[y][x] = piece
                                board[end_y][end_x] = temp_piece

                                # Eğer bir kurtuluş hamlesi bulunduysa, mat değil
                                if not still_in_check:
                                    return False
        return True

    @staticmethod
    def _is_valid_pawn_move(piece, start_pos, end_pos, positions):
        start_col, start_row = ord(start_pos[0]), int(start_pos[1])
        end_col, end_row = ord(end_pos[0]), int(end_pos[1])
        
        # Yön kontrolü (beyaz yukarı, siyah aşağı hareket eder)
        direction = 1 if piece.isupper() else -1
        
        # Düz hareket
        if start_col == end_col:
            # Bir kare ileri
            if end_row - start_row == direction:
                return positions.get(end_pos) is None
            # İki kare ileri (başlangıç konumu için)
            if (piece.isupper() and start_row == 2 and end_row == 4) or \
               (piece.islower() and start_row == 7 and end_row == 5):
                middle_pos = f"{chr(start_col)}{start_row + direction}"
                return positions.get(middle_pos) is None and positions.get(end_pos) is None
            
        # Çapraz hareket (yeme)
        elif abs(end_col - start_col) == 1 and end_row - start_row == direction:
            target_piece = positions.get(end_pos)
            if target_piece:
                return (piece.isupper() and target_piece.islower()) or \
                       (piece.islower() and target_piece.isupper())
        
        return False

    @staticmethod
    def _is_valid_rook_move(piece, start_pos, end_pos, positions):
        start_col, start_row = ord(start_pos[0]), int(start_pos[1])
        end_col, end_row = ord(end_pos[0]), int(end_pos[1])
        
        # Kale sadece yatay veya dikey hareket edebilir
        if start_col != end_col and start_row != end_row:
            return False
        
        # Yol üzerinde başka taş var mı kontrol et
        return is_path_clear(start_pos, end_pos, positions)

    @staticmethod
    def _is_valid_knight_move(piece, start_pos, end_pos, positions):
        start_col, start_row = ord(start_pos[0]), int(start_pos[1])
        end_col, end_row = ord(end_pos[0]), int(end_pos[1])
        
        # At L şeklinde hareket eder
        col_diff = abs(end_col - start_col)
        row_diff = abs(end_row - start_row)
        
        # Hedef karede kendi taşımız varsa hareket edemeyiz
        target_piece = positions.get(end_pos)
        if target_piece:
            if (piece.isupper() and target_piece.isupper()) or (piece.islower() and target_piece.islower()):
                return False
        
        return (col_diff == 2 and row_diff == 1) or (col_diff == 1 and row_diff == 2)

    @staticmethod
    def _is_valid_bishop_move(piece, start_pos, end_pos, positions):
        start_col, start_row = ord(start_pos[0]), int(start_pos[1])
        end_col, end_row = ord(end_pos[0]), int(end_pos[1])
        
        # Fil çapraz hareket etmeli
        if abs(end_col - start_col) != abs(end_row - start_row):
            return False
        
        # Yol üzerinde başka taş var mı kontrol et
        return is_path_clear(start_pos, end_pos, positions)

    @staticmethod
    def _is_valid_queen_move(piece, start_pos, end_pos, positions):
        # Vezir hem kale hem fil gibi hareket edebilir
        return Rules._is_valid_rook_move(piece, start_pos, end_pos, positions) or \
               Rules._is_valid_bishop_move(piece, start_pos, end_pos, positions)

    @staticmethod
    def _is_valid_king_move(piece, start_pos, end_pos, positions):
        start_col, start_row = ord(start_pos[0]), int(start_pos[1])
        end_col, end_row = ord(end_pos[0]), int(end_pos[1])
        
        # Şah her yönde sadece 1 kare hareket edebilir
        col_diff = abs(end_col - start_col)
        row_diff = abs(end_row - start_row)
        
        # Hedef karede kendi taşımız varsa hareket edemeyiz
        target_piece = positions.get(end_pos)
        if target_piece:
            if (piece.isupper() and target_piece.isupper()) or (piece.islower() and target_piece.islower()):
                return False
        
        return col_diff <= 1 and row_diff <= 1

    @staticmethod
    def will_move_cause_check(piece, start_pos, end_pos, positions, turn):
        # Hamleyi geçici olarak yap
        temp_positions = positions.copy()
        temp_positions[end_pos] = piece
        temp_positions[start_pos] = None
        
        # Hamle sonrası şah durumu kontrolü
        will_cause_check = Rules.is_check(temp_positions, turn)
        
        return will_cause_check
