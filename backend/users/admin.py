from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'id',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    search_fields = ('email', 'username')
