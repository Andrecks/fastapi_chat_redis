# fastapi_chat_redis
Чат для двух или нескольких пользователей

В репозитории имеется файл docker-compose
После клонирования выполнить команду "docker-compose up" в директории проекта. 
После успешного выполнения чат будет доступен по адресу локального хоста http://localhost:8000/
После ввода никнейма на странице логина он будет сохранен в cookie и после обновления страницы чата будет от туда же парситься.
Все сообщения храняться в отдельном контейнере redis.

Фичи: 
  • Сохранение ника
  • Хранение истории чата (10 последний сообщений)
  • Отображение списка онлайн участников чата
  • Отправка емодзи

возможные улучшения и доработки:
  • Внешний вид проекта 😅

