from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.filters import RecipeFilter
from app.models import (Favorite, Ingredient,
                        IngredientInRecipe, Recipe,
                        ShoppingList, Tag)
from app.permission import IsAuthorOrReadOnly, IsAdminOrReadOnly
from app.serializers import (TagSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeCreateSerializer,
                             ShortRecipeSerializer, FavoriteSerializer,
                             ShoppingCartSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """ Отображение тегов """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ Отображение ингредиентов """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Отображение и создание рецептов """
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            serializers = FavoriteSerializer(data=request.data,
                                             context={'request': request,
                                                      'pk': pk})
            if serializers.is_valid(raise_exception=True):
                recipe = get_object_or_404(Recipe, id=pk)
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializers = ShortRecipeSerializer(recipe)
                return Response(
                    {'message': 'Рецепт добавлен в избранное.',
                     'data': serializers.data},
                    status=status.HTTP_201_CREATED
                )
        get_object_or_404(
            Favorite, user=self.request.user,
            recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(
            {'message': 'Рецепт успешно удален из избранного'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            serializers = ShoppingCartSerializer(data=request.data,
                                                 context={'request': request,
                                                          'pk': pk})
            if serializers.is_valid(raise_exception=True):
                recipe = get_object_or_404(Recipe, id=pk)
                ShoppingList.objects.create(user=request.user, recipe=recipe)
                serializers = ShortRecipeSerializer(recipe)
                return Response(
                    {'message': 'Список покупок добавлен.',
                     'data': serializers.data},
                    status=status.HTTP_201_CREATED
                )
        get_object_or_404(
            ShoppingList, user=self.request.user,
            recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(
            {'message': 'Список покупок удален'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipe = (ShoppingList.objects.filter(user=user)).values_list('recipe')
        recipe = IngredientInRecipe.objects.filter(recipe__in=recipe).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount'))
        shopping_cart_list = ''
        for value in recipe:
            shopping_cart_list += (f"{value['ingredient__name']}"
                                   f"({value['ingredient__measurement_unit']})"
                                   f" - {value['amount']}\n")

        response = HttpResponse(shopping_cart_list, headers={
            'Content-Type': 'text/plain',
            'Content-Disposition':
            'attachment; filename="shopping_cart_list.txt"'})
        return response
