import tkinter as tk

class ToggleSwitch:
    """Кастомный переключатель с закруглёнными углами"""
    def __init__(self, parent, initial_state=False, command=None):
        self.parent = parent
        self.state = initial_state
        self.command = command
        
        # Создаём холст для переключателя
        self.canvas = tk.Canvas(
            parent,
            width=80,
            height=40,
            bg='#677DB4',
            highlightthickness=0,
            cursor='hand2'
        )
        self.canvas.bind("<Button-1>", self.toggle)
        
        # Рисуем переключатель
        self.draw()
    
    def draw(self):
        """Отрисовка переключателя с закруглёнными углами и рамкой D9D9D9"""
        self.canvas.delete("all")
        
        width, height = 80, 40
        radius = 20
        
        if self.state:
            fill_color = '#677DB4'
        else:
            fill_color = '#CCCCCC'
        
        # Рисуем рамку D9D9D9
        self._create_rounded_rect(self.canvas, 0, 0, width, height, radius, '#D9D9D9', '#D9D9D9', 0)
        # Рисуем основной цветной прямоугольник с отступом для рамки
        self._create_rounded_rect(self.canvas, 2, 2, width-2, height-2, radius-2, fill_color, fill_color, 0)
        
        # Рисуем круглую ручку (увеличенного размера)
        knob_radius = 16  # Было 14, стало 16
        if self.state:
            self.canvas.create_oval(width - knob_radius*2 - 2, 4, width - 4, height - 4, 
                                   fill='#D9D9D9', outline='#677DB4', width=1)
        else:
            self.canvas.create_oval(4, 4, knob_radius*2 + 2, height - 4, 
                                   fill='#D9D9D9', outline='#677DB4', width=1)
    
    def _create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, fill_color, outline_color, outline_width):
        """Создаёт идеально закруглённый прямоугольник (похожий на капсулу)"""
        height = y2 - y1
        if radius > height // 2:
            radius = height // 2
        
        canvas.create_arc(x1, y1, x1 + radius*2, y2, 
                         start=90, extent=180, fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_arc(x2 - radius*2, y1, x2, y2, 
                         start=270, extent=180, fill=fill_color, outline=outline_color, width=outline_width)
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, 
                               fill=fill_color, outline=outline_color, width=outline_width)
    
    def toggle(self, event=None):
        self.state = not self.state
        self.draw()
        if self.command:
            self.command(self.state)
    
    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state
        self.draw()


class BackButton:
    """Кнопка назад в стиле переключателя"""
    def __init__(self, parent, command=None):
        self.parent = parent
        self.command = command
        
        # Создаём холст для кнопки
        self.canvas = tk.Canvas(
            parent,
            width=80,
            height=40,
            bg='#677DB4',
            highlightthickness=0,
            cursor='hand2'
        )
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Enter>", self.on_hover)
        self.canvas.bind("<Leave>", self.on_leave)
        
        # Рисуем кнопку
        self.draw()
    
    def draw(self, hover=False):
        """Отрисовка кнопки назад"""
        self.canvas.delete("all")
        
        width, height = 80, 40
        radius = 20
        
        if hover:
            fill_color = '#D9D9D9'
        else:
            fill_color = '#D9D9D9'
        
        # Рисуем рамку D9D9D9
        self._create_rounded_rect(self.canvas, 0, 0, width, height, radius, '#D9D9D9', '#D9D9D9', 0)
        # Рисуем основной цветной прямоугольник
        self._create_rounded_rect(self.canvas, 2, 2, width-2, height-2, radius-2, fill_color, fill_color, 0)
        
        # Рисуем стрелку влево
        self.canvas.create_line(30, 20, 60, 20, fill='#677DB4', width=3)
        self.canvas.create_polygon(30, 14, 20, 20, 30, 26, fill='#677DB4', outline='#677DB4')
    
    def _create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, fill_color, outline_color, outline_width):
        """Создаёт закруглённый прямоугольник"""
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
            self.command(event)
    
    def place(self, **kwargs):
        self.canvas.place(**kwargs)


class SettingsWindow:
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Настройки")
        self.window.configure(bg='#677DB4')
        
        self.fullscreen = False
        self.window.attributes('-fullscreen', self.fullscreen)
        
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)
        
        self.main_frame = tk.Frame(self.window, bg='#677DB4')
        self.main_frame.pack(expand=True, fill='both')
        
        # Кнопка назад
        self.back_button = BackButton(self.main_frame, command=self.close_settings)
        self.back_button.place(x=30, y=30)
        
        # Заголовок
        title_font = ('Courier', 56, 'bold')
        title_label = tk.Label(
            self.main_frame,
            text="Настройки",
            font=title_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        title_label.pack(pady=(100, 100))
        
        # Контейнер для пунктов меню
        menu_container = tk.Frame(self.main_frame, bg='#677DB4')
        menu_container.pack(fill='x', padx=200)
        
        # Подсказки
        tips_frame = tk.Frame(menu_container, bg='#677DB4')
        tips_frame.pack(fill='x', pady=15)
        
        tips_label = tk.Label(
            tips_frame,
            text="Подсказки",
            font=('Courier', 32, 'bold'),
            bg='#677DB4',
            fg='#D9D9D9'
        )
        tips_label.pack(side='left', padx=20, pady=10)
        
        self.tips_switch = ToggleSwitch(
            tips_frame,
            initial_state=True,
            command=self.on_tips_toggle
        )
        self.tips_switch.canvas.pack(side='right', padx=10)
        
        # Тема
        theme_frame = tk.Frame(menu_container, bg='#677DB4')
        theme_frame.pack(fill='x', pady=15)
        
        theme_label = tk.Label(
            theme_frame,
            text="Тема",
            font=('Courier', 32, 'bold'),
            bg='#677DB4',
            fg='#D9D9D9'
        )
        theme_label.pack(side='left', padx=20, pady=10)
        
        self.theme_switch = ToggleSwitch(
            theme_frame,
            initial_state=False,
            command=self.on_theme_toggle
        )
        self.theme_switch.canvas.pack(side='right', padx=10)
        
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.window.attributes('-fullscreen', self.fullscreen)
    
    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.window.attributes('-fullscreen', False)
    
    def on_tips_toggle(self, state):
        pass
    
    def on_theme_toggle(self, state):
        pass
    
    def close_settings(self, event):
        self.window.destroy()
    
    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    settings = SettingsWindow()
    settings.run()