from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from redis import StrictRedis

import main

HOST = 'localhost'
PORT = 6379
DB = 10

sr = StrictRedis(host=HOST, port=PORT, db=DB)
client = TestClient(main.app)


@pytest.fixture
@patch('main.connection')
def post_response(mock_conn: Mock) -> Response:
    """Фикстура POST-запрос для добавления сайтов в базу"""
    mock_conn.return_value = sr
    sr.flushdb()
    response = client.post('/visited_links', json={
        "links": [
            "https://ya.ru",
            "https://ya.ru?q=123",
            "funbox.ru",
            "https://stackoverflow.com/questions/11/how-to-exit-the-vim-editor"
        ]
    })
    return response


@patch('main.connection')
def second_post_response(mock_conn: Mock) -> Response:
    """POST-запрос на добавление сайтов в базу"""
    mock_conn.return_value = sr
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
    return response


@patch('main.connection')
def test_post_links(mock_conn: Mock, post_response: Response) -> None:
    """Проверка добаления сайтов в базу"""
    mock_conn.return_value = sr
    print(type(mock_conn))

    assert post_response.status_code == 201
    assert post_response.json() == {"status": "ok"}
    assert len(sr.keys('*')) == 2
    assert sr.zcard('timings') == 1
    assert sr.llen('1') == 3

    response = second_post_response()
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}
    assert len(sr.keys('*')) == 3
    assert sr.zcard('timings') == 2
    assert sr.llen('1') == 3
    assert sr.llen('2') == 6


@patch('main.connection')
def test_get_links(mock_conn: Mock, post_response: Response) -> None:
    """Проверка GET-запроса и корректного колиество доменов в ответе"""
    mock_conn.return_value = sr

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
    sr.flushdb()


@patch('main.connection')
def test_get_links_past_time(mock_conn: Mock, post_response: Response) -> None:
    """Проверка корректной фильтрации по водным параметрам"""
    mock_conn.return_value = sr

    response = client.get('/visited_domains?since=1&to=1147483648')
    assert response.status_code == 200
    assert len(response.json()['domains']) == 0


@patch('main.connection')
def test_get_links_err(mock_conn: Mock) -> None:
    """Проерка ошибки при отсутствии водных параметров в GET-запросе"""
    mock_conn.return_value = sr

    response = client.get('/visited_domains')
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['query', 'since']
    assert response.json()['detail'][0]['msg'] == 'Field required'
    assert response.json()['detail'][1]['loc'] == ['query', 'to']
    assert response.json()['detail'][1]['msg'] == 'Field required'


@patch('main.connection')
def test_post_links_err(mock_conn: Mock) -> None:
    """Проверка ошибки на POST-запрос без links"""
    mock_conn.return_value = sr

    response = client.post('/visited_links')
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', 'links']
    assert response.json()['detail'][0]['msg'] == 'Field required'

    response = client.post('/visited_links', json={})
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', 'links']
    assert response.json()['detail'][0]['msg'] == 'Field required'
