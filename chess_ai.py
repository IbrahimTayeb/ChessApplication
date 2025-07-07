"""
Simple chess AI implementation
"""

import random
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
        """Get move using minimax algorithm (simplified)"""
        best_move = None
        best_score = float('-inf')
        
        for move in possible_moves:
            from_pos, to_pos = move
            score = self._minimax(board, from_pos, to_pos, depth=2, maximizing=True)
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move if best_move else random.choice(possible_moves)
        
    def _minimax(self, board, from_pos, to_pos, depth, maximizing):
        """Simplified minimax implementation"""
        if depth == 0:
            return self._evaluate_position(board)
            
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
            opponent_moves = board.get_all_possible_moves('white' if self.color == 'black' else 'black')
            for opponent_move in opponent_moves[:5]:  # Limit search for performance
                eval_score = self._minimax(board, opponent_move[0], opponent_move[1], depth-1, False)
                max_eval = max(max_eval, eval_score)
        else:
            min_eval = float('inf')
            my_moves = board.get_all_possible_moves(self.color)
            for my_move in my_moves[:5]:  # Limit search for performance
                eval_score = self._minimax(board, my_move[0], my_move[1], depth-1, True)
                min_eval = min(min_eval, eval_score)
            max_eval = min_eval
            
        # Restore board state
        board.board[from_row][from_col] = piece
        board.board[to_row][to_col] = captured
        piece.row, piece.col = original_pos
        
        return max_eval
        
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
        
    def set_difficulty(self, difficulty):
        """Set AI difficulty level"""
        if difficulty in ['easy', 'medium', 'hard']:
            self.difficulty = difficulty
