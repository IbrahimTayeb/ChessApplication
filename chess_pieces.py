"""
Chess piece definitions and movement logic
"""

class ChessPiece:
    """Base class for all chess pieces"""
    
    def __init__(self, color, row, col):
        self.color = color  # 'white' or 'black'
        self.row = row
        self.col = col
        self.has_moved = False
        
    def move_to(self, new_row, new_col):
        """Move piece to new position"""
        self.row = new_row
        self.col = new_col
        self.has_moved = True
        
    def get_symbol(self):
        """Get Unicode symbol for the piece"""
        symbols = {
            'white': {'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'},
            'black': {'king': '♚', 'queen': '♛', 'rook': '♜', 'bishop': '♝', 'knight': '♞', 'pawn': '♟'}
        }
        return symbols[self.color][self.piece_type]
        
    def is_valid_move(self, new_row, new_col, board):
        """Check if move is valid for this piece type"""
        raise NotImplementedError("Subclasses must implement is_valid_move")
        
    def get_possible_moves(self, board):
        """Get all possible moves for this piece"""
        moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col, board):
                    moves.append((row, col))
        return moves

class Pawn(ChessPiece):
    piece_type = 'pawn'
    
    def is_valid_move(self, new_row, new_col, board):
        row_diff = new_row - self.row
        col_diff = abs(new_col - self.col)
        
        # Direction based on color
        direction = 1 if self.color == 'white' else -1
        
        # Forward move
        if col_diff == 0:
            if row_diff == direction and board[new_row][new_col] is None:
                return True
            # Initial two-square move
            if not self.has_moved and row_diff == 2 * direction and board[new_row][new_col] is None:
                return True
        
        # Diagonal capture
        elif col_diff == 1 and row_diff == direction:
            target = board[new_row][new_col]
            if target is not None and target.color != self.color:
                return True
                
        return False

class Rook(ChessPiece):
    piece_type = 'rook'
    
    def is_valid_move(self, new_row, new_col, board):
        if new_row == self.row or new_col == self.col:
            return self._is_path_clear(new_row, new_col, board)
        return False
        
    def _is_path_clear(self, new_row, new_col, board):
        """Check if path is clear for rook movement"""
        row_step = 0 if new_row == self.row else (1 if new_row > self.row else -1)
        col_step = 0 if new_col == self.col else (1 if new_col > self.col else -1)
        
        current_row, current_col = self.row + row_step, self.col + col_step
        
        while current_row != new_row or current_col != new_col:
            if board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        # Check destination
        target = board[new_row][new_col]
        return target is None or target.color != self.color

class Knight(ChessPiece):
    piece_type = 'knight'
    
    def is_valid_move(self, new_row, new_col, board):
        row_diff = abs(new_row - self.row)
        col_diff = abs(new_col - self.col)
        
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            target = board[new_row][new_col]
            return target is None or target.color != self.color
        return False

class Bishop(ChessPiece):
    piece_type = 'bishop'
    
    def is_valid_move(self, new_row, new_col, board):
        row_diff = abs(new_row - self.row)
        col_diff = abs(new_col - self.col)
        
        if row_diff == col_diff and row_diff > 0:
            return self._is_diagonal_clear(new_row, new_col, board)
        return False
        
    def _is_diagonal_clear(self, new_row, new_col, board):
        """Check if diagonal path is clear"""
        row_step = 1 if new_row > self.row else -1
        col_step = 1 if new_col > self.col else -1
        
        current_row = self.row + row_step
        current_col = self.col + col_step
        
        while current_row != new_row:
            if board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        # Check destination
        target = board[new_row][new_col]
        return target is None or target.color != self.color

class Queen(ChessPiece):
    piece_type = 'queen'
    
    def is_valid_move(self, new_row, new_col, board):
        # Queen moves like rook or bishop
        rook_move = (new_row == self.row or new_col == self.col)
        bishop_move = abs(new_row - self.row) == abs(new_col - self.col)
        
        if rook_move:
            return self._is_straight_clear(new_row, new_col, board)
        elif bishop_move:
            return self._is_diagonal_clear(new_row, new_col, board)
        return False
        
    def _is_straight_clear(self, new_row, new_col, board):
        """Check if straight path is clear"""
        row_step = 0 if new_row == self.row else (1 if new_row > self.row else -1)
        col_step = 0 if new_col == self.col else (1 if new_col > self.col else -1)
        
        current_row, current_col = self.row + row_step, self.col + col_step
        
        while current_row != new_row or current_col != new_col:
            if board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        target = board[new_row][new_col]
        return target is None or target.color != self.color
        
    def _is_diagonal_clear(self, new_row, new_col, board):
        """Check if diagonal path is clear"""
        row_step = 1 if new_row > self.row else -1
        col_step = 1 if new_col > self.col else -1
        
        current_row = self.row + row_step
        current_col = self.col + col_step
        
        while current_row != new_row:
            if board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        target = board[new_row][new_col]
        return target is None or target.color != self.color

class King(ChessPiece):
    piece_type = 'king'
    
    def is_valid_move(self, new_row, new_col, board):
        row_diff = abs(new_row - self.row)
        col_diff = abs(new_col - self.col)
        
        # King moves one square in any direction
        if row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff > 0):
            target = board[new_row][new_col]
            return target is None or target.color != self.color
        return False
