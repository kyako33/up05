import tkinter as tk
import json
import os
import time

class BackButton:
    """Кнопка назад в стиле переключателя"""
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
        
        canvas.create_arc(x1, y1, x1 + radius*2, y2, 
                         start=90, extent=180, fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_arc(x2 - radius*2, y1, x2, y2, 
                         start=270, extent=180, fill=fill_color, outline=outline_color, width=outline_width)
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


class NonogramGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nonogramm")
        self.root.configure(bg='#677DB4')
        self.root.geometry("1200x800")
        
        self.root.eval('tk::PlaceWindow . center')
        
        self.fullscreen = False
        self.root.attributes('-fullscreen', self.fullscreen)
        
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_game)
        self.root.bind("<Configure>", self.on_window_resize)
        
        self.levels = self.load_levels()
        self.current_level = None
        self.progress = self.load_progress()
        
        self.start_time = None
        self.timer_running = False
        self.timer_id = None
        self.saved_time = 0
        
        self.main_frame = tk.Frame(self.root, bg='#677DB4')
        self.main_frame.pack(expand=True, fill='both')
        
        self.current_screen = None
        self.resize_timer = None
        self.in_game = False
        self.auto_save_timer = None
        
        self.show_catalog()
    
    def load_levels(self):
        levels = []
        levels_file = os.path.join(os.path.dirname(__file__), 'levels.json')
        
        with open(levels_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            levels = data.get('levels', [])
        
        return levels
    
    def load_progress(self):
        progress_file = os.path.join(os.path.dirname(__file__), 'progress.json')
        default_progress = {
            "completed_levels": [],
            "level_states": {}
        }
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                return progress
        except (FileNotFoundError, json.JSONDecodeError):
            return default_progress
    
    def save_progress(self):
        progress_file = os.path.join(os.path.dirname(__file__), 'progress.json')
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def auto_save_state(self):
        if self.in_game and hasattr(self, 'current_level') and self.current_level:
            self.save_current_level_state()
        self.auto_save_timer = self.root.after(5000, self.auto_save_state)
    
    def save_current_level_state(self):
        if not self.in_game or not hasattr(self, 'current_level') or not self.current_level:
            return
        
        level_id = self.current_level.get('id')
        if level_id is None:
            return
        
        cells_state = []
        if hasattr(self, 'cells'):
            for row in range(self.rows):
                row_state = []
                for col in range(self.cols):
                    row_state.append(self.cells[row][col])
                cells_state.append(row_state)
        
        elapsed = self.saved_time
        if self.timer_running and self.start_time:
            elapsed = self.saved_time + int(time.time() - self.start_time)
        
        self.progress["level_states"][str(level_id)] = {
            "cells": cells_state,
            "time": elapsed
        }
        
        self.save_progress()
    
    def load_level_state(self, level_id):
        level_id_str = str(level_id)
        if level_id_str in self.progress["level_states"]:
            return self.progress["level_states"][level_id_str]
        return None
    
    def mark_level_completed(self, level_id):
        if level_id not in self.progress["completed_levels"]:
            self.progress["completed_levels"].append(level_id)
            if str(level_id) in self.progress["level_states"]:
                del self.progress["level_states"][str(level_id)]
            self.save_progress()
    
    def is_level_completed(self, level_id):
        return level_id in self.progress["completed_levels"]
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        self.root.after(200, self.delayed_resize)
    
    def on_window_resize(self, event=None):
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        self.resize_timer = self.root.after(150, self.delayed_resize)
    
    def delayed_resize(self):
        if self.in_game and hasattr(self, 'board_canvas') and self.board_canvas.winfo_exists():
            self.update_cell_size()
            self.create_game_board()
    
    def clear_screen(self):
        self.in_game = False
        self.stop_timer()
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None
    
    def draw_level_preview(self, canvas, level, width, height):
        level_id = level.get('id')
        
        if self.is_level_completed(level_id):
            solution = level.get("solution", [])
            size = level.get("size", {})
            rows = size.get("rows", 5)
            cols = size.get("cols", 5)
            
            if solution:
                cell_w = width / cols
                cell_h = height / rows
                
                colors = [
                    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                    '#DFA5A5', '#A8D8EA', '#AA96DA', '#C5E99B', '#FFD93D',
                    '#FF9A9E', '#FECFEF', '#D4A5A5', '#9B59B6', '#3498DB'
                ]
                
                for row in range(min(rows, len(solution))):
                    for col in range(min(cols, len(solution[row]) if solution else 0)):
                        if solution[row][col] == 1:
                            color_index = (row * cols + col) % len(colors)
                            color = colors[color_index]
                        else:
                            color = '#425B99'
                        
                        canvas.create_rectangle(
                            col * cell_w, row * cell_h,
                            (col + 1) * cell_w, (row + 1) * cell_h,
                            fill=color, outline='', width=0
                        )
            else:
                canvas.create_rectangle(0, 0, width, height, fill='#425B99', outline='', width=0)
        else:
            canvas.create_rectangle(0, 0, width, height, fill='#425B99', outline='', width=0)
    
    def show_catalog(self, event=None):
        self.clear_screen()
        
        self.current_screen = tk.Frame(self.main_frame, bg='#677DB4')
        self.current_screen.pack(expand=True, fill='both')
        
        self.back_button = BackButton(self.current_screen, command=self.exit_game, dark_theme=False)
        self.back_button.place(x=30, y=30)
        
        title_font = ('Courier', 48, 'bold')
        title_label = tk.Label(
            self.current_screen,
            text="Каталог уровней",
            font=title_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        title_label.pack(pady=(80, 60))
        
        levels_container = tk.Frame(self.current_screen, bg='#677DB4')
        levels_container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(levels_container, bg='#677DB4', highlightthickness=0)
        scrollbar = tk.Scrollbar(levels_container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', expand=True, fill='both')
        
        levels_frame = tk.Frame(canvas, bg='#677DB4')
        canvas_window = canvas.create_window((0, 0), window=levels_frame, anchor='nw')
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        def on_canvas_configure(event):
            canvas_width = event.width
            frame_width = levels_frame.winfo_reqwidth()
            if canvas_width > frame_width:
                x_offset = (canvas_width - frame_width) // 2
                canvas.coords(canvas_window, x_offset, 0)
            else:
                canvas.coords(canvas_window, 0, 0)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        
        levels_frame.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.bind('<MouseWheel>', on_mousewheel)
        canvas.configure(xscrollcommand=None)
        
        cols = 3
        cell_width = 200
        padx_value = 120
        pady_value = 70
        
        for i, level in enumerate(self.levels):
            row = i // cols
            col = i % cols
            
            frame = tk.Frame(levels_frame, bg='#677DB4', cursor='hand2')
            frame.grid(row=row, column=col, padx=padx_value, pady=pady_value, sticky='nsew')
            
            level_id = level.get('id')
            image_name = level.get('image_name', '')
            is_completed = self.is_level_completed(level_id)
            
            # Для пройденных уровней - делаем некликабельными (без курсора и без привязки)
            if is_completed:
                cursor = 'arrow'
            else:
                cursor = 'hand2'
                frame.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            level_canvas = tk.Canvas(frame, width=cell_width, height=cell_width, highlightthickness=0, cursor=cursor)
            level_canvas.pack(pady=(0, 8))
            
            if not is_completed:
                level_canvas.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            self.draw_level_preview(level_canvas, level, cell_width, cell_width)
            
            name_label = tk.Label(frame, text=level.get("name", f"Уровень {level.get('id', i+1)}"),
                                  font=('Courier', 16, 'bold'), bg='#677DB4', fg='#D9D9D9', cursor=cursor)
            name_label.pack(pady=(4, 2))
            
            if not is_completed:
                name_label.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
            
            # Показываем название картинки ТОЛЬКО если уровень пройден
            if is_completed:
                image_label = tk.Label(
                    frame, 
                    text=image_name, 
                    font=('Courier', 14, 'bold'), 
                    bg='#677DB4', 
                    fg='#FFD93D', 
                    cursor='arrow'
                )
                image_label.pack(pady=(2, 2))
            else:
                questions_label = tk.Label(frame, text="? ? ?", font=('Courier', 20, 'bold'),
                                           bg='#677DB4', fg='#D9D9D9', cursor='hand2')
                questions_label.pack(pady=(2, 0))
                questions_label.bind("<Button-1>", lambda e, lvl=level: self.show_game(lvl))
        
        for i in range(cols):
            levels_frame.grid_columnconfigure(i, weight=1)
        
        levels_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
    
    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer_display()
    
    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.start_time and self.in_game:
            self.saved_time += int(time.time() - self.start_time)
    
    def update_timer_display(self):
        if self.timer_running and hasattr(self, 'timer_label'):
            elapsed = self.saved_time + int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            self.timer_id = self.root.after(1000, self.update_timer_display)
    
    def show_congratulations(self):
        """Показывает панель поздравления прямо в игровом окне"""
        self.stop_timer()
        
        # Получаем название картинки из уровня
        image_name = self.current_level.get('image_name', 'Картинка')
        
        # Создаём затемнённый фон
        overlay = tk.Frame(self.current_screen, bg='#677DB4')
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Создаём панель поздравления
        panel = tk.Frame(overlay, bg='#677DB4')
        panel.place(relx=0.5, rely=0.5, anchor='center', width=550, height=520)
        
        # Заголовок
        title_font = ('Courier', 32, 'bold')
        title_label = tk.Label(
            panel,
            text="ПОЗДРАВЛЯЕМ!",
            font=title_font,
            bg='#677DB4',
            fg='#4CAF50'
        )
        title_label.pack(pady=(20, 10))
        
        # Название картинки
        image_name_font = ('Courier', 24, 'bold')
        image_name_label = tk.Label(
            panel,
            text=f"Вы собрали: {image_name}!",
            font=image_name_font,
            bg='#677DB4',
            fg='#FFD93D'
        )
        image_name_label.pack(pady=(5, 10))
        
        # Сообщение
        message_font = ('Courier', 18, 'bold')
        message_label = tk.Label(
            panel,
            text=f"Уровень {self.current_level.get('name', '')} пройден!",
            font=message_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        message_label.pack(pady=10)
        
        # Пиксельная картинка
        self.draw_pixel_art_in_panel(panel)
        
        # Кнопка к каталогу
        button_frame = tk.Frame(panel, bg='#677DB4')
        button_frame.pack(pady=20)
        
        catalog_button = tk.Button(
            button_frame,
            text="К КАТАЛОГУ УРОВНЕЙ",
            font=('Courier', 16, 'bold'),
            bg='#425B99',
            fg='#D9D9D9',
            activebackground='#5A75BA',
            activeforeground='#D9D9D9',
            width=18,
            height=1,
            relief='solid',
            bd=2,
            cursor='hand2',
            command=lambda: self.close_congratulations_and_go_to_catalog(overlay)
        )
        catalog_button.pack()
        
        catalog_button.bind("<Enter>", lambda e, btn=catalog_button: btn.configure(bg="#5A75BA"))
        catalog_button.bind("<Leave>", lambda e, btn=catalog_button: btn.configure(bg='#425B99'))
    
    def draw_pixel_art_in_panel(self, panel):
        """Рисует пиксельную картинку внутри панели поздравления"""
        solution = self.current_level.get("solution", [])
        size = self.current_level.get("size", {})
        rows = size.get("rows", 5)
        cols = size.get("cols", 5)
        
        art_frame = tk.Frame(panel, bg='#677DB4')
        art_frame.pack(pady=15)
        
        if rows <= 8:
            pixel_size = 35
        elif rows <= 12:
            pixel_size = 28
        else:
            pixel_size = 22
        
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DFA5A5', '#A8D8EA', '#AA96DA', '#C5E99B', '#FFD93D',
            '#FF9A9E', '#FECFEF', '#D4A5A5', '#9B59B6', '#3498DB'
        ]
        
        for row in range(min(rows, len(solution))):
            for col in range(min(cols, len(solution[row]) if solution else 0)):
                if solution[row][col] == 1:
                    color_index = (row * cols + col) % len(colors)
                    color = colors[color_index]
                else:
                    color = '#425B99'
                
                pixel = tk.Canvas(
                    art_frame,
                    width=pixel_size,
                    height=pixel_size,
                    bg=color,
                    highlightthickness=0,
                    bd=0
                )
                pixel.grid(row=row, column=col, padx=0, pady=0, sticky='nsew')
        
        for i in range(rows):
            art_frame.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            art_frame.grid_columnconfigure(i, weight=1)
    
    def close_congratulations_and_go_to_catalog(self, overlay):
        """Закрывает панель поздравления и переходит в каталог"""
        overlay.destroy()
        self.show_catalog()
    
    def check_solution(self):
        if not hasattr(self, 'current_level'):
            return
        
        solution = self.current_level.get("solution", [])
        
        correct = True
        for row in range(self.rows):
            for col in range(self.cols):
                expected = solution[row][col] if solution and row < len(solution) and col < len(solution[row]) else 0
                current = 1 if self.cells[row][col] == 1 else 0
                if expected != current:
                    correct = False
                    break
            if not correct:
                break
        
        level_id = self.current_level.get('id')
        if correct:
            self.mark_level_completed(level_id)
            self.show_congratulations()
        else:
            self.show_error_message()
    
    def show_error_message(self):
        if hasattr(self, 'error_label') and self.error_label:
            self.error_label.destroy()
        
        self.error_label = tk.Label(
            self.current_screen,
            text="НЕПРАВИЛЬНО! Попробуйте ещё раз",
            font=('Courier', 24, 'bold'),
            bg='#677DB4',
            fg='#f44336'
        )
        self.error_label.place(relx=0.5, rely=0.85, anchor='center')
        
        self.root.after(2000, lambda: self.error_label.destroy() if hasattr(self, 'error_label') and self.error_label else None)
    
    def back_to_catalog(self):
        self.save_current_level_state()
        self.show_catalog()
    
    def show_game(self, level):
        # Проверяем, не пройден ли уровень (дополнительная защита)
        if self.is_level_completed(level.get('id')):
            return
        
        self.clear_screen()
        self.in_game = True
        self.current_level = level
        
        self.current_screen = tk.Frame(self.main_frame, bg='#677DB4')
        self.current_screen.pack(expand=True, fill='both')
        
        self.back_button = BackButton(self.current_screen, command=self.back_to_catalog, dark_theme=False)
        self.back_button.place(x=30, y=30)
        
        title_font = ('Courier', 32, 'bold')
        self.title_label = tk.Label(
            self.current_screen,
            text=level.get('name', 'Уровень'),
            font=title_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        self.title_label.pack(pady=(60, 30))
        
        timer_font = ('Courier', 24, 'bold')
        self.timer_label = tk.Label(
            self.current_screen,
            text="00:00",
            font=timer_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        self.timer_label.place(relx=0.95, y=30, anchor='ne')
        
        self.rows = level.get("size", {}).get("rows", 5)
        self.cols = level.get("size", {}).get("cols", 5)
        
        self.row_hints = level.get("row_hints", [])
        self.col_hints = level.get("col_hints", [])
        
        if not self.row_hints:
            self.row_hints = [[] for _ in range(self.rows)]
        if not self.col_hints:
            self.col_hints = [[] for _ in range(self.cols)]
        
        self.cells = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        level_id = level.get('id')
        saved_state = self.load_level_state(level_id)
        self.saved_time = 0
        
        if saved_state:
            saved_cells = saved_state.get("cells", [])
            self.saved_time = saved_state.get("time", 0)
            for row in range(min(len(saved_cells), self.rows)):
                for col in range(min(len(saved_cells[row]), self.cols)):
                    self.cells[row][col] = saved_cells[row][col]
        
        self.board_container = tk.Frame(self.current_screen, bg='#677DB4')
        self.board_container.pack(expand=True, fill='both')
        
        check_button = tk.Button(
            self.current_screen,
            text="ПРОВЕРИТЬ",
            font=('Courier', 20, 'bold'),
            bg='#425B99',
            fg='#D9D9D9',
            activebackground='#5A75BA',
            activeforeground='#D9D9D9',
            width=18,
            height=2,
            relief='solid',
            bd=1,
            highlightthickness=0,
            highlightbackground='#D9D9D9',
            highlightcolor='#D9D9D9',
            cursor='hand2',
            command=self.check_solution
        )
        check_button.pack(side='bottom', anchor='se', padx=40, pady=40)
        
        check_button.bind("<Enter>", lambda e, btn=check_button: btn.configure(bg="#5A75BA"))
        check_button.bind("<Leave>", lambda e, btn=check_button: btn.configure(bg='#425B99'))
        
        self.update_cell_size()
        self.create_game_board()
        
        if self.saved_time > 0:
            self.timer_running = True
            self.start_time = time.time()
            self.update_timer_display()
        else:
            self.start_timer()
        
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.auto_save_timer = self.root.after(5000, self.auto_save_state)
    
    def update_cell_size(self):
        if not hasattr(self, 'board_container') or not self.board_container.winfo_exists():
            return
        
        self.board_container.update_idletasks()
        
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        header_height = 140
        footer_height = 100
        available_height = window_height - header_height - footer_height
        available_width = window_width - 100
        
        max_cell_by_width = (available_width - 40) // max(self.cols, 1)
        max_cell_by_height = (available_height - 40) // max(self.rows, 1)
        
        if self.rows >= 10 or self.cols >= 10:
            max_size = 35
        elif self.rows >= 8 or self.cols >= 8:
            max_size = 45
        else:
            max_size = 55
        
        self.cell_size = max(20, min(max_cell_by_width, max_cell_by_height, max_size))
    
    def create_game_board(self):
        if hasattr(self, 'board_canvas') and self.board_canvas.winfo_exists():
            self.board_canvas.destroy()
        
        max_row_hints = max([len(hints) for hints in self.row_hints]) if self.row_hints else 0
        max_col_hints = max([len(hints) for hints in self.col_hints]) if self.col_hints else 0
        
        hint_cell_w = self.cell_size // 2
        hint_cell_h = self.cell_size // 2
        
        game_width = self.cols * self.cell_size + max_row_hints * hint_cell_w + 40
        game_height = self.rows * self.cell_size + max_col_hints * hint_cell_h + 40
        
        self.board_canvas = tk.Canvas(
            self.board_container,
            width=game_width,
            height=game_height,
            bg='#677DB4',
            highlightthickness=0
        )
        self.board_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        hint_font_size = max(8, min(14, self.cell_size // 4))
        
        for col in range(self.cols):
            hints = self.col_hints[col]
            y_offset = max_col_hints * hint_cell_h
            for hint in hints:
                self.board_canvas.create_text(
                    col * self.cell_size + self.cell_size // 2 + max_row_hints * hint_cell_w + 20,
                    y_offset - hint_cell_h // 2 + 8,
                    text=str(hint),
                    font=('Courier', hint_font_size, 'bold'),
                    fill='#D9D9D9'
                )
                y_offset -= hint_cell_h
        
        for row in range(self.rows):
            hints = self.row_hints[row]
            x_offset = max_row_hints * hint_cell_w
            for hint in hints:
                self.board_canvas.create_text(
                    x_offset - hint_cell_w // 2 + 8,
                    row * self.cell_size + self.cell_size // 2 + max_col_hints * hint_cell_h + 20,
                    text=str(hint),
                    font=('Courier', hint_font_size, 'bold'),
                    fill='#D9D9D9'
                )
                x_offset -= hint_cell_w
        
        self.cell_rects = []
        
        for row in range(self.rows):
            row_rects = []
            for col in range(self.cols):
                x1 = col * self.cell_size + max_row_hints * hint_cell_w + 20
                y1 = row * self.cell_size + max_col_hints * hint_cell_h + 20
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.cells[row][col] == 1:
                    fill = '#D9D9D9'
                elif self.cells[row][col] == 2:
                    fill = '#5a7ab9'
                else:
                    fill = '#425B99'
                
                rect = self.board_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill,
                    outline='#8ab3d9',
                    width=1,
                    tags=f"cell_{row}_{col}"
                )
                row_rects.append(rect)
                
                if self.cells[row][col] == 2:
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    r = self.cell_size // 3
                    self.board_canvas.create_line(cx - r, cy - r, cx + r, cy + r, fill='#D9D9D9', width=1, tags=f"cross_{row}_{col}")
                    self.board_canvas.create_line(cx + r, cy - r, cx - r, cy + r, fill='#D9D9D9', width=1, tags=f"cross_{row}_{col}")
                
                self.board_canvas.tag_bind(f"cell_{row}_{col}", "<Button-1>", 
                                           lambda e, r=row, c=col: self.cell_click(r, c))
                self.board_canvas.tag_bind(f"cell_{row}_{col}", "<Button-3>", 
                                           lambda e, r=row, c=col: self.cell_right_click(r, c))
            self.cell_rects.append(row_rects)
    
    def cell_click(self, row, col):
        if self.cells[row][col] == 0:
            self.cells[row][col] = 1
            self.board_canvas.itemconfig(self.cell_rects[row][col], fill='#D9D9D9')
            self.board_canvas.delete(f"cross_{row}_{col}")
        elif self.cells[row][col] == 1:
            self.cells[row][col] = 0
            self.board_canvas.itemconfig(self.cell_rects[row][col], fill='#425B99')
    
    def cell_right_click(self, row, col):
        if self.cells[row][col] == 0:
            self.cells[row][col] = 2
            self.board_canvas.itemconfig(self.cell_rects[row][col], fill='#5a7ab9')
            x1, y1, x2, y2 = self.board_canvas.coords(self.cell_rects[row][col])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            r = self.cell_size // 3
            self.board_canvas.create_line(cx - r, cy - r, cx + r, cy + r, fill='#D9D9D9', width=1, tags=f"cross_{row}_{col}")
            self.board_canvas.create_line(cx + r, cy - r, cx - r, cy + r, fill='#D9D9D9', width=1, tags=f"cross_{row}_{col}")
        elif self.cells[row][col] == 2:
            self.cells[row][col] = 0
            self.board_canvas.itemconfig(self.cell_rects[row][col], fill='#425B99')
            self.board_canvas.delete(f"cross_{row}_{col}")
    
    def exit_game(self, event=None):
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.save_current_level_state()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = NonogramGame()
    game.run()