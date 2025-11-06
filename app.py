from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem

from helpers.choice_random import select_random_items


Window.size = (480, 853)

Builder.load_file('screens/start_screen.kv')
Builder.load_file('screens/main_screen.kv')
Builder.load_file('screens/registration_screen.kv')

COUNT_QUESTIONS = 4
SUBJECTS = {
    "math": "Математика", 
    "russian": "Русский язык", 
    "history": "История",
    "biology": "Биология"
    }


class StartScreen(MDScreen):
    def start_app(self):
        self.manager.current = 'registration'


class RegistrationScreen(MDScreen):
    subject = None
    subject_menu = None

    def register_user(self):
        name_field = self.ids.name_field
        surname_field = self.ids.surname_field
        class_field = self.ids.class_field        

        main_screen = self.manager.get_screen('main')
        main_screen.registered_name = name_field.text
        main_screen.registered_surname = surname_field.text
        main_screen.registered_class = class_field.text
        main_screen.registered_subject = self.subject

        if not name_field.text:
            name_field.error = True
            name_field.helper_text = "Введите имя"
        if not surname_field.text:
            surname_field.error = True
            surname_field.helper_text = "Введите фамилию"
        if not class_field.text:
            class_field.error = True
            class_field.helper_text = "Введите класс, например 5а"
        if self.subject is None:
            self.ids.err_sub.error = True
            self.ids.helper_text = "Выберите предмет"
        if (name_field.text and surname_field.text and class_field.text and self.subject is not None):
            name_field.error = False
            surname_field.error = False
            class_field.error = False
            self.ids.err_sub.error = False

            self.manager.current = 'main'


    def menu_subjects(self):
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=subject, name=name: self.menu_callback(x, name),
            } for subject, name in SUBJECTS.items()
        ]
        self.subject_menu = MDDropdownMenu(
            caller=self.ids.button, items=menu_items
        )
        self.subject_menu.open()

    def menu_callback(self, text_item, name):
        self.ids.button.text = name
        self.subject = text_item

        if self.subject:
            self.subject_menu.dismiss()


class MainScreen(MDScreen):

    grid_content = ObjectProperty(None)
    user_answers = {}
    questions = {}
    dropdown_menus = {}
    selected_questions = []

    subject = None

    def on_enter(self):
        self.user_answers = {}
        self.questions = {}
        self.dropdown_menus = {}
        self.selected_questions = []

        if self.registered_name and self.registered_subject:
            self.ids.user.text = (
                f"{self.registered_name} {self.registered_surname} {self.registered_class}"
                )
            self.ids.subject.text = SUBJECTS[self.registered_subject]
            print(self.registered_subject)
            self.subject = self.registered_subject

        button = self.ids.questions_button
        button.text = 'Завершить'

        self.clear_grid()

        file_path = f'questions/{self.subject}.txt'
        print(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for i, line in enumerate(file):
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        question = parts[0]
                        right_answer = parts[1]
                        answers = parts[1:]

                        self.questions[i] = {
                            "question": question,
                            "right_answer": right_answer,
                            "answers": answers
                        }
 
        except FileNotFoundError:
            self.show_file_not_found_popup(file_path)

        self.selected_questions = select_random_items(list(self.questions.keys()), COUNT_QUESTIONS)

        for question in self.selected_questions:
            self.grid_content.add_widget(
                self.create_label(self.questions[question]["question"], halign='left')
            )
            self.grid_content.add_widget(
                self.create_dropdown_button(
                    self.questions[question]["answers"], question, self.questions[question]["question"])
            )

    def create_dropdown_button(self, options, question_index, question_text):

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
        
        menu_items = [
            {
                "text": option,
                # "viewclass": "OneLineListItem",
                "on_release": lambda x=option, idx=question_index, btn=dropdown_button: self.on_answer_select(btn, x, idx),
            } for option in selected_answers
        ]
        
        menu = MDDropdownMenu(
            caller=dropdown_button,
            items=menu_items,
            max_height=300
        )

        self.dropdown_menus[question_index] = menu

        dropdown_button.bind(on_release=lambda instance: menu.open())
        
        return dropdown_button

    def on_answer_select(self, button, answer, question_index):
        button.text = answer
        self.user_answers[question_index] = answer

        if self.dropdown_menus[question_index]:
            self.dropdown_menus[question_index].dismiss()

        if self.questions[question_index]["right_answer"] == answer:
            print("Верный ответ!!!")
        
        print(f"Вопрос {question_index+1}: Выбран ответ: {answer}")

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

        correct_answers = 0
        
        for i in self.selected_questions:
            if i in self.user_answers and self.user_answers[i] == self.questions[i]["right_answer"]:
                correct_answers += 1

        if len(self.selected_questions) < COUNT_QUESTIONS:
            self.show_results_popup(correct_answers, len(self.selected_questions))  
        else:          
            self.show_results_popup(correct_answers, COUNT_QUESTIONS)

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
        
        for menu in self.dropdown_menus.values():
            if menu:
                menu.dismiss()
        self.dropdown_menus.clear()
        self.ids.grid_layout.clear_widgets()
    
    def exit_app(self):
        MDApp.get_running_app().stop()


class TestIMApp(MDApp):
    questions = []

    def build(self):
        # Цветовая схема
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Brown"
        # 'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 
        # 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 
        # 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray'
        
        # Стиль темы
        self.theme_cls.theme_style = "Dark"
        
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