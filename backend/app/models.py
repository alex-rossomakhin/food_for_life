from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()
MinValue = 1
MaxValue = 32000


class Tag(models.Model):
    """ Модель для тегов """

    name = models.CharField(
        max_length=200,
        verbose_name='Название тега'
    )

    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )

    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """ Модель для ингредиентов """

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )

    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """ Модель для рецептов """

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиент',
        through='IngredientInRecipe'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        null=True
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )

    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='app/'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )

    text = models.TextField(
        verbose_name='Текст рецепта'
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=[
            MinValueValidator(MinValue),
            MaxValueValidator(MaxValue)],
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'{self.name}.'


class IngredientInRecipe(models.Model):
    """ Модель для связи ингредиента и рецепта """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_list',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MinValue),
            MaxValueValidator(MaxValue)],
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'Связка рецепта и ингредиента'
        verbose_name_plural = 'Связка рецепта и ингредиента'

    def __str__(self):
        return ({self.ingredient.name}, {self.recipe})


class Favorite(models.Model):
    """ Модель для избранного"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт избранного'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.recipe}'


class ShoppingList(models.Model):
    """ Модель для списака покупок """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping',
        verbose_name='Рецепт покупок'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list')
        ]

    def __str__(self):
        return f'{self.recipe}'
