import tkinter as tk
import json
import os
import time

class BackButton:
    def __init__(self, parent, command=None, dark_theme=False):
        self.parent = parent
        self.command = command
        self.dark_theme = dark_theme
        
        self.canvas = tk.Canvas(
            parent,
            width=80,
            height=40,
            highlightthickness=0,
            cursor='hand2'
        )
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Enter>", self.on_hover)
        self.canvas.bind("<Leave>", self.on_leave)
        self.draw()
    
    def update_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.draw()
    
    def draw(self, hover=False):
        self.canvas.delete("all")
        width, height = 80, 40
        radius = 20
        
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
        
        self._create_rounded_rect(self.canvas, 0, 0, width, height, radius, frame_color, frame_color, 0)
        self._create_rounded_rect(self.canvas, 2, 2, width-2, height-2, radius-2, fill_color, fill_color, 0)
        self.canvas.create_line(30, 20, 60, 20, fill=arrow_color, width=3)
        self.canvas.create_polygon(30, 14, 20, 20, 30, 26, fill=arrow_color, outline=arrow_color)
    
    def _create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, fill_color, outline_color, outline_width):
        height = y2 - y1
        if radius > height // 2:
            radius = height // 2
        canvas.create_arc(x1, y1, x1 + radius*2, y2, start=90, extent=180,
                         fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_arc(x2 - radius*2, y1, x2, y2, start=270, extent=180,
                         fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                               fill=fill_color, outline=outline_color, width=outline_width)
    
    def on_hover(self, event):
        self.draw(hover=True)
    
    def on_leave(self, event):
        self.draw(hover=False)
    
    def click(self, event):
        if self.command:
            self.command()
    
    def place(self, **kwargs):
        self.canvas.place(**kwargs)
    
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)


class ToggleSwitch:
    def __init__(self, parent, initial_state=False, command=None, dark_theme=False):
        self.parent = parent
        self.state = initial_state
        self.command = command
        self.dark_theme = dark_theme
        self.canvas = tk.Canvas(parent, width=80, height=40, highlightthickness=0, cursor='hand2')
        self.canvas.bind("<Button-1>", self.toggle)
        self.draw()
    
    def update_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        width, height = 80, 40
        radius = 20
        
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
        
        self._create_rounded_rect(self.canvas, 0, 0, width, height, radius, frame_color, frame_color, 0)
        self._create_rounded_rect(self.canvas, 2, 2, width-2, height-2, radius-2, fill_color, fill_color, 0)
        
        knob_radius = 17
        if self.state:
            self.canvas.create_oval(width - knob_radius*2 - 2, 4, width - 4, height - 4,
                                   fill='#D9D9D9', outline=outline_color, width=1)
        else:
            self.canvas.create_oval(4, 4, knob_radius*2 + 2, height - 4,
                                   fill='#D9D9D9', outline=outline_color, width=1)
    
    def _create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, fill_color, outline_color, outline_width):
        height = y2 - y1
        if radius > height // 2:
            radius = height // 2
        canvas.create_arc(x1, y1, x1 + radius*2, y2, start=90, extent=180,
                         fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_arc(x2 - radius*2, y1, x2, y2, start=270, extent=180,
                         fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                               fill=fill_color, outline=outline_color, width=outline_width)
    
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
        
        self.bg_color = '#19233D' if self.dark_theme else '#677DB4'
        
        self.overlay = tk.Frame(parent, bg=self.bg_color)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.panel = tk.Frame(self.overlay, bg=self.bg_color)
        self.panel.place(relx=0.5, rely=0.5, anchor='center', width=650, height=620)
        
        self.panel.lift()
        
        if is_success:
            self.show_success()
        else:
            self.show_error()
    
    def update_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.bg_color = '#19233D' if self.dark_theme else '#677DB4'
        
        self.overlay.configure(bg=self.bg_color)
        self.panel.configure(bg=self.bg_color)
        
        for widget in self.panel.winfo_children():
            if isinstance(widget, tk.Label):
                current_fg = widget.cget('fg')
                if current_fg not in ['#4CAF50', '#FFD93D', '#f44336']:
                    widget.configure(bg=self.bg_color)
                else:
                    widget.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.bg_color)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        self.update_button_theme(child)
                    elif isinstance(child, tk.Label):
                        child.configure(bg=self.bg_color)
                    elif isinstance(child, tk.Canvas):
                        child.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Button):
                self.update_button_theme(widget)
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=self.bg_color)
    
    def update_button_theme(self, button):
        if button.winfo_exists():
            if self.dark_theme:
                button.configure(bg='#0D1938', activebackground='#122145')
            else:
                button.configure(bg='#425B99', activebackground='#5A75BA')
    
    def create_styled_button(self, parent, text, command):
        if self.dark_theme:
            bg = '#0D1938'
            active = '#122145'
            frame_bg = '#D9D9D9'
        else:
            bg = '#425B99'
            active = '#5A75BA'
            frame_bg = '#D9D9D9'
        
        frame = tk.Frame(parent, bg=frame_bg, bd=0, relief='flat')
        frame.pack(pady=8)
        
        btn = tk.Button(frame, text=text, font=('Courier', 18, 'bold'),
                       bg=bg, fg='#D9D9D9', activebackground=active, activeforeground='#D9D9D9',
                       width=22, height=2, relief='flat', bd=0, cursor='hand2',
                       command=command)
        btn.pack(padx=2, pady=2)
        
        def on_enter(e):
            btn.configure(bg=active)
        
        def on_leave(e):
            btn.configure(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def show_success(self):
        image_name = self.level.get('image_name', 'Картинка')
        
        tk.Label(self.panel, text="ПОЗДРАВЛЯЕМ!", font=('Courier', 38, 'bold'),
                bg=self.bg_color, fg='#4CAF50').pack(pady=(25, 15))
        tk.Label(self.panel, text=f"Вы собрали: {image_name}!", font=('Courier', 28, 'bold'),
                bg=self.bg_color, fg="#D5EDED").pack(pady=(10, 15))
        tk.Label(self.panel, text=f"{self.level.get('name', '')} пройден!",
                font=('Courier', 22, 'bold'), bg=self.bg_color, fg='#D9D9D9').pack(pady=15)
        
        solution = self.level.get("solution", [])
        size = self.level.get("size", {})
        rows = size.get("rows", 5)
        cols = size.get("cols", 5)
        
        if solution and rows > 0 and cols > 0:
            art_frame = tk.Frame(self.panel, bg=self.bg_color)
            art_frame.pack(pady=20)
            
            if rows <= 8:
                pixel_size = 45
            elif rows <= 12:
                pixel_size = 35
            else:
                pixel_size = 28
            
            fill_color = '#D9D9D9'
            
            for r in range(min(rows, len(solution))):
                for c in range(min(cols, len(solution[r]) if solution else 0)):
                    if solution[r][c] == 1:
                        color = fill_color
                    else:
                        color = '#425B99'
                    
                    pixel = tk.Canvas(art_frame, width=pixel_size, height=pixel_size,
                                     bg=color, highlightthickness=0, bd=0)
                    pixel.grid(row=r, column=c, padx=0, pady=0)
        
        button_frame = tk.Frame(self.panel, bg=self.bg_color)
        button_frame.pack(pady=25)
        
        self.create_styled_button(button_frame, "К КАТАЛОГУ УРОВНЕЙ", self.close_and_go_to_catalog)
    
    def show_error(self):
        tk.Label(self.panel, text="ОШИБКА!", font=('Courier', 38, 'bold'),
                bg=self.bg_color, fg='#f44336').pack(pady=(35, 15))
        tk.Label(self.panel, text="Поле заполнено неверно!", font=('Courier', 26, 'bold'),
                bg=self.bg_color, fg='#f44336').pack(pady=15)
        tk.Label(self.panel, text="Попробуйте ещё раз", font=('Courier', 20, 'bold'),
                bg=self.bg_color, fg='#D9D9D9').pack(pady=15)
        
        button_frame = tk.Frame(self.panel, bg=self.bg_color)
        button_frame.pack(pady=35)
        
        self.create_styled_button(button_frame, "ВЕРНУТЬСЯ К УРОВНЮ", self.close_and_retry)
        self.create_styled_button(button_frame, "К КАТАЛОГУ УРОВНЕЙ", self.close_and_go_to_catalog)
    
    def close_and_go_to_catalog(self):
        self.overlay.destroy()
        if self.on_catalog:
            self.on_catalog()
    
    def close_and_retry(self):
        self.overlay.destroy()
        if self.on_retry:
            self.on_retry()


class NonogramGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nonogramm")
        self.root.configure(bg='#677DB4')
        self.root.geometry("1200x800")
        self.root.eval('tk::PlaceWindow . center')
        
        self.fullscreen = False
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
        self.load_settings()  # Загружаем настройки
        
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_game)
        
        self.show_main_menu()
    
    def load_levels(self):
        try:
            with open('levels.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.levels = data.get('levels', [])
                for level in self.levels:
                    if 'image_name' not in level:
                        level['image_name'] = f"Уровень {level.get('id', 1)}"
                    if 'solution' not in level:
                        level['solution'] = []
                    if 'row_hints' not in level:
                        level['row_hints'] = []
                    if 'col_hints' not in level:
                        level['col_hints'] = []
                    if 'size' not in level:
                        level['size'] = {"rows": 5, "cols": 5}
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
            self.completed_levels = []
            self.level_states = {}
            self.guide_shown_for_level = False
    
    def save_progress(self):
        try:
            with open('progress.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'completed_levels': self.completed_levels,
                    'level_states': self.level_states,
                    'guide_shown_for_level': self.guide_shown_for_level,
                    'settings': {
                        'dark_theme': self.dark_theme,
                        'show_hints': self.show_hints
                    }
                }, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_settings(self):
        try:
            with open('progress.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                settings = data.get('settings', {})
                self.dark_theme = settings.get('dark_theme', False)
                self.show_hints = settings.get('show_hints', True)
        except:
            self.dark_theme = False
            self.show_hints = True
    
    def save_settings(self):
        try:
            with open('progress.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
        
        data['settings'] = {
            'dark_theme': self.dark_theme,
            'show_hints': self.show_hints
        }
        
        try:
            with open('progress.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def reset_progress(self):
        self.completed_levels = []
        self.level_states = {}
        self.guide_shown_for_level = False
        self.save_progress()
        self.show_catalog()
        self.show_catalog_message("Прогресс успешно сброшен!", is_success=True)
    
    def show_catalog_message(self, text, is_success=True):
        if self.message_label and self.message_label.winfo_exists():
            self.message_label.destroy()
        if self.message_after_id:
            self.root.after_cancel(self.message_after_id)
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        msg_color = "#BDDDED" if is_success else "#da635b"
        
        self.message_label = tk.Label(
            self.current_screen,
            text=text,
            font=('Courier', 16, 'bold'),
            bg=msg_color,
            fg='#FFFFFF',
            padx=20,
            pady=10,
            relief='raised',
            bd=2
        )
        self.message_label.place(relx=0.5, rely=0.15, anchor='center')
        
        self.message_after_id = self.root.after(2000, self.hide_catalog_message)
    
    def hide_catalog_message(self):
        if self.message_label and self.message_label.winfo_exists():
            self.message_label.destroy()
        self.message_label = None
        self.message_after_id = None
    
    def show_guide(self):
        if self.guide_frame:
            return
        
        if self.dark_theme:
            bg_color = '#14142d'
            border_color = '#5a6a8a'
        else:
            bg_color = '#425B99'
            border_color = '#8ab3d9'
        
        self.guide_frame = tk.Frame(self.current_screen, bg=bg_color, bd=1, relief='flat', highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
        self.guide_frame.place(relx=0.75, rely=0.5, anchor='center', width=350, height=240)
        
        tk.Label(self.guide_frame, text="Подсказка!", font=('Courier', 16, 'bold'),
                bg=bg_color, fg='#D5EDED').pack(pady=(12, 8))
        
        frame1 = tk.Frame(self.guide_frame, bg=bg_color)
        frame1.pack(pady=8, padx=10)
        tk.Label(frame1, text="🖱️", font=('Arial', 20), bg=bg_color).pack(side='left', padx=5)
        tk.Label(frame1, text="Левая кнопка мыши", font=('Courier', 11, 'bold'),
                bg=bg_color, fg='#D9D9D9').pack(side='left')
        
        tk.Label(self.guide_frame, text="→ закрасить клетку", font=('Courier', 11),
                bg=bg_color, fg='#D5EDED').pack(pady=(0, 5))
        
        tk.Frame(self.guide_frame, bg='#5a6a8a', height=1).pack(fill='x', padx=20, pady=6)
        
        frame2 = tk.Frame(self.guide_frame, bg=bg_color)
        frame2.pack(pady=8, padx=10)
        tk.Label(frame2, text="🖱️", font=('Arial', 20), bg=bg_color).pack(side='left', padx=5)
        tk.Label(frame2, text="Правая кнопка мыши", font=('Courier', 11, 'bold'),
                bg=bg_color, fg='#D9D9D9').pack(side='left')
        
        tk.Label(self.guide_frame, text="→ снять закраску", font=('Courier', 11),
                bg=bg_color, fg='#D5EDED').pack(pady=(0, 5))
        
        self.guide_hide_after_id = self.root.after(15000, self.hide_guide)
    
    def hide_guide(self):
        if self.guide_frame and self.guide_frame.winfo_exists():
            self.guide_frame.destroy()
        self.guide_frame = None
        if self.guide_hide_after_id:
            self.root.after_cancel(self.guide_hide_after_id)
            self.guide_hide_after_id = None
    
    def on_cell_click(self):
        if self.guide_frame and self.guide_frame.winfo_exists():
            self.guide_click_count += 1
            if self.guide_click_count >= 2:
                self.hide_guide()
                self.guide_shown_for_level = True
                self.save_progress()
    
    def save_current_level_state(self):
        if not self.in_game or not self.current_level:
            return
        level_id = self.current_level.get('id')
        if level_id is None:
            return
        if hasattr(self, 'cells'):
            if self.timer_running and self.start_time:
                self.saved_time += int(time.time() - self.start_time)
                self.start_time = time.time()
            self.level_states[str(level_id)] = {
                'cells': [row[:] for row in self.cells],
                'time': self.saved_time
            }
            self.save_progress()
    
    def auto_save(self):
        if self.in_game:
            self.save_current_level_state()
        self.auto_save_timer = self.root.after(5000, self.auto_save)
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
    
    def clear_screen(self):
        self.in_game = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.hide_catalog_message()
        self.hide_guide()
        self.guide_click_count = 0
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None
    
    def exit_game(self, event=None):
        self.save_current_level_state()
        self.save_settings()  # Сохраняем настройки перед выходом
        self.root.quit()
        self.root.destroy()
    
    def update_main_menu_theme(self):
        if not self.menu_buttons:
            return
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        fg_color = '#D9D9D9'
        button_bg = '#0D1938' if self.dark_theme else '#425B99'
        button_active = '#122145' if self.dark_theme else '#5A75BA'
        frame_bg = '#D9D9D9'
        
        for button_info in self.menu_buttons:
            button = button_info['button']
            frame = button_info['frame']
            if frame.winfo_exists():
                frame.configure(bg=frame_bg)
            if button.winfo_exists():
                button.configure(bg=button_bg, fg=fg_color, activebackground=button_active, activeforeground=fg_color)
                button.unbind("<Enter>")
                button.unbind("<Leave>")
                button.bind("<Enter>", lambda e, btn=button: btn.configure(bg=button_active))
                button.bind("<Leave>", lambda e, btn=button: btn.configure(bg=button_bg))
    
    def update_all_widgets_theme(self):
        if not self.current_screen:
            return
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        fg_color = '#D9D9D9'
        
        self.root.configure(bg=bg_color)
        self.main_frame.configure(bg=bg_color)
        self.current_screen.configure(bg=bg_color)
        
        def update_widget(widget):
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)
            elif isinstance(widget, tk.Label):
                current_fg = widget.cget('fg')
                if current_fg not in ['#4CAF50', '#FFD93D', '#f44336', '#FFFFFF', '#DCE7EA', '#D5EDED']:
                    widget.configure(bg=bg_color, fg=fg_color)
                else:
                    widget.configure(bg=bg_color)
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=bg_color)
            elif isinstance(widget, tk.Button):
                self.update_button_theme(widget)
            for child in widget.winfo_children():
                update_widget(child)
        
        update_widget(self.current_screen)
        self.update_main_menu_theme()
        
        for switch in self.toggle_switches:
            if switch and hasattr(switch, 'update_theme'):
                switch.update_theme(self.dark_theme)
        
        if self.settings_back_button:
            self.settings_back_button.update_theme(self.dark_theme)
        
        if self.reset_progress_button and self.reset_progress_button.winfo_exists():
            self.update_button_theme(self.reset_progress_button)
        
        if self.check_button and self.check_button.winfo_exists():
            self.update_button_theme(self.check_button)
        
        if self.result_panel:
            self.result_panel.update_theme(self.dark_theme)
        
        if self.message_label and self.message_label.winfo_exists():
            self.message_label.configure(bg='#BDDDED' if 'успешно' in self.message_label.cget('text') else '#da635b')
        
        if self.guide_frame and self.guide_frame.winfo_exists():
            if self.dark_theme:
                guide_bg = "#14142d"
                guide_border = '#5a6a8a'
            else:
                guide_bg = '#425B99'
                guide_border = '#8ab3d9'
            
            self.guide_frame.configure(bg=guide_bg, highlightbackground=guide_border)
            
            for widget in self.guide_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=guide_bg)
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(bg=guide_bg)
                elif isinstance(widget, tk.Label):
                    if widget.cget('fg') == '#FFD93D':
                        widget.configure(bg=guide_bg)
                    else:
                        widget.configure(bg=guide_bg, fg=fg_color)
        
        for preview_info in self.level_previews:
            canvas, level = preview_info
            if canvas.winfo_exists():
                self.draw_level_preview(canvas, level, canvas.winfo_width(), canvas.winfo_height())
        
        if self.in_game and self.current_level:
            self.create_game_board_for_current_level()
    
    def update_button_theme(self, button):
        if button.winfo_exists():
            if self.dark_theme:
                button.configure(bg='#0D1938', activebackground='#122145')
            else:
                button.configure(bg='#425B99', activebackground='#5A75BA')
    
    def show_main_menu(self, event=None):
        self.clear_screen()
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        fg_color = '#D9D9D9'
        button_bg = '#0D1938' if self.dark_theme else '#425B99'
        button_active = "#122145" if self.dark_theme else '#5A75BA'
        frame_bg = '#D9D9D9'
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg_color)
        self.current_screen.pack(expand=True, fill='both')
        
        self.root.configure(bg=bg_color)
        self.main_frame.configure(bg=bg_color)
        
        tk.Label(self.current_screen, text="Nonogramm", font=('Courier', 67, 'bold'),
                bg=bg_color, fg=fg_color).pack(pady=(100, 80))
        
        def create_button(text, command):
            frame = tk.Frame(self.current_screen, bg=frame_bg, bd=0, relief='flat')
            frame.pack(pady=10)
            btn = tk.Button(frame, text=text, font=('Courier', 30, 'bold'),
                           bg=button_bg, fg=fg_color, width=15, height=2,
                           relief='flat', bd=0, cursor='hand2')
            btn.pack(padx=2, pady=2)
            btn.bind("<Button-1>", command)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=button_active))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=button_bg))
            self.menu_buttons.append({'button': btn, 'frame': frame})
            return btn
        
        create_button("Старт", self.show_catalog)
        create_button("Настройки", self.show_settings)
        create_button("Выход", self.exit_game)
    
    def show_settings(self, event=None):
        self.clear_screen()
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        fg_color = '#D9D9D9'
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg_color)
        self.current_screen.pack(expand=True, fill='both')
        
        self.settings_back_button = BackButton(self.current_screen, command=self.show_main_menu, dark_theme=self.dark_theme)
        self.settings_back_button.place(x=30, y=30)
        
        tk.Label(self.current_screen, text="Настройки", font=('Courier', 56, 'bold'),
                bg=bg_color, fg=fg_color).pack(pady=(100, 100))
        
        menu_container = tk.Frame(self.current_screen, bg=bg_color)
        menu_container.pack(fill='x', padx=200)
        
        hints_frame = tk.Frame(menu_container, bg=bg_color)
        hints_frame.pack(fill='x', pady=15)
        tk.Label(hints_frame, text="Подсказки", font=('Courier', 32, 'bold'),
                bg=bg_color, fg=fg_color).pack(side='left', padx=20, pady=10)
        
        self.hints_switch = ToggleSwitch(hints_frame, initial_state=self.show_hints,
                                          command=self.on_hints_toggle, dark_theme=self.dark_theme)
        self.hints_switch.canvas.pack(side='right', padx=10)
        self.toggle_switches.append(self.hints_switch)
        
        theme_frame = tk.Frame(menu_container, bg=bg_color)
        theme_frame.pack(fill='x', pady=15)
        tk.Label(theme_frame, text="Тема", font=('Courier', 32, 'bold'),
                bg=bg_color, fg=fg_color).pack(side='left', padx=20, pady=10)
        
        self.theme_switch = ToggleSwitch(theme_frame, initial_state=self.dark_theme,
                                          command=self.on_theme_toggle, dark_theme=self.dark_theme)
        self.theme_switch.canvas.pack(side='right', padx=10)
        self.toggle_switches.append(self.theme_switch)
    
    def on_hints_toggle(self, state):
        self.show_hints = state
        self.save_settings()  # Сохраняем настройку
        if self.in_game and self.current_level:
            self.update_hint_warnings()
    
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
    
    def on_theme_toggle(self, state):
        self.dark_theme = state
        self.save_settings()  # Сохраняем настройку
        self.update_all_widgets_theme()
    
    def create_game_board_for_current_level(self):
        if hasattr(self, 'game_container') and self.game_container.winfo_exists():
            bg_color = '#19233D' if self.dark_theme else '#677DB4'
            self.game_container.configure(bg=bg_color)
            if hasattr(self, 'game_canvas') and self.game_canvas.winfo_exists():
                self.game_canvas.configure(bg=bg_color)
            if hasattr(self, 'current_level'):
                max_row_hints, max_col_hints = self.calculate_cell_size()
                self.create_game_board(max_row_hints, max_col_hints)
    
    def draw_level_preview(self, canvas, level, width, height):
        level_id = level.get('id')
        
        if self.dark_theme:
            filled_color = '#D9D9D9'
            empty_color = '#14142d'
            locked_color = "#14142d"
        else:
            filled_color = '#425B99'
            empty_color = '#8ab3d9'
            locked_color = '#425B99'
        
        if level_id in self.completed_levels:
            solution = level.get("solution", [])
            size = level.get("size", {})
            rows = size.get("rows", 5)
            cols = size.get("cols", 5)
            
            if solution and rows > 0 and cols > 0:
                cell_w = width / cols
                cell_h = height / rows
                
                for row in range(min(rows, len(solution))):
                    for col in range(min(cols, len(solution[row]) if solution else 0)):
                        if solution[row][col] == 1:
                            color = filled_color
                        else:
                            color = empty_color
                        canvas.create_rectangle(col * cell_w, row * cell_h,
                                               (col + 1) * cell_w, (row + 1) * cell_h,
                                               fill=color, outline='', width=0)
            else:
                canvas.create_rectangle(0, 0, width, height, fill=locked_color, outline='', width=0)
        else:
            canvas.create_rectangle(0, 0, width, height, fill=locked_color, outline='', width=0)
    
    def show_catalog(self, event=None):
        self.clear_screen()
        self.level_previews = []
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        fg_color = '#D9D9D9'
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg_color)
        self.current_screen.pack(expand=True, fill='both')
        
        top_panel = tk.Frame(self.current_screen, bg=bg_color)
        top_panel.pack(fill='x', padx=30, pady=(30, 0))
        
        self.back_button = BackButton(top_panel, command=self.show_main_menu, dark_theme=self.dark_theme)
        self.back_button.pack(side='left')
        
        reset_frame = tk.Frame(top_panel, bg='#D9D9D9', bd=0)
        reset_frame.pack(side='right')
        self.reset_progress_button = tk.Button(reset_frame, text="СБРОСИТЬ ПРОГРЕСС", font=('Courier', 14, 'bold'),
                              bg='#0D1938' if self.dark_theme else '#425B99', 
                              fg='#D9D9D9', activebackground='#122145' if self.dark_theme else '#5A75BA',
                              width=18, height=1, relief='flat', bd=0, cursor='hand2',
                              command=self.reset_progress)
        self.reset_progress_button.pack(padx=3, pady=3)
        self.reset_progress_button.bind("<Enter>", lambda e: self.reset_progress_button.configure(
            bg="#122145" if self.dark_theme else "#5A75BA"))
        self.reset_progress_button.bind("<Leave>", lambda e: self.reset_progress_button.configure(
            bg='#0D1938' if self.dark_theme else '#425B99'))
        
        tk.Label(self.current_screen, text="Каталог уровней", font=('Courier', 48, 'bold'),
                bg=bg_color, fg=fg_color).pack(pady=(20, 60))
        
        levels_container = tk.Frame(self.current_screen, bg=bg_color)
        levels_container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(levels_container, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(levels_container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', expand=True, fill='both')
        
        levels_frame = tk.Frame(canvas, bg=bg_color)
        canvas_window = canvas.create_window((0, 0), window=levels_frame, anchor='nw')
        
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
            
            frame = tk.Frame(levels_frame, bg=bg_color, cursor='arrow' if is_completed else 'hand2')
            frame.grid(row=row, column=col, padx=padx_val, pady=pady_val, sticky='nsew')
            
            if not is_completed:
                frame.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            preview = tk.Canvas(frame, width=cell_width, height=cell_width, highlightthickness=0,
                                cursor='arrow' if is_completed else 'hand2', bg=bg_color)
            preview.pack(pady=(0, 8))
            if not is_completed:
                preview.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            self.level_previews.append((preview, level))
            self.draw_level_preview(preview, level, cell_width, cell_width)
            
            name = tk.Label(frame, text=level.get("name", f"Уровень {level_id}"),
                           font=('Courier', 16, 'bold'), bg=bg_color, fg=fg_color,
                           cursor='arrow' if is_completed else 'hand2')
            name.pack(pady=(4, 2))
            if not is_completed:
                name.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            if is_completed and image_name:
                tk.Label(frame, text=image_name, font=('Courier', 16, 'bold'),
                        bg=bg_color, fg="#DCE7EA", cursor='arrow').pack(pady=(2, 2))
            else:
                q = tk.Label(frame, text="? ? ?", font=('Courier', 20, 'bold'),
                            bg=bg_color, fg=fg_color, cursor='hand2')
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
            return {
                'empty': "#14142B",
                'filled': '#D9D9D9',
                'outline': '#5a6a8a'
            }
        else:
            return {
                'empty': '#425B99',
                'filled': '#D9D9D9',
                'outline': '#8ab3d9'
            }
    
    def show_game(self, level):
        if level.get('id') in self.completed_levels:
            return
        
        self.clear_screen()
        self.in_game = True
        self.current_level = level
        self.result_panel = None
        self.guide_click_count = 0
        
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        fg_color = '#D9D9D9'
        
        self.current_screen = tk.Frame(self.main_frame, bg=bg_color)
        self.current_screen.pack(expand=True, fill='both')
        
        self.back_button = BackButton(self.current_screen, command=self.back_to_catalog, dark_theme=self.dark_theme)
        self.back_button.place(x=30, y=30)
        
        self.title_label = tk.Label(self.current_screen, text=level.get('name', 'Уровень'),
                                    font=('Courier', 32, 'bold'), bg=bg_color, fg=fg_color)
        self.title_label.pack(pady=(60, 30))
        
        self.timer_label = tk.Label(self.current_screen, text="00:00",
                                    font=('Courier', 24, 'bold'), bg=bg_color, fg=fg_color)
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
        
        self.game_container = tk.Frame(self.current_screen, bg=bg_color)
        self.game_container.pack(expand=True, fill='both')
        
        check_btn_frame = tk.Frame(self.current_screen, bg='#D9D9D9', bd=0)
        check_btn_frame.pack(side='bottom', anchor='se', padx=40, pady=30)
        self.check_button = tk.Button(check_btn_frame, text="ПРОВЕРИТЬ", font=('Courier', 20, 'bold'),
                                   bg='#0D1938' if self.dark_theme else '#425B99', 
                                   fg='#D9D9D9', width=15, height=2,
                                   relief='flat', bd=0, cursor='hand2', command=self.check_solution)
        self.check_button.pack(padx=3, pady=3)
        self.check_button.bind("<Enter>", lambda e: self.check_button.configure(
            bg="#122145" if self.dark_theme else "#5A75BA"))
        self.check_button.bind("<Leave>", lambda e: self.check_button.configure(
            bg='#0D1938' if self.dark_theme else '#425B99'))
        
        self.game_container.update_idletasks()
        max_row_hints, max_col_hints = self.calculate_cell_size()
        
        self.create_game_board(max_row_hints, max_col_hints)
        
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
    
    def create_game_board(self, max_row_hints, max_col_hints):
        if hasattr(self, 'game_canvas'):
            self.game_canvas.destroy()
        
        colors = self.get_cell_colors()
        bg_color = '#19233D' if self.dark_theme else '#677DB4'
        
        hint_cell_w = self.cell_size // 2
        hint_cell_h = self.cell_size // 2
        
        game_width = self.cols * self.cell_size + max_row_hints * hint_cell_w + 60
        game_height = self.rows * self.cell_size + max_col_hints * hint_cell_h + 60
        
        self.game_canvas = tk.Canvas(self.game_container, width=game_width, height=game_height,
                                     bg=bg_color, highlightthickness=0)
        self.game_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        hint_font = max(8, min(14, self.cell_size // 4))
        
        for col in range(self.cols):
            hints = self.col_hints[col] if col < len(self.col_hints) else []
            y_offset = max_col_hints * hint_cell_h
            for hint in reversed(hints):
                self.game_canvas.create_text(
                    col * self.cell_size + self.cell_size // 2 + max_row_hints * hint_cell_w + 20,
                    y_offset - hint_cell_h // 2 + 8,
                    text=str(hint), font=('Courier', hint_font, 'bold'), fill='#D9D9D9'
                )
                y_offset -= hint_cell_h
        
        for row in range(self.rows):
            hints = self.row_hints[row] if row < len(self.row_hints) else []
            x_offset = max_row_hints * hint_cell_w
            for hint in reversed(hints):
                self.game_canvas.create_text(
                    x_offset - hint_cell_w // 2 + 8,
                    row * self.cell_size + self.cell_size // 2 + max_col_hints * hint_cell_h + 20,
                    text=str(hint), font=('Courier', hint_font, 'bold'), fill='#D9D9D9'
                )
                x_offset -= hint_cell_w
        
        self.cell_rects = []
        for row in range(self.rows):
            row_rects = []
            for col in range(self.cols):
                x1 = col * self.cell_size + max_row_hints * hint_cell_w + 20
                y1 = row * self.cell_size + max_col_hints * hint_cell_h + 20
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
        elif self.cells[row][col] == 1:
            self.cells[row][col] = 0
            self.game_canvas.itemconfig(self.cell_rects[row][col], fill=colors['empty'])
        
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