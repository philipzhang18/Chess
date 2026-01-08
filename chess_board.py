"""
国际象棋棋盘模块
实现8x8棋盘、棋子表示和基本操作
"""

class ChessBoard:
    """国际象棋棋盘类"""

    # 棋子类型常量
    EMPTY = '.'
    PAWN = 'P'
    KNIGHT = 'N'
    BISHOP = 'B'
    ROOK = 'R'
    QUEEN = 'Q'
    KING = 'K'

    # 棋子价值表（用于AI评估）
    PIECE_VALUES = {
        PAWN: 100,
        KNIGHT: 320,
        BISHOP: 330,
        ROOK: 500,
        QUEEN: 900,
        KING: 20000
    }

    def __init__(self):
        """初始化棋盘，设置标准开局位置"""
        self.board = self._create_initial_board()
        self.current_turn = 'white'  # 白方先行
        self.move_history = []  # 移动历史
        self.captured_pieces = []  # 被吃棋子

        # 王车易位相关标志
        self.white_king_moved = False
        self.white_rook_king_side_moved = False
        self.white_rook_queen_side_moved = False
        self.black_king_moved = False
        self.black_rook_king_side_moved = False
        self.black_rook_queen_side_moved = False

        # 吃过路兵相关
        self.en_passant_target = None  # 可以被吃过路兵的目标位置

        # 白王和黑王位置（用于快速查找）
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

    def _create_initial_board(self):
        """创建初始棋盘布局

        棋盘表示：
        - 大写字母代表白方棋子
        - 小写字母代表黑方棋子
        - '.' 代表空格
        """
        board = []

        # 黑方后排（第8行）
        board.append(['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'])
        # 黑方兵（第7行）
        board.append(['p'] * 8)
        # 空行（第6-3行）
        for _ in range(4):
            board.append([self.EMPTY] * 8)
        # 白方兵（第2行）
        board.append([self.PAWN] * 8)
        # 白方后排（第1行）
        board.append([self.ROOK, self.KNIGHT, self.BISHOP, self.QUEEN,
                     self.KING, self.BISHOP, self.KNIGHT, self.ROOK])

        return board

    def get_piece(self, row, col):
        """获取指定位置的棋子"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def set_piece(self, row, col, piece):
        """设置指定位置的棋子"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece

    def is_white_piece(self, piece):
        """判断是否为白方棋子"""
        return piece.isupper() and piece != self.EMPTY

    def is_black_piece(self, piece):
        """判断是否为黑方棋子"""
        return piece.islower() and piece != self.EMPTY

    def get_piece_color(self, piece):
        """获取棋子颜色"""
        if self.is_white_piece(piece):
            return 'white'
        elif self.is_black_piece(piece):
            return 'black'
        return None

    def is_enemy_piece(self, piece1, piece2):
        """判断两个棋子是否为敌对方"""
        if piece1 == self.EMPTY or piece2 == self.EMPTY:
            return False
        return self.get_piece_color(piece1) != self.get_piece_color(piece2)

    def switch_turn(self):
        """切换回合"""
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def copy(self):
        """创建棋盘的深拷贝"""
        new_board = ChessBoard()
        new_board.board = [row[:] for row in self.board]
        new_board.current_turn = self.current_turn
        new_board.move_history = self.move_history[:]
        new_board.captured_pieces = self.captured_pieces[:]

        new_board.white_king_moved = self.white_king_moved
        new_board.white_rook_king_side_moved = self.white_rook_king_side_moved
        new_board.white_rook_queen_side_moved = self.white_rook_queen_side_moved
        new_board.black_king_moved = self.black_king_moved
        new_board.black_rook_king_side_moved = self.black_rook_king_side_moved
        new_board.black_rook_queen_side_moved = self.black_rook_queen_side_moved

        new_board.en_passant_target = self.en_passant_target
        new_board.white_king_pos = self.white_king_pos
        new_board.black_king_pos = self.black_king_pos

        return new_board

    def to_fen(self):
        """将棋盘转换为FEN表示法（Forsyth-Edwards Notation）"""
        fen_parts = []

        # 1. 棋盘布局
        for row in self.board:
            empty_count = 0
            row_str = ''
            for piece in row:
                if piece == self.EMPTY:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece
            if empty_count > 0:
                row_str += str(empty_count)
            fen_parts.append(row_str)

        board_fen = '/'.join(fen_parts)

        # 2. 当前回合
        turn = 'w' if self.current_turn == 'white' else 'b'

        # 3. 王车易位权限
        castling = ''
        if not self.white_king_moved:
            if not self.white_rook_king_side_moved:
                castling += 'K'
            if not self.white_rook_queen_side_moved:
                castling += 'Q'
        if not self.black_king_moved:
            if not self.black_rook_king_side_moved:
                castling += 'k'
            if not self.black_rook_queen_side_moved:
                castling += 'q'
        if not castling:
            castling = '-'

        # 4. 吃过路兵目标
        en_passant = '-'
        if self.en_passant_target:
            col = chr(ord('a') + self.en_passant_target[1])
            row = str(8 - self.en_passant_target[0])
            en_passant = col + row

        return f"{board_fen} {turn} {castling} {en_passant} 0 1"

    def __str__(self):
        """打印棋盘（用于调试）"""
        result = "  a b c d e f g h\n"
        for i, row in enumerate(self.board):
            result += f"{8-i} {' '.join(row)} {8-i}\n"
        result += "  a b c d e f g h"
        return result
