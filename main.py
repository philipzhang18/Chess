"""
国际象棋主程序
整合所有模块，提供游戏入口
"""
import sys
from game_manager import GameManager
from chess_ai import ChessAI
from chess_ai_gpu import ChessAIGPU
from ui.pygame_ui import PygameUI
from ai_self_play import AISelfPlay


def main():
    """主函数"""
    print("=" * 50)
    print("国际象棋程序")
    print("=" * 50)
    print()

    # 询问游戏模式
    print("请选择游戏模式:")
    print("1. 人机对战（玩家执白，AI执黑）")
    print("2. 人机对战（玩家执黑，AI执白）")
    print("3. 双人对战（本地）")
    print("4. AI自对弈（观看）")
    print()

    try:
        mode = input("请输入选项 (1-4): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n程序退出")
        sys.exit(0)

    # 创建游戏管理器
    game_manager = GameManager()

    # AI配置
    ai_player = None
    ai_depth = 6  # 默认搜索深度
    use_gpu = False  # 默认不使用GPU

    if mode in ['1', '2', '4']:
        print()
        print("AI难度设置:")
        print("1. 简单（搜索深度3层，约1秒）")
        print("2. 中等（搜索深度5层，约3秒）")
        print("3. 困难（搜索深度6层，约10秒）")
        print("4. 极难（搜索深度7层，约30秒+）")
        print()

        try:
            difficulty = input("请输入难度 (1-4，默认3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n程序退出")
            sys.exit(0)

        if difficulty == '1':
            ai_depth = 3
        elif difficulty == '2':
            ai_depth = 5
        elif difficulty == '3':
            ai_depth = 6
        elif difficulty == '4':
            ai_depth = 7
        else:
            ai_depth = 6

        # GPU加速选项
        print()
        print("是否使用GPU加速？")
        print("1. 是（需要安装CuPy和CUDA）")
        print("2. 否（使用CPU）")
        print()

        try:
            use_gpu_choice = input("请输入选项 (1-2，默认2): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n程序退出")
            sys.exit(0)

        use_gpu = (use_gpu_choice == '1')

    # 根据模式创建AI
    if mode == '1':
        # 玩家执白，AI执黑
        if use_gpu:
            ai_player = ChessAIGPU(game_manager.board, color='black', max_depth=ai_depth, use_gpu=True)
            print(f"\n游戏开始! 玩家执白，AI执黑（GPU加速，搜索深度: {ai_depth}层）")
        else:
            ai_player = ChessAI(game_manager.board, color='black', max_depth=ai_depth)
            print(f"\n游戏开始! 玩家执白，AI执黑（CPU模式，搜索深度: {ai_depth}层）")
        print("使用鼠标点击棋子进行移动")

    elif mode == '2':
        # 玩家执黑，AI执白
        if use_gpu:
            ai_player = ChessAIGPU(game_manager.board, color='white', max_depth=ai_depth, use_gpu=True)
            print(f"\n游戏开始! AI执白，玩家执黑（GPU加速，搜索深度: {ai_depth}层）")
        else:
            ai_player = ChessAI(game_manager.board, color='white', max_depth=ai_depth)
            print(f"\n游戏开始! AI执白，玩家执黑（CPU模式，搜索深度: {ai_depth}层）")
        print("使用鼠标点击棋子进行移动")

    elif mode == '3':
        # 双人对战
        print("\n游戏开始! 双人对战模式")
        print("白方先行，使用鼠标点击棋子进行移动")

    elif mode == '4':
        # AI自对弈
        gpu_mode_text = "GPU加速" if use_gpu else "CPU模式"
        print(f"\n开始AI自对弈（{gpu_mode_text}，双方搜索深度: {ai_depth}层）")
        print("正在运行，请稍候...")
        print()

        # 创建自对弈实例
        self_play = AISelfPlay(
            white_depth=ai_depth,
            black_depth=ai_depth,
            display_board=True,
            delay=0.5,
            use_gpu=use_gpu
        )

        # 开始对弈
        result = self_play.play_game()

        # 游戏结束，直接退出
        print("\n感谢观看！")
        sys.exit(0)

    else:
        print("无效选项，使用默认模式（玩家执白，AI执黑）")
        if use_gpu:
            ai_player = ChessAIGPU(game_manager.board, color='black', max_depth=ai_depth, use_gpu=True)
        else:
            ai_player = ChessAI(game_manager.board, color='black', max_depth=ai_depth)

    print("\n正在启动Pygame界面...")
    print()

    # 创建并运行Pygame界面
    try:
        ui = PygameUI(game_manager)
        ui.run(ai_player)
    except KeyboardInterrupt:
        print("\n程序被中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n游戏结束，感谢游玩!")


if __name__ == "__main__":
    main()
