"""
Enhanced chess AI implementation with Alpha-Beta pruning and advanced evaluation
"""

import random
import time
from chess_pieces import Pawn, Rook, Knight, Bishop, Queen, King

class ChessAI:
    """Basic chess AI using simple evaluation"""
    
    def __init__(self, color='black', difficulty='medium'):
        self.color = color
        self.difficulty = difficulty
        self.piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9,
            'king': 100
        }
        
    def get_best_move(self, board):
        """Get the best move for the AI"""
        possible_moves = board.get_all_possible_moves(self.color)
        
        if not possible_moves:
            return None
            
        if self.difficulty == 'easy':
            return self._get_random_move(possible_moves)
        elif self.difficulty == 'medium':
            return self._get_evaluated_move(board, possible_moves)
        else:  # hard
            return self._get_minimax_move(board, possible_moves)
            
    def _get_random_move(self, possible_moves):
        """Get a random valid move"""
        return random.choice(possible_moves)
        
    def _get_evaluated_move(self, board, possible_moves):
        """Get move based on simple evaluation"""
        best_move = None
        best_score = float('-inf')
        
        for move in possible_moves:
            from_pos, to_pos = move
            score = self._evaluate_move(board, from_pos, to_pos)
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move if best_move else random.choice(possible_moves)
        
    def _evaluate_move(self, board, from_pos, to_pos):
        """Evaluate a single move"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = board.get_piece(from_row, from_col)
        target = board.get_piece(to_row, to_col)
        
        score = 0
        
        # Capture bonus
        if target:
            score += self.piece_values[target.piece_type]
            
        # Center control bonus
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if (to_row, to_col) in center_squares:
            score += 0.5
            
        # Piece development bonus (move pieces from back rank)
        if self.color == 'black' and from_row == 0 and to_row > 0:
            score += 0.3
        elif self.color == 'white' and from_row == 7 and to_row < 7:
            score += 0.3
            
        # King safety penalty (don't move king early)
        if piece.piece_type == 'king' and not piece.has_moved:
            score -= 1.0
            
        # Pawn advancement bonus
        if piece.piece_type == 'pawn':
            if self.color == 'white':
                score += (7 - to_row) * 0.1
            else:
                score += to_row * 0.1
                
        # Random factor for variety
        score += random.uniform(-0.1, 0.1)
        
        return score
        
    def _get_minimax_move(self, board, possible_moves):
        """Get move using minimax algorithm with alpha-beta pruning"""
        best_move = None
        best_score = float('-inf')
        
        # Use iterative deepening for better time management
        max_depth = 4 if self.difficulty == 'hard' else 3
        start_time = time.time()
        time_limit = 5.0  # 5 seconds max thinking time
        
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > time_limit:
                break
                
            current_best = None
            alpha = float('-inf')
            beta = float('inf')
            
            for move in possible_moves:
                if time.time() - start_time > time_limit:
                    break
                    
                from_pos, to_pos = move
                score = self._alpha_beta(board, from_pos, to_pos, depth, alpha, beta, True)
                
                if score > best_score:
                    best_score = score
                    current_best = move
                
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            if current_best:
                best_move = current_best
                
        return best_move if best_move else random.choice(possible_moves)
        
    def _alpha_beta(self, board, from_pos, to_pos, depth, alpha, beta, maximizing):
        """Alpha-beta pruning implementation"""
        if depth == 0:
            return self._evaluate_position_advanced(board)
            
        # Make temporary move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = board.board[from_row][from_col]
        captured = board.board[to_row][to_col]
        
        board.board[to_row][to_col] = piece
        board.board[from_row][from_col] = None
        original_pos = (piece.row, piece.col)
        piece.row, piece.col = to_row, to_col
        
        if maximizing:
            max_eval = float('-inf')
            opponent_color = 'white' if self.color == 'black' else 'black'
            opponent_moves = board.get_all_possible_moves(opponent_color)
            
            # Sort moves by potential (captures first)
            opponent_moves = self._order_moves(board, opponent_moves)
            
            for opponent_move in opponent_moves:
                eval_score = self._alpha_beta(board, opponent_move[0], opponent_move[1], depth-1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
        else:
            min_eval = float('inf')
            my_moves = board.get_all_possible_moves(self.color)
            my_moves = self._order_moves(board, my_moves)
            
            for my_move in my_moves:
                eval_score = self._alpha_beta(board, my_move[0], my_move[1], depth-1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            max_eval = min_eval
            
        # Restore board state
        board.board[from_row][from_col] = piece
        board.board[to_row][to_col] = captured
        piece.row, piece.col = original_pos
        
        return max_eval
    
    def _order_moves(self, board, moves):
        """Order moves for better alpha-beta pruning (captures first)"""
        capture_moves = []
        quiet_moves = []
        
        for move in moves:
            from_pos, to_pos = move
            to_row, to_col = to_pos
            if board.board[to_row][to_col] is not None:
                capture_moves.append(move)
            else:
                quiet_moves.append(move)
        
        return capture_moves + quiet_moves
        
    def _evaluate_position(self, board):
        """Evaluate the current board position"""
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    piece_value = self.piece_values[piece.piece_type]
                    if piece.color == self.color:
                        score += piece_value
                    else:
                        score -= piece_value
                        
        return score
    
    def _evaluate_position_advanced(self, board):
        """Advanced position evaluation with multiple factors"""
        score = 0
        
        # Material count
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    piece_value = self.piece_values[piece.piece_type]
                    
                    # Position-specific bonuses
                    position_bonus = self._get_position_bonus(piece, row, col)
                    total_value = piece_value + position_bonus
                    
                    if piece.color == self.color:
                        score += total_value
                    else:
                        score -= total_value
        
        # King safety
        score += self._evaluate_king_safety(board, self.color) * 2
        score -= self._evaluate_king_safety(board, 'white' if self.color == 'black' else 'black') * 2
        
        # Mobility (number of legal moves)
        my_moves = len(board.get_all_possible_moves(self.color))
        opponent_moves = len(board.get_all_possible_moves('white' if self.color == 'black' else 'black'))
        score += (my_moves - opponent_moves) * 0.1
        
        return score
    
    def _get_position_bonus(self, piece, row, col):
        """Get positional bonus for piece placement"""
        center_distance = abs(3.5 - row) + abs(3.5 - col)
        
        if piece.piece_type == 'pawn':
            # Pawn advancement bonus
            if piece.color == 'white':
                return (7 - row) * 0.1
            else:
                return row * 0.1
        elif piece.piece_type == 'knight':
            # Knights prefer center
            return (4 - center_distance) * 0.1
        elif piece.piece_type == 'bishop':
            # Bishops prefer long diagonals
            return (7 - center_distance) * 0.05
        elif piece.piece_type == 'king':
            # King safety in early game, activity in endgame
            return -center_distance * 0.1
        
        return 0
    
    def _evaluate_king_safety(self, board, color):
        """Evaluate king safety"""
        king_pos = board.find_king(color)
        if not king_pos:
            return -100  # King is missing (shouldn't happen)
        
        king_row, king_col = king_pos
        safety_score = 0
        
        # Check for pawn shield
        if color == 'white' and king_row == 7:
            for col_offset in [-1, 0, 1]:
                shield_col = king_col + col_offset
                if 0 <= shield_col < 8:
                    if board.board[6][shield_col] and board.board[6][shield_col].piece_type == 'pawn' and board.board[6][shield_col].color == 'white':
                        safety_score += 1
        elif color == 'black' and king_row == 0:
            for col_offset in [-1, 0, 1]:
                shield_col = king_col + col_offset
                if 0 <= shield_col < 8:
                    if board.board[1][shield_col] and board.board[1][shield_col].piece_type == 'pawn' and board.board[1][shield_col].color == 'black':
                        safety_score += 1
        
        return safety_score
        
    def set_difficulty(self, difficulty):
        """Set AI difficulty level"""
        if difficulty in ['easy', 'medium', 'hard']:
            self.difficulty = difficulty
