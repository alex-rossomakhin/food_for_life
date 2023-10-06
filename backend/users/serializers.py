from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from app.models import Recipe
from users.models import Subscriptions

User = get_user_model()


class CustomCreateUserSerializer(UserCreateSerializer):
    """Сериализатор регистрации юзера"""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
        read_only_fields = ('id',)


class CustomUserSerializer(UserSerializer):
    """Сериализатор отображения юзера"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        return (obj.author.filter(user=user)).exists()


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
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


class SubscriptionsSerializer(CustomUserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (CustomUserSerializer.Meta.fields
                  + ('recipes', 'recipes_count'))
        read_only_fields = ('email', 'username')

    def validate(self, attrs):
        author = self.context['author']
        request = self.context['request']
        user = request.user
        if author == user:
            raise serializers.ValidationError(
                    'Нельзя подписаться на себя!')
        if Subscriptions.objects.filter(user=user, author=author):
            raise serializers.ValidationError('Подписка уже создана')
        return attrs

    def get_recipes(self, obj):
        request = self.context['request']
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            recipes = recipes[:recipes_limit]
        serializer = SubscriptionsRecipeSerializer(
            recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = obj.recipes.all()
        return recipes.count()
