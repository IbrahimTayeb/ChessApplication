"""
Game serialization for save/load functionality
"""

import json
import pickle
import datetime
from typing import Dict, Any, Optional

class GameSerializer:
    """Handles saving and loading of chess game states"""
    
    def __init__(self):
        self.save_directory = "saved_games"
        
    def save_game(self, board, game_state, timer_state, filename: Optional[str] = None) -> str:
        """Save current game state to file"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Prepare game data
        game_data = {
            'version': '1.0',
            'timestamp': datetime.datetime.now().isoformat(),
            'board_state': self._serialize_board(board),
            'game_state': self._serialize_game_state(game_state),
            'timer_state': timer_state,
            'move_history': board.move_history
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(game_data, f, indent=2, default=str)
            return filename
        except Exception as e:
            raise Exception(f"Failed to save game: {e}")
    
    def load_game(self, filename: str) -> Dict[str, Any]:
        """Load game state from file"""
        try:
            with open(filename, 'r') as f:
                game_data = json.load(f)
            
            return {
                'board_state': game_data['board_state'],
                'game_state': game_data['game_state'],
                'timer_state': game_data['timer_state'],
                'move_history': game_data['move_history'],
                'timestamp': game_data.get('timestamp', 'Unknown')
            }
        except Exception as e:
            raise Exception(f"Failed to load game: {e}")
    
    def _serialize_board(self, board) -> Dict[str, Any]:
        """Serialize board state"""
        board_state = []
        
        for row in range(8):
            row_data = []
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_data = {
                        'type': piece.piece_type,
                        'color': piece.color,
                        'has_moved': piece.has_moved,
                        'row': piece.row,
                        'col': piece.col
                    }
                    row_data.append(piece_data)
                else:
                    row_data.append(None)
            board_state.append(row_data)
        
        return {
            'board': board_state,
            'current_player': board.current_player,
            'game_over': board.game_over,
            'winner': board.winner
        }
    
    def _serialize_game_state(self, game_state) -> Dict[str, Any]:
        """Serialize game state"""
        return {
            'game_mode': game_state.game_mode,
            'ai_difficulty': game_state.ai_difficulty,
            'ai_color': game_state.ai_color,
            'time_control': game_state.time_control,
            'move_count': game_state.move_count,
            'game_started': game_state.game_started,
            'network_role': game_state.network_role,
            'player_color': game_state.player_color,
            'spectator_mode': game_state.spectator_mode
        }
    
    def restore_board_state(self, board, board_data: Dict[str, Any]):
        """Restore board from serialized data"""
        from chess_pieces import Pawn, Rook, Knight, Bishop, Queen, King
        
        piece_classes = {
            'pawn': Pawn,
            'rook': Rook,
            'knight': Knight,
            'bishop': Bishop,
            'queen': Queen,
            'king': King
        }
        
        # Clear current board
        board.board = [[None for _ in range(8)] for _ in range(8)]
        
        # Restore pieces
        for row in range(8):
            for col in range(8):
                piece_data = board_data['board'][row][col]
                if piece_data:
                    piece_class = piece_classes[piece_data['type']]
                    piece = piece_class(
                        piece_data['color'],
                        piece_data['row'],
                        piece_data['col']
                    )
                    piece.has_moved = piece_data['has_moved']
                    board.board[row][col] = piece
        
        # Restore board state
        board.current_player = board_data['current_player']
        board.game_over = board_data['game_over']
        board.winner = board_data['winner']
    
    def restore_game_state(self, game_state, state_data: Dict[str, Any]):
        """Restore game state from serialized data"""
        game_state.game_mode = state_data['game_mode']
        game_state.ai_difficulty = state_data['ai_difficulty']
        game_state.ai_color = state_data['ai_color']
        game_state.time_control = state_data['time_control']
        game_state.move_count = state_data['move_count']
        game_state.game_started = state_data['game_started']
        game_state.network_role = state_data.get('network_role')
        game_state.player_color = state_data.get('player_color', 'white')
        game_state.spectator_mode = state_data.get('spectator_mode', False)
    
    def get_saved_games(self) -> list:
        """Get list of saved game files"""
        import os
        try:
            files = [f for f in os.listdir('.') if f.startswith('chess_game_') and f.endswith('.json')]
            return sorted(files, reverse=True)  # Most recent first
        except:
            return []
    
    def export_pgn(self, board, filename: Optional[str] = None) -> str:
        """Export game to PGN format"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.pgn"
        
        if not filename.endswith('.pgn'):
            filename += '.pgn'
        
        # Basic PGN header
        pgn_content = '[Event "Casual Game"]\n'
        pgn_content += f'[Date "{datetime.datetime.now().strftime("%Y.%m.%d")}"]\n'
        pgn_content += '[White "Player"]\n'
        pgn_content += '[Black "Player"]\n'
        
        if board.game_over:
            if board.winner == 'white':
                pgn_content += '[Result "1-0"]\n'
            elif board.winner == 'black':
                pgn_content += '[Result "0-1"]\n'
            else:
                pgn_content += '[Result "1/2-1/2"]\n'
        else:
            pgn_content += '[Result "*"]\n'
        
        pgn_content += '\n'
        
        # Convert moves to algebraic notation (simplified)
        move_line = ""
        for i, move in enumerate(board.move_history):
            if i % 2 == 0:
                move_line += f"{(i // 2) + 1}. "
            
            from_pos = move['from']
            to_pos = move['to']
            piece = move['piece']
            
            # Simple move notation (not full algebraic)
            from_square = f"{chr(ord('a') + from_pos[1])}{8 - from_pos[0]}"
            to_square = f"{chr(ord('a') + to_pos[1])}{8 - to_pos[0]}"
            
            if piece.piece_type == 'pawn':
                move_notation = to_square
            else:
                move_notation = f"{piece.piece_type[0].upper()}{to_square}"
            
            move_line += f"{move_notation} "
            
            if len(move_line) > 70:  # Line wrap
                pgn_content += move_line + '\n'
                move_line = ""
        
        if move_line:
            pgn_content += move_line
        
        # Add result
        if board.game_over:
            if board.winner == 'white':
                pgn_content += " 1-0"
            elif board.winner == 'black':
                pgn_content += " 0-1"
            else:
                pgn_content += " 1/2-1/2"
        else:
            pgn_content += " *"
        
        try:
            with open(filename, 'w') as f:
                f.write(pgn_content)
            return filename
        except Exception as e:
            raise Exception(f"Failed to export PGN: {e}")