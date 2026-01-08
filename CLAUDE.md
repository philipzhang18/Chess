# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete chess game implementation in Python featuring:
- Full chess rules engine with special moves (castling, en passant, pawn promotion)
- AI opponent using Minimax algorithm with Alpha-Beta pruning
- Game state management and move validation
- Text-based or web-based UI

**Target Python Environment**: `E:\AI\cursor\starone\venv\Scripts\python.exe`

## Development Commands

### Running the Application
```bash
python chess_board.py  # Main entry point (when implemented)
```

### Testing
```bash
python -m pytest  # Run all tests (when test framework is added)
python -m pytest tests/test_chess_board.py  # Run specific test file
```

## Architecture

### Core Components

**ChessBoard (`chess_board.py`)** - Central game state manager
- Maintains 8x8 board representation using 2D array
- Piece notation: Uppercase = White pieces, Lowercase = Black pieces, '.' = Empty
- Tracks game state: current turn, move history, captured pieces
- Manages special move flags: castling rights, en passant targets, king positions
- Provides FEN (Forsyth-Edwards Notation) export for board state serialization

**Piece Values** (for AI evaluation):
- Pawn: 100, Knight: 320, Bishop: 330, Rook: 500, Queen: 900, King: 20000

### Key Design Patterns

**State Management**: The `ChessBoard` class maintains multiple state flags that must be synchronized:
- Castling rights (6 separate flags for white/black, king/queen side)
- En passant target position (updated after pawn double-moves)
- King positions (cached for performance in check detection)

**Board Copying**: The `copy()` method creates deep copies of the entire game state. This is critical for:
- AI move exploration (Minimax algorithm needs to simulate moves)
- Move validation (test if move results in self-check)
- Undo functionality

### Module Structure

The codebase follows a modular design where additional components should be added as separate files:

- `chess_board.py` - Board state and piece management (current)
- `move_validator.py` - Move legality checking (to be implemented)
- `chess_ai.py` - Minimax AI implementation (to be implemented)
- `game_controller.py` - Game loop and user interaction (to be implemented)
- `ui/` - User interface implementation (to be implemented)

### Special Rules Implementation

**Castling**: Requires tracking whether king and rooks have moved via boolean flags
- Must verify king is not in check, doesn't pass through check, and doesn't land in check
- Requires clear path between king and rook

**En Passant**: Uses `en_passant_target` to store the position where an enemy pawn can be captured
- Set when a pawn moves two squares forward
- Valid only for the immediate next move, then cleared

**Pawn Promotion**: Occurs when pawn reaches opposite end (row 0 for white, row 7 for black)
- Player chooses promotion piece (Queen, Rook, Bishop, Knight)

### Board Coordinate System

- Rows: 0-7 (0 = Black's back rank, 7 = White's back rank)
- Columns: 0-7 (maps to files a-h)
- Standard notation: e.g., position (7, 4) = e1 in algebraic notation

### FEN Notation

The `to_fen()` method generates standard FEN strings with components:
1. Board layout (piece positions)
2. Active color (w/b)
3. Castling availability (KQkq)
4. En passant target square
5. Halfmove clock and fullmove number

## Code Conventions

**Language**: All code comments and docstrings are in Chinese (中文)

**Piece Representation**: Single character codes:
- P/p = Pawn (兵), N/n = Knight (马), B/b = Bishop (象)
- R/r = Rook (车), Q/q = Queen (后), K/k = King (王)

**Color Detection**: Use `is_white_piece()` and `is_black_piece()` helper methods rather than direct case checking

**State Mutation**: When modifying board state, remember to update:
1. The piece position in the board array
2. King position cache if moving kings
3. Castling flags if moving kings or rooks
4. En passant target after any move
5. Move history and captured pieces list
