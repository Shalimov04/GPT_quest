from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from generation.generators import *
from shared.models import Chat

import os
import telebot

TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
bot = telebot.TeleBot(TG_BOT_TOKEN)


class BotView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return HttpResponse("")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        chat, created = Chat.objects.get_or_create(user_id=str(message.chat.id))
        if not Game.objects.filter(status=True, chat_id=chat).exists():
            m = bot.reply_to(message, start_game(chat))
            game = Game.objects.get(chat_id=chat, status=True)
            description, steps = get_next_step(chat, game)

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                telebot.types.InlineKeyboardButton(text=text, callback_data=str(i))
                for i, text in enumerate(steps.keys())
            ]
            keyboard.add(*buttons)

            bot.reply_to(m, description, reply_markup=keyboard)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data in ['1', '2', '3', '4', '0'])
def step(call):
    message = call.message
    chat_id = str(message.chat.id)
    chat = Chat.objects.get(user_id=chat_id)
    option = int(call.data)
    game = Game.objects.filter(chat_id=chat, status=True).first()
    choice, type = list(Message.objects.filter(game_id=game, content__role='system').order_by('-timestamp').first()
                        .content['content'].items())[option]
    print(choice, type)
    if type == 'pass':
        Message.objects.create(
            game_id=game,
            content={'role': 'user', 'content': choice},
        )
        description, steps = get_next_step(chat, game)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            telebot.types.InlineKeyboardButton(text=text, callback_data=str(i))
            for i, text in enumerate(steps.keys())
        ]
        keyboard.add(*buttons)
        bot.reply_to(message, description, reply_markup=keyboard)
    else:
        bot.reply_to(message, get_end_message(chat, game) + '\n\n /start для новой игры')
