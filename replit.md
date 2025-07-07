# Chess Game Application

## Overview

This is a desktop chess application built with Python and Tkinter that features both human vs human and human vs AI gameplay modes. The application implements a complete chess engine with piece movement validation, game state management, and a graphical user interface. The AI opponent uses evaluation-based algorithms with multiple difficulty levels.

## System Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns:

- **Model-View-Controller Pattern**: The chess board logic (model), GUI presentation (view), and game flow control are separated into distinct modules
- **Component-Based Design**: Each chess piece type is implemented as a separate class with shared inheritance
- **State Management**: Centralized game state handling for mode switching and game progression
- **AI Integration**: Pluggable AI system with configurable difficulty levels

## Key Components

### Core Game Engine
- **ChessBoard** (`chess_board.py`): Manages the 8x8 game board, piece positions, move validation, and game rules
- **ChessPiece Classes** (`chess_pieces.py`): Base class and specific implementations for each piece type (Pawn, Rook, Knight, Bishop, Queen, King) with movement logic
- **GameState** (`game_state.py`): Centralized state management for game modes, AI settings, and move tracking

### User Interface
- **ChessGUI** (`chess_gui.py`): Tkinter-based graphical interface with interactive board, piece selection, and move highlighting
- **Visual Features**: Color-coded squares, piece symbols, move validation feedback, and game status display

### AI System
- **ChessAI** (`chess_ai.py`): Multi-level AI opponent with three difficulty modes:
  - Easy: Random move selection
  - Medium: Position evaluation-based moves
  - Hard: Minimax algorithm implementation

### Application Entry
- **Main** (`main.py`): Application bootstrap and window initialization

## Data Flow

1. **User Interaction**: Player clicks on board squares through the GUI
2. **Move Validation**: ChessBoard validates moves using piece-specific logic
3. **State Updates**: Successful moves update board state and switch players
4. **AI Processing**: When AI's turn, ChessAI calculates and executes optimal move
5. **Visual Updates**: GUI refreshes to reflect new board state and game status
6. **Game Progression**: GameState tracks moves and manages game modes

## External Dependencies

- **Python Standard Library**:
  - `tkinter`: GUI framework for cross-platform desktop interface
  - `random`: AI move randomization for easy difficulty
  - `threading`: Asynchronous AI move processing
  - `time`: Move timing and delays

- **No external packages required**: The application uses only Python built-in modules for maximum compatibility

## Deployment Strategy

- **Desktop Application**: Standalone Python application requiring Python 3.x runtime
- **Cross-Platform**: Compatible with Windows, macOS, and Linux through Tkinter
- **Single Executable**: Can be packaged using PyInstaller or similar tools for distribution
- **No Installation Required**: Direct execution from source code

## Changelog

- July 07, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.