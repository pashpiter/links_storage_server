import pytest
from fastapi.testclient import TestClient
from httpx import Response
from pytest_redis import factories
from redis.client import Redis

from main import app

client = TestClient(app)
redis = factories.redisdb('redis_nooproc')


@pytest.fixture
def post_response() -> Response:
    """Фикстура POST-запрос для добавления сайтов в базу"""
    response = client.post('/visited_links', json={
        "links": [
            "https://ya.ru",
            "https://ya.ru?q=123",
            "funbox.ru",
            "https://stackoverflow.com/questions/11/how-to-exit-the-vim-editor"
        ]
    })
    response.status_code == 200
    return response


def second_post_response() -> Response:
    """POST-запрос на добавление сайтов в базу"""
    response = client.post('/visited_links', json={
        "links": [
            "google.com",
            "https://yahoo.com",
            "https://www.twitch.tv/",
            "redis.io/commands/?group=list",
            'https://funbox.ru/q/python.pdf',
            'ya.ru'
        ]
    })
    response.status_code == 200
    return response


def test_post_links(redis: Redis, post_response: Response) -> None:
    """Проверка добаления сайтов в базу"""
    assert post_response.json() == {"status": "ok"}
    assert len(redis.keys('*')) == 2
    assert redis.zcard('timings') == 1
    assert redis.llen('1') == 3

    response = second_post_response()
    assert response.json() == {"status": "ok"}
    assert len(redis.keys('*')) == 3
    assert redis.zcard('timings') == 2
    assert redis.llen('1') == 3
    assert redis.llen('2') == 6


def test_get_links(redis: Redis, post_response: Response) -> None:
    """Проверка GET-запроса и корректного колиество доменов в ответе"""
    response = client.get('/visited_domains?since=1&to=2147483648')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert len(response.json()['domains']) == 3
    assert response.json()['domains'] == ['funbox.ru',
                                          'stackoverflow.com',
                                          'ya.ru']

    response = second_post_response()
    response = client.get('/visited_domains?since=1&to=2147483648')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert len(response.json()['domains']) == 7


def test_get_links_past_time(redis: Redis, post_response: Response) -> None:
    """Проверка корректной фильтрации по водным параметрам"""
    response = client.get('/visited_domains?since=1&to=1147483648')
    assert response.status_code == 200
    assert len(response.json()['domains']) == 0


def test_get_links_err(redis: Redis) -> None:
    """Проерка ошибки при отсутствии водных параметров в GET-запросе"""
    response = client.get('/visited_domains')
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['query', 'since']
    assert response.json()['detail'][0]['msg'] == 'Field required'
    assert response.json()['detail'][1]['loc'] == ['query', 'to']
    assert response.json()['detail'][1]['msg'] == 'Field required'


def test_post_links_err(redis: Redis) -> None:
    """Проверка ошибки на POST-запрос без links"""
    response = client.post('/visited_links')
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', 'links']
    assert response.json()['detail'][0]['msg'] == 'Field required'

    response = client.post('/visited_links', json={})
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', 'links']
    assert response.json()['detail'][0]['msg'] == 'Field required'
