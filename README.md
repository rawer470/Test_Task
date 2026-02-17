 Запустить проект
docker-compose up --build


Создать суперпользователя

docker-compose exec web python manage.py createsuperuser
username, email (можно пропустить), password.



Открыть в браузере

http://localhost:8000/admin/
Войти с теми данными, которые ввели

