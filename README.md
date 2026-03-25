# 国际象棋程序

一个完整的国际象棋对战程序，使用Python和Pygame实现。

## 功能特性

- 完整的国际象棋规则引擎（王车易位、吃过路兵、兵升变）
- 将军、将死、僵局判定
- AI对手（Minimax算法 + Alpha-Beta剪枝，可调深度3-7层）
- Qwen大模型AI对战（通过DashScope API，支持战术分析与SAN/UCI多格式解析）
- GPU加速支持（可选，需CuPy + CUDA）
- AI自对弈观战模式
- 精美Pygame图形界面（深色主题、棋子描边、走法圆点指示、将军径向高亮、被吃棋子展示）
- 超时保护与降级处理机制

## 环境要求

- Python 3.7+
- Pygame 2.0+
- openai（Qwen模式需要）

### Qwen大模型对战额外要求

设置以下环境变量：

```bash
export DASHSCOPE_API_KEY="your-api-key"
export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 可选，有默认值
export QWEN_MODEL="qwen3.5-plus"  # 可选，有默认值
```

## 安装与运行

```bash
pip install -r requirements.txt
python main.py
```

## 游戏模式

| 选项 | 模式 | 说明 |
|------|------|------|
| 1 | 人机对战 | 玩家执白，Minimax AI执黑 |
| 2 | 人机对战 | 玩家执黑，Minimax AI执白 |
| 3 | 双人对战 | 本地双人 |
| 4 | AI自对弈 | 观看Minimax AI对战 |
| 5 | Qwen对战 | 玩家执白，Qwen大模型执黑 |
| 6 | Qwen对战 | 玩家执黑，Qwen大模型执白 |

## 操作说明

- 鼠标点击选择棋子，合法走法以圆点/三角标记显示
- 点击目标位置完成移动
- 兵到达底线弹出升变选择
- 上一步走法自动高亮，将军时王的位置红色渐变警示

## 项目结构

```
Chess/
├── chess_board.py      # 棋盘类，管理棋盘状态与FEN导出
├── move_validator.py   # 移动规则验证器
├── game_manager.py     # 游戏管理器，处理移动和特殊规则
├── chess_ai.py         # AI引擎（Minimax + Alpha-Beta剪枝）
├── chess_ai_gpu.py     # GPU加速版AI引擎（惰性导入，不阻塞启动）
├── chess_ai_qwen.py    # Qwen大模型AI引擎（含SAN解析、重试机制）
├── ai_self_play.py     # AI自对弈模块
├── ui/
│   ├── __init__.py
│   └── pygame_ui.py    # Pygame图形界面（深色主题）
├── main.py             # 主程序入口
├── test_all.py         # 测试
├── test_gpu.py         # GPU功能测试
├── quick_start.py      # 快速启动（跳过菜单）
├── requirements.txt    # 依赖包列表
├── README.md
└── CLAUDE.md           # 开发文档
```

## 技术实现

### AI算法

- **Minimax + Alpha-Beta剪枝**：搜索最优走法，支持3-7层深度
- **Qwen大模型**：发送FEN棋局+合法走法列表给Qwen API，返回最佳走法
  - 强制从合法走法列表中选择，大幅降低无效走法率
  - 支持UCI（e2e4）、带分隔符（e2-e4）、标准代数记谱法SAN（Nf3, O-O, exd5）多格式解析
  - 无效走法时自动重试一次，仍失败则回退到Minimax
  - qwen3系列自动关闭深度思考，响应约4-5秒
- **评估函数**：材料价值 + 位置价值表 + 移动自由度 + 王的安全 + 中心控制 + 兵型结构

### 图形界面

- 深色主题，木质棋盘配色
- 棋子Unicode符号 + 描边增强辨识度
- 走法指示：空格圆点、吃子三角标记
- 上一步高亮、将军径向红色渐变
- 顶部状态栏（回合、将军警告、回合数）
- 底部被吃棋子展示栏

## 更新日志

### v1.2.0 (2026-03-25)
- 新增Qwen大模型AI对战模式（选项5/6）
- 强化Qwen提示词，强制从合法走法列表选择
- 支持UCI/SAN多格式解析 + 重试机制，回退率接近0
- 全新深色主题UI：棋子描边、走法圆点指示、将军渐变、被吃棋子展示
- GPU/Qwen/自对弈模块改为惰性导入，修复CuPy阻塞启动问题

### v1.1.0 (2026-01-15)
- 新增GPU加速支持（chess_ai_gpu.py）
- 新增AI自对弈模式（ai_self_play.py）
- 修复AI在将军时评分-inf导致卡住的问题
- 添加超时保护与降级处理机制

## 许可证

本项目仅供学习和研究使用。
