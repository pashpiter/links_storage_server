# links_storage_server

##### Стек: Python, FastAPI, Redis, pytest
***

### Что умеет links_storage_server
Web-приложение для хранения посещенных ссылок

* Добаление посещенных ссылок (время посещения ссылки = время добаления в базу)
* Получение списка уникальных доменов за определнный период

***
### Запуск проекта

Для запуска проекта необходимо: 
* Клонировать репозиторий
```
git clone git@github.com:pashpiter/links_storage_server.git
```
* Запустить [Redis](https://redis.io/docs/getting-started/), команда для Docker
```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```
* Перейти в папку links_storage_server
* Создать виртуальное окружение
```
python3 -m venv venv
```
* Активировать виртуальное окружение

на macOS и Ubuntu
```
source venv/bin/activate
```
на Windows
```
source venv/Scripts/activate.bat
```
* Установить зависимости
```
pip install -r requirements.txt
```
* Запустить проект
```
python main.py
```
***
Проект покрыт тестами, команда для запуска тестов:
```
pytest
```

### Примеры команд API

* Добавление сайтов 
```
POST http://localhost:8000/visited_links
{
    "links": [
        "https://ya.ru",
        "rbc.ru",
        "https://fastapi.tiangolo.com/tutorial/testing/"
    ]
}
```
```
curl -X POST "http://localhost:8000/visited_links" \
  -H "Content-type: application/json" \
  -d '{"links":["https://ya.ru", "rbc.ru", "https://fastapi.tiangolo.com/tutorial/testing/"]}'
```

* Получение списка уникальных доменов, посещенных за переданный интервал времени
```
GET http://localhost:8000/visited_domains?since=1&to=2145217638
```
```
curl -X GET "http://localhost:8000/visited_domains?since=1&to=2145217638"
```
