"""
游戏管理器模块
负责执行移动、更新游戏状态、处理特殊规则
"""
from chess_board import ChessBoard
from move_validator import MoveValidator


class GameManager:
    """游戏管理器类"""

    def __init__(self):
        """初始化游戏管理器"""
        self.board = ChessBoard()
        self.validator = MoveValidator(self.board)
        self.game_over = False
        self.winner = None
        self.game_result = None  # 'checkmate', 'stalemate', None

    def make_move(self, from_row, from_col, to_row, to_col, promotion_piece=None):
        """
        执行移动

        Args:
            from_row: 起始行
            from_col: 起始列
            to_row: 目标行
            to_col: 目标列
            promotion_piece: 兵升变选择的棋子类型（'Q', 'R', 'B', 'N'）

        Returns:
            bool: 移动是否成功
        """
        # 验证移动是否合法
        if not self.validator.is_valid_move(from_row, from_col, to_row, to_col):
            return False

        piece = self.board.get_piece(from_row, from_col)
        target = self.board.get_piece(to_row, to_col)
        piece_type = piece.upper()
        is_white = self.board.is_white_piece(piece)

        # 记录移动信息
        move_info = {
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece,
            'captured': target,
            'special': None
        }

        # 处理吃过路兵
        if piece_type == self.board.PAWN and self.board.en_passant_target == (to_row, to_col):
            # 移除被吃的兵
            en_passant_row = to_row + (1 if is_white else -1)
            captured_pawn = self.board.get_piece(en_passant_row, to_col)
            self.board.set_piece(en_passant_row, to_col, self.board.EMPTY)
            self.board.captured_pieces.append(captured_pawn)
            move_info['special'] = 'en_passant'
            move_info['captured'] = captured_pawn

        # 处理王车易位
        elif piece_type == self.board.KING and abs(to_col - from_col) == 2:
            is_kingside = to_col > from_col
            rook_col = 7 if is_kingside else 0
            rook_new_col = 5 if is_kingside else 3
            rook = self.board.get_piece(from_row, rook_col)

            # 移动车
            self.board.set_piece(from_row, rook_new_col, rook)
            self.board.set_piece(from_row, rook_col, self.board.EMPTY)
            move_info['special'] = 'castling'

        # 执行基本移动
        self.board.set_piece(to_row, to_col, piece)
        self.board.set_piece(from_row, from_col, self.board.EMPTY)

        # 记录被吃的棋子
        if target != self.board.EMPTY:
            self.board.captured_pieces.append(target)

        # 更新王的位置
        if piece_type == self.board.KING:
            if is_white:
                self.board.white_king_pos = (to_row, to_col)
            else:
                self.board.black_king_pos = (to_row, to_col)

        # 处理兵升变
        if piece_type == self.board.PAWN:
            promotion_row = 0 if is_white else 7
            if to_row == promotion_row:
                if promotion_piece is None:
                    promotion_piece = 'Q'  # 默认升变为后
                promoted = promotion_piece if is_white else promotion_piece.lower()
                self.board.set_piece(to_row, to_col, promoted)
                move_info['special'] = 'promotion'
                move_info['promoted_to'] = promoted

        # 更新吃过路兵目标
        self.board.en_passant_target = None
        if piece_type == self.board.PAWN and abs(to_row - from_row) == 2:
            en_passant_row = from_row + (1 if is_white else -1)
            self.board.en_passant_target = (en_passant_row, to_col)

        # 更新王车易位标志
        if piece_type == self.board.KING:
            if is_white:
                self.board.white_king_moved = True
            else:
                self.board.black_king_moved = True
        elif piece_type == self.board.ROOK:
            if is_white:
                if from_col == 7:
                    self.board.white_rook_king_side_moved = True
                elif from_col == 0:
                    self.board.white_rook_queen_side_moved = True
            else:
                if from_col == 7:
                    self.board.black_rook_king_side_moved = True
                elif from_col == 0:
                    self.board.black_rook_queen_side_moved = True

        # 记录移动历史
        self.board.move_history.append(move_info)

        # 切换回合
        self.board.switch_turn()

        # 检查游戏是否结束
        self._check_game_over()

        return True

    def _check_game_over(self):
        """检查游戏是否结束"""
        current_color = self.board.current_turn

        # 检查将死
        if self.validator.is_checkmate(current_color):
            self.game_over = True
            self.winner = 'black' if current_color == 'white' else 'white'
            self.game_result = 'checkmate'
            return

        # 检查僵局
        if self.validator.is_stalemate(current_color):
            self.game_over = True
            self.winner = None
            self.game_result = 'stalemate'
            return

        self.game_over = False
        self.winner = None
        self.game_result = None

    def get_legal_moves_for_piece(self, row, col):
        """获取指定位置棋子的所有合法移动"""
        piece = self.board.get_piece(row, col)
        if piece == self.board.EMPTY:
            return []

        if self.board.get_piece_color(piece) != self.board.current_turn:
            return []

        legal_moves = []
        for to_row in range(8):
            for to_col in range(8):
                if self.validator.is_valid_move(row, col, to_row, to_col):
                    legal_moves.append((to_row, to_col))

        return legal_moves

    def is_check(self):
        """检查当前回合方是否被将军"""
        return self.validator.is_in_check(self.board.current_turn)

    def get_game_status(self):
        """获取游戏状态信息"""
        status = {
            'current_turn': self.board.current_turn,
            'is_check': self.is_check(),
            'game_over': self.game_over,
            'winner': self.winner,
            'result': self.game_result,
            'move_count': len(self.board.move_history)
        }
        return status

    def undo_last_move(self):
        """撤销上一步移动（用于AI搜索或悔棋功能）"""
        if not self.board.move_history:
            return False

        # 注意：这是一个简化版本，只支持基本撤销
        # 完整实现需要保存更多状态信息
        # 目前主要用于AI搜索时使用board.copy()
        return False

    def reset_game(self):
        """重置游戏"""
        self.board = ChessBoard()
        self.validator = MoveValidator(self.board)
        self.game_over = False
        self.winner = None
        self.game_result = None

    def get_move_notation(self, from_row, from_col, to_row, to_col):
        """
        获取移动的代数记谱法表示

        Returns:
            str: 如 "e2e4", "e7e8q"（兵升变）
        """
        from_pos = chr(ord('a') + from_col) + str(8 - from_row)
        to_pos = chr(ord('a') + to_col) + str(8 - to_row)

        # 检查是否是兵升变
        piece = self.board.get_piece(from_row, from_col)
        if piece.upper() == self.board.PAWN:
            is_white = self.board.is_white_piece(piece)
            promotion_row = 0 if is_white else 7
            if to_row == promotion_row:
                return from_pos + to_pos + 'q'  # 默认升变为后

        return from_pos + to_pos

    def parse_move_notation(self, notation):
        """
        解析代数记谱法

        Args:
            notation: 如 "e2e4" 或 "e7e8q"

        Returns:
            tuple: (from_row, from_col, to_row, to_col, promotion_piece)
        """
        if len(notation) < 4:
            return None

        try:
            from_col = ord(notation[0]) - ord('a')
            from_row = 8 - int(notation[1])
            to_col = ord(notation[2]) - ord('a')
            to_row = 8 - int(notation[3])

            promotion_piece = None
            if len(notation) == 5:
                promotion_piece = notation[4].upper()

            return (from_row, from_col, to_row, to_col, promotion_piece)
        except (ValueError, IndexError):
            return None
