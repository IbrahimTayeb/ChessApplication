"""
Game timer implementation for time control features
"""

import threading
import time
from typing import Callable, Optional

class GameTimer:
    """Manages time control for chess games"""
    
    def __init__(self, white_time: int = 600, black_time: int = 600, 
                 increment: int = 0, on_time_up: Callable = None):
        """
        Initialize game timer
        
        Args:
            white_time: Initial time for white player in seconds
            black_time: Initial time for black player in seconds  
            increment: Time increment per move in seconds
            on_time_up: Callback when time runs out
        """
        self.white_time = white_time
        self.black_time = black_time
        self.initial_white_time = white_time
        self.initial_black_time = black_time
        self.increment = increment
        self.on_time_up = on_time_up
        
        self.current_player = 'white'
        self.is_running = False
        self.is_paused = False
        self.timer_thread: Optional[threading.Thread] = None
        self.last_update = 0
        
    def start_timer(self, player: str = 'white'):
        """Start the timer for the given player"""
        self.current_player = player
        self.is_running = True
        self.is_paused = False
        self.last_update = time.time()
        
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()
    
    def pause_timer(self):
        """Pause the timer"""
        if self.is_running:
            self._update_current_time()
            self.is_paused = True
    
    def resume_timer(self):
        """Resume the timer"""
        if self.is_paused:
            self.is_paused = False
            self.last_update = time.time()
    
    def stop_timer(self):
        """Stop the timer completely"""
        self.is_running = False
        self.is_paused = False
    
    def switch_player(self, new_player: str):
        """Switch to the other player's timer"""
        if self.is_running and not self.is_paused:
            # Update current player's time
            self._update_current_time()
            
            # Add increment to the player who just moved
            if self.increment > 0:
                if self.current_player == 'white':
                    self.white_time += self.increment
                else:
                    self.black_time += self.increment
        
        self.current_player = new_player
        self.last_update = time.time()
    
    def _timer_loop(self):
        """Main timer loop"""
        while self.is_running:
            if not self.is_paused:
                self._update_current_time()
                
                # Check if time is up
                if self.get_current_time() <= 0:
                    self.is_running = False
                    if self.on_time_up:
                        self.on_time_up(self.current_player)
                    break
            
            time.sleep(0.1)  # Update every 100ms for smooth display
    
    def _update_current_time(self):
        """Update the current player's time"""
        now = time.time()
        elapsed = now - self.last_update
        
        if self.current_player == 'white':
            self.white_time = max(0, self.white_time - elapsed)
        else:
            self.black_time = max(0, self.black_time - elapsed)
        
        self.last_update = now
    
    def get_current_time(self) -> float:
        """Get current player's remaining time"""
        if self.current_player == 'white':
            return self.white_time
        else:
            return self.black_time
    
    def get_time(self, player: str) -> float:
        """Get remaining time for a specific player"""
        if not self.is_running or self.is_paused:
            return self.white_time if player == 'white' else self.black_time
        
        # If it's the current player, calculate real-time remaining
        if player == self.current_player:
            now = time.time()
            elapsed = now - self.last_update
            if player == 'white':
                return max(0, self.white_time - elapsed)
            else:
                return max(0, self.black_time - elapsed)
        else:
            return self.white_time if player == 'white' else self.black_time
    
    def format_time(self, seconds: float) -> str:
        """Format time as MM:SS or HH:MM:SS"""
        if seconds < 0:
            return "00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def get_formatted_time(self, player: str) -> str:
        """Get formatted time string for a player"""
        return self.format_time(self.get_time(player))
    
    def reset_timer(self, white_time: int = None, black_time: int = None):
        """Reset timer to initial values"""
        self.stop_timer()
        
        if white_time is not None:
            self.white_time = white_time
            self.initial_white_time = white_time
        else:
            self.white_time = self.initial_white_time
            
        if black_time is not None:
            self.black_time = black_time
            self.initial_black_time = black_time
        else:
            self.black_time = self.initial_black_time
        
        self.current_player = 'white'
    
    def set_time_control(self, white_time: int, black_time: int, increment: int = 0):
        """Set new time control settings"""
        self.initial_white_time = white_time
        self.initial_black_time = black_time
        self.increment = increment
        self.reset_timer()
    
    def get_status(self) -> dict:
        """Get timer status"""
        return {
            'white_time': self.get_time('white'),
            'black_time': self.get_time('black'),
            'current_player': self.current_player,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'increment': self.increment,
            'white_formatted': self.get_formatted_time('white'),
            'black_formatted': self.get_formatted_time('black')
        }