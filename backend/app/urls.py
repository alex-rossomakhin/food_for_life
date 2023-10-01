from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls))
]
