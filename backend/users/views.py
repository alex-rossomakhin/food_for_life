from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User, Subscriptions
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
            if author == user:
                return Response({'errors': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Subscriptions.objects.filter(user=user, author=author):
                return Response({'errors': 'Подписка уже создана'},
                                status=status.HTTP_400_BAD_REQUEST)
            Subscriptions.objects.create(user=user, author=author)
            serializer = SubscriptionsSerializer(author,
                                                 data=request.data,
                                                 context={"request": request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            get_object_or_404(
                Subscriptions, user=self.request.user,
                author=author_id).delete()
            return Response(
                {'message': ' Подписка удалена '},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = (Subscriptions.objects.filter(
            user=user)).values_list("author")
        users = User.objects.filter(pk__in=subscriptions)
        serializer = SubscriptionsSerializer(
            users, many=True, context={"request": request})
        return Response(serializer.data)
