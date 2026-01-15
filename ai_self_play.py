"""
AI自对弈模块
实现两个AI互相对弈的功能
"""
import time
from chess_board import ChessBoard
from game_manager import GameManager
from chess_ai import ChessAI
from chess_ai_gpu import ChessAIGPU


class AISelfPlay:
    """AI自对弈类"""

    def __init__(self, white_depth=3, black_depth=3, display_board=True, delay=0.5, use_gpu=False):
        """
        初始化AI自对弈

        Args:
            white_depth: 白方AI搜索深度
            black_depth: 黑方AI搜索深度
            display_board: 是否显示棋盘
            delay: 每步之间的延迟（秒）
            use_gpu: 是否使用GPU加速
        """
        self.game_manager = GameManager()

        # 根据use_gpu选择AI类型
        if use_gpu:
            self.white_ai = ChessAIGPU(self.game_manager.board, color='white', max_depth=white_depth, use_gpu=True)
            self.black_ai = ChessAIGPU(self.game_manager.board, color='black', max_depth=black_depth, use_gpu=True)
        else:
            self.white_ai = ChessAI(self.game_manager.board, color='white', max_depth=white_depth)
            self.black_ai = ChessAI(self.game_manager.board, color='black', max_depth=black_depth)

        self.display_board = display_board
        self.delay = delay
        self.move_count = 0
        self.max_moves = 200  # 最大移动数限制，防止无限循环

    def play_game(self):
        """
        开始AI自对弈

        Returns:
            dict: 游戏结果信息
        """
        print("=" * 60)
        print("AI自对弈开始")
        print(f"白方AI深度: {self.white_ai.max_depth}, 黑方AI深度: {self.black_ai.max_depth}")
        print("=" * 60)

        if self.display_board:
            print("\n初始棋盘:")
            print(self.game_manager.board)
            print()

        start_time = time.time()

        while not self.game_manager.game_over and self.move_count < self.max_moves:
            self.move_count += 1
            current_turn = self.game_manager.board.current_turn

            print(f"\n--- 第 {self.move_count} 回合 ({current_turn}) ---")

            # 选择当前AI
            current_ai = self.white_ai if current_turn == 'white' else self.black_ai

            # 更新AI的棋盘引用（确保AI使用最新的棋盘状态）
            current_ai.board = self.game_manager.board

            # 获取最佳移动
            best_move = current_ai.get_best_move()

            if best_move is None:
                print(f"{current_turn} 无合法移动！")
                break

            from_pos, to_pos = best_move
            from_row, from_col = from_pos
            to_row, to_col = to_pos

            # 获取棋子信息
            piece = self.game_manager.board.get_piece(from_row, from_col)
            move_notation = self._get_move_description(from_row, from_col, to_row, to_col, piece)

            # 执行移动
            success = self.game_manager.make_move(from_row, from_col, to_row, to_col)

            if not success:
                print(f"移动失败: {move_notation}")
                break

            print(f"{current_turn} 移动: {move_notation}")

            # 显示棋盘
            if self.display_board:
                print(self.game_manager.board)

            # 显示游戏状态
            status = self.game_manager.get_game_status()
            if status['is_check']:
                print(f"[将军] {self.game_manager.board.current_turn} 被将军！")

            # 延迟
            if self.delay > 0:
                time.sleep(self.delay)

        # 游戏结束
        end_time = time.time()
        elapsed_time = end_time - start_time

        print("\n" + "=" * 60)
        print("游戏结束")
        print("=" * 60)

        result = self._get_game_result()
        result['total_moves'] = self.move_count
        result['duration'] = elapsed_time

        self._print_result(result)

        return result

    def _get_move_description(self, from_row, from_col, to_row, to_col, piece):
        """获取移动描述"""
        piece_names = {
            'P': '兵', 'p': '兵',
            'N': '马', 'n': '马',
            'B': '象', 'b': '象',
            'R': '车', 'r': '车',
            'Q': '后', 'q': '后',
            'K': '王', 'k': '王'
        }

        from_notation = chr(ord('a') + from_col) + str(8 - from_row)
        to_notation = chr(ord('a') + to_col) + str(8 - to_row)
        piece_name = piece_names.get(piece, piece)

        target = self.game_manager.board.get_piece(to_row, to_col)
        capture_symbol = 'x' if target != self.game_manager.board.EMPTY else '-'

        return f"{piece_name}({from_notation}){capture_symbol}{to_notation}"

    def _get_game_result(self):
        """获取游戏结果"""
        status = self.game_manager.get_game_status()

        result = {
            'winner': status['winner'],
            'result_type': status['result'],
            'final_position': self.game_manager.board.to_fen(),
            'white_pieces': self._count_pieces('white'),
            'black_pieces': self._count_pieces('black'),
            'captured_pieces': len(self.game_manager.board.captured_pieces)
        }

        return result

    def _count_pieces(self, color):
        """统计指定颜色的棋子数量"""
        count = 0
        for row in range(8):
            for col in range(8):
                piece = self.game_manager.board.get_piece(row, col)
                if piece != self.game_manager.board.EMPTY:
                    if self.game_manager.board.get_piece_color(piece) == color:
                        count += 1
        return count

    def _print_result(self, result):
        """打印游戏结果"""
        print(f"\n总回合数: {result['total_moves']}")
        print(f"游戏时长: {result['duration']:.2f} 秒")

        if result['winner']:
            winner_name = '白方' if result['winner'] == 'white' else '黑方'
            if result['result_type'] == 'checkmate':
                print(f"[胜利] 胜利者: {winner_name} (将死)")
            else:
                print(f"[胜利] 胜利者: {winner_name}")
        elif result['result_type'] == 'stalemate':
            print("[平局] 平局 (僵局)")
        else:
            print("[超时] 游戏达到最大回合数限制")

        print(f"\n剩余棋子:")
        print(f"  白方: {result['white_pieces']} 个")
        print(f"  黑方: {result['black_pieces']} 个")
        print(f"  被吃棋子: {result['captured_pieces']} 个")

        print(f"\n最终局面 (FEN):")
        print(f"  {result['final_position']}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("国际象棋 AI 自对弈")
    print("=" * 60)

    # 可以调整AI深度和其他参数
    # 深度越大，AI越强但速度越慢
    # 建议范围: 2-4 (快速), 5-6 (中等), 7+ (慢但强)
    white_depth = 6
    black_depth = 6

    print(f"\n设置:")
    print(f"  白方AI深度: {white_depth}")
    print(f"  黑方AI深度: {black_depth}")
    print(f"  显示棋盘: 是")
    print(f"  移动延迟: 0.5秒")

    # 创建自对弈实例
    self_play = AISelfPlay(
        white_depth=white_depth,
        black_depth=black_depth,
        display_board=True,
        delay=0.5
    )

    # 开始对弈
    result = self_play.play_game()

    print("\n" + "=" * 60)
    print("感谢观看！")
    print("=" * 60)


if __name__ == "__main__":
    main()
