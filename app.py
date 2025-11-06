from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel


Window.size = (480, 853)

Builder.load_file('screens/start_screen.kv')
Builder.load_file('screens/main_screen.kv')
Builder.load_file('screens/registration_screen.kv')


class StartScreen(MDScreen):
    def start_app(self):
        self.manager.current = 'registration'


class RegistrationScreen(MDScreen):

    name = StringProperty("")
    surname = StringProperty("")
    class_name = StringProperty("")
    subject = StringProperty("")

    def register_user(self):
        self.manager.current = 'main'


class MainScreen(MDScreen):
    grid_content = ObjectProperty(None)
    spinners = []
    questions = []

    def on_kv_post(self, widget):
        self.load_questions()

    def load_questions(self):
        button = self.ids.questions_button
        button.text = 'Завершить'

        self.clear_grid()
        self.spinners = {}
        self.questions = []

        file_path = 'example.txt'

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        question = parts[0]
                        right_answer = parts[1]
                        answers = parts[2:]

                        self.questions.append({
                            "question": question,
                            "right_answer": right_answer,
                            "answers": answers
                        })
 
        except FileNotFoundError:
            self.show_file_not_found_popup(file_path)

        for question_index, question in enumerate(self.questions):
            self.grid_content.add_widget(
                self.create_label(question["question"], halign='left')
            )
            self.grid_content.add_widget(
                self.create_spinner(
                    question["answers"], question_index))

    def show_file_not_found_popup(self, file_path):
        content = MDLabel(
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

        label = MDLabel(
            text=text,
            halign=kwargs.get('halign', 'right'),
            valign='middle',
            size_hint_y=None,
            height=60,
            text_size=(self.width * 0.4, None)
        )
        label.bind(size=label.setter('text_size'))
        return label

    def create_spinner(self, options, question_index):
        spinner = Spinner(
            text='Выберите ответ',
            values=options,  
            size_hint_y=None,
            height=60,
            background_color=self.theme_cls.primary_color,  # Основной цвет темы
            background_normal='',  # Убираем стандартный фон
            color=(1, 1, 1, 1),  # Белый текст
            # background_down=self.theme_cls.primary_dark,  # Темнее при нажатии
        )

        spinner.bind(text=lambda instance, value: self.on_spinner_select(
            instance, value, question_index)
            )
        return spinner

    def on_spinner_select(self, spinner, text, question_index):
        self.spinners[question_index] = text
        if self.questions[question_index]["right_answer"] == text:
            print("Верный ответ!!!")
            print(f"Вопрос {question_index+1}: Выбран ответ: {text}")
        print(self.spinners)
    
    # def create_textinput(self, hint_text, helper_text=""):

    #     textinput = MDTextField(
    #         hint_text=hint_text,
    #         helper_text=helper_text,
    #         # helper_text_mode="on_error",
    #         size_hint_y=None,
    #         height=60,
    #         size_hint_x=0.5,
    #         multiline=False,
    #         padding=[10, 10]
    #     )
    #     return textinput

    # def show_form(self):
    #     self.ids.grid_layout.clear_widgets()
    #     self.ids.grid_layout.add_widget(self.create_textinput('Имя'))
    #     self.ids.grid_layout.add_widget(self.create_textinput('Фамилия'))
    #     self.ids.grid_layout.add_widget(self.create_textinput('Класс', 'например 5а'))
        # self.ids.grid_layout.add_widget(self.create_button('Предмет'))
    
    def accept_answers(self):
        pass

    def clear_grid(self):
        self.ids.grid_layout.clear_widgets()
    
    def exit_app(self):
        MDApp.get_running_app().stop()


class TestIMApp(MDApp):
    questions = []
    def get_hex_color(self, hex_color):
        return get_color_from_hex(hex_color)

    def build(self):
        # Цветовая схема
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Orange"
        
        # Стиль темы
        self.theme_cls.theme_style = "Light"  # или "Light" "Dark"
        
        # Дополнительные настройки
        self.theme_cls.primary_hue = "500"    # Оттенок основного цвета
        self.theme_cls.accent_hue = "200"     # Оттенок акцентного цвета
        
        sm = MDScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(RegistrationScreen(name='registration'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    TestIMApp().run()
