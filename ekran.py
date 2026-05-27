import tkinter as tk

class NonogramGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nonogramm")
        self.root.configure(bg='#1a3a5f')
        
        # Установка полноэкранного режима
        self.fullscreen = False
        self.root.attributes('-fullscreen', self.fullscreen)
        
        # Привязка клавиши F11 для переключения полноэкранного режима
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        
        # Создание основного фрейма с отступами
        self.main_frame = tk.Frame(self.root, bg='#677DB4')
        self.main_frame.pack(expand=True, fill='both')
        
        # Заголовок # Nonogramm
        title_font = ('Courier', 67, 'bold')
        title_label = tk.Label(
            self.main_frame,
            text="Nonogramm",
            font=title_font,
            bg='#677DB4',
            fg='#DDE5FF'
        )
        title_label.pack(pady=(100, 80))
        
        # Стиль для кнопок
        button_font = ('Courier', 30, 'bold')
        button_width = 15
        button_height = 2
        
        # Функция для создания кнопки с белой рамкой
        def create_button(text, command):
            # Создаём фрейм-рамку белого цвета
            frame = tk.Frame(
                self.main_frame,
                bg='white',
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
                fg='#DDE5FF',
                activebackground='#425B99',
                activeforeground='white',
                width=button_width,
                height=button_height,
                relief='flat',
                bd=0,
                cursor='hand2'
            )
            button.pack(padx=1, pady=1)  # Отступ создаёт видимую белую рамку
            
            # Привязываем события
            button.bind("<Button-1>", command)
            
            # Эффект наведения для кнопки
            button.bind("<Enter>", lambda e, btn=button: btn.configure(bg="#5A75BA"))
            button.bind("<Leave>", lambda e, btn=button: btn.configure(bg='#425B99'))
            
            return button
        
        # Создаём кнопки
        self.start_button = create_button("Старт", self.start_game)
        self.settings_button = create_button("Настройки", self.open_settings)
        self.exit_button = create_button("Выход", self.exit_game)
    
    def toggle_fullscreen(self, event=None):
        """Переключение полноэкранного режима"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
    
    def exit_fullscreen(self, event=None):
        """Выход из полноэкранного режима"""
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)
    
    def start_game(self, event):
        """Начало игры"""
        print("Игра началась!")
        # Здесь будет логика игры
    
    def open_settings(self, event):
        """Открытие настроек"""
        print("Настройки открыты")
        # Здесь будет логика настроек
    
    def exit_game(self, event):
        """Выход из игры"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = NonogramGame()
    game.run()