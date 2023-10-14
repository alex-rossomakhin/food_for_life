from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import IntegerField

from app.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.serializers import CustomUserSerializer

MinValue = 1
MaxValue = 32000


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для ингредиентов """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тегов """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.IntegerField(max_value=MaxValue,
                                            min_value=MinValue)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_tags(self, obj):
        return TagSerializer(
            obj.tags.all(),
            many=True,).data

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = request.user
        if not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = request.user
        return obj.recipe_shopping.filter(user=user).exists()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)
    amount = serializers.IntegerField(max_value=MaxValue, min_value=MinValue)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = set()
        for item in value:
            ingredient = Ingredient.objects.get(id=item['id'])
            if ingredient in ingredients:
                raise serializers.ValidationError({
                    'Ингридиенты повторятюся'})
            ingredients.add(ingredient)
        return value

    def validate_tags(self, value):
        tags = set()
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    {'Теги повторятюся'})
            tags.add(tag)
        return value

    def create_ingredients(self, ingredients, recipe):
        ingredients_list = []
        for item in ingredients:
            ingredient_id = item.get('id')
            ingredient = Ingredient.objects.get(
                id=ingredient_id)
            ingredients_list.append(
                IngredientInRecipe(
                    ingredient=ingredient,
                    amount=item.get('amount'),
                    recipe=recipe,
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance,
                                ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор для краткого вывода рецептов."""

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.Serializer):
    def validate(self, attrs):
        request = self.context['request']
        pk = self.context['pk']
        user = request.user
        if user.favorites.filter(recipe__id=pk):
            raise serializers.ValidationError('Рецепт уже добавлен!')
        return attrs


class ShoppingCartSerializer(serializers.Serializer):
    def validate(self, attrs):
        request = self.context['request']
        pk = self.context['pk']
        user = request.user
        if user.user_shopping.filter(recipe__id=pk):
            raise serializers.ValidationError('Список покупок уже добавлен!')
        return attrs
