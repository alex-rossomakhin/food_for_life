from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Subscriptions(models.Model):
    """ Модель  для подписок """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта',
        null=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписка на автора'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user}, {self.author}'
