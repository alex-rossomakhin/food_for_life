from django_filters import rest_framework as filters

from app.models import Recipe


class RecipeFilter(filters.FilterSet):
    """ Фильтры для страницы рецепта"""

    author = filters.CharFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(
        method='favorite')
    is_in_shopping_cart = filters.NumberFilter(
        method='shopping_cart')
    tags = filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart', 'tags']

    def favorite(self, queryset, name, value):
        return queryset.filter(favorites__user=self.request.user)

    def shopping_cart(self, queryset, name, value):
        return queryset.filter(recipe_shopping__user=self.request.user)
