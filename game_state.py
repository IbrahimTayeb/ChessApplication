"""
Game state management and utilities
"""

class GameState:
    """Manages overall game state and modes"""
    
    def __init__(self):
        self.game_mode = 'human_vs_human'  # 'human_vs_human', 'human_vs_ai', 'network'
        self.ai_difficulty = 'medium'
        self.ai_color = 'black'
        self.time_control = {'white_time': 600, 'black_time': 600, 'increment': 0}
        self.move_count = 0
        self.game_started = False
        self.network_role = None  # 'server' or 'client'
        self.player_color = 'white'  # For network games
        self.spectator_mode = False
        
    def set_game_mode(self, mode):
        """Set the game mode"""
        valid_modes = ['human_vs_human', 'human_vs_ai', 'network']
        if mode in valid_modes:
            self.game_mode = mode
            return True
        return False
        
    def set_ai_difficulty(self, difficulty):
        """Set AI difficulty"""
        valid_difficulties = ['easy', 'medium', 'hard']
        if difficulty in valid_difficulties:
            self.ai_difficulty = difficulty
            return True
        return False
        
    def set_ai_color(self, color):
        """Set which color the AI plays"""
        if color in ['white', 'black']:
            self.ai_color = color
            return True
        return False
        
    def is_ai_turn(self, current_player):
        """Check if it's the AI's turn"""
        return (self.game_mode == 'human_vs_ai' and 
                current_player == self.ai_color)
                
    def increment_move_count(self):
        """Increment the move counter"""
        self.move_count += 1
        
    def reset_game_state(self):
        """Reset game state for new game"""
        self.move_count = 0
        self.game_started = False
        
    def set_network_role(self, role):
        """Set network role (server/client)"""
        if role in ['server', 'client']:
            self.network_role = role
            return True
        return False
    
    def set_player_color(self, color):
        """Set player color for network games"""
        if color in ['white', 'black']:
            self.player_color = color
            return True
        return False
    
    def set_time_control(self, white_time, black_time, increment=0):
        """Set time control settings"""
        self.time_control = {
            'white_time': white_time,
            'black_time': black_time,
            'increment': increment
        }
    
    def is_network_game(self):
        """Check if this is a network game"""
        return self.game_mode == 'network'
    
    def can_make_move(self, current_player):
        """Check if the local player can make a move"""
        if self.game_mode == 'network':
            return current_player == self.player_color and not self.spectator_mode
        return True  # For local games, always allow moves
    
    def get_status_info(self):
        """Get current game status information"""
        return {
            'mode': self.game_mode,
            'ai_difficulty': self.ai_difficulty,
            'ai_color': self.ai_color,
            'move_count': self.move_count,
            'game_started': self.game_started,
            'network_role': self.network_role,
            'player_color': self.player_color,
            'spectator_mode': self.spectator_mode,
            'time_control': self.time_control
        }
