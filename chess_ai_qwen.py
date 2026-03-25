"""
Qwen大模型增强国际象棋AI模块
通过调用Qwen API分析棋局，结合Minimax算法实现更强的对战能力
"""
import os
import re
import time
from openai import OpenAI
from chess_ai import ChessAI
from move_validator import MoveValidator


class ChessAIQwen:
    """Qwen大模型增强的国际象棋AI类"""

    SYSTEM_PROMPT = """你是一个专业的国际象棋引擎。给定FEN局面和合法走法列表，你必须从中选择最佳走法。

严格规则：
1. 你必须且只能从提供的"合法走法"列表中选择一个走法
2. 使用UCI格式输出（如e2e4, g1f3, e7e8q）
3. 最后一行必须是：MOVE: <你选择的走法>
4. 禁止输出不在合法走法列表中的走法

分析要点：子力价值、棋子活动性、王的安全、兵型、中心控制、战术组合。
简要分析后输出走法。"""

    def __init__(self, board, color='black', max_depth=4, fallback_depth=4):
        """
        初始化Qwen增强AI

        Args:
            board: ChessBoard实例
            color: AI执棋颜色
            max_depth: Minimax后备搜索深度
            fallback_depth: 后备AI搜索深度
        """
        self.board = board
        self.color = color
        self.max_depth = max_depth

        # 初始化OpenAI兼容客户端
        api_key = os.environ.get('DASHSCOPE_API_KEY')
        base_url = os.environ.get('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = os.environ.get('QWEN_MODEL', 'qwen-plus')

        if not api_key:
            raise ValueError("未找到DASHSCOPE_API_KEY环境变量，请先配置API密钥")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

        # 后备Minimax AI
        self.fallback_ai = ChessAI(board, color=color, max_depth=fallback_depth)

        # API超时（秒）
        self.api_timeout = 30

        # 统计信息
        self.qwen_calls = 0
        self.qwen_successes = 0
        self.fallback_count = 0

    def get_best_move(self):
        """
        获取最佳移动：先尝试Qwen API（含重试），失败则回退到Minimax

        Returns:
            tuple: ((from_row, from_col), (to_row, to_col)) 或 None
        """
        self.fallback_ai.board = self.board

        validator = MoveValidator(self.board)
        legal_moves = validator.get_all_legal_moves(self.color)

        if not legal_moves:
            return None

        # 构建合法走法UCI映射表（用于快速查找）
        legal_moves_map = {}
        for (fr, fc), (tr, tc) in legal_moves:
            uci = self._pos_to_uci(fr, fc, tr, tc)
            legal_moves_map[uci] = ((fr, fc), (tr, tc))

        # 尝试Qwen（最多2次）
        start_time = time.time()
        qwen_move = self._get_qwen_move_with_retry(legal_moves, legal_moves_map)
        elapsed = time.time() - start_time

        if qwen_move:
            self.qwen_successes += 1
            print(f"Qwen AI走法 (耗时{elapsed:.1f}秒) | "
                  f"成功率: {self.qwen_successes}/{self.qwen_calls}")
            return qwen_move

        # 回退到Minimax
        self.fallback_count += 1
        print(f"Qwen回退到Minimax (深度{self.max_depth}) | "
              f"回退次数: {self.fallback_count}/{self.qwen_calls}")
        return self.fallback_ai.get_best_move()

    def _get_qwen_move_with_retry(self, legal_moves, legal_moves_map):
        """带重试的Qwen走法获取"""
        self.qwen_calls += 1

        fen = self.board.to_fen()
        color_name = "白方" if self.color == 'white' else "黑方"
        legal_uci_list = list(legal_moves_map.keys())

        history_str = self._get_move_history_str()

        user_msg = f"FEN: {fen}\n你执{color_name}。\n"
        if history_str:
            user_msg += f"走法历史: {history_str}\n"
        user_msg += f"合法走法列表: {', '.join(legal_uci_list)}\n"
        user_msg += "从以上列表中选择最佳走法。"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ]

        # 第一次尝试
        reply = self._call_api(messages)
        if reply is None:
            return None

        print(f"Qwen分析: {reply}")
        move = self._extract_move(reply, legal_moves_map)
        if move:
            return move

        # 第二次尝试：纠正提示
        print("Qwen第一次走法无效，重试中...")
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content":
            f"你的走法不在合法列表中。请直接从以下列表中选一个：\n"
            f"{', '.join(legal_uci_list)}\n"
            f"只输出 MOVE: <走法>"
        })

        reply2 = self._call_api(messages)
        if reply2 is None:
            return None

        print(f"Qwen重试: {reply2}")
        return self._extract_move(reply2, legal_moves_map)

    def _call_api(self, messages):
        """调用Qwen API"""
        try:
            api_params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 300,
                "timeout": self.api_timeout,
            }
            if 'qwen3' in self.model.lower():
                api_params["extra_body"] = {"enable_thinking": False}

            response = self.client.chat.completions.create(**api_params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Qwen API调用失败: {e}")
            return None

    def _extract_move(self, response, legal_moves_map):
        """
        从回复中提取合法走法，支持多种格式

        Args:
            response: Qwen回复文本
            legal_moves_map: {uci_str: (from_pos, to_pos)} 映射

        Returns:
            tuple 或 None
        """
        # 收集所有可能的UCI走法
        candidates = []

        # 匹配 MOVE: xxx 格式
        match = re.search(r'MOVE:\s*([a-h][1-8][a-h][1-8][qrbn]?)', response, re.IGNORECASE)
        if match:
            candidates.append(match.group(1).lower())

        # 匹配所有 UCI 格式走法（4-5字符，如 e2e4, e7e8q）
        for m in re.finditer(r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b', response, re.IGNORECASE):
            candidates.append(m.group(1).lower())

        # 匹配带分隔符的格式 e2-e4, e2 e4
        for m in re.finditer(r'\b([a-h][1-8])[-\s]([a-h][1-8])([qrbn]?)\b', response, re.IGNORECASE):
            candidates.append((m.group(1) + m.group(2) + m.group(3)).lower())

        # 按优先级检查每个候选是否合法
        for uci in candidates:
            if uci in legal_moves_map:
                return legal_moves_map[uci]

        # SAN格式兜底：尝试解析代数记谱法（如 Nf3, e4, Bxe5, O-O）
        san_move = self._try_parse_san(response, legal_moves_map)
        if san_move:
            return san_move

        if candidates:
            print(f"Qwen走法候选 {candidates} 均不在合法列表中")
        else:
            print("Qwen回复中未找到走法")
        return None

    def _try_parse_san(self, response, legal_moves_map):
        """
        尝试解析标准代数记谱法（SAN），转换为合法走法

        支持: e4, Nf3, Bxe5, O-O, O-O-O, Qd1+, Raxb1 等
        """
        # 提取SAN走法候选
        san_patterns = [
            r'\b(O-O-O|O-O)\b',
            r'\b([KQRBN])([a-h]?)([1-8]?)(x?)([a-h][1-8])([+#]?)\b',
            r'\b([a-h])(x?)([a-h][1-8])(?:=?([QRBN]))?([+#]?)\b',
            r'\b([a-h][1-8])(?:=?([QRBN]))?([+#]?)\b',
        ]

        for pattern in san_patterns:
            for match in re.finditer(pattern, response):
                san = match.group(0).rstrip('+#')
                result = self._san_to_uci(san, legal_moves_map)
                if result:
                    return result
        return None

    def _san_to_uci(self, san, legal_moves_map):
        """将单个SAN走法转为合法走法"""
        # 王车易位
        if san == 'O-O':
            king_side = 'e1g1' if self.color == 'white' else 'e8g8'
            if king_side in legal_moves_map:
                return legal_moves_map[king_side]
        elif san == 'O-O-O':
            queen_side = 'e1c1' if self.color == 'white' else 'e8c8'
            if queen_side in legal_moves_map:
                return legal_moves_map[queen_side]
            return None

        # 简单兵走法：如 "e4" -> 找合法兵走法到e4
        if re.match(r'^[a-h][1-8]$', san):
            to_col = ord(san[0]) - ord('a')
            to_row = 8 - int(san[1])
            for uci, positions in legal_moves_map.items():
                (fr, fc), (tr, tc) = positions
                piece = self.board.get_piece(fr, fc)
                if piece.upper() == 'P' and tr == to_row and tc == to_col and fc == to_col:
                    return positions
            return None

        # 兵吃子：如 "exd5"
        m = re.match(r'^([a-h])x?([a-h][1-8])(?:=?([QRBN]))?$', san)
        if m:
            from_file = ord(m.group(1)) - ord('a')
            to_col = ord(m.group(2)[0]) - ord('a')
            to_row = 8 - int(m.group(2)[1])
            promo = m.group(3).lower() if m.group(3) else ''
            for uci, positions in legal_moves_map.items():
                (fr, fc), (tr, tc) = positions
                piece = self.board.get_piece(fr, fc)
                if piece.upper() == 'P' and fc == from_file and tr == to_row and tc == to_col:
                    return positions
            return None

        # 棋子走法：如 "Nf3", "Bxe5", "Rae1"
        m = re.match(r'^([KQRBN])([a-h]?)([1-8]?)(x?)([a-h][1-8])$', san)
        if m:
            piece_type = m.group(1)
            disambig_file = ord(m.group(2)) - ord('a') if m.group(2) else None
            disambig_rank = 8 - int(m.group(3)) if m.group(3) else None
            to_col = ord(m.group(5)[0]) - ord('a')
            to_row = 8 - int(m.group(5)[1])

            for uci, positions in legal_moves_map.items():
                (fr, fc), (tr, tc) = positions
                piece = self.board.get_piece(fr, fc)
                if piece.upper() != piece_type:
                    continue
                if tr != to_row or tc != to_col:
                    continue
                if disambig_file is not None and fc != disambig_file:
                    continue
                if disambig_rank is not None and fr != disambig_rank:
                    continue
                return positions

        return None

    def _pos_to_uci(self, from_row, from_col, to_row, to_col):
        """棋盘坐标转UCI格式"""
        from_str = chr(ord('a') + from_col) + str(8 - from_row)
        to_str = chr(ord('a') + to_col) + str(8 - to_row)
        return from_str + to_str

    def _get_move_history_str(self):
        """获取最近走法历史字符串"""
        history = self.board.move_history
        if not history:
            return ""
        recent = history[-10:]
        moves = []
        for move_info in recent:
            fr, fc = move_info['from']
            tr, tc = move_info['to']
            moves.append(self._pos_to_uci(fr, fc, tr, tc))
        return ' '.join(moves)
