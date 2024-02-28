from django.db import models


class Chat(models.Model):
    user_id = models.CharField(max_length=100, unique=True)


class Game(models.Model):
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    description = models.TextField(help_text=2048, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.title)


class Message(models.Model):
    content = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f'({self.id}) {self.game_id.title}: {self.content["role"]}'
