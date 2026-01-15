# 国际象棋程序

一个完整的国际象棋对战程序，使用Python和Pygame实现。

## 功能特性

- ✅ 完整的国际象棋规则引擎
- ✅ 所有棋子的合法走法验证
- ✅ 特殊规则支持：王车易位、吃过路兵、兵升变
- ✅ 将军、将死、僵局判定
- ✅ AI对手（Minimax算法 + Alpha-Beta剪枝）
- ✅ GPU加速支持（可选，需要CuPy和CUDA）
- ✅ AI自对弈模式（观看AI对战）
- ✅ 精美的Pygame图形界面
- ✅ 多种游戏模式（人机对战、双人对战、AI自对弈）
- ✅ 可调节的AI难度（3-7层搜索深度）
- ✅ 超时保护和降级处理机制

## 环境要求

- Python 3.7+
- Pygame 2.0+

## 安装步骤

1. 确保已安装Python环境（推荐使用虚拟环境）

```bash
# 使用指定的Python环境
E:\AI\cursor\starone\venv\Scripts\python.exe -m pip install -r requirements.txt
```

或者使用系统Python：

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
# 使用指定的Python环境
E:\AI\cursor\starone\venv\Scripts\python.exe main.py

# 或使用系统Python
python main.py
```

## 使用说明

1. 启动程序后，选择游戏模式：
   - 人机对战（玩家执白或执黑）
   - 双人对战
   - AI自对弈（观看）

2. 选择AI难度：
   - 简单：3层搜索深度（约1秒）
   - 中等：5层搜索深度（约3秒）
   - 困难：6层搜索深度（约10秒）
   - 极难：7层搜索深度（约30秒+）

3. 游戏操作：
   - 使用鼠标点击选择棋子
   - 合法移动位置会高亮显示
   - 再次点击目标位置完成移动
   - 当兵到达底线时，会弹出升变选择窗口

## 项目结构

```
Chess/
├── chess_board.py      # 棋盘类，管理棋盘状态
├── move_validator.py   # 移动规则验证器
├── game_manager.py     # 游戏管理器，处理移动和特殊规则
├── chess_ai.py         # AI引擎（Minimax + Alpha-Beta）
├── chess_ai_gpu.py     # GPU加速版AI引擎
├── ai_self_play.py     # AI自对弈模块
├── ui/
│   ├── __init__.py
│   └── pygame_ui.py    # Pygame图形界面
├── main.py             # 主程序入口
├── test_gpu.py         # GPU功能测试
├── requirements.txt    # 依赖包列表
├── README.md           # 本文件
└── CLAUDE.md           # 开发文档（供Claude Code使用）
```

## 最近更新

### v1.1.0 (2026-01-15)
- ✨ 新增GPU加速支持（chess_ai_gpu.py）
- ✨ 新增AI自对弈模式（ai_self_play.py）
- 🐛 修复AI在将军时评分-inf导致卡住的问题
- 🔧 添加超时保护机制，防止搜索时间过长
- 🔧 添加降级处理，确保AI在困难局面下仍能选择合法移动

## 技术实现

### 规则引擎
- 使用2D数组表示8x8棋盘
- 大写字母代表白方棋子，小写字母代表黑方棋子
- 实现了所有标准国际象棋规则
- 支持FEN记谱法导出

### AI算法
- **Minimax算法**：搜索最优走法
- **Alpha-Beta剪枝**：优化搜索效率
- **超时保护**：防止搜索时间过长，超时时返回静态评估
- **降级处理**：在极端情况下确保能选择合法移动
- **评估函数**：
  - 材料价值（棋子基础分值）
  - 位置价值（基于位置价值表）
  - 移动自由度（可行走法数量）
  - 王的安全性（将军状态检测）
  - 中心控制（占据中心格子奖励）
  - 兵型结构（双兵惩罚、兵链奖励）

### 图形界面
- 使用Pygame实现
- Unicode棋子符号显示
- 交互式移动操作
- 合法走法高亮提示
- 将军状态红色警告
- 游戏状态实时显示

## 开发说明

详细的开发文档请参考 `CLAUDE.md` 文件。

## 已知限制

- AI深度7层以上可能导致响应时间过长
- 暂不支持悔棋功能
- 暂不支持游戏保存/加载

## 许可证

本项目仅供学习和研究使用。
