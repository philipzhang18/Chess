"""
Pygame图形界面模块
实现国际象棋的图形化界面
"""
import pygame
import sys
import os
import math


class PygameUI:
    """Pygame图形界面类"""

    # 棋盘配色 - 典雅木质风格
    LIGHT_SQUARE = (240, 217, 181)
    DARK_SQUARE = (181, 136, 99)
    BOARD_BORDER = (101, 67, 33)
    BOARD_BORDER_INNER = (139, 90, 43)

    # 交互高亮色
    SELECTED_COLOR = (246, 246, 105, 180)
    LAST_MOVE_COLOR = (205, 210, 106, 100)
    CHECK_COLOR = (235, 67, 52)

    # 合法走法指示
    MOVE_DOT_COLOR = (0, 0, 0, 60)
    CAPTURE_RING_COLOR = (0, 0, 0, 60)

    # UI配色
    BG_COLOR = (48, 46, 43)
    PANEL_COLOR = (39, 37, 34)
    TEXT_PRIMARY = (220, 220, 220)
    TEXT_SECONDARY = (160, 160, 160)
    TEXT_ACCENT = (129, 182, 76)
    TEXT_WARNING = (235, 97, 80)
    BUTTON_BG = (80, 76, 72)
    BUTTON_HOVER_BG = (100, 96, 92)

    # 棋子Unicode字符
    PIECE_SYMBOLS = {
        'K': '\u2654', 'Q': '\u2655', 'R': '\u2656',
        'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
        'k': '\u265A', 'q': '\u265B', 'r': '\u265C',
        'b': '\u265D', 'n': '\u265E', 'p': '\u265F'
    }

    def __init__(self, game_manager, width=860, height=760):
        """初始化Pygame界面"""
        pygame.init()

        self.game_manager = game_manager
        self.width = width
        self.height = height

        # 棋盘尺寸与布局
        self.square_size = 80
        self.board_size = self.square_size * 8
        self.coord_margin = 24
        self.board_offset_x = (width - self.board_size) // 2
        self.board_offset_y = 68

        # 创建窗口
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("\u265A Chess")

        # 加载字体
        self.piece_font = self._load_chess_font(int(self.square_size * 0.78))
        self.piece_font_small = self._load_chess_font(int(self.square_size * 0.5))
        self.info_font = self._load_chinese_font(26)
        self.small_font = self._load_chinese_font(18)
        self.coord_font = self._load_chinese_font(14)
        self.title_font = self._load_chinese_font(36)

        self.use_unicode = self._test_unicode_support()

        # 状态
        self.selected_piece = None
        self.legal_moves = []
        self.ai_thinking = False
        self.last_move = None  # 记录上一步走法用于高亮
        self.think_anim_frame = 0

        # 预渲染棋盘表面
        self._board_surface = self._create_board_surface()

    def _load_chess_font(self, size):
        """加载棋子字体"""
        font_names = ['Segoe UI Symbol', 'Arial Unicode MS', 'DejaVu Sans',
                       'Noto Sans Symbols', 'Apple Symbols']
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size)
                if font.render('\u2654', True, (0, 0, 0)).get_width() > 0:
                    return font
            except:
                continue
        return pygame.font.Font(None, size)

    def _load_chinese_font(self, size):
        """加载中文字体"""
        font_names = ['microsoftyahei', 'Microsoft YaHei', 'simhei', 'SimHei',
                       'simsun', 'Arial Unicode MS', 'PingFang SC',
                       'Noto Sans CJK SC', 'WenQuanYi Micro Hei']
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size)
                if font.render('\u6d4b', True, (0, 0, 0)).get_width() > 10:
                    return font
            except:
                continue
        # 尝试Windows字体文件
        for path in [r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf']:
            if os.path.exists(path):
                try:
                    return pygame.font.Font(path, size)
                except:
                    continue
        return pygame.font.Font(None, size)

    def _test_unicode_support(self):
        """测试Unicode棋子符号支持"""
        try:
            return self.piece_font.render('\u2654', True, (0, 0, 0)).get_width() > 5
        except:
            return False

    def _create_board_surface(self):
        """预渲染静态棋盘（含坐标标记）"""
        total = self.board_size + self.coord_margin * 2
        surface = pygame.Surface((total, total))
        surface.fill(self.BOARD_BORDER)

        # 内边框
        pygame.draw.rect(surface, self.BOARD_BORDER_INNER,
                         (2, 2, total - 4, total - 4))

        # 棋盘格子
        for row in range(8):
            for col in range(8):
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                x = self.coord_margin + col * self.square_size
                y = self.coord_margin + row * self.square_size
                pygame.draw.rect(surface, color, (x, y, self.square_size, self.square_size))

        # 坐标标记 - 嵌入棋盘格角落
        for i in range(8):
            # 列标记 a-h（底部）
            label = self.coord_font.render(chr(ord('a') + i), True,
                                           self.DARK_SQUARE if i % 2 == 1 else self.LIGHT_SQUARE)
            x = self.coord_margin + i * self.square_size + self.square_size - label.get_width() - 3
            y = self.coord_margin + 7 * self.square_size + self.square_size - label.get_height() - 1
            surface.blit(label, (x, y))

            # 行标记 8-1（左侧）
            label = self.coord_font.render(str(8 - i), True,
                                           self.LIGHT_SQUARE if i % 2 == 1 else self.DARK_SQUARE)
            x = self.coord_margin + 3
            y = self.coord_margin + i * self.square_size + 2
            surface.blit(label, (x, y))

        return surface

    def run(self, ai_player=None):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    if not self.game_manager.game_over:
                        self._handle_mouse_click(event.pos)

            # AI移动
            if (ai_player and
                not self.game_manager.game_over and
                self.game_manager.board.current_turn == ai_player.color and
                not self.ai_thinking):
                self.ai_thinking = True
                self._draw()
                pygame.display.flip()

                best_move = ai_player.get_best_move()
                if best_move:
                    from_pos, to_pos = best_move
                    self.last_move = (from_pos, to_pos)
                    self.game_manager.make_move(from_pos[0], from_pos[1],
                                                to_pos[0], to_pos[1])
                self.ai_thinking = False

            self.think_anim_frame += 1
            self._draw()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        # 计算相对于棋盘的坐标（考虑坐标边距）
        bx = self.board_offset_x - self.coord_margin
        by = self.board_offset_y - self.coord_margin
        rel_x = pos[0] - bx - self.coord_margin
        rel_y = pos[1] - by - self.coord_margin

        col = rel_x // self.square_size
        row = rel_y // self.square_size

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        piece = self.game_manager.board.get_piece(row, col)

        if self.selected_piece:
            from_row, from_col = self.selected_piece

            if (row, col) in self.legal_moves:
                moving_piece = self.game_manager.board.get_piece(from_row, from_col)
                promotion_piece = None

                if moving_piece.upper() == 'P':
                    is_white = self.game_manager.board.is_white_piece(moving_piece)
                    if row == (0 if is_white else 7):
                        promotion_piece = self._show_promotion_dialog(is_white)

                self.last_move = ((from_row, from_col), (row, col))
                success = self.game_manager.make_move(from_row, from_col, row, col, promotion_piece)
                if success:
                    self.selected_piece = None
                    self.legal_moves = []
            elif (piece != self.game_manager.board.EMPTY and
                  self.game_manager.board.get_piece_color(piece) == self.game_manager.board.current_turn):
                self.selected_piece = (row, col)
                self.legal_moves = self.game_manager.get_legal_moves_for_piece(row, col)
            else:
                self.selected_piece = None
                self.legal_moves = []
        elif (piece != self.game_manager.board.EMPTY and
              self.game_manager.board.get_piece_color(piece) == self.game_manager.board.current_turn):
            self.selected_piece = (row, col)
            self.legal_moves = self.game_manager.get_legal_moves_for_piece(row, col)

    def _show_promotion_dialog(self, is_white):
        """显示兵升变选择对话框"""
        pieces = ['Q', 'R', 'B', 'N']
        piece_names = ['\u540e', '\u8f66', '\u8c61', '\u9a6c']

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        dialog_w, dialog_h = 380, 160
        dx = (self.width - dialog_w) // 2
        dy = (self.height - dialog_h) // 2

        # 圆角对话框
        dialog_surf = pygame.Surface((dialog_w, dialog_h), pygame.SRCALPHA)
        pygame.draw.rect(dialog_surf, (50, 48, 45, 240), (0, 0, dialog_w, dialog_h),
                         border_radius=12)
        pygame.draw.rect(dialog_surf, (100, 96, 92), (0, 0, dialog_w, dialog_h),
                         width=2, border_radius=12)
        self.screen.blit(dialog_surf, (dx, dy))

        title = self.info_font.render("\u9009\u62e9\u5347\u53d8\u68cb\u5b50", True, self.TEXT_PRIMARY)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, dy + 32)))

        btn_size = 70
        btn_y = dy + 70
        gap = 12
        total_w = 4 * btn_size + 3 * gap
        start_x = (self.width - total_w) // 2
        buttons = []

        for i, (p, name) in enumerate(zip(pieces, piece_names)):
            bx = start_x + i * (btn_size + gap)
            buttons.append((bx, btn_y, btn_size, btn_size, p))

            pygame.draw.rect(self.screen, self.BUTTON_BG,
                             (bx, btn_y, btn_size, btn_size), border_radius=8)
            pygame.draw.rect(self.screen, (120, 116, 112),
                             (bx, btn_y, btn_size, btn_size), width=1, border_radius=8)

            if self.use_unicode:
                sym = self.PIECE_SYMBOLS[p if is_white else p.lower()]
                color = (255, 255, 255) if is_white else (40, 40, 40)
                txt = self.piece_font_small.render(sym, True, color)
            else:
                txt = self.info_font.render(name, True, self.TEXT_PRIMARY)
            self.screen.blit(txt, txt.get_rect(center=(bx + btn_size // 2, btn_y + btn_size // 2)))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for bx, by, bw, bh, p in buttons:
                        if bx <= x <= bx + bw and by <= y <= by + bh:
                            return p

    def _draw(self):
        """绘制整个界面"""
        self.screen.fill(self.BG_COLOR)

        # 绘制顶部状态栏
        self._draw_status_bar()

        # 绘制棋盘底板（预渲染）
        bx = self.board_offset_x - self.coord_margin
        by = self.board_offset_y - self.coord_margin
        self.screen.blit(self._board_surface, (bx, by))

        # 绘制动态叠加层（高亮、指示器）
        self._draw_highlights()

        # 绘制棋子
        self._draw_pieces()

        # 绘制底部信息栏
        self._draw_bottom_bar()

        # 叠加层
        if self.game_manager.game_over:
            self._draw_game_over()
        elif self.ai_thinking:
            self._draw_ai_thinking()

    def _draw_status_bar(self):
        """绘制顶部状态栏"""
        bar_h = 52
        pygame.draw.rect(self.screen, self.PANEL_COLOR, (0, 0, self.width, bar_h))
        pygame.draw.line(self.screen, (60, 58, 55), (0, bar_h), (self.width, bar_h))

        # 回合指示 - 带棋子颜色圆点
        is_white_turn = self.game_manager.board.current_turn == 'white'
        dot_color = (240, 240, 240) if is_white_turn else (40, 40, 40)
        dot_x, dot_y = 24, bar_h // 2
        pygame.draw.circle(self.screen, dot_color, (dot_x, dot_y), 10)
        pygame.draw.circle(self.screen, (100, 100, 100), (dot_x, dot_y), 10, 1)

        turn_text = "\u767d\u65b9\u8d70\u68cb" if is_white_turn else "\u9ed1\u65b9\u8d70\u68cb"
        txt = self.info_font.render(turn_text, True, self.TEXT_PRIMARY)
        self.screen.blit(txt, (dot_x + 18, (bar_h - txt.get_height()) // 2))

        # 将军警告
        if self.game_manager.is_check():
            check_txt = self.info_font.render("\u2620 \u5c06\u519b!", True, self.TEXT_WARNING)
            self.screen.blit(check_txt, (self.width - check_txt.get_width() - 20,
                                         (bar_h - check_txt.get_height()) // 2))

        # 步数
        move_count = len(self.game_manager.board.move_history)
        round_num = move_count // 2 + 1
        count_txt = self.small_font.render(f"\u7b2c {round_num} \u56de\u5408", True, self.TEXT_SECONDARY)
        cx = self.width // 2 - count_txt.get_width() // 2
        self.screen.blit(count_txt, (cx, (bar_h - count_txt.get_height()) // 2))

    def _draw_highlights(self):
        """绘制棋盘上的动态高亮层"""
        ox = self.board_offset_x
        oy = self.board_offset_y
        sq = self.square_size

        # 上一步走法高亮
        if self.last_move:
            from_pos, to_pos = self.last_move
            for (r, c) in [from_pos, to_pos]:
                surf = pygame.Surface((sq, sq), pygame.SRCALPHA)
                surf.fill(self.LAST_MOVE_COLOR)
                self.screen.blit(surf, (ox + c * sq, oy + r * sq))

        # 选中棋子高亮
        if self.selected_piece:
            r, c = self.selected_piece
            surf = pygame.Surface((sq, sq), pygame.SRCALPHA)
            surf.fill(self.SELECTED_COLOR)
            self.screen.blit(surf, (ox + c * sq, oy + r * sq))

        # 合法走法指示
        for (r, c) in self.legal_moves:
            cx = ox + c * sq + sq // 2
            cy = oy + r * sq + sq // 2
            target = self.game_manager.board.get_piece(r, c)

            indicator = pygame.Surface((sq, sq), pygame.SRCALPHA)
            if target != self.game_manager.board.EMPTY:
                # 吃子 - 角落三角标记
                tri_size = sq // 4
                corners = [
                    [(0, 0), (tri_size, 0), (0, tri_size)],
                    [(sq, 0), (sq - tri_size, 0), (sq, tri_size)],
                    [(0, sq), (tri_size, sq), (0, sq - tri_size)],
                    [(sq, sq), (sq - tri_size, sq), (sq, sq - tri_size)],
                ]
                for tri in corners:
                    pygame.draw.polygon(indicator, (0, 0, 0, 50), tri)
            else:
                # 空格 - 中心小圆点
                pygame.draw.circle(indicator, self.MOVE_DOT_COLOR,
                                   (sq // 2, sq // 2), sq // 7)
            self.screen.blit(indicator, (ox + c * sq, oy + r * sq))

        # 将军时王的位置红色高亮
        if self.game_manager.is_check():
            board = self.game_manager.board
            king_pos = (board.white_king_pos if board.current_turn == 'white'
                        else board.black_king_pos)
            r, c = king_pos
            # 径向渐变红色
            surf = pygame.Surface((sq, sq), pygame.SRCALPHA)
            center = sq // 2
            for radius in range(sq // 2, 0, -1):
                alpha = int(100 * (1 - radius / (sq // 2)))
                pygame.draw.circle(surf, (self.CHECK_COLOR[0], self.CHECK_COLOR[1],
                                          self.CHECK_COLOR[2], alpha),
                                   (center, center), radius)
            self.screen.blit(surf, (ox + c * sq, oy + r * sq))

    def _draw_pieces(self):
        """绘制棋子（带描边增强辨识度）"""
        ox = self.board_offset_x
        oy = self.board_offset_y
        sq = self.square_size

        for row in range(8):
            for col in range(8):
                piece = self.game_manager.board.get_piece(row, col)
                if piece == self.game_manager.board.EMPTY:
                    continue

                cx = ox + col * sq + sq // 2
                cy = oy + row * sq + sq // 2

                if not self.use_unicode:
                    # ASCII回退
                    is_w = self.game_manager.board.is_white_piece(piece)
                    color = (255, 220, 160) if is_w else (80, 40, 10)
                    txt = self.piece_font.render(piece.upper(), True, color)
                    self.screen.blit(txt, txt.get_rect(center=(cx, cy)))
                    continue

                symbol = self.PIECE_SYMBOLS.get(piece, piece)
                is_white = self.game_manager.board.is_white_piece(piece)

                # 描边效果：先绘制偏移的深色文字作为阴影
                outline_color = (40, 40, 40) if is_white else (200, 200, 200)
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                    outline = self.piece_font.render(symbol, True, outline_color)
                    self.screen.blit(outline, outline.get_rect(center=(cx + dx, cy + dy)))

                # 主体颜色
                main_color = (255, 255, 255) if is_white else (30, 30, 30)
                main = self.piece_font.render(symbol, True, main_color)
                self.screen.blit(main, main.get_rect(center=(cx, cy)))

    def _draw_bottom_bar(self):
        """绘制底部信息栏（被吃棋子展示）"""
        bar_y = self.board_offset_y + self.board_size + self.coord_margin + 8
        bar_h = self.height - bar_y
        pygame.draw.rect(self.screen, self.PANEL_COLOR, (0, bar_y, self.width, bar_h))
        pygame.draw.line(self.screen, (60, 58, 55), (0, bar_y), (self.width, bar_y))

        captured = self.game_manager.board.captured_pieces
        if not captured:
            hint = self.small_font.render(
                "\u9f20\u6807\u70b9\u51fb\u68cb\u5b50\u79fb\u52a8 | "
                "\u9ad8\u4eae\u5706\u70b9\u4e3a\u53ef\u8d70\u4f4d\u7f6e",
                True, self.TEXT_SECONDARY)
            self.screen.blit(hint, (20, bar_y + (bar_h - hint.get_height()) // 2))
            return

        # 分组展示被吃棋子
        white_captured = sorted([p for p in captured if self.game_manager.board.is_white_piece(p)],
                                key=lambda p: -{'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 99}.get(p.upper(), 0))
        black_captured = sorted([p for p in captured if self.game_manager.board.is_black_piece(p)],
                                key=lambda p: -{'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 99}.get(p.upper(), 0))

        x_start = 20
        cy = bar_y + bar_h // 2

        # 黑方吃的白子
        if white_captured:
            label = self.small_font.render("\u9ed1\u65b9\u5403:", True, self.TEXT_SECONDARY)
            self.screen.blit(label, (x_start, cy - label.get_height() // 2))
            px = x_start + label.get_width() + 4
            for p in white_captured:
                if self.use_unicode:
                    sym = self.PIECE_SYMBOLS.get(p, p)
                    txt = self.piece_font_small.render(sym, True, (200, 200, 200))
                else:
                    txt = self.small_font.render(p, True, (200, 200, 200))
                self.screen.blit(txt, (px, cy - txt.get_height() // 2))
                px += txt.get_width() + 2

        # 白方吃的黑子
        if black_captured:
            rx = self.width // 2 + 20
            label = self.small_font.render("\u767d\u65b9\u5403:", True, self.TEXT_SECONDARY)
            self.screen.blit(label, (rx, cy - label.get_height() // 2))
            px = rx + label.get_width() + 4
            for p in black_captured:
                if self.use_unicode:
                    sym = self.PIECE_SYMBOLS.get(p, p)
                    txt = self.piece_font_small.render(sym, True, (60, 60, 60))
                else:
                    txt = self.small_font.render(p.upper(), True, (60, 60, 60))
                self.screen.blit(txt, (px, cy - txt.get_height() // 2))
                px += txt.get_width() + 2

    def _draw_game_over(self):
        """绘制游戏结束覆盖层"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        cy = self.height // 2

        # 结果文字
        if self.game_manager.game_result == 'checkmate':
            winner = '\u767d\u65b9' if self.game_manager.winner == 'white' else '\u9ed1\u65b9'
            main_text = f"\u5c06\u6b7b! {winner}\u83b7\u80dc!"
            main_color = self.TEXT_ACCENT
        elif self.game_manager.game_result == 'stalemate':
            main_text = "\u50f5\u5c40 - \u5e73\u5c40!"
            main_color = self.TEXT_SECONDARY
        else:
            main_text = "\u6e38\u620f\u7ed3\u675f"
            main_color = self.TEXT_PRIMARY

        # 背景卡片
        card_w, card_h = 400, 140
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (50, 48, 45, 230), (0, 0, card_w, card_h),
                         border_radius=16)
        pygame.draw.rect(card_surf, (100, 96, 92), (0, 0, card_w, card_h),
                         width=2, border_radius=16)
        self.screen.blit(card_surf, ((self.width - card_w) // 2, cy - card_h // 2))

        txt = self.title_font.render(main_text, True, main_color)
        self.screen.blit(txt, txt.get_rect(center=(self.width // 2, cy - 15)))

        hint = self.small_font.render(
            "\u5173\u95ed\u7a97\u53e3\u9000\u51fa", True, self.TEXT_SECONDARY)
        self.screen.blit(hint, hint.get_rect(center=(self.width // 2, cy + 35)))

    def _draw_ai_thinking(self):
        """绘制AI思考动画"""
        cy = self.height // 2

        # 半透明遮罩
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.screen.blit(overlay, (0, 0))

        # 动画卡片
        card_w, card_h = 260, 70
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (50, 48, 45, 220), (0, 0, card_w, card_h),
                         border_radius=12)
        pygame.draw.rect(card_surf, (80, 180, 100, 180), (0, 0, card_w, card_h),
                         width=2, border_radius=12)
        self.screen.blit(card_surf, ((self.width - card_w) // 2, cy - card_h // 2))

        # 跳动的点动画
        base_text = "AI \u601d\u8003\u4e2d"
        dots_count = (self.think_anim_frame // 10) % 4
        text = base_text + "." * dots_count

        txt = self.info_font.render(text, True, self.TEXT_ACCENT)
        self.screen.blit(txt, txt.get_rect(center=(self.width // 2, cy)))
