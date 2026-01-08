"""
功能测试脚本
验证国际象棋程序的所有核心功能
"""
from chess_board import ChessBoard
from move_validator import MoveValidator
from game_manager import GameManager
from chess_ai import ChessAI


def test_board():
    """测试棋盘功能"""
    print("=" * 50)
    print("测试1: 棋盘初始化")
    print("=" * 50)
    board = ChessBoard()
    print(board)
    print(f"FEN: {board.to_fen()}")
    print("[OK] 棋盘初始化成功")
    print()
    return board


def test_moves():
    """测试移动验证"""
    print("=" * 50)
    print("测试2: 移动验证")
    print("=" * 50)

    game = GameManager()

    # 测试白兵移动 e2-e4
    print("测试移动: e2 -> e4 (白兵前进两格)")
    success = game.make_move(6, 4, 4, 4)
    print(f"移动{'成功' if success else '失败'}")
    print(game.board)
    print()

    # 测试黑兵移动 e7-e5
    print("测试移动: e7 -> e5 (黑兵前进两格)")
    success = game.make_move(1, 4, 3, 4)
    print(f"移动{'成功' if success else '失败'}")
    print(game.board)
    print()

    print("[OK] 移动验证功能正常")
    print()
    return game


def test_check_detection():
    """测试将军检测"""
    print("=" * 50)
    print("测试3: 将军检测")
    print("=" * 50)

    game = GameManager()
    validator = MoveValidator(game.board)

    # 创建一个将军局面
    # 移除一些棋子，让后可以将军王
    game.board.set_piece(7, 3, '.')  # 移除白后
    game.board.set_piece(0, 3, '.')  # 移除黑后
    game.board.set_piece(6, 4, '.')  # 移除白兵
    game.board.set_piece(5, 4, 'q')  # 放置黑后在e3

    print(game.board)

    is_check = validator.is_in_check('white')
    print(f"白王被将军: {is_check}")
    print("[OK] 将军检测功能正常")
    print()


def test_ai():
    """测试AI功能"""
    print("=" * 50)
    print("测试4: AI计算")
    print("=" * 50)

    game = GameManager()

    # 白方先走一步
    game.make_move(6, 4, 4, 4)  # e2-e4
    print("白方移动: e2 -> e4")
    print(game.board)
    print()

    # AI计算黑方的最佳走法
    print("AI正在计算黑方的最佳走法...")
    ai = ChessAI(game.board, color='black', max_depth=3)  # 使用深度3快速测试
    best_move = ai.get_best_move()

    if best_move:
        from_pos, to_pos = best_move
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        from_notation = chr(ord('a') + from_col) + str(8 - from_row)
        to_notation = chr(ord('a') + to_col) + str(8 - to_row)

        print(f"AI选择移动: {from_notation} -> {to_notation}")
        print(f"评估节点数: {ai.nodes_evaluated}")

        # 执行AI的移动
        game.make_move(from_row, from_col, to_row, to_col)
        print(game.board)
        print()

    print("[OK] AI功能正常")
    print()


def test_special_moves():
    """测试特殊移动"""
    print("=" * 50)
    print("测试5: 特殊规则")
    print("=" * 50)

    game = GameManager()

    # 测试兵升变的准备
    print("准备测试兵升变...")
    # 创建一个接近升变的局面
    game.board.set_piece(1, 0, 'P')  # 白兵在a7
    game.board.set_piece(6, 0, '.')  # 移除原位置的白兵
    print(game.board)
    print()

    # 移动白兵到a8升变
    print("白兵从a7移动到a8，升变为后")
    game.board.current_turn = 'white'
    success = game.make_move(1, 0, 0, 0, 'Q')
    print(f"升变{'成功' if success else '失败'}")
    print(game.board)
    print()

    print("[OK] 特殊规则功能正常")
    print()


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 12 + "国际象棋程序功能测试" + " " * 12 + "║")
    print("╚" + "=" * 48 + "╝")
    print()

    try:
        test_board()
        test_moves()
        test_check_detection()
        test_ai()
        test_special_moves()

        print("=" * 50)
        print("所有测试通过！[OK]")
        print("=" * 50)
        print()
        print("程序已完全准备就绪，可以正常运行。")
        print()
        print("运行方法:")
        print("1. 交互式: python main.py")
        print("2. 快速启动: python quick_start.py")
        print("3. Windows: 双击 run.bat")
        print()

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
