# Food for life - сервис для публикации рецептов
## Описание
Онлайн-сервис Food for life и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Доступный функционал
Аутентификация реализована с помощью стандартного модуля DRF - Authtoken.
У неаутентифицированных пользователей доступ к API только на уровне чтения.
Создание объектов разрешено только зарегистрированным пользователям.
Управление пользователями.
Возможность получения подробной информации о себе и ее редактирование.
Возможность подписаться на других пользователей и отписаться от них.
Получение списка всех тегов и ингредиентов.
Получение списка всех рецептов, их добавление.Получение, обновление и удаление конкретного рецепта.
Возможность добавить рецепт в избранное.
Возможность добавить рецепт в список покупок.
Возможность скачать список покупок в PDF формате.
Фильтрация по полям.
## Технологи
• Python 3.9
• Django 3.2.6
• Django Rest Framework 3.12.4
• Authtoken
• Docker
• Docker-compose
• PostgreSQL
• Gunicorn
• Nginx
• GitHub Actions
