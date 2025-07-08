#!/usr/bin/env python3
"""
Main entry point for the Enhanced Chess Application
"""

import tkinter as tk
from enhanced_chess_gui import EnhancedChessGUI

def main():
    """Main function to start the enhanced chess application"""
    root = tk.Tk()
    root.title("Enhanced Chess Game - Network & AI")
    root.geometry("1000x800")
    root.resizable(True, True)
    
    # Set minimum window size
    root.minsize(900, 700)
    
    # Create and start the enhanced chess game
    chess_app = EnhancedChessGUI(root)
    
    # Handle window close event
    def on_closing():
        if hasattr(chess_app, 'network_manager'):
            chess_app.network_manager.disconnect()
        if hasattr(chess_app, 'game_timer'):
            chess_app.game_timer.stop_timer()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
