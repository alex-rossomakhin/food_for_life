from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Subscriptions, User
from users.serializers import SubscriptionsSerializer


class CustomUserViewSet(UserViewSet):
    """ Отображение тегов """
    queryset = User.objects.all()
    serializer_class = SubscriptionsSerializer
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(author,
                                                 data=request.data,
                                                 context={'request': request,
                                                          'author': author})
            if serializer.is_valid(raise_exception=True):
                Subscriptions.objects.create(user=user, author=author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscriptions, user=self.request.user,
            author=author_id).delete()
        return Response(
            {'message': ' Подписка удалена '},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        user = request.user
        users = User.objects.filter(author__user=user)
        pages = self.paginate_queryset(users)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
