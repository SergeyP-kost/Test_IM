from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem

from helpers.choice_random import select_random_items


Window.size = (480, 853)

Builder.load_file('screens/start_screen.kv')
Builder.load_file('screens/main_screen.kv')
Builder.load_file('screens/registration_screen.kv')

COUNT_QUESTIONS = 2


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
    dropdown_menus = {}  # Словарь для хранения меню

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown_menus = {}

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
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        question = parts[0]
                        right_answer = parts[1]
                        answers = parts[1:]

                        self.questions.append({
                            "question": question,
                            "right_answer": right_answer,
                            "answers": answers
                        })
 
        except FileNotFoundError:
            self.show_file_not_found_popup(file_path)

        selected_questions = select_random_items(self.questions, COUNT_QUESTIONS)

        for question_index, question in enumerate(selected_questions):
            self.grid_content.add_widget(
                self.create_label(question["question"], halign='left')
            )
            self.grid_content.add_widget(
                self.create_dropdown_button(
                    question["answers"], question_index, question["question"])
            )

    def create_dropdown_button(self, options, question_index, question_text):
        """Создание кнопки с выпадающим меню"""
        # Создаем кнопку, которая будет открывать меню
        dropdown_button = MDFlatButton(
            text="Выберите ответ",
            size_hint_y=None,
            height=50,
            theme_text_color="Primary",
            line_color=self.theme_cls.primary_color,
            md_bg_color=self.theme_cls.primary_color,
            text_color=(1, 1, 1, 1),
        )

        selected_answers = select_random_items(options, len(options))
        
        # Создаем элементы меню
        menu_items = [
            {
                "text": option,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=option, idx=question_index, btn=dropdown_button: self.on_answer_select(btn, x, idx),
            } for option in selected_answers
        ]
        
        # Создаем меню
        menu = MDDropdownMenu(
            caller=dropdown_button,
            items=menu_items,
            max_height=300
        )

        # Сохраняем ссылку на меню
        self.dropdown_menus[question_index] = menu

        dropdown_button.bind(on_release=lambda instance: menu.open())
        
        return dropdown_button

    def on_answer_select(self, button, answer, question_index):
        """Обработчик выбора ответа"""
        # Обновляем текст кнопки
        button.text = answer
        self.spinners[question_index] = answer

        print(self.dropdown_menus)

        if self.questions[question_index]["right_answer"] == answer:
            print("Верный ответ!!!")
        
        print(f"Вопрос {question_index+1}: Выбран ответ: {answer}")
        print("Все ответы:", self.spinners)

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

    def accept_answers(self):
        """Обработчик завершения теста"""
        # Подсчет результатов
        correct_answers = 0
        total_questions = len(self.questions)
        
        for i in range(total_questions):
            if i in self.spinners and self.spinners[i] == self.questions[i]["right_answer"]:
                correct_answers += 1
        
        # Показываем результаты
        self.show_results_popup(correct_answers, total_questions)

    def show_results_popup(self, correct, total):
        """Показать результаты теста"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton
        
        percentage = (correct / total) * 100 if total > 0 else 0
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint_y=None,
            height=200
        )
        
        result_text = f"Результаты теста:\n\nПравильных ответов: {correct}/{total}\nУспеваемость: {percentage:.1f}%"
        
        result_label = MDLabel(
            text=result_text,
            halign='center',
            theme_text_color='Primary',
            size_hint_y=0.7
        )
        
        ok_button = MDRaisedButton(
            text='OK',
            size_hint_y=None,
            height=40
        )
        
        content.add_widget(result_label)
        content.add_widget(ok_button)
        
        popup = Popup(
            title='Результаты тестирования',
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()

    def clear_grid(self):
        # Закрываем все открытые меню перед очисткой
        for menu in self.dropdown_menus.values():
            if menu:
                menu.dismiss()
        self.dropdown_menus.clear()
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
        self.theme_cls.theme_style = "Light"
        
        # Дополнительные настройки
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_hue = "200"
        
        sm = MDScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(RegistrationScreen(name='registration'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    TestIMApp().run()