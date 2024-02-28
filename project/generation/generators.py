from typing import Tuple, Any

from .prompt_templates import *
from .openai_api import complete
from shared.models import *


def start_game(chat_id: Chat) -> str:
    messages = [
        {"role": "system", "content": main_sys_prompt},
        {"role": "system", "content": start_game_prompt}
    ]
    response = complete(messages)

    game = Game.objects.create(
        chat_id=chat_id,
        title=response["title"],
        description=response["description"],
    )
    Message.objects.create(
        game_id=game,
        content={'role': 'system', 'content': response['description']}
    )

    return f'{response["title"]}: \n\n{response["description"]}'


def get_next_step(chat: Chat, game: Game) -> tuple[str, dict]:
    messages = \
        [{"role": "system", "content": main_sys_prompt}] + \
        [Message.objects.filter(game_id=game, content__role='system').order_by('timestamp').first().content] + \
        [
            {"role": message.content['role'], "content": str(message.content["content"])}
            for message in Message.objects.filter(game_id=game).order_by('-timestamp')[:9]
         ] + \
        [{"role": "system", "content": next_step_prompt}]
    response = complete(messages)

    Message.objects.create(
        game_id=game,
        content={'role': 'system', 'content': response['description']},
    )

    Message.objects.create(
        game_id=game,
        content={'role': 'system', 'content': response['steps']},
    )
    return response["description"], response["steps"]


def get_end_message(chat: Chat, game: Game) -> tuple[str, dict]:
    messages = \
        [{"role": "system", "content": main_sys_prompt}] + \
        [Message.objects.filter(game_id=game, content__role='system').order_by('timestamp').first().content] + \
        [
            {"role": message.content['role'], "content": str(message.content["content"])}
            for message in Message.objects.filter(game_id=game).order_by('-timestamp')[:9]
         ] + \
        [{"role": "system", "content": end_prompt}]
    response = complete(messages)

    Message.objects.create(
        game_id=game,
        content={'role': 'system', 'content': response['description']},
    )

    game.status = False
    game.save()
    return response["description"]
