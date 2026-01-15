"""
国际象棋AI模块 - GPU加速版本
使用CuPy进行GPU加速，提升Minimax算法的计算效率
"""
import time
import numpy as np
from move_validator import MoveValidator

# 尝试导入CuPy，如果失败则使用NumPy
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("GPU加速已启用 (CuPy)")
except ImportError:
    cp = np
    GPU_AVAILABLE = False
    print("GPU不可用，使用CPU模式 (NumPy)")


class ChessAIGPU:
    """国际象棋AI类 - GPU加速版本"""

    def __init__(self, board, color='black', max_depth=6, use_gpu=True):
        """
        初始化AI

        Args:
            board: ChessBoard实例
            color: AI执棋颜色（'white' 或 'black'）
            max_depth: 最大搜索深度
            use_gpu: 是否使用GPU加速（如果可用）
        """
        self.board = board
        self.color = color
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.time_limit = 30.0  # 每步最大思考时间（秒）
        self.start_time = 0

        # GPU设置
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.xp = cp if self.use_gpu else np

        # 初始化位置价值表（转换为GPU数组）
        self._init_position_tables()

        print(f"AI初始化完成 - 模式: {'GPU' if self.use_gpu else 'CPU'}, 深度: {max_depth}")

    def _init_position_tables(self):
        """初始化位置价值表并转换为GPU数组"""
        # 兵的位置价值表
        pawn_table = [
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
        knight_table = [
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
        bishop_table = [
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
        rook_table = [
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
        queen_table = [
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
        king_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]

        # 转换为GPU数组
        self.pawn_table = self.xp.array(pawn_table, dtype=self.xp.float32)
        self.knight_table = self.xp.array(knight_table, dtype=self.xp.float32)
        self.bishop_table = self.xp.array(bishop_table, dtype=self.xp.float32)
        self.rook_table = self.xp.array(rook_table, dtype=self.xp.float32)
        self.queen_table = self.xp.array(queen_table, dtype=self.xp.float32)
        self.king_table = self.xp.array(king_table, dtype=self.xp.float32)

        # 棋子价值字典
        self.piece_values = {
            'P': 100, 'N': 320, 'B': 330,
            'R': 500, 'Q': 900, 'K': 20000
        }

    def get_best_move(self):
        """
        获取最佳移动（GPU加速版本）

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

        print(f"开始评估 {len(legal_moves)} 个候选移动...")

        # 对每个合法移动进行评估
        for i, move in enumerate(legal_moves):
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

            # 显示进度
            if (i + 1) % 5 == 0 or (i + 1) == len(legal_moves):
                print(f"进度: {i + 1}/{len(legal_moves)}, 当前最佳评分: {best_value:.1f}")

        # 降级处理：如果所有移动都是-inf（例如必输局面），选择第一个合法移动
        if best_move is None and legal_moves:
            best_move = legal_moves[0]
            best_value = float('-inf')
            print("警告: 所有移动评分均为-inf，选择第一个合法移动作为降级方案")

        elapsed_time = time.time() - self.start_time
        print(f"AI思考完成 - 时间: {elapsed_time:.2f}秒, 节点数: {self.nodes_evaluated}, 深度: {self.max_depth}")
        print(f"最佳移动评分: {best_value:.1f}")

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
                if time.time() - self.start_time > self.time_limit:
                    # 如果还没评估任何移动，返回静态评估而不是-inf
                    if max_eval == float('-inf'):
                        return self._evaluate_board(board)
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
                if time.time() - self.start_time > self.time_limit:
                    # 如果还没评估任何移动，返回静态评估而不是+inf
                    if min_eval == float('inf'):
                        return self._evaluate_board(board)
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
        评估棋盘局面（GPU加速版本）

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
                piece_value = self.piece_values.get(piece_type, 0)

                # 位置价值（使用GPU数组）
                position_value = self._get_position_value_gpu(piece_type, row, col, is_white)

                total_value = piece_value + position_value

                # 根据颜色决定加减
                if piece_color == self.color:
                    score += total_value
                else:
                    score -= total_value

        # 添加其他评估因素
        score += self._evaluate_mobility(board)
        score += self._evaluate_king_safety(board)
        score += self._evaluate_center_control(board)

        return score

    def _get_position_value_gpu(self, piece_type, row, col, is_white):
        """获取棋子的位置价值（GPU加速版本）"""
        # 黑方需要翻转棋盘
        eval_row = row if is_white else 7 - row

        # 使用GPU数组查询位置价值
        if piece_type == 'P':
            value = float(self.pawn_table[eval_row, col])
        elif piece_type == 'N':
            value = float(self.knight_table[eval_row, col])
        elif piece_type == 'B':
            value = float(self.bishop_table[eval_row, col])
        elif piece_type == 'R':
            value = float(self.rook_table[eval_row, col])
        elif piece_type == 'Q':
            value = float(self.queen_table[eval_row, col])
        elif piece_type == 'K':
            value = float(self.king_table[eval_row, col])
        else:
            value = 0

        # 如果使用GPU，需要将结果转回CPU
        if self.use_gpu and hasattr(value, 'get'):
            value = value.get()

        return value

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

    def _evaluate_center_control(self, board):
        """评估中心控制"""
        score = 0
        # 中心格子：d4, e4, d5, e5
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        # 扩展中心
        extended_center = [
            (2, 2), (2, 3), (2, 4), (2, 5),
            (3, 2), (3, 5),
            (4, 2), (4, 5),
            (5, 2), (5, 3), (5, 4), (5, 5)
        ]

        # 评估中心控制
        for row, col in center_squares:
            piece = board.get_piece(row, col)
            if piece != board.EMPTY:
                piece_color = 'white' if board.is_white_piece(piece) else 'black'
                if piece_color == self.color:
                    score += 30
                else:
                    score -= 30

        # 评估扩展中心控制
        for row, col in extended_center:
            piece = board.get_piece(row, col)
            if piece != board.EMPTY:
                piece_color = 'white' if board.is_white_piece(piece) else 'black'
                if piece_color == self.color:
                    score += 10
                else:
                    score -= 10

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
