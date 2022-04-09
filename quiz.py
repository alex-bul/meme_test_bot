import random

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Quiz:
    def __init__(self, vk, send_message, end_keyboard):
        self.vk = vk
        self.send_message = send_message
        self.end_keyboard = end_keyboard

        self.users_steps = {}
        self.questions = [
            self.pancakes,
            self.guess_button,
            self.is_like_live,
            self.live_place,
            self.investing,
            self.pay_or_bad_results,
            self.part_in_vezdekod,
            self.danya
        ]

    def is_user_in_quiz(self, user_id):
        return user_id in self.users_steps

    def delete_user(self, user_id):
        return self.users_steps.pop(user_id, '')

    @staticmethod
    def add_stop_button(keyboard):
        keyboard.add_line()
        keyboard.add_button('Выйти из теста', payload=['stop_test'])
        return keyboard

    def send_error(self, user_id, error_text, keyboard='default'):
        if keyboard == 'default':
            keyboard = self.end_keyboard
        self.send_message(user_id, error_text,
                          keyboard=keyboard)

    def send_error_of_old(self, user_id):
        self.send_error(user_id, "Этот тест уже устарел :(\nНачните тестирование заново!")

    def start(self, user_id):
        self.users_steps[user_id] = 0
        self.next(user_id)

    def next(self, user_id):
        try:
            step = self.users_steps[user_id]
        except KeyError:
            self.send_error_of_old(user_id)
            return
        if step < len(self.questions):
            self.questions[step](user_id)
            self.users_steps[user_id] += 1
        else:
            self.end(user_id)

    def end(self, user_id):
        results = [
            'Вы потрясяющий человек!',
            'Похоже, вы один из самых счастливых людей!',
            'Ваша жизнь гармонична и у вас всё получится!',
            'У вас точно большое будущее!',
            'Петр 1 гордился бы вами...',
            'Результатов нет. Заскамили мамонта'
        ]
        self.send_message(user_id, f'Тест окончен ❤\n\nРезультат:\n{random.choice(results)}',
                          keyboard=self.end_keyboard)
        self.delete_user(user_id)

    def is_like_live(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_openlink_button('Что такое жизнь?',
                                     link='https://ru.wikipedia.org/wiki/%D0%96%D0%B8%D0%B7%D0%BD%D1%8C')
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'Вам нравится ваша жизнь?', keyboard=keyboard)

    def live_place(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('В лесу')
        keyboard.add_button('На теплотрассе')
        keyboard.add_line()
        keyboard.add_button('Я живу не на Земле')
        keyboard.add_line()
        keyboard.add_location_button()
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'Где вы живете?', keyboard=keyboard)

    def investing(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('СБЕР', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Газпром', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Норникель')
        keyboard.add_button('Роснефть', color=VkKeyboardColor.NEGATIVE)
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'В какую компанию вы бы инвестировали?', keyboard=keyboard)

    def pay_or_bad_results(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Нет.', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Вы скамеры')
        keyboard.add_line()
        keyboard.add_vkpay_button(hash='action=transfer-to-group&group_id=212547314')
        keyboard.add_line()
        keyboard.add_button('Я заплатил', color=VkKeyboardColor.POSITIVE)
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'Хотите хорошие результаты теста? Заплатите нам. (шутка 🙃)', keyboard=keyboard)

    def part_in_vezdekod(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_vkapps_button(app_id=7543093, label='Принять участие', hash='', owner_id=197700721)
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'Участвуете в вездекоде?', keyboard=keyboard)

    def guess_button(self, user_id):
        true_button = random.randint(1, 6)

        keyboard = VkKeyboard(inline=True)
        keyboard.add_callback_button('Эта', payload=(["true"] if true_button == 1 else ["false"]))
        keyboard.add_callback_button('Эта', payload=(["true"] if true_button == 2 else ["false"]))
        keyboard.add_callback_button('Эта', payload=(["true"] if true_button == 3 else ["false"]))
        keyboard.add_line()
        keyboard.add_callback_button('Эта', payload=(["true"] if true_button == 4 else ["false"]))
        keyboard.add_callback_button('Эта', payload=(["true"] if true_button == 5 else ["false"]))
        keyboard.add_callback_button('Эта', payload=(["true"] if true_button == 6 else ["false"]))
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'Угадаете какая кнопка рабочая? 😎',
                          keyboard=keyboard)

    def pancakes(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Не есть блины', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Сгущенка')
        keyboard.add_button('Мороженное')
        keyboard.add_line()
        keyboard.add_button('Творог')
        keyboard.add_button('Сметана')
        keyboard.add_button('Варенье')
        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'С чем есть блины?', keyboard=keyboard)

    def danya(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Алексахин', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Рубцов', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Захарьев', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Расторгуев', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Затрудняюсь ответить', color=VkKeyboardColor.PRIMARY)

        keyboard = self.add_stop_button(keyboard).get_keyboard()

        self.send_message(user_id, 'Какая фамилия должна быть у Дани?', keyboard=keyboard)
