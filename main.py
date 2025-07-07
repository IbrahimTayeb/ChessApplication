#!/usr/bin/env python3
"""
Main entry point for the Chess Application
"""

import tkinter as tk
from chess_gui import ChessGUI

def main():
    """Main function to start the chess application"""
    root = tk.Tk()
    root.title("Chess Game")
    root.geometry("800x600")
    root.resizable(False, False)
    
    # Create and start the chess game
    chess_app = ChessGUI(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
