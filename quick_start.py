"""
国际象棋快速启动程序
默认模式：玩家执白 vs AI执黑（中等难度）
"""
import sys
from game_manager import GameManager
from chess_ai import ChessAI
from ui.pygame_ui import PygameUI


def main():
    """主函数 - 快速启动模式"""
    print("=" * 50)
    print("国际象棋程序 - 快速启动")
    print("=" * 50)
    print()
    print("游戏模式: 玩家执白 vs AI执黑")
    print("AI难度: 中等（搜索深度4层，响应快速）")
    print()
    print("操作说明:")
    print("- 使用鼠标点击选择棋子")
    print("- 合法移动位置会高亮显示")
    print("- 点击目标位置完成移动")
    print("- 兵到达底线时会弹出升变选择")
    print("- AI思考时间约2-5秒")
    print()
    print("正在启动游戏界面...")
    print()

    # 创建游戏管理器
    game_manager = GameManager()

    # 创建AI（执黑，中等难度 - 搜索深度4层）
    ai_player = ChessAI(game_manager.board, color='black', max_depth=4)

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
