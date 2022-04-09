import json
import random

import vk_api.exceptions

from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config import *
from quiz import Quiz
from DBmodule import User, Meme, Mark, get_new_meme
from photo_utils import download


def bot():
    vk = VkApi(token=token)
    users_step = {

    }

    def send_message(user_id, message, keyboard=None, attachment=None):
        return vk.method('messages.send', {'user_id': user_id,
                                           'message': message,
                                           'attachment': attachment,
                                           'keyboard': keyboard,
                                           'random_id': random.randint(1, 2147483648)})

    def delete_keyboard_from_text_message(peer_id, conversation_message_id, new_text=None):
        message = vk.method('messages.getByConversationMessageId', {'conversation_message_ids': conversation_message_id,
                                                                    'peer_id': peer_id})['items'][0]
        message_id = message['id']
        text = new_text if new_text else message['text']
        try:
            vk.method('messages.edit', {'peer_id': peer_id, 'message': text, 'message_id': message_id})
        except vk_api.exceptions.VkApiError:
            pass

    # Главная клавиатура
    keyboard_main = VkKeyboard(one_time=False)
    keyboard_main.add_button('Привет')
    keyboard_main.add_line()
    keyboard_main.add_button('Пройти тест', color=VkKeyboardColor.PRIMARY)
    keyboard_main.add_line()
    keyboard_main.add_button('Мем', color=VkKeyboardColor.POSITIVE)
    keyboard_main.add_button('Статистика', color=VkKeyboardColor.POSITIVE)
    keyboard_main.add_line()
    keyboard_main.add_button('Загрузить свой мем')
    keyboard_main = keyboard_main.get_keyboard()

    def keyboard_vote(meme_id):
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('👍🏻', color=VkKeyboardColor.POSITIVE, payload=[f"like_{meme_id}"])
        keyboard.add_button('👎🏻', color=VkKeyboardColor.NEGATIVE, payload=[f"dislike_{meme_id}"])
        return keyboard.get_keyboard()

    quiz = Quiz(vk, send_message, keyboard_main)
    longpoll = VkBotLongPoll(vk, group_id=212547314)
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_EVENT:
            user_id = event.object['user_id']
            peer_id = event.object['peer_id']

            payload = event.object.get('payload', [' '])
            if payload:
                payload = payload[0]
            event_id = event.object.get('event_id')
            conversation_message_id = event.object.get('conversation_message_id')

            if not quiz.is_user_in_quiz(user_id):
                delete_keyboard_from_text_message(peer_id, conversation_message_id)
                quiz.send_error_of_old(user_id)
                continue

            if payload == 'true':
                delete_keyboard_from_text_message(peer_id, conversation_message_id,
                                                  new_text='Правильно! Вы определенно везучи.')
                quiz.next(user_id)
            else:
                vk.method('messages.sendMessageEventAnswer',
                          {'event_id': event_id, 'user_id': user_id, 'peer_id': peer_id, 'event_data': json.dumps({
                              "type": "show_snackbar",
                              "text": "Ха-ха, не угадал!"
                          })})
            continue

        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            message = event.object['message']

            user_id = message['from_id']
            body = message['text'].lower()
            payload = message.get('payload', '').strip('["\']')
            attachments = message['attachments']

            if not User.select().where(User.vkid == user_id).exists():
                User(vkid=user_id).save()

            if payload == 'stop_test':
                quiz.delete_user(user_id)

            if 'like' in payload:
                action, meme_id = payload.split('_')
                meme_id = int(meme_id)
                user = User.select().where(User.vkid == user_id).get()
                meme = Meme.get_by_id(meme_id)
                if Mark.select().where(Mark.user == user, Mark.meme == meme).exists():
                    send_message(user_id, "Вы уже оценили данный мем ранее!")
                else:
                    if action == 'like':
                        Mark(user=user, meme=meme, is_like=True).save()
                        meme.rating += 1
                    else:
                        Mark(user=user, meme=meme, is_like=False).save()
                        meme.rating -= 1
                    meme.save()
                    send_message(user_id, 'Оценка принята!')
                continue

            if quiz.is_user_in_quiz(user_id):
                quiz.next(user_id)
            elif 'привет' == body:
                send_message(user_id, 'Привет вездекодерам!', keyboard_main)
            elif 'пройти тест' == body:
                quiz.start(user_id)
            elif 'мем' == body:
                meme = get_new_meme(user_id)
                if meme is None:
                    send_message(user_id, "Вы уже оценили все доступные мемы!")
                    continue
                upload = VkUpload(vk)
                r = upload.photo_messages(get_meme_path(meme.filename), user_id)[0]
                photo = f'photo{r["owner_id"]}_{r["id"]}'
                send_message(user_id, "Оцени мем с помощью лайка и дизлайка", attachment=photo,
                             keyboard=keyboard_vote(meme.id))
            elif 'статистика' == body:
                send_message(user_id, 'Формирую топ...')
                user = User.select().where(User.vkid == user_id).get()

                likes_me = Mark.select().where(Mark.user == user, Mark.is_like == True).count()
                dislikes_me = Mark.select().where(Mark.user == user, Mark.is_like == False).count()

                memes = [i for i in Meme.select().order_by(Meme.rating)][::-1][:9]

                top_photos = []
                upload = VkUpload(vk)
                for meme in memes:
                    r = upload.photo_messages(get_meme_path(meme.filename), user_id)[0]
                    top_photos.append(f'photo{r["owner_id"]}_{r["id"]}')

                send_message(user_id, f"Статистика:\n\nЛайков поставлено: {likes_me}\nДизлайков поставлено: {dislikes_me}",
                             attachment=','.join(top_photos))
            elif 'загрузить свой мем' == body:
                send_message(user_id, 'Отправь мем!\n\nЕсли будет отправлено в одном сообщении несколько мемов, '
                                      'то будет добавлен только первый!')
                users_step[user_id] = 'add_meme'
            elif users_step.get(user_id, '') == 'add_meme' and attachments and attachments[0]['type'] == 'photo':
                meme_photo = attachments[0]['photo']
                filename = download(meme_photo)
                Meme(filename=filename.strip(memes_folder)).save()
                send_message(user_id, 'Мем был успешно добавлен!')
            else:
                send_message(user_id, "Пользуйся командами на клавиатуре!", keyboard_main)


bot()
