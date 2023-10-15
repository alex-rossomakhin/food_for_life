from django.contrib import admin
from app.models import Ingredient, IngredientInRecipe, Recipe, Tag


class TegAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class IngredientRecipe(admin.TabularInline):
    model = IngredientInRecipe
    extra = 3
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipe, ]
    list_display = ('author', 'name', 'cooking_time', 'ingredient')
    search_fields = ('name', 'author', 'tags')


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
