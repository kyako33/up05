import tkinter as tk
import json
import time

class BackButton:
    def __init__(self, parent, command=None, dark_theme=False):
        self.parent = parent
        self.command = command
        self.dark_theme = dark_theme
        self.canvas = tk.Canvas(parent, width=80, height=40, highlightthickness=0, cursor='hand2')
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Enter>", lambda e: self.draw(True))
        self.canvas.bind("<Leave>", lambda e: self.draw(False))
        self.draw()
    
    def update_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.draw()
        # Принудительно обновляем canvas
        self.canvas.update_idletasks()
    
    def draw(self, hover=False):
        self.canvas.delete("all")
        if self.dark_theme:
            bg_color = '#19233D'
            arrow_color = '#D9D9D9'
            frame_color = '#0D1938'
        else:
            bg_color = '#677DB4'
            arrow_color = '#677DB4'
            frame_color = '#D9D9D9'
        
        self.canvas.configure(bg=bg_color)
        fill_color = frame_color
        
        self._rounded_rect(0, 0, 80, 40, 20, frame_color, frame_color)
        self._rounded_rect(2, 2, 78, 38, 18, fill_color, fill_color)
        self.canvas.create_line(30, 20, 60, 20, fill=arrow_color, width=3)
        self.canvas.create_polygon(30, 14, 20, 20, 30, 26, fill=arrow_color, outline=arrow_color)
    
    def _rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        self.canvas.create_arc(x1, y1, x1+r*2, y2, start=90, extent=180, fill=fill, outline=outline, width=0)
        self.canvas.create_arc(x2-r*2, y1, x2, y2, start=270, extent=180, fill=fill, outline=outline, width=0)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=outline, width=0)
    
    def click(self, event):
        if self.command: self.command()
    def place(self, **kwargs): self.canvas.place(**kwargs)
    def pack(self, **kwargs): self.canvas.pack(**kwargs)


class ToggleSwitch:
    def __init__(self, parent, initial_state=False, command=None, dark_theme=False):
        self.state = initial_state
        self.command = command
        self.dark_theme = dark_theme
        self.canvas = tk.Canvas(parent, width=80, height=40, highlightthickness=0, cursor='hand2')
        self.canvas.bind("<Button-1>", self.toggle)
        self.draw()
    
    def update_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.draw()
        # Принудительно обновляем canvas
        self.canvas.update_idletasks()
    
    def draw(self):
        self.canvas.delete("all")
        if self.dark_theme:
            bg_color = '#19233D'
            outline_color = '#0D1938'
            frame_color = '#D9D9D9'
        else:
            bg_color = '#677DB4'
            outline_color = '#677DB4'
            frame_color = '#D9D9D9'
        
        self.canvas.configure(bg=bg_color)
        fill_color = bg_color if self.state else '#CCCCCC'
        
        self._rounded_rect(0, 0, 80, 40, 20, frame_color, frame_color)
        self._rounded_rect(2, 2, 78, 38, 18, fill_color, fill_color)
        
        knob_radius = 17
        if self.state:
            self.canvas.create_oval(80 - knob_radius*2 - 2, 4, 80 - 4, 40 - 4,
                                   fill='#D9D9D9', outline=outline_color, width=1)
        else:
            self.canvas.create_oval(4, 4, knob_radius*2 + 2, 40 - 4,
                                   fill='#D9D9D9', outline=outline_color, width=1)
    
    def _rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        self.canvas.create_arc(x1, y1, x1+r*2, y2, start=90, extent=180, fill=fill, outline=outline, width=0)
        self.canvas.create_arc(x2-r*2, y1, x2, y2, start=270, extent=180, fill=fill, outline=outline, width=0)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=outline, width=0)
    
    def toggle(self, event=None):
        self.state = not self.state
        self.draw()
        if self.command: 
            self.command(self.state)


class ResultPanel:
    def __init__(self, parent, is_success, level, on_catalog, on_retry=None, dark_theme=False):
        self.parent = parent
        self.is_success = is_success
        self.level = level
        self.on_catalog = on_catalog
        self.on_retry = on_retry
        self.dark_theme = dark_theme
        self.bg_color = '#19233D' if dark_theme else '#677DB4'
        self.pixel_canvases = []
        
        self.overlay = tk.Frame(parent, bg=self.bg_color)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.panel = tk.Frame(self.overlay, bg=self.bg_color)
        self.panel.place(relx=0.5, rely=0.5, anchor='center', width=650, height=620)
        
        (self.show_success if is_success else self.show_error)()
    
    def update_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.bg_color = '#19233D' if dark_theme else '#677DB4'
        self.overlay.configure(bg=self.bg_color)
        self.panel.configure(bg=self.bg_color)
        for widget in self.panel.winfo_children():
            if isinstance(widget, (tk.Frame, tk.Label, tk.Canvas)):
                widget.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Button):
                self._style_button(widget)
        if self.is_success and self.pixel_canvases:
            self._update_pixel_colors()
    
    def _style_button(self, btn):
        if btn.winfo_exists():
            if self.dark_theme:
                btn.configure(bg='#0D1938', activebackground='#122145')
            else:
                btn.configure(bg='#425B99', activebackground='#5A75BA')
    
    def _update_pixel_colors(self):
        solution = self.level.get("solution", [])
        filled = '#D9D9D9'
        empty = '#14142B' if self.dark_theme else '#425B99'
        for r, row in enumerate(self.pixel_canvases):
            for c, pixel in enumerate(row):
                if pixel.winfo_exists():
                    color = filled if solution and r < len(solution) and c < len(solution[r]) and solution[r][c] == 1 else empty
                    pixel.configure(bg=color)
    
    def _make_button(self, parent, text, cmd):
        frame = tk.Frame(parent, bg='#D9D9D9')
        frame.pack(pady=8)
        btn = tk.Button(frame, text=text, font=('Courier', 18, 'bold'), fg='#D9D9D9',
                       width=22, height=2, relief='flat', cursor='hand2', command=cmd)
        btn.pack(padx=2, pady=2)
        self._style_button(btn)
        btn.bind("<Enter>", lambda e: btn.configure(bg='#122145' if self.dark_theme else '#5A75BA'))
        btn.bind("<Leave>", lambda e: self._style_button(btn))
        return btn
    
    def show_success(self):
        level = self.level
        for text, fg in [("ПОЗДРАВЛЯЕМ!", '#4CAF50'), (f"Вы собрали: {level.get('image_name', 'Картинка')}!", "#D5EDED"), 
                         (f"{level.get('name', '')} пройден!", '#D9D9D9')]:
            tk.Label(self.panel, text=text, font=('Courier', 38 if 'ПОЗДРАВЛЯЕМ' in text else (28 if 'Вы собрали' in text else 22), 'bold'),
                    bg=self.bg_color, fg=fg).pack(pady=(25, 15) if 'ПОЗДРАВЛЯЕМ' in text else (10, 15))
        
        solution = level.get("solution", [])
        size = level.get("size", {})
        rows, cols = size.get("rows", 5), size.get("cols", 5)
        
        if solution and rows > 0:
            frame = tk.Frame(self.panel, bg=self.bg_color)
            frame.pack(pady=20)
            pixel_size = 45 if rows <= 8 else (35 if rows <= 12 else 28)
            filled = '#D9D9D9'
            empty = '#14142B' if self.dark_theme else '#425B99'
            
            for r in range(min(rows, len(solution))):
                row_canvases = []
                for c in range(min(cols, len(solution[r]))):
                    color = filled if solution[r][c] == 1 else empty
                    pixel = tk.Canvas(frame, width=pixel_size, height=pixel_size, bg=color, highlightthickness=0, bd=0)
                    pixel.grid(row=r, column=c)
                    row_canvases.append(pixel)
                self.pixel_canvases.append(row_canvases)
        
        self._make_button(self.panel, "К КАТАЛОГУ УРОВНЕЙ", self.close_and_go_to_catalog)
    
    def show_error(self):
        for text, fg in [("ОШИБКА!", '#f44336'), ("Поле заполнено неверно!", '#f44336'), ("Попробуйте ещё раз", '#D9D9D9')]:
            tk.Label(self.panel, text=text, font=('Courier', 38 if 'ОШИБКА' in text else (26 if 'Поле' in text else 20), 'bold'),
                    bg=self.bg_color, fg=fg).pack(pady=(35, 15) if 'ОШИБКА' in text else (15, 15))
        frame = tk.Frame(self.panel, bg=self.bg_color)
        frame.pack(pady=35)
        self._make_button(frame, "ВЕРНУТЬСЯ К УРОВНЮ", self.close_and_retry)
        self._make_button(frame, "К КАТАЛОГУ УРОВНЕЙ", self.close_and_go_to_catalog)
    
    def close_and_go_to_catalog(self):
        self.overlay.destroy()
        if self.on_catalog: self.on_catalog()
    
    def close_and_retry(self):
        self.overlay.destroy()
        if self.on_retry: self.on_retry()


class NonogramGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nonogramm")
        self.root.geometry("1200x800")
        self.root.eval('tk::PlaceWindow . center')
        
        self.dark_theme = False
        self.show_hints = True
        self.in_game = False
        self.current_level = None
        self.levels = []
        self.completed_levels = []
        self.level_states = {}
        
        self.start_time = None
        self.timer_running = False
        self.timer_id = None
        self.saved_time = 0
        self.auto_save_timer = None
        
        self.main_frame = tk.Frame(self.root, bg='#677DB4')
        self.main_frame.pack(expand=True, fill='both')
        self.current_screen = None
        self.menu_buttons = []
        self.toggle_switches = []
        self.settings_back_button = None
        self.hints_switch = None
        self.theme_switch = None
        self.reset_progress_button = None
        self.check_button = None
        self.result_panel = None
        self.message_label = None
        self.message_after_id = None
        self.level_previews = []
        self.guide_shown_for_level = False
        self.guide_frame = None
        self.guide_click_count = 0
        self.guide_hide_after_id = None
        
        self.load_levels()
        self.load_progress()
        self.load_settings()
        
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_game)
        
        self.show_main_menu()
    
    def load_levels(self):
        try:
            with open('levels.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.levels = data.get('levels', [])
            for lvl in self.levels:
                lvl.setdefault('image_name', f"Уровень {lvl.get('id', 1)}")
                lvl.setdefault('solution', [])
                lvl.setdefault('row_hints', [])
                lvl.setdefault('col_hints', [])
                lvl.setdefault('size', {"rows": 5, "cols": 5})
        except:
            self.levels = []
    
    def load_progress(self):
        try:
            with open('progress.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.completed_levels = data.get('completed_levels', [])
                self.level_states = data.get('level_states', {})
                self.guide_shown_for_level = data.get('guide_shown_for_level', False)
        except:
            self.completed_levels, self.level_states, self.guide_shown_for_level = [], {}, False
    
    def save_progress(self):
        try:
            with open('progress.json', 'w', encoding='utf-8') as f:
                json.dump({'completed_levels': self.completed_levels, 'level_states': self.level_states,
                          'guide_shown_for_level': self.guide_shown_for_level,
                          'settings': {'dark_theme': self.dark_theme, 'show_hints': self.show_hints}}, f, indent=2)
        except:
            pass
    
    def load_settings(self):
        try:
            with open('progress.json', 'r', encoding='utf-8') as f:
                s = json.load(f).get('settings', {})
                self.dark_theme = s.get('dark_theme', False)
                self.show_hints = s.get('show_hints', True)
        except:
            self.dark_theme, self.show_hints = False, True
    
    def save_settings(self): 
        self.save_progress()
    
    def reset_progress(self):
        self.completed_levels = []
        self.level_states = {}
        self.guide_shown_for_level = False
        self.save_progress()
        self.show_catalog()
        self._show_msg("Прогресс успешно сброшен!", True)
    
    def _get_message_color(self, is_success):
        if self.dark_theme:
            return "#1E2658" if is_success else "#C62828"
        else:
            return "#718DC1" if is_success else "#f44336"
    
    def _show_msg(self, text, is_success):
        if self.message_label and self.message_label.winfo_exists():
            self.message_label.destroy()
        if self.message_after_id:
            self.root.after_cancel(self.message_after_id)
        
        msg_bg = self._get_message_color(is_success)
        
        self.message_label = tk.Label(self.current_screen, text=text, font=('Courier', 16, 'bold'),
                                      bg=msg_bg, fg='#FFFFFF', padx=20, pady=10, relief='raised', bd=2)
        self.message_label.place(relx=0.5, rely=0.15, anchor='center')
        self.message_is_success = is_success
        self.message_after_id = self.root.after(2000, lambda: self.message_label.destroy() if self.message_label else None)
    
    def show_guide(self):
        if self.guide_frame: 
            return
        bg = '#14142d' if self.dark_theme else '#425B99'
        self.guide_frame = tk.Frame(self.current_screen, bg=bg, bd=1, highlightthickness=1,
                                    highlightbackground='#5a6a8a' if self.dark_theme else '#8ab3d9')
        self.guide_frame.place(relx=0.75, rely=0.5, anchor='center', width=350, height=240)
        tk.Label(self.guide_frame, text="Подсказка!", font=('Courier', 16, 'bold'), bg=bg, fg='#D5EDED').pack(pady=(12, 8))
        for text, desc in [("Левая кнопка мыши", "→ закрасить клетку"), ("Правая кнопка мыши", "→ снять закраску")]:
            f = tk.Frame(self.guide_frame, bg=bg)
            f.pack(pady=8, padx=10)
            tk.Label(f, text="🖱️", font=('Arial', 20), bg=bg).pack(side='left', padx=5)
            tk.Label(f, text=text, font=('Courier', 11, 'bold'), bg=bg, fg='#D9D9D9').pack(side='left')
            tk.Label(self.guide_frame, text=desc, font=('Courier', 11), bg=bg, fg='#D5EDED').pack(pady=(0, 5))
            if text == "Левая кнопка мыши":
                tk.Frame(self.guide_frame, bg='#5a6a8a', height=1).pack(fill='x', padx=20, pady=6)
        self.guide_hide_after_id = self.root.after(15000, lambda: self.guide_frame.destroy() if self.guide_frame else None)
    
    def hide_guide(self):
        if self.guide_frame: 
            self.guide_frame.destroy()
        self.guide_frame = None
        if self.guide_hide_after_id:
            self.root.after_cancel(self.guide_hide_after_id)
            self.guide_hide_after_id = None
    
    def on_cell_click(self):
        if self.guide_frame:
            self.guide_click_count += 1
            if self.guide_click_count >= 2:
                self.hide_guide()
                self.guide_shown_for_level = True
                self.save_progress()
    
    def save_current_level_state(self):
        if self.in_game and self.current_level and hasattr(self, 'cells'):
            if self.timer_running and self.start_time:
                self.saved_time += int(time.time() - self.start_time)
                self.start_time = time.time()
            self.level_states[str(self.current_level.get('id'))] = {'cells': [row[:] for row in self.cells], 'time': self.saved_time}
            self.save_progress()
    
    def auto_save(self):
        if self.in_game: 
            self.save_current_level_state()
        self.auto_save_timer = self.root.after(5000, self.auto_save)
    
    def toggle_fullscreen(self, e=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
    
    def clear_screen(self):
        self.in_game = False
        if self.timer_id: 
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.hide_guide()
        self.guide_click_count = 0
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None
    
    def exit_game(self, e=None):
        self.save_current_level_state()
        self.save_progress()
        self.root.quit()
        self.root.destroy()
    
    def _get_bg(self): 
        return '#19233D' if self.dark_theme else '#677DB4'
    
    def _get_fg(self): 
        return '#D9D9D9'
    
    def update_all_widgets_theme(self):
        if not self.current_screen:
            return
        
        bg = self._get_bg()
        fg = self._get_fg()
        
        # Обновляем корневые элементы
        self.root.configure(bg=bg)
        self.main_frame.configure(bg=bg)
        self.current_screen.configure(bg=bg)
        
        # Обновляем все виджеты на экране
        def update_widget(w):
            if isinstance(w, (tk.Frame, tk.Canvas)):
                w.configure(bg=bg)
            elif isinstance(w, tk.Label):
                current_fg = w.cget('fg')
                if current_fg not in ['#4CAF50', '#f44336', '#FFFFFF', '#DCE7EA', '#D5EDED']:
                    w.configure(bg=bg, fg=fg)
                else:
                    w.configure(bg=bg)
            elif isinstance(w, tk.Button):
                self._style_button(w)
            for child in w.winfo_children():
                update_widget(child)
        
        update_widget(self.current_screen)
        
        # Обновляем кнопки главного меню
        for btn in self.menu_buttons:
            if btn['frame'].winfo_exists():
                btn['frame'].configure(bg='#D9D9D9')
            if btn['button'].winfo_exists():
                self._style_button(btn['button'])
        
        # Обновляем переключатели - ПЕРВЫЙ ПРИОРИТЕТ
        for sw in self.toggle_switches:
            if sw:
                sw.update_theme(self.dark_theme)
                # Принудительно обновляем canvas переключателя
                sw.canvas.update_idletasks()
        
        # Обновляем кнопку "назад" в настройках - ВТОРОЙ ПРИОРИТЕТ
        if self.settings_back_button:
            self.settings_back_button.update_theme(self.dark_theme)
            self.settings_back_button.canvas.update_idletasks()
        
        # Обновляем остальные кнопки
        if self.reset_progress_button and self.reset_progress_button.winfo_exists():
            self._style_button(self.reset_progress_button)
        
        if self.check_button and self.check_button.winfo_exists():
            self._style_button(self.check_button)
        
        # Обновляем панель результатов
        if self.result_panel:
            self.result_panel.update_theme(self.dark_theme)
        
        # Обновляем всплывающее сообщение
        if self.message_label and self.message_label.winfo_exists():
            if hasattr(self, 'message_is_success'):
                new_bg = self._get_message_color(self.message_is_success)
                self.message_label.configure(bg=new_bg)
        
        # Обновляем превью уровней
        for canvas, level in self.level_previews:
            if canvas.winfo_exists():
                self.draw_level_preview(canvas, level, canvas.winfo_width(), canvas.winfo_height())
        
        # Обновляем игровое поле
        if self.in_game and self.current_level:
            self.create_game_board_for_current_level()
        
        # Финальное принудительное обновление
        self.root.update_idletasks()
    
    def _style_button(self, btn):
        if btn.winfo_exists():
            if self.dark_theme:
                btn.configure(bg='#0D1938', activebackground='#122145', fg='#D9D9D9')
            else:
                btn.configure(bg='#425B99', activebackground='#5A75BA', fg='#D9D9D9')
    
    def show_main_menu(self):
        self.clear_screen()
        bg = self._get_bg()
        fg = self._get_fg()
        self.current_screen = tk.Frame(self.main_frame, bg=bg)
        self.current_screen.pack(expand=True, fill='both')
        
        self.root.configure(bg=bg)
        self.main_frame.configure(bg=bg)
        
        tk.Label(self.current_screen, text="Nonogramm", font=('Courier', 67, 'bold'),
                bg=bg, fg=fg).pack(pady=(100, 80))
        
        for text, cmd in [("Старт", self.show_catalog), ("Настройки", self.show_settings), ("Выход", self.exit_game)]:
            frame = tk.Frame(self.current_screen, bg='#D9D9D9')
            frame.pack(pady=10)
            btn = tk.Button(frame, text=text, font=('Courier', 30, 'bold'), fg='#D9D9D9',
                           width=15, height=2, relief='flat', bd=0, cursor='hand2')
            btn.pack(padx=2, pady=2)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            self._style_button(btn)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#122145' if self.dark_theme else '#5A75BA'))
            btn.bind("<Leave>", lambda e, b=btn: self._style_button(b))
            self.menu_buttons.append({'button': btn, 'frame': frame})
    
    def show_settings(self):
        self.clear_screen()
        bg = self._get_bg()
        fg = self._get_fg()
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg)
        self.current_screen.pack(expand=True, fill='both')
        
        # Создаем кнопку "назад" с текущей темой
        self.settings_back_button = BackButton(self.current_screen, self.show_main_menu, self.dark_theme)
        self.settings_back_button.place(x=30, y=30)
        
        tk.Label(self.current_screen, text="Настройки", font=('Courier', 56, 'bold'),
                bg=bg, fg=fg).pack(pady=(100, 100))
        
        container = tk.Frame(self.current_screen, bg=bg)
        container.pack(fill='x', padx=200)
        
        # Очищаем список переключателей перед созданием новых
        self.toggle_switches = []
        
        for text, state, cmd in [("Подсказки", self.show_hints, self.on_hints_toggle), 
                                  ("Тема", self.dark_theme, self.on_theme_toggle)]:
            frame = tk.Frame(container, bg=bg)
            frame.pack(fill='x', pady=15)
            tk.Label(frame, text=text, font=('Courier', 32, 'bold'),
                    bg=bg, fg=fg).pack(side='left', padx=20, pady=10)
            sw = ToggleSwitch(frame, state, cmd, self.dark_theme)
            sw.canvas.pack(side='right', padx=10)
            self.toggle_switches.append(sw)
            if text == "Тема":
                self.theme_switch = sw
            else:
                self.hints_switch = sw
        
        # Принудительно обновляем экран
        self.root.update_idletasks()
    
    def on_hints_toggle(self, state):
        self.show_hints = state
        self.save_settings()
        if self.in_game:
            self.update_hint_warnings()
    
    def on_theme_toggle(self, state):
        self.dark_theme = state
        self.save_settings()
        self.update_all_widgets_theme()
    
    def check_row_has_errors(self, row, solution):
        for col in range(self.cols):
            if self.cells[row][col] == 1:
                expected = solution[row][col] if row < len(solution) and col < len(solution[row]) else 0
                if expected == 0:
                    return True
        return False
    
    def check_col_has_errors(self, col, solution):
        for row in range(self.rows):
            if self.cells[row][col] == 1:
                expected = solution[row][col] if row < len(solution) and col < len(solution[row]) else 0
                if expected == 0:
                    return True
        return False
    
    def update_hint_warnings(self):
        if not hasattr(self, 'game_canvas') or not self.game_canvas.winfo_exists():
            return
        
        self.game_canvas.delete("hint_warning")
        
        if not self.show_hints:
            return
        
        solution = self.current_level.get("solution", [])
        if not solution:
            return
        
        for row in range(self.rows):
            if self.check_row_has_errors(row, solution):
                x_pos = 15
                y_pos = row * self.cell_size + self.max_col_hints * (self.cell_size // 2) + self.cell_size // 2 + 20
                self.game_canvas.create_text(
                    x_pos, y_pos,
                    text="✘", font=('Arial', self.cell_size // 2, 'bold'),
                    fill='#f44336', tags="hint_warning"
                )
        
        for col in range(self.cols):
            if self.check_col_has_errors(col, solution):
                x_pos = col * self.cell_size + self.max_row_hints * (self.cell_size // 2) + self.cell_size // 2 + 20
                y_pos = 15
                self.game_canvas.create_text(
                    x_pos, y_pos,
                    text="✘", font=('Arial', self.cell_size // 2, 'bold'),
                    fill='#f44336', tags="hint_warning"
                )
    
    def create_game_board_for_current_level(self):
        if hasattr(self, 'game_container') and self.game_container.winfo_exists():
            self.game_container.configure(bg=self._get_bg())
            if hasattr(self, 'game_canvas') and self.game_canvas.winfo_exists():
                self.game_canvas.configure(bg=self._get_bg())
            if hasattr(self, 'current_level'):
                self.calculate_cell_size()
                self.create_game_board()
    
    def draw_level_preview(self, canvas, level, w, h):
        if self.dark_theme:
            filled_color = '#D9D9D9'
            empty_color = '#14142d'
            locked_color = "#14142d"
        else:
            filled_color = '#D9D9D9'
            empty_color = '#425B99'
            locked_color = '#425B99'
        
        if level.get('id') in self.completed_levels:
            solution = level.get("solution", [])
            size = level.get("size", {})
            rows = size.get("rows", 5)
            cols = size.get("cols", 5)
            
            if solution and rows > 0 and cols > 0:
                cell_w = w / cols
                cell_h = h / rows
                
                for r in range(min(rows, len(solution))):
                    for c in range(min(cols, len(solution[r]) if solution else 0)):
                        if solution[r][c] == 1:
                            color = filled_color
                        else:
                            color = empty_color
                        canvas.create_rectangle(c * cell_w, r * cell_h,
                                               (c + 1) * cell_w, (r + 1) * cell_h,
                                               fill=color, outline='', width=0)
                return
        canvas.create_rectangle(0, 0, w, h, fill=locked_color, outline='', width=0)
    
    def show_catalog(self):
        self.clear_screen()
        self.level_previews = []
        bg = self._get_bg()
        fg = self._get_fg()
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg)
        self.current_screen.pack(expand=True, fill='both')
        
        top_panel = tk.Frame(self.current_screen, bg=bg)
        top_panel.pack(fill='x', padx=30, pady=(30, 0))
        
        back_btn = BackButton(top_panel, self.show_main_menu, self.dark_theme)
        back_btn.pack(side='left')
        
        reset_frame = tk.Frame(top_panel, bg='#D9D9D9', bd=0)
        reset_frame.pack(side='right')
        self.reset_progress_button = tk.Button(reset_frame, text="СБРОСИТЬ ПРОГРЕСС", font=('Courier', 14, 'bold'),
                              fg='#D9D9D9', width=18, height=1, relief='flat', bd=0, cursor='hand2',
                              command=self.reset_progress)
        self.reset_progress_button.pack(padx=3, pady=3)
        self._style_button(self.reset_progress_button)
        
        tk.Label(self.current_screen, text="Каталог уровней", font=('Courier', 48, 'bold'),
                bg=bg, fg=fg).pack(pady=(20, 60))
        
        levels_container = tk.Frame(self.current_screen, bg=bg)
        levels_container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(levels_container, bg=bg, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(levels_container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', expand=True, fill='both')
        
        levels_frame = tk.Frame(canvas, bg=bg)
        canvas.create_window((0, 0), window=levels_frame, anchor='nw')
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        levels_frame.bind('<Configure>', on_frame_configure)
        
        def on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        canvas.bind('<MouseWheel>', on_mousewheel)
        
        cols = 3
        cell_width = 200
        padx_val = 150
        pady_val = 70
        
        for i, level in enumerate(self.levels):
            row, col = i // cols, i % cols
            level_id = level.get('id')
            image_name = level.get('image_name', '')
            is_completed = level_id in self.completed_levels
            
            frame = tk.Frame(levels_frame, bg=bg, cursor='arrow' if is_completed else 'hand2')
            frame.grid(row=row, column=col, padx=padx_val, pady=pady_val, sticky='nsew')
            
            if not is_completed:
                frame.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            preview = tk.Canvas(frame, width=cell_width, height=cell_width, highlightthickness=0, bd=0, bg=bg)
            preview.pack(pady=(0, 8))
            if not is_completed:
                preview.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            self.level_previews.append((preview, level))
            self.draw_level_preview(preview, level, cell_width, cell_width)
            
            name = tk.Label(frame, text=level.get("name", f"Уровень {level_id}"),
                           font=('Courier', 16, 'bold'), bg=bg, fg=fg,
                           cursor='arrow' if is_completed else 'hand2')
            name.pack(pady=(4, 2))
            if not is_completed:
                name.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            if is_completed and image_name:
                tk.Label(frame, text=image_name, font=('Courier', 16, 'bold'),
                        bg=bg, fg="#DCE7EA", cursor='arrow').pack(pady=(2, 2))
            else:
                q = tk.Label(frame, text="? ? ?", font=('Courier', 20, 'bold'),
                            bg=bg, fg=fg, cursor='hand2')
                q.pack(pady=(2, 0))
                q.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
        
        for i in range(cols):
            levels_frame.grid_columnconfigure(i, weight=1)
        levels_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
    
    def start_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()
    
    def stop_timer(self):
        if self.timer_running and self.start_time:
            self.saved_time += int(time.time() - self.start_time)
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
    
    def update_timer(self):
        if self.timer_running and hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            elapsed = self.saved_time + int(time.time() - self.start_time)
            minutes, seconds = elapsed // 60, elapsed % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def retry_level(self):
        if self.current_level:
            self.show_game(self.current_level)
    
    def check_solution(self):
        if not self.current_level:
            return
        solution = self.current_level.get("solution", [])
        
        correct = True
        for row in range(self.rows):
            for col in range(self.cols):
                expected = solution[row][col] if solution and row < len(solution) and col < len(solution[row]) else 0
                if (self.cells[row][col] == 1) != (expected == 1):
                    correct = False
                    break
            if not correct:
                break
        
        level_id = self.current_level.get('id')
        if correct:
            if level_id not in self.completed_levels:
                self.completed_levels.append(level_id)
                if str(level_id) in self.level_states:
                    del self.level_states[str(level_id)]
                self.save_progress()
            self.stop_timer()
            self.result_panel = ResultPanel(self.current_screen, True, self.current_level, self.show_catalog, None, self.dark_theme)
        else:
            self.result_panel = ResultPanel(self.current_screen, False, self.current_level, self.show_catalog, self.retry_level, self.dark_theme)
    
    def back_to_catalog(self):
        self.save_current_level_state()
        self.stop_timer()
        self.show_catalog()
    
    def calculate_cell_size(self):
        self.max_row_hints = max([len(hints) for hints in self.row_hints]) if self.row_hints else 0
        self.max_col_hints = max([len(hints) for hints in self.col_hints]) if self.col_hints else 0
        
        hints_width = self.max_row_hints * 25
        hints_height = self.max_col_hints * 25
        
        available_width = self.game_container.winfo_width() - hints_width - 80
        available_height = self.game_container.winfo_height() - hints_height - 80
        
        max_cell_by_width = available_width // max(self.cols, 1)
        max_cell_by_height = available_height // max(self.rows, 1)
        
        if self.rows >= 15 or self.cols >= 15:
            max_size = 30
        elif self.rows >= 10 or self.cols >= 10:
            max_size = 35
        elif self.rows >= 8 or self.cols >= 8:
            max_size = 40
        else:
            max_size = 50
        
        self.cell_size = max(20, min(max_cell_by_width, max_cell_by_height, max_size))
        
        return self.max_row_hints, self.max_col_hints
    
    def get_cell_colors(self):
        if self.dark_theme:
            return {'empty': "#14142B", 'filled': '#D9D9D9', 'outline': '#5a6a8a'}
        else:
            return {'empty': '#425B99', 'filled': '#D9D9D9', 'outline': '#8ab3d9'}
    
    def show_game(self, level):
        if level.get('id') in self.completed_levels:
            return
        
        self.clear_screen()
        self.in_game = True
        self.current_level = level
        self.result_panel = None
        self.guide_click_count = 0
        
        bg = self._get_bg()
        fg = self._get_fg()
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg)
        self.current_screen.pack(expand=True, fill='both')
        
        BackButton(self.current_screen, self.back_to_catalog, self.dark_theme).place(x=30, y=30)
        
        self.title_label = tk.Label(self.current_screen, text=level.get('name', 'Уровень'),
                                    font=('Courier', 32, 'bold'), bg=bg, fg=fg)
        self.title_label.pack(pady=(60, 30))
        
        self.timer_label = tk.Label(self.current_screen, text="00:00",
                                    font=('Courier', 24, 'bold'), bg=bg, fg=fg)
        self.timer_label.place(relx=0.95, y=30, anchor='ne')
        
        size = level.get("size", {})
        self.rows = size.get("rows", 5)
        self.cols = size.get("cols", 5)
        
        self.row_hints = level.get("row_hints", [])
        self.col_hints = level.get("col_hints", [])
        
        if not self.row_hints:
            self.row_hints = [[] for _ in range(self.rows)]
        if not self.col_hints:
            self.col_hints = [[] for _ in range(self.cols)]
        
        self.cells = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        level_id = level.get('id')
        saved_state = self.level_states.get(str(level_id), {})
        self.saved_time = saved_state.get('time', 0)
        saved_cells = saved_state.get('cells', [])
        for r in range(min(len(saved_cells), self.rows)):
            for c in range(min(len(saved_cells[r]), self.cols)):
                self.cells[r][c] = saved_cells[r][c]
        
        self.game_container = tk.Frame(self.current_screen, bg=bg)
        self.game_container.pack(expand=True, fill='both')
        
        check_btn_frame = tk.Frame(self.current_screen, bg='#D9D9D9', bd=0)
        check_btn_frame.pack(side='bottom', anchor='se', padx=40, pady=30)
        self.check_button = tk.Button(check_btn_frame, text="ПРОВЕРИТЬ", font=('Courier', 20, 'bold'),
                                   fg='#D9D9D9', width=15, height=2,
                                   relief='flat', bd=0, cursor='hand2', command=self.check_solution)
        self.check_button.pack(padx=3, pady=3)
        self._style_button(self.check_button)
        
        self.game_container.update_idletasks()
        self.calculate_cell_size()
        self.create_game_board()
        
        if level_id == 1 and not self.guide_shown_for_level:
            self.root.after(500, self.show_guide)
        
        if self.saved_time > 0:
            self.timer_running = True
            self.start_time = time.time()
            self.update_timer()
        else:
            self.start_timer()
        
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.auto_save_timer = self.root.after(5000, self.auto_save)
    
    def create_game_board(self):
        if hasattr(self, 'game_canvas'):
            self.game_canvas.destroy()
        
        colors = self.get_cell_colors()
        bg = self._get_bg()
        
        hint_cell_w = self.cell_size // 2
        hint_cell_h = self.cell_size // 2
        
        game_width = self.cols * self.cell_size + self.max_row_hints * hint_cell_w + 60
        game_height = self.rows * self.cell_size + self.max_col_hints * hint_cell_h + 60
        
        self.game_canvas = tk.Canvas(self.game_container, width=game_width, height=game_height,
                                     bg=bg, highlightthickness=0)
        self.game_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        hint_font = max(8, min(14, self.cell_size // 4))
        
        for col in range(self.cols):
            hints = self.col_hints[col] if col < len(self.col_hints) else []
            y_offset = self.max_col_hints * hint_cell_h
            for hint in reversed(hints):
                self.game_canvas.create_text(
                    col * self.cell_size + self.cell_size // 2 + self.max_row_hints * hint_cell_w + 20,
                    y_offset - hint_cell_h // 2 + 8,
                    text=str(hint), font=('Courier', hint_font, 'bold'), fill='#D9D9D9'
                )
                y_offset -= hint_cell_h
        
        for row in range(self.rows):
            hints = self.row_hints[row] if row < len(self.row_hints) else []
            x_offset = self.max_row_hints * hint_cell_w
            for hint in reversed(hints):
                self.game_canvas.create_text(
                    x_offset - hint_cell_w // 2 + 8,
                    row * self.cell_size + self.cell_size // 2 + self.max_col_hints * hint_cell_h + 20,
                    text=str(hint), font=('Courier', hint_font, 'bold'), fill='#D9D9D9'
                )
                x_offset -= hint_cell_w
        
        self.cell_rects = []
        for row in range(self.rows):
            row_rects = []
            for col in range(self.cols):
                x1 = col * self.cell_size + self.max_row_hints * hint_cell_w + 20
                y1 = row * self.cell_size + self.max_col_hints * hint_cell_h + 20
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                val = self.cells[row][col]
                fill = colors['filled'] if val == 1 else colors['empty']
                
                rect = self.game_canvas.create_rectangle(x1, y1, x2, y2, fill=fill,
                                                         outline=colors['outline'], width=1,
                                                         tags=f"cell_{row}_{col}")
                row_rects.append(rect)
                
                self.game_canvas.tag_bind(f"cell_{row}_{col}", "<Button-1>",
                                         lambda e, r=row, c=col: self.cell_left_click(r, c))
                self.game_canvas.tag_bind(f"cell_{row}_{col}", "<Button-3>",
                                         lambda e, r=row, c=col: self.cell_right_click(r, c))
            self.cell_rects.append(row_rects)
        
        if self.show_hints:
            self.update_hint_warnings()
    
    def cell_left_click(self, row, col):
        colors = self.get_cell_colors()
        if self.cells[row][col] == 0:
            self.cells[row][col] = 1
            self.game_canvas.itemconfig(self.cell_rects[row][col], fill=colors['filled'])
        self.on_cell_click()
        if self.show_hints:
            self.update_hint_warnings()
    
    def cell_right_click(self, row, col):
        colors = self.get_cell_colors()
        if self.cells[row][col] == 1:
            self.cells[row][col] = 0
            self.game_canvas.itemconfig(self.cell_rects[row][col], fill=colors['empty'])
        self.on_cell_click()
        if self.show_hints:
            self.update_hint_warnings()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = NonogramGame()
    game.run()