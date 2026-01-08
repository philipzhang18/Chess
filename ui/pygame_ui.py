"""
Pygame图形界面模块
实现国际象棋的图形化界面
"""
import pygame
import sys
import os


class PygameUI:
    """Pygame图形界面类"""

    # 颜色定义
    WHITE = (240, 217, 181)
    BLACK = (181, 136, 99)
    HIGHLIGHT = (186, 202, 68)
    CHECK_HIGHLIGHT = (255, 100, 100)
    TEXT_COLOR = (50, 50, 50)
    BUTTON_COLOR = (100, 150, 200)
    BUTTON_HOVER = (120, 170, 220)

    # 棋子Unicode字符（用于支持Unicode的字体）
    PIECE_SYMBOLS_UNICODE = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
    }

    # 棋子ASCII字符（备选方案）
    PIECE_SYMBOLS_ASCII = {
        'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': 'P',
        'k': 'K', 'q': 'Q', 'r': 'R', 'b': 'B', 'n': 'N', 'p': 'P'
    }

    def __init__(self, game_manager, width=800, height=800):
        """
        初始化Pygame界面

        Args:
            game_manager: GameManager实例
            width: 窗口宽度
            height: 窗口高度
        """
        pygame.init()

        self.game_manager = game_manager
        self.width = width
        self.height = height
        self.board_size = min(width, height) - 100  # 留出空间显示信息
        self.square_size = self.board_size // 8
        self.board_offset_x = (width - self.board_size) // 2
        self.board_offset_y = 50

        # 创建窗口
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("国际象棋")

        # 字体 - 尝试使用支持Unicode chess符号的字体
        self.piece_font = self._load_chess_font(int(self.square_size * 0.7))

        # 加载支持中文的字体
        self.info_font = self._load_chinese_font(32)
        self.small_font = self._load_chinese_font(24)

        # 是否使用Unicode棋子符号
        self.use_unicode = self._test_unicode_support()

        # 选中状态
        self.selected_piece = None  # (row, col)
        self.legal_moves = []

        # AI思考状态
        self.ai_thinking = False

    def _load_chess_font(self, size):
        """
        加载支持国际象棋Unicode字符的字体

        Args:
            size: 字体大小

        Returns:
            pygame.font.Font: 字体对象
        """
        # 尝试加载支持Unicode chess符号的系统字体
        font_names = [
            'Segoe UI Symbol',  # Windows
            'Arial Unicode MS',  # Windows/Mac
            'DejaVu Sans',  # Linux
            'Noto Sans Symbols',  # Linux
            'Apple Symbols',  # Mac
        ]

        for font_name in font_names:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试字体是否支持chess符号
                test_surface = font.render('♔', True, (0, 0, 0))
                if test_surface.get_width() > 0:
                    print(f"使用棋子字体: {font_name}")
                    return font
            except:
                continue

        # 如果都失败，使用默认字体（将使用ASCII显示）
        print("未找到支持Unicode chess符号的字体，将使用ASCII字符显示棋子")
        return pygame.font.Font(None, size)

    def _load_chinese_font(self, size):
        """
        加载支持中文的字体

        Args:
            size: 字体大小

        Returns:
            pygame.font.Font: 字体对象
        """
        # 尝试加载支持中文的系统字体（使用英文和中文名称）
        font_names = [
            'microsoftyahei',       # 微软雅黑 - Windows (小写无空格)
            'Microsoft YaHei',      # 微软雅黑 - Windows
            'simhei',               # 黑体 - Windows
            'SimHei',               # 黑体 - Windows
            'simsun',               # 宋体 - Windows
            'SimSun',               # 宋体 - Windows
            'msgothic',             # MS Gothic - Windows
            'Arial Unicode MS',     # Windows/Mac
            'PingFang SC',          # 苹方 - Mac
            'Noto Sans CJK SC',     # Linux
            'WenQuanYi Micro Hei',  # 文泉驿微米黑 - Linux
        ]

        for font_name in font_names:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试字体是否支持中文
                test_surface = font.render('测', True, (0, 0, 0))
                if test_surface.get_width() > 10:
                    print(f"使用中文字体: {font_name}")
                    return font
            except Exception as e:
                continue

        # 尝试直接加载Windows常见字体文件
        try:
            import os
            windows_font_paths = [
                r'C:\Windows\Fonts\msyh.ttc',      # 微软雅黑
                r'C:\Windows\Fonts\simhei.ttf',    # 黑体
                r'C:\Windows\Fonts\simsun.ttc',    # 宋体
                r'C:\Windows\Fonts\msgothic.ttc',  # MS Gothic
            ]
            for font_path in windows_font_paths:
                if os.path.exists(font_path):
                    try:
                        font = pygame.font.Font(font_path, size)
                        print(f"使用字体文件: {font_path}")
                        return font
                    except:
                        continue
        except:
            pass

        # 如果都失败，使用默认字体（中文可能显示为方框）
        print("警告: 未找到支持中文的字体，界面文字可能显示为方框")
        print("建议: 确保系统已安装微软雅黑或其他中文字体")
        return pygame.font.Font(None, size)

    def _test_unicode_support(self):
        """
        测试当前字体是否支持Unicode chess符号

        Returns:
            bool: 是否支持
        """
        try:
            test_surface = self.piece_font.render('♔', True, (0, 0, 0))
            # 如果渲染的宽度太小，说明不支持
            return test_surface.get_width() > 5
        except:
            return False

    def run(self, ai_player=None):
        """
        运行游戏主循环

        Args:
            ai_player: ChessAI实例，如果不为None则启用AI对手
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    self._handle_mouse_click(event.pos)

            # 如果轮到AI移动
            if (ai_player and
                not self.game_manager.game_over and
                self.game_manager.board.current_turn == ai_player.color and
                not self.ai_thinking):
                self.ai_thinking = True
                self._draw()
                pygame.display.flip()

                # AI计算最佳移动
                best_move = ai_player.get_best_move()
                if best_move:
                    from_pos, to_pos = best_move
                    from_row, from_col = from_pos
                    to_row, to_col = to_pos
                    self.game_manager.make_move(from_row, from_col, to_row, to_col)

                self.ai_thinking = False

            # 绘制界面
            self._draw()

            # 更新显示
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        x, y = pos

        # 转换为棋盘坐标
        col = (x - self.board_offset_x) // self.square_size
        row = (y - self.board_offset_y) // self.square_size

        # 检查是否点击在棋盘内
        if not (0 <= row < 8 and 0 <= col < 8):
            return

        piece = self.game_manager.board.get_piece(row, col)

        # 如果已选中棋子，尝试移动
        if self.selected_piece:
            from_row, from_col = self.selected_piece

            # 如果点击的是合法移动目标
            if (row, col) in self.legal_moves:
                # 检查是否需要兵升变
                moving_piece = self.game_manager.board.get_piece(from_row, from_col)
                promotion_piece = None

                if moving_piece.upper() == 'P':
                    is_white = self.game_manager.board.is_white_piece(moving_piece)
                    promotion_row = 0 if is_white else 7
                    if row == promotion_row:
                        # 显示兵升变选择界面
                        promotion_piece = self._show_promotion_dialog(is_white)

                # 执行移动
                success = self.game_manager.make_move(from_row, from_col, row, col, promotion_piece)

                if success:
                    self.selected_piece = None
                    self.legal_moves = []
            # 如果点击的是己方其他棋子，重新选择
            elif (piece != self.game_manager.board.EMPTY and
                  self.game_manager.board.get_piece_color(piece) == self.game_manager.board.current_turn):
                self.selected_piece = (row, col)
                self.legal_moves = self.game_manager.get_legal_moves_for_piece(row, col)
            else:
                # 取消选择
                self.selected_piece = None
                self.legal_moves = []

        # 如果未选中棋子，选择当前位置的棋子
        elif (piece != self.game_manager.board.EMPTY and
              self.game_manager.board.get_piece_color(piece) == self.game_manager.board.current_turn):
            self.selected_piece = (row, col)
            self.legal_moves = self.game_manager.get_legal_moves_for_piece(row, col)

    def _show_promotion_dialog(self, is_white):
        """
        显示兵升变选择对话框

        Args:
            is_white: 是否为白方

        Returns:
            str: 选择的棋子类型（'Q', 'R', 'B', 'N'）
        """
        pieces = ['Q', 'R', 'B', 'N']
        piece_names = ['后', '车', '象', '马']

        # 绘制对话框背景
        dialog_width = 400
        dialog_height = 150
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, (255, 255, 255),
                        (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, (0, 0, 0),
                        (dialog_x, dialog_y, dialog_width, dialog_height), 3)

        # 显示标题
        title = self.info_font.render("选择升变棋子", True, self.TEXT_COLOR)
        title_rect = title.get_rect(center=(self.width // 2, dialog_y + 30))
        self.screen.blit(title, title_rect)

        # 显示棋子选项
        button_width = 80
        button_height = 60
        button_y = dialog_y + 70
        buttons = []

        for i, (piece, name) in enumerate(zip(pieces, piece_names)):
            button_x = dialog_x + 20 + i * (button_width + 10)
            buttons.append((button_x, button_y, button_width, button_height, piece))

            pygame.draw.rect(self.screen, self.BUTTON_COLOR,
                           (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, (0, 0, 0),
                           (button_x, button_y, button_width, button_height), 2)

            # 显示棋子符号和名称
            if self.use_unicode:
                symbol = self.PIECE_SYMBOLS_UNICODE[piece if is_white else piece.lower()]
                piece_text = self.piece_font.render(symbol, True, (0, 0, 0))
            else:
                # 使用ASCII字母 + 中文名称
                symbol_text = self.PIECE_SYMBOLS_ASCII[piece]
                piece_text = self.small_font.render(f"{symbol_text}-{name}", True, (0, 0, 0))

            piece_rect = piece_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(piece_text, piece_rect)

        pygame.display.flip()

        # 等待用户选择
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for bx, by, bw, bh, piece in buttons:
                        if bx <= x <= bx + bw and by <= y <= by + bh:
                            return piece

    def _draw(self):
        """绘制整个界面"""
        self.screen.fill((220, 220, 220))

        # 绘制棋盘
        self._draw_board()

        # 绘制棋子
        self._draw_pieces()

        # 绘制信息面板
        self._draw_info_panel()

        # 如果游戏结束，显示结果
        if self.game_manager.game_over:
            self._draw_game_over()

        # 如果AI正在思考，显示提示
        if self.ai_thinking:
            self._draw_ai_thinking()

    def _draw_board(self):
        """绘制棋盘"""
        for row in range(8):
            for col in range(8):
                x = self.board_offset_x + col * self.square_size
                y = self.board_offset_y + row * self.square_size

                # 确定方格颜色
                color = self.WHITE if (row + col) % 2 == 0 else self.BLACK

                # 如果是选中的棋子，高亮显示
                if self.selected_piece == (row, col):
                    color = self.HIGHLIGHT

                # 如果是合法移动目标，高亮显示
                if (row, col) in self.legal_moves:
                    color = self.HIGHLIGHT

                # 如果王被将军，红色高亮
                if self.game_manager.is_check():
                    king_pos = (self.game_manager.board.white_king_pos
                               if self.game_manager.board.current_turn == 'white'
                               else self.game_manager.board.black_king_pos)
                    if (row, col) == king_pos:
                        color = self.CHECK_HIGHLIGHT

                pygame.draw.rect(self.screen, color,
                               (x, y, self.square_size, self.square_size))

        # 绘制坐标标记
        for i in range(8):
            # 列标记 (a-h)
            label = self.small_font.render(chr(ord('a') + i), True, self.TEXT_COLOR)
            x = self.board_offset_x + i * self.square_size + self.square_size // 2
            y = self.board_offset_y + self.board_size + 5
            label_rect = label.get_rect(center=(x, y))
            self.screen.blit(label, label_rect)

            # 行标记 (1-8)
            label = self.small_font.render(str(8 - i), True, self.TEXT_COLOR)
            x = self.board_offset_x - 15
            y = self.board_offset_y + i * self.square_size + self.square_size // 2
            label_rect = label.get_rect(center=(x, y))
            self.screen.blit(label, label_rect)

    def _draw_pieces(self):
        """绘制棋子"""
        for row in range(8):
            for col in range(8):
                piece = self.game_manager.board.get_piece(row, col)
                if piece == self.game_manager.board.EMPTY:
                    continue

                x = self.board_offset_x + col * self.square_size + self.square_size // 2
                y = self.board_offset_y + row * self.square_size + self.square_size // 2

                # 根据字体支持选择符号集
                if self.use_unicode:
                    symbol = self.PIECE_SYMBOLS_UNICODE.get(piece, piece)
                else:
                    symbol = self.PIECE_SYMBOLS_ASCII.get(piece, piece)

                # 棋子颜色
                is_white = self.game_manager.board.is_white_piece(piece)
                if self.use_unicode:
                    # Unicode符号用黑白色区分
                    color = (255, 255, 255) if is_white else (0, 0, 0)
                else:
                    # ASCII字符用颜色背景区分
                    color = (255, 200, 100) if is_white else (100, 50, 20)

                # 绘制棋子
                text = self.piece_font.render(symbol, True, color)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

    def _draw_info_panel(self):
        """绘制信息面板"""
        # 当前回合
        turn_text = f"当前回合: {'白方' if self.game_manager.board.current_turn == 'white' else '黑方'}"
        text = self.info_font.render(turn_text, True, self.TEXT_COLOR)
        self.screen.blit(text, (20, 10))

        # 将军状态
        if self.game_manager.is_check():
            check_text = self.info_font.render("将军!", True, (255, 0, 0))
            self.screen.blit(check_text, (self.width - 150, 10))

        # 移动次数
        move_count = len(self.game_manager.board.move_history)
        count_text = self.small_font.render(f"移动次数: {move_count}", True, self.TEXT_COLOR)
        self.screen.blit(count_text, (20, self.height - 30))

    def _draw_game_over(self):
        """绘制游戏结束界面"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 显示结果
        if self.game_manager.game_result == 'checkmate':
            result_text = f"将死! {'白方' if self.game_manager.winner == 'white' else '黑方'}获胜!"
        elif self.game_manager.game_result == 'stalemate':
            result_text = "僵局! 平局!"
        else:
            result_text = "游戏结束"

        text = self.info_font.render(result_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

        # 显示提示
        hint_text = self.small_font.render("关闭窗口退出", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(hint_text, hint_rect)

    def _draw_ai_thinking(self):
        """绘制AI思考提示"""
        text = self.info_font.render("AI思考中...", True, (100, 100, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))

        # 半透明背景
        bg = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
        bg.set_alpha(200)
        bg.fill((255, 255, 255))
        bg_rect = bg.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(bg, bg_rect)

        self.screen.blit(text, text_rect)
