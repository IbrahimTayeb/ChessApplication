"""
Chess board implementation and game logic
"""

from chess_pieces import Pawn, Rook, Knight, Bishop, Queen, King

class ChessBoard:
    """Chess board with piece management and move validation"""
    
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.setup_initial_position()
        
    def setup_initial_position(self):
        """Set up the initial chess position"""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Pawn('black', 1, col)
            self.board[6][col] = Pawn('white', 6, col)
            
        # Place other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        for col, piece_class in enumerate(piece_order):
            self.board[0][col] = piece_class('black', 0, col)
            self.board[7][col] = piece_class('white', 7, col)
            
    def get_piece(self, row, col):
        """Get piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
        
    def is_valid_position(self, row, col):
        """Check if position is on the board"""
        return 0 <= row < 8 and 0 <= col < 8
        
    def make_move(self, from_row, from_col, to_row, to_col):
        """Make a move on the board"""
        piece = self.get_piece(from_row, from_col)
        
        if not piece:
            return False, "No piece at source position"
            
        if piece.color != self.current_player:
            return False, "Not your piece"
            
        if not self.is_valid_position(to_row, to_col):
            return False, "Invalid destination"
            
        if not piece.is_valid_move(to_row, to_col, self.board):
            return False, "Invalid move for this piece"
            
        # Check if move would put own king in check
        if self.would_be_in_check_after_move(from_row, from_col, to_row, to_col):
            return False, "Move would put king in check"
            
        # Make the move
        captured_piece = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.move_to(to_row, to_col)
        
        # Record move
        move = {
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece,
            'captured': captured_piece,
            'player': self.current_player
        }
        self.move_history.append(move)
        
        # Switch players
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        # Check for game end conditions
        self.check_game_end()
        
        return True, "Move successful"
        
    def would_be_in_check_after_move(self, from_row, from_col, to_row, to_col):
        """Check if a move would result in check for the current player"""
        # Temporarily make the move
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        original_row, original_col = piece.row, piece.col
        piece.row, piece.col = to_row, to_col
        
        # Check if king is in check
        in_check = self.is_in_check(self.current_player)
        
        # Restore board state
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        piece.row, piece.col = original_row, original_col
        
        return in_check
        
    def is_in_check(self, color):
        """Check if the king of given color is in check"""
        king_pos = self.find_king(color)
        if not king_pos:
            return False
            
        king_row, king_col = king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check if any opponent piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if piece.is_valid_move(king_row, king_col, self.board):
                        return True
        return False
        
    def find_king(self, color):
        """Find the king of the given color"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    return (row, col)
        return None
        
    def get_all_possible_moves(self, color):
        """Get all possible moves for a player"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    piece_moves = piece.get_possible_moves(self.board)
                    for to_row, to_col in piece_moves:
                        if not self.would_be_in_check_after_move(row, col, to_row, to_col):
                            moves.append(((row, col), (to_row, to_col)))
        return moves
        
    def is_checkmate(self, color):
        """Check if the given color is in checkmate"""
        if not self.is_in_check(color):
            return False
        return len(self.get_all_possible_moves(color)) == 0
        
    def is_stalemate(self, color):
        """Check if the given color is in stalemate"""
        if self.is_in_check(color):
            return False
        return len(self.get_all_possible_moves(color)) == 0
        
    def check_game_end(self):
        """Check if the game has ended"""
        if self.is_checkmate(self.current_player):
            self.game_over = True
            self.winner = 'black' if self.current_player == 'white' else 'white'
        elif self.is_stalemate(self.current_player):
            self.game_over = True
            self.winner = 'draw'
            
    def get_board_state(self):
        """Get current board state as string representation"""
        state = []
        for row in range(8):
            row_str = []
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    row_str.append(piece.get_symbol())
                else:
                    row_str.append('.')
            state.append(' '.join(row_str))
        return '\n'.join(state)
        
    def reset_game(self):
        """Reset the game to initial state"""
        self.__init__()
