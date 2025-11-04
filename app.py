from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label

class MainScreen(Screen):
    grid_content = ObjectProperty(None)

    def on_kv_post(self, widget):
        self.load_questions()

    def load_questions(self):
        self.clear_grid()
        file_path = 'example.txt'
        questions = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        question = parts[0]
                        answers = parts[1:]
                        questions.append((question, answers))
        except FileNotFoundError:
            self.show_file_not_found_popup(file_path)

        for question, answers in questions:
            self.grid_content.add_widget(
                self.create_label(question, halign='left')
            )
            self.grid_content.add_widget(
                self.create_spinner(answers)
            )

    def show_file_not_found_popup(self, file_path):
        content = Label(
            text=f"Файл с вопросами не найден:\n{file_path}",
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        popup = Popup(
            title='Ошибка',
            content=content,
            size_hint=(0.6, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        popup.open()

    def create_label(self, text, **kwargs):
        from kivy.uix.label import Label
        label = Label(
            text=text,
            halign=kwargs.get('halign', 'center'),
            valign='middle',
            size_hint_y=None,
            height=60,
            text_size=(self.width * 0.4, None)
        )
        label.bind(size=label.setter('text_size'))
        return label

    def create_spinner(self, options):
        spinner = Spinner(
            text='Выберите ответ',  # Текст по умолчанию
            values=options,       # Список вариантов
            size_hint_y=None,
            height=60,
            background_color=(0.8, 0.8, 1, 1),  # Светло‑синий фон
            color=(0, 0, 0, 1)  # Чёрный текст
        )
        # Обработчик выбора (можно расширить)
        spinner.bind(text=self.on_spinner_select)
        return spinner

    def on_spinner_select(self, spinner, text):
        print(f"Выбран ответ: {text}")
        # Здесь можно добавить логику проверки правильности и т.п.

    def create_button(self, text):
        from kivy.uix.button import Button
        return Button(
            text=text,
            size_hint_y=None,
            height=60
        )

    def show_form(self):
        self.ids.grid_layout.clear_widgets()
        self.ids.grid_layout.add_widget(self.create_label('Имя:'))
        self.ids.grid_layout.add_widget(self.create_button('Ввести имя'))
        self.ids.grid_layout.add_widget(self.create_label('Email:'))
        self.ids.grid_layout.add_widget(self.create_button('Ввести email'))
        self.ids.grid_layout.add_widget(self.create_label('Возраст:'))
        self.ids.grid_layout.add_widget(self.create_button('Выбрать возраст'))

    def show_table(self):
        self.ids.grid_layout.clear_widgets()
        for i in range(3):
            for j in range(2):
                text = f'Ряд {i+1}, Кол {j+1}'
                self.ids.grid_layout.add_widget(self.create_button(text))

    def clear_grid(self):
        self.ids.grid_layout.clear_widgets()

class MyApp(App):
    questions = []

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MyApp().run()
