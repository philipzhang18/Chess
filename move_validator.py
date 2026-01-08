"""
移动规则验证器模块
实现所有棋子的合法走法校验，包括特殊规则
"""
from chess_board import ChessBoard


class MoveValidator:
    """移动规则验证器类"""

    def __init__(self, board):
        """
        初始化验证器

        Args:
            board: ChessBoard实例
        """
        self.board = board

    def is_valid_move(self, from_row, from_col, to_row, to_col, check_king_safety=True):
        """
        验证移动是否合法

        Args:
            from_row: 起始行
            from_col: 起始列
            to_row: 目标行
            to_col: 目标列
            check_king_safety: 是否检查移动后王的安全（默认True）

        Returns:
            bool: 移动是否合法
        """
        # 检查坐标是否在棋盘范围内
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and
                0 <= to_row < 8 and 0 <= to_col < 8):
            return False

        piece = self.board.get_piece(from_row, from_col)
        target = self.board.get_piece(to_row, to_col)

        # 检查起始位置是否有棋子
        if piece == self.board.EMPTY:
            return False

        # 检查是否移动到相同位置
        if from_row == to_row and from_col == to_col:
            return False

        # 检查是否轮到该方移动
        piece_color = self.board.get_piece_color(piece)
        if piece_color != self.board.current_turn:
            return False

        # 检查目标位置是否有己方棋子
        if target != self.board.EMPTY:
            if self.board.get_piece_color(target) == piece_color:
                return False

        # 根据棋子类型验证移动
        piece_type = piece.upper()
        is_valid = False

        if piece_type == self.board.PAWN:
            is_valid = self._is_valid_pawn_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.KNIGHT:
            is_valid = self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.BISHOP:
            is_valid = self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.ROOK:
            is_valid = self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.QUEEN:
            is_valid = self._is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.KING:
            is_valid = self._is_valid_king_move(from_row, from_col, to_row, to_col)

        # 如果基本移动合法，检查是否会导致己方王被将军
        if is_valid and check_king_safety:
            is_valid = not self._would_cause_check(from_row, from_col, to_row, to_col)

        return is_valid

    def _is_valid_pawn_move(self, from_row, from_col, to_row, to_col):
        """验证兵的移动"""
        piece = self.board.get_piece(from_row, from_col)
        target = self.board.get_piece(to_row, to_col)
        is_white = self.board.is_white_piece(piece)

        # 白兵向上（行减小），黑兵向下（行增大）
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1

        # 向前移动一格
        if to_col == from_col and to_row == from_row + direction:
            return target == self.board.EMPTY

        # 初始位置可以向前移动两格
        if to_col == from_col and from_row == start_row and to_row == from_row + 2 * direction:
            middle_row = from_row + direction
            if (target == self.board.EMPTY and
                    self.board.get_piece(middle_row, from_col) == self.board.EMPTY):
                return True

        # 斜向吃子
        if abs(to_col - from_col) == 1 and to_row == from_row + direction:
            # 普通吃子
            if target != self.board.EMPTY and self.board.is_enemy_piece(piece, target):
                return True
            # 吃过路兵
            if self.board.en_passant_target == (to_row, to_col):
                return True

        return False

    def _is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        """验证马的移动（日字形）"""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        """验证象的移动（斜线）"""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)

        # 必须是斜线移动
        if row_diff != col_diff:
            return False

        # 检查路径是否被阻挡
        return self._is_path_clear(from_row, from_col, to_row, to_col)

    def _is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        """验证车的移动（直线）"""
        # 必须是水平或垂直移动
        if from_row != to_row and from_col != to_col:
            return False

        # 检查路径是否被阻挡
        return self._is_path_clear(from_row, from_col, to_row, to_col)

    def _is_valid_queen_move(self, from_row, from_col, to_row, to_col):
        """验证后的移动（直线或斜线）"""
        # 后的移动是车和象的组合
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)

        # 直线或斜线移动
        if from_row == to_row or from_col == to_col or row_diff == col_diff:
            return self._is_path_clear(from_row, from_col, to_row, to_col)

        return False

    def _is_valid_king_move(self, from_row, from_col, to_row, to_col):
        """验证王的移动"""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)

        # 普通移动：一格
        if row_diff <= 1 and col_diff <= 1:
            return True

        # 王车易位
        if row_diff == 0 and col_diff == 2:
            return self._is_valid_castling(from_row, from_col, to_row, to_col)

        return False

    def _is_valid_castling(self, from_row, from_col, to_row, to_col):
        """验证王车易位是否合法"""
        piece = self.board.get_piece(from_row, from_col)
        is_white = self.board.is_white_piece(piece)

        # 检查王是否已移动
        if is_white and self.board.white_king_moved:
            return False
        if not is_white and self.board.black_king_moved:
            return False

        # 检查王是否在被将军状态
        if self.is_in_check(self.board.current_turn):
            return False

        # 判断是王翼易位还是后翼易位
        is_kingside = to_col > from_col
        rook_col = 7 if is_kingside else 0

        # 检查车是否已移动
        if is_white:
            if is_kingside and self.board.white_rook_king_side_moved:
                return False
            if not is_kingside and self.board.white_rook_queen_side_moved:
                return False
        else:
            if is_kingside and self.board.black_rook_king_side_moved:
                return False
            if not is_kingside and self.board.black_rook_queen_side_moved:
                return False

        # 检查车是否还在原位
        rook = self.board.get_piece(from_row, rook_col)
        if rook.upper() != self.board.ROOK:
            return False

        # 检查王和车之间的路径是否畅通
        step = 1 if is_kingside else -1
        for col in range(from_col + step, rook_col, step):
            if self.board.get_piece(from_row, col) != self.board.EMPTY:
                return False

        # 检查王经过的格子是否被攻击
        for col in range(from_col, to_col + step, step):
            if self._is_square_under_attack(from_row, col, self.board.current_turn):
                return False

        return True

    def _is_path_clear(self, from_row, from_col, to_row, to_col):
        """检查两点之间的路径是否畅通（不包括目标点）"""
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)

        current_row = from_row + row_step
        current_col = from_col + col_step

        while current_row != to_row or current_col != to_col:
            if self.board.get_piece(current_row, current_col) != self.board.EMPTY:
                return False
            current_row += row_step
            current_col += col_step

        return True

    def _would_cause_check(self, from_row, from_col, to_row, to_col):
        """检查移动是否会导致己方王被将军"""
        # 创建临时棋盘模拟移动
        temp_board = self.board.copy()
        piece = temp_board.get_piece(from_row, from_col)
        target = temp_board.get_piece(to_row, to_col)

        # 执行移动
        temp_board.set_piece(to_row, to_col, piece)
        temp_board.set_piece(from_row, from_col, temp_board.EMPTY)

        # 更新王的位置
        if piece.upper() == self.board.KING:
            if temp_board.is_white_piece(piece):
                temp_board.white_king_pos = (to_row, to_col)
            else:
                temp_board.black_king_pos = (to_row, to_col)

        # 创建临时验证器并检查
        temp_validator = MoveValidator(temp_board)
        return temp_validator.is_in_check(self.board.current_turn)

    def is_in_check(self, color):
        """检查指定颜色的王是否被将军"""
        # 找到王的位置
        king_pos = self.board.white_king_pos if color == 'white' else self.board.black_king_pos
        return self._is_square_under_attack(king_pos[0], king_pos[1], color)

    def _is_square_under_attack(self, row, col, defender_color):
        """检查指定位置是否被攻击"""
        attacker_color = 'black' if defender_color == 'white' else 'white'

        # 检查所有敌方棋子是否能攻击该位置
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece == self.board.EMPTY:
                    continue
                if self.board.get_piece_color(piece) == attacker_color:
                    # 检查该敌方棋子是否能移动到目标位置
                    # 注意：这里不检查王的安全，避免无限递归
                    if self._can_piece_attack(r, c, row, col):
                        return True

        return False

    def _can_piece_attack(self, from_row, from_col, to_row, to_col):
        """检查棋子是否能攻击目标位置（不考虑王的安全）"""
        piece = self.board.get_piece(from_row, from_col)
        piece_type = piece.upper()

        if piece_type == self.board.PAWN:
            return self._can_pawn_attack(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.KNIGHT:
            return self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.BISHOP:
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.ROOK:
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.QUEEN:
            return self._is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece_type == self.board.KING:
            row_diff = abs(to_row - from_row)
            col_diff = abs(to_col - from_col)
            return row_diff <= 1 and col_diff <= 1

        return False

    def _can_pawn_attack(self, from_row, from_col, to_row, to_col):
        """检查兵是否能攻击目标位置"""
        piece = self.board.get_piece(from_row, from_col)
        is_white = self.board.is_white_piece(piece)
        direction = -1 if is_white else 1

        # 兵只能斜向攻击
        if abs(to_col - from_col) == 1 and to_row == from_row + direction:
            return True

        return False

    def get_all_legal_moves(self, color):
        """获取指定颜色的所有合法移动"""
        legal_moves = []

        for from_row in range(8):
            for from_col in range(8):
                piece = self.board.get_piece(from_row, from_col)
                if piece == self.board.EMPTY:
                    continue
                if self.board.get_piece_color(piece) != color:
                    continue

                # 尝试所有可能的目标位置
                for to_row in range(8):
                    for to_col in range(8):
                        if self.is_valid_move(from_row, from_col, to_row, to_col):
                            legal_moves.append(((from_row, from_col), (to_row, to_col)))

        return legal_moves

    def is_checkmate(self, color):
        """检查是否将死"""
        # 必须先处于被将军状态
        if not self.is_in_check(color):
            return False

        # 检查是否有任何合法移动可以解除将军
        return len(self.get_all_legal_moves(color)) == 0

    def is_stalemate(self, color):
        """检查是否僵局（无子可动但未被将军）"""
        # 不能处于被将军状态
        if self.is_in_check(color):
            return False

        # 检查是否有任何合法移动
        return len(self.get_all_legal_moves(color)) == 0
