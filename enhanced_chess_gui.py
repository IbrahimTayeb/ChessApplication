"""
Enhanced Chess GUI with networking, timers, and drag-and-drop functionality
"""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import threading
import time

from chess_board import ChessBoard
from chess_ai import ChessAI
from game_state import GameState
from network_manager import NetworkManager
from game_timer import GameTimer
from game_serializer import GameSerializer

class EnhancedChessGUI:
    """Enhanced GUI class with networking and advanced features"""
    
    def __init__(self, root):
        self.root = root
        self.board = ChessBoard()
        self.game_state = GameState()
        self.ai = None
        self.network_manager = NetworkManager(
            on_move_received=self.on_network_move_received,
            on_connection_lost=self.on_connection_lost
        )
        self.game_timer = GameTimer(
            white_time=600, black_time=600, increment=0,
            on_time_up=self.on_time_up
        )
        self.game_serializer = GameSerializer()
        
        # GUI state
        self.selected_square = None
        self.highlighted_squares = []
        self.dragging_piece = None
        self.drag_start_pos = None
        self.square_size = 60
        self.board_offset_x = 50
        self.board_offset_y = 80
        
        # Colors
        self.light_square_color = '#F0D9B5'
        self.dark_square_color = '#B58863'
        self.highlight_color = '#FFD700'
        self.selected_color = '#FF6347'
        self.move_highlight_color = '#90EE90'
        
        # Chat for network games
        self.chat_messages = []
        
        self.setup_gui()
        self.draw_board()
        self.update_status()
        self.start_timer_update()
        
    def setup_gui(self):
        """Set up the enhanced GUI components"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for timers
        self.timer_frame = tk.Frame(self.main_frame, bg='white', height=60)
        self.timer_frame.pack(fill=tk.X, padx=10, pady=5)
        self.timer_frame.pack_propagate(False)
        
        # Black timer (top)
        self.black_timer_label = tk.Label(
            self.timer_frame, 
            text="Black: 10:00", 
            font=('Arial', 14, 'bold'),
            bg='lightgray',
            relief=tk.RAISED,
            width=12
        )
        self.black_timer_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # White timer (top right)
        self.white_timer_label = tk.Label(
            self.timer_frame, 
            text="White: 10:00", 
            font=('Arial', 14, 'bold'),
            bg='lightblue',
            relief=tk.RAISED,
            width=12
        )
        self.white_timer_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Middle frame for board and controls
        self.middle_frame = tk.Frame(self.main_frame, bg='white')
        self.middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for chess board
        self.canvas = tk.Canvas(
            self.middle_frame, 
            width=8 * self.square_size + 2 * self.board_offset_x,
            height=8 * self.square_size + 2 * self.board_offset_y,
            bg='white'
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bind mouse events for drag and drop
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
        # Right panel for controls and info
        self.right_panel = tk.Frame(self.middle_frame, bg='white', width=250)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.right_panel.pack_propagate(False)
        
        self.setup_control_panel()
        
    def setup_control_panel(self):
        """Set up the enhanced control panel"""
        # Title
        title_label = tk.Label(
            self.right_panel, 
            text="Enhanced Chess", 
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
        
        tk.Radiobutton(
            mode_frame, 
            text="Network Game", 
            variable=self.mode_var, 
            value='network',
            command=self.on_mode_change,
            bg='white'
        ).pack(anchor=tk.W)
        
        # Network settings
        self.network_frame = tk.LabelFrame(self.right_panel, text="Network Settings", bg='white')
        
        tk.Button(
            self.network_frame, 
            text="Host Game", 
            command=self.host_network_game,
            bg='lightgreen'
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            self.network_frame, 
            text="Join Game", 
            command=self.join_network_game,
            bg='lightcoral'
        ).pack(fill=tk.X, pady=2)
        
        # AI settings
        self.ai_frame = tk.LabelFrame(self.right_panel, text="AI Settings", bg='white')
        
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
        
        # Time control settings
        self.time_frame = tk.LabelFrame(self.right_panel, text="Time Control", bg='white')
        self.time_frame.pack(fill=tk.X, pady=5)
        
        time_options_frame = tk.Frame(self.time_frame, bg='white')
        time_options_frame.pack(fill=tk.X)
        
        tk.Button(
            time_options_frame, 
            text="Blitz (3+2)", 
            command=lambda: self.set_time_control(180, 2),
            bg='yellow',
            width=8
        ).pack(side=tk.LEFT, padx=1)
        
        tk.Button(
            time_options_frame, 
            text="Rapid (10+0)", 
            command=lambda: self.set_time_control(600, 0),
            bg='orange',
            width=8
        ).pack(side=tk.LEFT, padx=1)
        
        tk.Button(
            time_options_frame, 
            text="Custom", 
            command=self.set_custom_time_control,
            bg='lightblue',
            width=8
        ).pack(side=tk.LEFT, padx=1)
        
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
            text="Pause/Resume", 
            command=self.toggle_pause,
            bg='lightyellow'
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            control_frame, 
            text="Save Game", 
            command=self.save_game,
            bg='lightgreen'
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            control_frame, 
            text="Load Game", 
            command=self.load_game,
            bg='lightsalmon'
        ).pack(fill=tk.X, pady=2)
        
        # Status display
        self.status_frame = tk.LabelFrame(self.right_panel, text="Game Status", bg='white')
        self.status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="White to move", 
            bg='white',
            wraplength=220,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, pady=5)
        
        # Network status
        self.network_status_label = tk.Label(
            self.status_frame, 
            text="Not connected", 
            bg='white',
            fg='red',
            wraplength=220
        )
        
        # Chat for network games
        self.chat_frame = tk.LabelFrame(self.right_panel, text="Chat", bg='white')
        
        self.chat_text = tk.Text(
            self.chat_frame, 
            height=6, 
            width=25,
            state=tk.DISABLED,
            bg='white'
        )
        chat_scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_text.yview)
        self.chat_text.config(yscrollcommand=chat_scrollbar.set)
        
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_entry = tk.Entry(self.chat_frame)
        self.chat_entry.pack(fill=tk.X, pady=2)
        self.chat_entry.bind('<Return>', self.send_chat_message)
        
        # Move history
        history_frame = tk.LabelFrame(self.right_panel, text="Move History", bg='white')
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_text = tk.Text(
            history_frame, 
            height=8, 
            width=25,
            state=tk.DISABLED,
            bg='white'
        )
        history_scrollbar = tk.Scrollbar(history_frame, command=self.history_text.yview)
        self.history_text.config(yscrollcommand=history_scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initially hide network and AI settings
        self.toggle_mode_settings()
    
    def toggle_mode_settings(self):
        """Show/hide settings based on game mode"""
        mode = self.mode_var.get()
        
        # Hide all first
        self.ai_frame.pack_forget()
        self.network_frame.pack_forget()
        self.chat_frame.pack_forget()
        self.network_status_label.pack_forget()
        
        if mode == 'human_vs_ai':
            self.ai_frame.pack(fill=tk.X, pady=5, after=self.network_frame)
        elif mode == 'network':
            self.network_frame.pack(fill=tk.X, pady=5)
            self.network_status_label.pack(anchor=tk.W, pady=2)
            self.chat_frame.pack(fill=tk.X, pady=5)
    
    def on_mode_change(self):
        """Handle game mode change"""
        mode = self.mode_var.get()
        self.game_state.set_game_mode(mode)
        self.toggle_mode_settings()
        
        if mode == 'human_vs_ai':
            self.ai = ChessAI(
                color=self.ai_color_var.get(),
                difficulty=self.difficulty_var.get()
            )
        else:
            self.ai = None
            
        self.update_status()
    
    def host_network_game(self):
        """Host a network game"""
        port = simpledialog.askinteger("Host Game", "Enter port number:", initialvalue=8888)
        if port:
            if self.network_manager.start_server(port):
                self.game_state.set_network_role('server')
                self.game_state.set_player_color('white')
                self.network_status_label.config(text=f"Hosting on port {port}...", fg='orange')
                self.add_chat_message("System", f"Waiting for opponent on port {port}")
            else:
                messagebox.showerror("Error", "Failed to start server")
    
    def join_network_game(self):
        """Join a network game"""
        host = simpledialog.askstring("Join Game", "Enter host IP address:", initialvalue="localhost")
        if host:
            port = simpledialog.askinteger("Join Game", "Enter port number:", initialvalue=8888)
            if port:
                if self.network_manager.connect_to_server(host, port):
                    self.game_state.set_network_role('client')
                    self.game_state.set_player_color('black')
                    self.network_status_label.config(text=f"Connected to {host}:{port}", fg='green')
                    self.add_chat_message("System", f"Connected to {host}:{port}")
                else:
                    messagebox.showerror("Error", f"Failed to connect to {host}:{port}")
    
    def on_network_move_received(self, move_data):
        """Handle received network move"""
        try:
            from_pos = tuple(move_data['from'])
            to_pos = tuple(move_data['to'])
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            success, message = self.board.make_move(from_row, from_col, to_row, to_col)
            if success:
                self.root.after(0, self._update_after_network_move, from_row, from_col, to_row, to_col)
            else:
                print(f"Network move failed: {message}")
        except Exception as e:
            print(f"Error processing network move: {e}")
    
    def _update_after_network_move(self, from_row, from_col, to_row, to_col):
        """Update GUI after network move"""
        self.draw_board()
        self.update_status()
        self.add_move_to_history(from_row, from_col, to_row, to_col)
        self.game_timer.switch_player(self.board.current_player)
        
        if self.board.game_over:
            self.show_game_end_message()
    
    def on_connection_lost(self):
        """Handle lost network connection"""
        self.root.after(0, self._handle_disconnection)
    
    def _handle_disconnection(self):
        """Handle disconnection on main thread"""
        self.network_status_label.config(text="Connection lost", fg='red')
        self.add_chat_message("System", "Connection lost")
        messagebox.showwarning("Connection Lost", "Network connection was lost")
    
    def send_chat_message(self, event=None):
        """Send chat message"""
        message = self.chat_entry.get().strip()
        if message and self.network_manager.is_connected:
            self.network_manager.send_chat_message(message)
            self.add_chat_message("You", message)
            self.chat_entry.delete(0, tk.END)
    
    def add_chat_message(self, sender, message):
        """Add message to chat"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{sender}: {message}\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def set_time_control(self, time_seconds, increment):
        """Set predefined time control"""
        self.game_timer.set_time_control(time_seconds, time_seconds, increment)
        self.game_state.set_time_control(time_seconds, time_seconds, increment)
        self.update_timer_display()
    
    def set_custom_time_control(self):
        """Set custom time control"""
        time_minutes = simpledialog.askinteger("Time Control", "Enter time per player (minutes):", initialvalue=10)
        if time_minutes:
            increment = simpledialog.askinteger("Time Control", "Enter increment per move (seconds):", initialvalue=0)
            if increment is not None:
                self.set_time_control(time_minutes * 60, increment)
    
    def toggle_pause(self):
        """Toggle timer pause/resume"""
        if self.game_timer.is_paused:
            self.game_timer.resume_timer()
        else:
            self.game_timer.pause_timer()
    
    def on_time_up(self, player):
        """Handle time running out"""
        self.root.after(0, lambda: self._handle_time_up(player))
    
    def _handle_time_up(self, player):
        """Handle time up on main thread"""
        winner = 'black' if player == 'white' else 'white'
        self.board.game_over = True
        self.board.winner = winner
        messagebox.showinfo("Time's Up!", f"{player.capitalize()}'s time is up! {winner.capitalize()} wins!")
    
    def start_timer_update(self):
        """Start timer display updates"""
        self.update_timer_display()
        self.root.after(100, self.start_timer_update)  # Update every 100ms
    
    def update_timer_display(self):
        """Update timer display"""
        white_time = self.game_timer.get_formatted_time('white')
        black_time = self.game_timer.get_formatted_time('black')
        
        # Highlight current player's timer
        if self.board.current_player == 'white' and self.game_timer.is_running:
            self.white_timer_label.config(bg='lightgreen', text=f"White: {white_time}")
            self.black_timer_label.config(bg='lightgray', text=f"Black: {black_time}")
        elif self.board.current_player == 'black' and self.game_timer.is_running:
            self.black_timer_label.config(bg='lightgreen', text=f"Black: {black_time}")
            self.white_timer_label.config(bg='lightgray', text=f"White: {white_time}")
        else:
            self.white_timer_label.config(bg='lightblue', text=f"White: {white_time}")
            self.black_timer_label.config(bg='lightgray', text=f"Black: {black_time}")
    
    # Mouse handling for drag and drop
    def on_mouse_down(self, event):
        """Handle mouse button down"""
        if self.board.game_over:
            return
            
        # Don't allow moves if it's not player's turn in network game
        if (self.game_state.is_network_game() and 
            not self.game_state.can_make_move(self.board.current_player)):
            return
            
        # Don't allow human moves when it's AI's turn
        if self.game_state.is_ai_turn(self.board.current_player):
            return
            
        # Calculate clicked square
        col = (event.x - self.board_offset_x) // self.square_size
        row = (event.y - self.board_offset_y) // self.square_size
        
        if not self.board.is_valid_position(row, col):
            return
            
        piece = self.board.get_piece(row, col)
        if piece and piece.color == self.board.current_player:
            self.selected_square = (row, col)
            self.dragging_piece = piece
            self.drag_start_pos = (event.x, event.y)
            self.highlight_possible_moves(row, col)
            self.draw_board()
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.dragging_piece and self.selected_square:
            # Redraw board
            self.draw_board()
            
            # Draw dragging piece at mouse position
            self.canvas.create_text(
                event.x, event.y,
                text=self.dragging_piece.get_symbol(),
                font=('Arial', 36),
                fill='red',
                tags="dragging_piece"
            )
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        if not self.dragging_piece or not self.selected_square:
            return
            
        # Calculate target square
        col = (event.x - self.board_offset_x) // self.square_size
        row = (event.y - self.board_offset_y) // self.square_size
        
        if self.board.is_valid_position(row, col):
            from_row, from_col = self.selected_square
            
            # Attempt move
            success, message = self.board.make_move(from_row, from_col, row, col)
            
            if success:
                # Send move over network if needed
                if self.game_state.is_network_game() and self.network_manager.is_connected:
                    piece_type = self.dragging_piece.piece_type
                    self.network_manager.send_move((from_row, from_col), (row, col), piece_type)
                
                self.add_move_to_history(from_row, from_col, row, col)
                self.game_timer.switch_player(self.board.current_player)
                
                # Check for game end
                if self.board.game_over:
                    self.show_game_end_message()
                elif self.game_state.is_ai_turn(self.board.current_player):
                    # AI's turn
                    self.root.after(500, self.make_ai_move)
            else:
                # Invalid move, show message briefly
                self.show_temporary_message(message)
        
        # Reset drag state
        self.dragging_piece = None
        self.selected_square = None
        self.highlighted_squares = []
        self.drag_start_pos = None
        self.draw_board()
        self.update_status()
    
    def on_mouse_move(self, event):
        """Handle mouse movement for hover effects"""
        # Could add hover effects here in the future
        pass
    
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
    
    def draw_board(self):
        """Draw the enhanced chess board and pieces"""
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
                
                # Draw piece if present (skip if being dragged)
                piece = self.board.get_piece(row, col)
                if piece and (not self.dragging_piece or self.selected_square != (row, col)):
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
            self.game_timer.switch_player(self.board.current_player)
            
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
            
            if self.game_state.is_network_game():
                if self.game_state.can_make_move(self.board.current_player):
                    status = f"{current} to move (Your turn)"
                else:
                    status = f"{current} to move (Opponent's turn)"
            elif self.game_state.is_ai_turn(self.board.current_player):
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
        self.game_timer.stop_timer()
    
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
        self.dragging_piece = None
        
        # Reset timer
        self.game_timer.reset_timer()
        self.game_timer.start_timer('white')
        
        # Clear history
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        # Clear chat if network game
        if self.game_state.is_network_game():
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)
        
        # Reinitialize AI if needed
        if self.game_state.game_mode == 'human_vs_ai':
            self.ai = ChessAI(
                color=self.ai_color_var.get(),
                difficulty=self.difficulty_var.get()
            )
        
        self.draw_board()
        self.update_status()
        
        # If AI plays white, make first move
        if (self.ai and self.ai.color == 'white' and 
            self.board.current_player == 'white'):
            self.root.after(1000, self.make_ai_move)
    
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
    
    def disconnect_network(self):
        """Disconnect from network game"""
        if self.network_manager.is_connected:
            self.network_manager.disconnect()
            self.network_status_label.config(text="Disconnected", fg='red')
            self.add_chat_message("System", "Disconnected from game")
    
    def save_game(self):
        """Save current game state"""
        try:
            timer_state = self.game_timer.get_status()
            filename = self.game_serializer.save_game(
                self.board, 
                self.game_state, 
                timer_state
            )
            messagebox.showinfo("Game Saved", f"Game saved as {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save game: {str(e)}")
    
    def load_game(self):
        """Load a saved game"""
        saved_games = self.game_serializer.get_saved_games()
        
        if not saved_games:
            messagebox.showinfo("No Saved Games", "No saved games found.")
            return
        
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Game")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Select a saved game:", font=('Arial', 12)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for game in saved_games:
            listbox.insert(tk.END, game)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                filename = saved_games[selection[0]]
                try:
                    game_data = self.game_serializer.load_game(filename)
                    
                    # Restore board state
                    self.game_serializer.restore_board_state(self.board, game_data['board_state'])
                    
                    # Restore game state
                    self.game_serializer.restore_game_state(self.game_state, game_data['game_state'])
                    
                    # Restore timer
                    timer_data = game_data['timer_state']
                    self.game_timer.white_time = timer_data['white_time']
                    self.game_timer.black_time = timer_data['black_time']
                    self.game_timer.current_player = timer_data['current_player']
                    
                    # Restore move history
                    self.board.move_history = game_data['move_history']
                    
                    # Update GUI
                    self.draw_board()
                    self.update_status()
                    
                    # Restore move history display
                    self.history_text.config(state=tk.NORMAL)
                    self.history_text.delete(1.0, tk.END)
                    
                    for i, move in enumerate(self.board.move_history):
                        from_pos = move['from']
                        to_pos = move['to']
                        from_square = f"{chr(ord('a') + from_pos[1])}{8 - from_pos[0]}"
                        to_square = f"{chr(ord('a') + to_pos[1])}{8 - to_pos[0]}"
                        
                        if i % 2 == 0:
                            move_text = f"{(i + 2) // 2}. {from_square}-{to_square}"
                        else:
                            move_text = f" {from_square}-{to_square}\n"
                        
                        self.history_text.insert(tk.END, move_text)
                    
                    self.history_text.config(state=tk.DISABLED)
                    
                    dialog.destroy()
                    messagebox.showinfo("Game Loaded", f"Game loaded from {filename}")
                    
                except Exception as e:
                    messagebox.showerror("Load Error", f"Failed to load game: {str(e)}")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="Load", command=load_selected, bg='lightgreen').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg='lightcoral').pack(side=tk.RIGHT, padx=5)
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'network_manager'):
            self.network_manager.disconnect()
        if hasattr(self, 'game_timer'):
            self.game_timer.stop_timer()