"""
Game state management and utilities
"""

class GameState:
    """Manages overall game state and modes"""
    
    def __init__(self):
        self.game_mode = 'human_vs_human'  # 'human_vs_human', 'human_vs_ai'
        self.ai_difficulty = 'medium'
        self.ai_color = 'black'
        self.time_control = None  # Future feature
        self.move_count = 0
        self.game_started = False
        
    def set_game_mode(self, mode):
        """Set the game mode"""
        valid_modes = ['human_vs_human', 'human_vs_ai']
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
        
    def get_status_info(self):
        """Get current game status information"""
        return {
            'mode': self.game_mode,
            'ai_difficulty': self.ai_difficulty,
            'ai_color': self.ai_color,
            'move_count': self.move_count,
            'game_started': self.game_started
        }
