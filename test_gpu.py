"""
GPU加速测试脚本
测试GPU加速AI的功能和性能
"""
import time
from chess_board import ChessBoard
from chess_ai import ChessAI
from chess_ai_gpu import ChessAIGPU

def test_gpu_availability():
    """测试GPU是否可用"""
    print("=" * 60)
    print("测试1: GPU可用性检测")
    print("=" * 60)

    try:
        import cupy as cp
        print(f"[OK] CuPy已安装，版本: {cp.__version__}")
        print(f"[OK] CUDA运行时版本: {cp.cuda.runtime.runtimeGetVersion()}")
        print(f"[OK] GPU设备数量: {cp.cuda.runtime.getDeviceCount()}")
        return True
    except ImportError:
        print("[FAIL] CuPy未安装，将使用CPU模式")
        return False
    except Exception as e:
        print(f"[FAIL] GPU检测失败: {e}")
        return False

def test_ai_initialization():
    """测试AI初始化"""
    print("\n" + "=" * 60)
    print("测试2: AI初始化")
    print("=" * 60)

    board = ChessBoard()

    # 测试CPU AI
    print("\n初始化CPU AI...")
    cpu_ai = ChessAI(board, color='black', max_depth=3)
    print("[OK] CPU AI初始化成功")

    # 测试GPU AI
    print("\n初始化GPU AI...")
    gpu_ai = ChessAIGPU(board, color='black', max_depth=3, use_gpu=True)
    print("[OK] GPU AI初始化成功")

    return cpu_ai, gpu_ai

def test_ai_move():
    """测试AI移动计算"""
    print("\n" + "=" * 60)
    print("测试3: AI移动计算")
    print("=" * 60)

    board = ChessBoard()

    # 测试CPU AI
    print("\nCPU AI计算最佳移动...")
    cpu_ai = ChessAI(board, color='white', max_depth=3)
    start_time = time.time()
    cpu_move = cpu_ai.get_best_move()
    cpu_time = time.time() - start_time
    print(f"[OK] CPU AI完成，耗时: {cpu_time:.2f}秒")
    print(f"  最佳移动: {cpu_move}")

    # 重置棋盘
    board = ChessBoard()

    # 测试GPU AI
    print("\nGPU AI计算最佳移动...")
    gpu_ai = ChessAIGPU(board, color='white', max_depth=3, use_gpu=True)
    start_time = time.time()
    gpu_move = gpu_ai.get_best_move()
    gpu_time = time.time() - start_time
    print(f"[OK] GPU AI完成，耗时: {gpu_time:.2f}秒")
    print(f"  最佳移动: {gpu_move}")

    # 性能对比
    print("\n" + "-" * 60)
    print("性能对比:")
    print(f"  CPU时间: {cpu_time:.2f}秒")
    print(f"  GPU时间: {gpu_time:.2f}秒")
    if gpu_time < cpu_time:
        speedup = cpu_time / gpu_time
        print(f"  GPU加速比: {speedup:.2f}x")
    else:
        print(f"  注意: GPU模式较慢，可能是因为数据传输开销")

    return cpu_time, gpu_time

if __name__ == "__main__":
    print("国际象棋AI GPU加速测试")
    print()

    # 测试1: GPU可用性
    gpu_available = test_gpu_availability()

    # 测试2: AI初始化
    test_ai_initialization()

    # 测试3: AI移动计算
    test_ai_move()

    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
