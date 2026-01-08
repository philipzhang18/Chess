"""
国际象棋AI模块
实现Minimax算法配合Alpha-Beta剪枝
"""
import time
from move_validator import MoveValidator


class ChessAI:
    """国际象棋AI类"""

    # 位置价值表 - 白方视角
    # 兵的位置价值表
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]

    # 马的位置价值表
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]

    # 象的位置价值表
    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]

    # 车的位置价值表
    ROOK_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]

    # 后的位置价值表
    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]

    # 王的位置价值表（中局）
    KING_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]

    def __init__(self, board, color='black', max_depth=6):
        """
        初始化AI

        Args:
            board: ChessBoard实例
            color: AI执棋颜色（'white' 或 'black'）
            max_depth: 最大搜索深度
        """
        self.board = board
        self.color = color
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.time_limit = 15.0  # 每步最大思考时间（秒）
        self.start_time = 0

    def get_best_move(self):
        """
        获取最佳移动

        Returns:
            tuple: ((from_row, from_col), (to_row, to_col)) 或 None
        """
        self.nodes_evaluated = 0
        self.start_time = time.time()

        validator = MoveValidator(self.board)
        legal_moves = validator.get_all_legal_moves(self.color)

        if not legal_moves:
            return None

        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # 对每个合法移动进行评估
        for move in legal_moves:
            # 检查是否超时
            if time.time() - self.start_time > self.time_limit:
                print(f"AI搜索超时，已评估 {self.nodes_evaluated} 节点")
                break

            from_pos, to_pos = move
            from_row, from_col = from_pos
            to_row, to_col = to_pos

            # 创建临时棋盘并执行移动
            temp_board = self.board.copy()
            self._execute_move(temp_board, from_row, from_col, to_row, to_col)

            # 使用Minimax评估
            value = self._minimax(temp_board, self.max_depth - 1, alpha, beta, False)

            # 更新最佳移动
            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)

        elapsed_time = time.time() - self.start_time
        print(f"AI思考时间: {elapsed_time:.2f}秒, 评估节点数: {self.nodes_evaluated}, 深度: {self.max_depth}")

        return best_move

    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Minimax算法配合Alpha-Beta剪枝

        Args:
            board: 当前棋盘状态
            depth: 剩余搜索深度
            alpha: Alpha值
            beta: Beta值
            is_maximizing: 是否是最大化玩家

        Returns:
            float: 评估值
        """
        self.nodes_evaluated += 1

        # 检查超时
        if time.time() - self.start_time > self.time_limit:
            return self._evaluate_board(board)

        # 达到最大深度或游戏结束
        if depth == 0:
            return self._evaluate_board(board)

        validator = MoveValidator(board)
        current_color = self.color if is_maximizing else self._opposite_color(self.color)

        # 检查游戏是否结束
        if validator.is_checkmate(current_color):
            return float('-inf') if is_maximizing else float('inf')
        if validator.is_stalemate(current_color):
            return 0

        legal_moves = validator.get_all_legal_moves(current_color)
        if not legal_moves:
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                # 超时检测
                if time.time() - self.start_time > self.time_limit:
                    return max_eval

                from_pos, to_pos = move
                from_row, from_col = from_pos
                to_row, to_col = to_pos

                temp_board = board.copy()
                self._execute_move(temp_board, from_row, from_col, to_row, to_col)

                eval_value = self._minimax(temp_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_value)

                alpha = max(alpha, eval_value)
                if beta <= alpha:
                    break  # Beta剪枝

            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                # 超时检测
                if time.time() - self.start_time > self.time_limit:
                    return min_eval

                from_pos, to_pos = move
                from_row, from_col = from_pos
                to_row, to_col = to_pos

                temp_board = board.copy()
                self._execute_move(temp_board, from_row, from_col, to_row, to_col)

                eval_value = self._minimax(temp_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_value)

                beta = min(beta, eval_value)
                if beta <= alpha:
                    break  # Alpha剪枝

            return min_eval

    def _evaluate_board(self, board):
        """
        评估棋盘局面

        Returns:
            float: 评估值（正值对AI有利，负值对对手有利）
        """
        score = 0

        # 遍历棋盘上的所有棋子
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece == board.EMPTY:
                    continue

                piece_type = piece.upper()
                is_white = board.is_white_piece(piece)
                piece_color = 'white' if is_white else 'black'

                # 基础材料价值
                piece_value = board.PIECE_VALUES.get(piece_type, 0)

                # 位置价值
                position_value = self._get_position_value(piece_type, row, col, is_white)

                total_value = piece_value + position_value

                # 根据颜色决定加减
                if piece_color == self.color:
                    score += total_value
                else:
                    score -= total_value

        # 添加其他评估因素
        score += self._evaluate_mobility(board)
        score += self._evaluate_king_safety(board)

        return score

    def _get_position_value(self, piece_type, row, col, is_white):
        """获取棋子的位置价值"""
        # 黑方需要翻转棋盘
        eval_row = row if is_white else 7 - row

        if piece_type == 'P':
            return self.PAWN_TABLE[eval_row][col]
        elif piece_type == 'N':
            return self.KNIGHT_TABLE[eval_row][col]
        elif piece_type == 'B':
            return self.BISHOP_TABLE[eval_row][col]
        elif piece_type == 'R':
            return self.ROOK_TABLE[eval_row][col]
        elif piece_type == 'Q':
            return self.QUEEN_TABLE[eval_row][col]
        elif piece_type == 'K':
            return self.KING_TABLE[eval_row][col]

        return 0

    def _evaluate_mobility(self, board):
        """评估移动自由度"""
        validator = MoveValidator(board)

        ai_moves = len(validator.get_all_legal_moves(self.color))
        opponent_moves = len(validator.get_all_legal_moves(self._opposite_color(self.color)))

        return (ai_moves - opponent_moves) * 10

    def _evaluate_king_safety(self, board):
        """评估王的安全性"""
        validator = MoveValidator(board)
        score = 0

        # 检查AI的王是否被将军
        if validator.is_in_check(self.color):
            score -= 50

        # 检查对手的王是否被将军
        if validator.is_in_check(self._opposite_color(self.color)):
            score += 50

        return score

    def _execute_move(self, board, from_row, from_col, to_row, to_col):
        """
        在棋盘上执行移动（简化版本，仅用于AI搜索）

        Args:
            board: ChessBoard实例
            from_row, from_col: 起始位置
            to_row, to_col: 目标位置
        """
        piece = board.get_piece(from_row, from_col)
        piece_type = piece.upper()
        is_white = board.is_white_piece(piece)

        # 处理吃过路兵
        if piece_type == 'P' and board.en_passant_target == (to_row, to_col):
            en_passant_row = to_row + (1 if is_white else -1)
            board.set_piece(en_passant_row, to_col, board.EMPTY)

        # 处理王车易位
        elif piece_type == 'K' and abs(to_col - from_col) == 2:
            is_kingside = to_col > from_col
            rook_col = 7 if is_kingside else 0
            rook_new_col = 5 if is_kingside else 3
            rook = board.get_piece(from_row, rook_col)
            board.set_piece(from_row, rook_new_col, rook)
            board.set_piece(from_row, rook_col, board.EMPTY)

        # 执行移动
        board.set_piece(to_row, to_col, piece)
        board.set_piece(from_row, from_col, board.EMPTY)

        # 更新王的位置
        if piece_type == 'K':
            if is_white:
                board.white_king_pos = (to_row, to_col)
            else:
                board.black_king_pos = (to_row, to_col)

        # 处理兵升变（默认升变为后）
        if piece_type == 'P':
            promotion_row = 0 if is_white else 7
            if to_row == promotion_row:
                promoted = 'Q' if is_white else 'q'
                board.set_piece(to_row, to_col, promoted)

        # 更新吃过路兵目标
        board.en_passant_target = None
        if piece_type == 'P' and abs(to_row - from_row) == 2:
            en_passant_row = from_row + (1 if is_white else -1)
            board.en_passant_target = (en_passant_row, to_col)

        # 更新王车易位标志
        if piece_type == 'K':
            if is_white:
                board.white_king_moved = True
            else:
                board.black_king_moved = True
        elif piece_type == 'R':
            if is_white:
                if from_col == 7:
                    board.white_rook_king_side_moved = True
                elif from_col == 0:
                    board.white_rook_queen_side_moved = True
            else:
                if from_col == 7:
                    board.black_rook_king_side_moved = True
                elif from_col == 0:
                    board.black_rook_queen_side_moved = True

        # 切换回合
        board.switch_turn()

    def _opposite_color(self, color):
        """获取对方颜色"""
        return 'black' if color == 'white' else 'white'
