"""
Chess GUI implementation using Tkinter
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time

from chess_board import ChessBoard
from chess_ai import ChessAI
from game_state import GameState

class ChessGUI:
    """Main GUI class for the chess application"""
    
    def __init__(self, root):
        self.root = root
        self.board = ChessBoard()
        self.game_state = GameState()
        self.ai = None
        
        # GUI state
        self.selected_square = None
        self.highlighted_squares = []
        self.square_size = 60
        self.board_offset_x = 50
        self.board_offset_y = 50
        
        # Colors
        self.light_square_color = '#F0D9B5'
        self.dark_square_color = '#B58863'
        self.highlight_color = '#FFD700'
        self.selected_color = '#FF6347'
        
        self.setup_gui()
        self.draw_board()
        self.update_status()
        
    def setup_gui(self):
        """Set up the GUI components"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for chess board
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=8 * self.square_size + 2 * self.board_offset_x,
            height=8 * self.square_size + 2 * self.board_offset_y,
            bg='white'
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_square_click)
        
        # Right panel for controls and info
        self.right_panel = tk.Frame(self.main_frame, bg='white', width=200)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.right_panel.pack_propagate(False)
        
        self.setup_control_panel()
        
    def setup_control_panel(self):
        """Set up the control panel"""
        # Title
        title_label = tk.Label(
            self.right_panel, 
            text="Chess Game", 
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title_label.pack(pady=10)
        
        # Game mode selection
        mode_frame = tk.LabelFrame(self.right_panel, text="Game Mode", bg='white')
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.mode_var = tk.StringVar(value='human_vs_human')
        tk.Radiobutton(
            mode_frame, 
            text="Human vs Human", 
            variable=self.mode_var, 
            value='human_vs_human',
            command=self.on_mode_change,
            bg='white'
        ).pack(anchor=tk.W)
        
        tk.Radiobutton(
            mode_frame, 
            text="Human vs AI", 
            variable=self.mode_var, 
            value='human_vs_ai',
            command=self.on_mode_change,
            bg='white'
        ).pack(anchor=tk.W)
        
        # AI settings
        self.ai_frame = tk.LabelFrame(self.right_panel, text="AI Settings", bg='white')
        self.ai_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.ai_frame, text="Difficulty:", bg='white').pack(anchor=tk.W)
        self.difficulty_var = tk.StringVar(value='medium')
        difficulty_combo = ttk.Combobox(
            self.ai_frame, 
            textvariable=self.difficulty_var,
            values=['easy', 'medium', 'hard'],
            state='readonly'
        )
        difficulty_combo.pack(fill=tk.X, pady=2)
        difficulty_combo.bind('<<ComboboxSelected>>', self.on_difficulty_change)
        
        tk.Label(self.ai_frame, text="AI Color:", bg='white').pack(anchor=tk.W, pady=(10,0))
        self.ai_color_var = tk.StringVar(value='black')
        color_combo = ttk.Combobox(
            self.ai_frame,
            textvariable=self.ai_color_var,
            values=['white', 'black'],
            state='readonly'
        )
        color_combo.pack(fill=tk.X, pady=2)
        color_combo.bind('<<ComboboxSelected>>', self.on_ai_color_change)
        
        # Game controls
        control_frame = tk.LabelFrame(self.right_panel, text="Game Controls", bg='white')
        control_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            control_frame, 
            text="New Game", 
            command=self.new_game,
            bg='lightblue'
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            control_frame, 
            text="Undo Move", 
            command=self.undo_move,
            bg='lightyellow'
        ).pack(fill=tk.X, pady=2)
        
        # Status display
        self.status_frame = tk.LabelFrame(self.right_panel, text="Game Status", bg='white')
        self.status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="White to move", 
            bg='white',
            wraplength=180,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, pady=5)
        
        # Move history
        history_frame = tk.LabelFrame(self.right_panel, text="Move History", bg='white')
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_text = tk.Text(
            history_frame, 
            height=8, 
            width=20,
            state=tk.DISABLED,
            bg='white'
        )
        history_scrollbar = tk.Scrollbar(history_frame, command=self.history_text.yview)
        self.history_text.config(yscrollcommand=history_scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initially hide AI settings
        self.toggle_ai_settings()
        
    def on_mode_change(self):
        """Handle game mode change"""
        mode = self.mode_var.get()
        self.game_state.set_game_mode(mode)
        self.toggle_ai_settings()
        
        if mode == 'human_vs_ai':
            self.ai = ChessAI(
                color=self.ai_color_var.get(),
                difficulty=self.difficulty_var.get()
            )
        else:
            self.ai = None
            
        self.update_status()
        
    def toggle_ai_settings(self):
        """Show/hide AI settings based on game mode"""
        if self.mode_var.get() == 'human_vs_ai':
            self.ai_frame.pack(fill=tk.X, pady=5, after=self.right_panel.children['!labelframe'])
        else:
            self.ai_frame.pack_forget()
            
    def on_difficulty_change(self, event=None):
        """Handle AI difficulty change"""
        if self.ai:
            self.ai.set_difficulty(self.difficulty_var.get())
            
    def on_ai_color_change(self, event=None):
        """Handle AI color change"""
        self.game_state.set_ai_color(self.ai_color_var.get())
        if self.ai:
            self.ai.color = self.ai_color_var.get()
        self.update_status()
        
    def draw_board(self):
        """Draw the chess board and pieces"""
        self.canvas.delete("all")
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = self.board_offset_x + col * self.square_size
                y1 = self.board_offset_y + row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = self.light_square_color if is_light else self.dark_square_color
                
                # Highlight selected square
                if self.selected_square == (row, col):
                    color = self.selected_color
                elif (row, col) in self.highlighted_squares:
                    color = self.highlight_color
                    
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=color, 
                    outline='black',
                    tags=f"square_{row}_{col}"
                )
                
                # Draw piece if present
                piece = self.board.get_piece(row, col)
                if piece:
                    center_x = x1 + self.square_size // 2
                    center_y = y1 + self.square_size // 2
                    
                    self.canvas.create_text(
                        center_x, center_y,
                        text=piece.get_symbol(),
                        font=('Arial', 36),
                        fill='black',
                        tags=f"piece_{row}_{col}"
                    )
                    
        # Draw coordinates
        for i in range(8):
            # Files (a-h)
            file_letter = chr(ord('a') + i)
            x = self.board_offset_x + i * self.square_size + self.square_size // 2
            y = self.board_offset_y + 8 * self.square_size + 15
            self.canvas.create_text(x, y, text=file_letter, font=('Arial', 12))
            
            # Ranks (1-8)
            rank_number = str(8 - i)
            x = self.board_offset_x - 15
            y = self.board_offset_y + i * self.square_size + self.square_size // 2
            self.canvas.create_text(x, y, text=rank_number, font=('Arial', 12))
            
    def on_square_click(self, event):
        """Handle square click events"""
        if self.board.game_over:
            return
            
        # Don't allow human moves when it's AI's turn
        if self.game_state.is_ai_turn(self.board.current_player):
            return
            
        # Calculate clicked square
        col = (event.x - self.board_offset_x) // self.square_size
        row = (event.y - self.board_offset_y) // self.square_size
        
        if not self.board.is_valid_position(row, col):
            return
            
        if self.selected_square is None:
            # Select a piece
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.board.current_player:
                self.selected_square = (row, col)
                self.highlight_possible_moves(row, col)
                self.draw_board()
        else:
            # Try to move the selected piece
            from_row, from_col = self.selected_square
            
            if (row, col) == self.selected_square:
                # Deselect
                self.selected_square = None
                self.highlighted_squares = []
                self.draw_board()
            else:
                # Attempt move
                success, message = self.board.make_move(from_row, from_col, row, col)
                
                if success:
                    self.selected_square = None
                    self.highlighted_squares = []
                    self.draw_board()
                    self.update_status()
                    self.add_move_to_history(from_row, from_col, row, col)
                    
                    # Check for game end
                    if self.board.game_over:
                        self.show_game_end_message()
                    elif self.game_state.is_ai_turn(self.board.current_player):
                        # AI's turn
                        self.root.after(500, self.make_ai_move)
                else:
                    # Invalid move, show message briefly
                    self.show_temporary_message(message)
                    
    def highlight_possible_moves(self, row, col):
        """Highlight possible moves for the selected piece"""
        piece = self.board.get_piece(row, col)
        if piece:
            possible_moves = piece.get_possible_moves(self.board.board)
            # Filter out moves that would put king in check
            valid_moves = []
            for to_row, to_col in possible_moves:
                if not self.board.would_be_in_check_after_move(row, col, to_row, to_col):
                    valid_moves.append((to_row, to_col))
            self.highlighted_squares = valid_moves
            
    def make_ai_move(self):
        """Make an AI move in a separate thread"""
        if not self.ai or self.board.game_over:
            return
            
        def ai_move_thread():
            try:
                move = self.ai.get_best_move(self.board)
                if move:
                    from_pos, to_pos = move
                    from_row, from_col = from_pos
                    to_row, to_col = to_pos
                    
                    # Make the move on the main thread
                    self.root.after(0, lambda: self.execute_ai_move(from_row, from_col, to_row, to_col))
            except Exception as e:
                self.root.after(0, lambda: self.show_temporary_message(f"AI Error: {str(e)}"))
                
        # Start AI calculation in background thread
        threading.Thread(target=ai_move_thread, daemon=True).start()
        
    def execute_ai_move(self, from_row, from_col, to_row, to_col):
        """Execute the AI move on the main thread"""
        success, message = self.board.make_move(from_row, from_col, to_row, to_col)
        
        if success:
            self.draw_board()
            self.update_status()
            self.add_move_to_history(from_row, from_col, to_row, to_col)
            
            if self.board.game_over:
                self.show_game_end_message()
        else:
            self.show_temporary_message(f"AI move failed: {message}")
            
    def add_move_to_history(self, from_row, from_col, to_row, to_col):
        """Add move to history display"""
        from_square = f"{chr(ord('a') + from_col)}{8 - from_row}"
        to_square = f"{chr(ord('a') + to_col)}{8 - to_row}"
        
        move_number = len(self.board.move_history)
        if move_number % 2 == 1:
            move_text = f"{(move_number + 1) // 2}. {from_square}-{to_square}"
        else:
            move_text = f" {from_square}-{to_square}\n"
            
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, move_text)
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
        
    def update_status(self):
        """Update the status display"""
        if self.board.game_over:
            if self.board.winner == 'draw':
                status = "Game Over - Draw!"
            else:
                status = f"Game Over - {self.board.winner.capitalize()} wins!"
        else:
            current = self.board.current_player.capitalize()
            if self.game_state.is_ai_turn(self.board.current_player):
                status = f"{current} to move (AI thinking...)"
            else:
                status = f"{current} to move"
                
            # Add check status
            if self.board.is_in_check(self.board.current_player):
                status += " - In Check!"
                
        self.status_label.config(text=status)
        
    def show_game_end_message(self):
        """Show game end message"""
        if self.board.winner == 'draw':
            message = "Game ended in a draw!"
        else:
            message = f"{self.board.winner.capitalize()} wins!"
            
        messagebox.showinfo("Game Over", message)
        
    def show_temporary_message(self, message):
        """Show a temporary status message"""
        original_text = self.status_label.cget('text')
        self.status_label.config(text=message, fg='red')
        self.root.after(2000, lambda: self.status_label.config(text=original_text, fg='black'))
        
    def new_game(self):
        """Start a new game"""
        self.board.reset_game()
        self.game_state.reset_game_state()
        self.selected_square = None
        self.highlighted_squares = []
        
        # Clear history
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        # Reinitialize AI if needed
        if self.mode_var.get() == 'human_vs_ai':
            self.ai = ChessAI(
                color=self.ai_color_var.get(),
                difficulty=self.difficulty_var.get()
            )
            
        self.draw_board()
        self.update_status()
        
        # If AI plays white, make first move
        if (self.ai and self.ai.color == 'white'):
            self.root.after(1000, self.make_ai_move)
            
    def undo_move(self):
        """Undo the last move (simple implementation)"""
        if not self.board.move_history:
            self.show_temporary_message("No moves to undo")
            return
            
        # For simplicity, just restart the game
        # A full implementation would properly restore the previous board state
        if messagebox.askyesno("Undo Move", "This will restart the game. Continue?"):
            self.new_game()
