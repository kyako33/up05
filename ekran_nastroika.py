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
        
        # Рисуем круглую ручку
        knob_radius = 16
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


class NonogramGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nonogramm")
        self.root.configure(bg='#677DB4')
        self.root.geometry("800x600")
        
        # Центрирование окна
        self.root.eval('tk::PlaceWindow . center')
        
        # Установка полноэкранного режима
        self.fullscreen = False
        self.root.attributes('-fullscreen', self.fullscreen)
        
        # Привязка клавиш
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_game)
        
        # Создание основного фрейма
        self.main_frame = tk.Frame(self.root, bg='#677DB4')
        self.main_frame.pack(expand=True, fill='both')
        
        # Переменная для хранения текущего экрана
        self.current_screen = None
        
        # Показываем главное меню
        self.show_main_menu()
    
    def toggle_fullscreen(self, event=None):
        """Переключение полноэкранного режима"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
    
    def clear_screen(self):
        """Очищает текущий экран"""
        if self.current_screen:
            self.current_screen.destroy()
    
    def show_main_menu(self, event=None):
        """Показывает главное меню"""
        self.clear_screen()
        
        self.current_screen = tk.Frame(self.main_frame, bg='#677DB4')
        self.current_screen.pack(expand=True, fill='both')
        
        # Заголовок
        title_font = ('Courier', 67, 'bold')
        title_label = tk.Label(
            self.current_screen,
            text="Nonogramm",
            font=title_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        title_label.pack(pady=(100, 80))
        
        # Стиль для кнопок
        button_font = ('Courier', 30, 'bold')
        button_width = 15
        button_height = 2
        
        # Функция для создания кнопки с рамкой D9D9D9
        def create_button(text, command):
            # Создаём фрейм-рамку цвета D9D9D9
            frame = tk.Frame(
                self.current_screen,
                bg='#D9D9D9',
                bd=0,
                relief='flat'
            )
            frame.pack(pady=10)
            
            # Создаём саму кнопку
            button = tk.Button(
                frame,
                text=text,
                font=button_font,
                bg='#425B99',
                fg='#D9D9D9',
                activebackground='#425B99',
                activeforeground='#D9D9D9',
                width=button_width,
                height=button_height,
                relief='flat',
                bd=0,
                cursor='hand2'
            )
            button.pack(padx=1, pady=1)
            
            # Привязываем события
            button.bind("<Button-1>", command)
            
            # Эффект наведения для кнопки
            button.bind("<Enter>", lambda e, btn=button: btn.configure(bg="#5A75BA"))
            button.bind("<Leave>", lambda e, btn=button: btn.configure(bg='#425B99'))
            
            return button
        
        # Создаём кнопки
        self.start_button = create_button("Старт", self.start_game)
        self.settings_button = create_button("Настройки", self.show_settings)
        self.exit_button = create_button("Выход", self.exit_game)
          
    def show_settings(self, event=None):
        """Показывает экран настроек"""
        self.clear_screen()
        
        self.current_screen = tk.Frame(self.main_frame, bg='#677DB4')
        self.current_screen.pack(expand=True, fill='both')
        
        # Кнопка назад с использованием класса BackButton
        self.back_button = BackButton(self.current_screen, command=self.show_main_menu)
        self.back_button.place(x=30, y=30)
        
        # Заголовок
        title_font = ('Courier', 56, 'bold')
        title_label = tk.Label(
            self.current_screen,
            text="Настройки",
            font=title_font,
            bg='#677DB4',
            fg='#D9D9D9'
        )
        title_label.pack(pady=(100, 100))
        
        # Контейнер для пунктов меню
        menu_container = tk.Frame(self.current_screen, bg='#677DB4')
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
    
    def start_game(self, event=None):
        """Начало игры"""
        print("Игра началась!")
    
    def on_tips_toggle(self, state):
        """Обработчик переключения подсказок"""
        print(f"Подсказки: {'Включены' if state else 'Выключены'}")
    
    def on_theme_toggle(self, state):
        """Обработчик переключения темы"""
        print(f"Тема: {'Тёмная' if state else 'Светлая'}")
    
    def exit_game(self, event=None):
        """Выход из игры"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = NonogramGame()
    game.run()