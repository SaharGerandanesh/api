import pytest
from flask import json
from my_app import app, db, Books, Reviews

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['TESTING'] = True

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_books(client):
    response = client.get('/books')
    assert response.status_code == 200
    assert 'books' in response.json

def test_add_books(client):
    book_data = {
        "title": "Testbok",
        "author": "Testförfattare",
        "summary": "Testsummering",
        "genre": "Testgenre"
    }
    response = client.post('/books', json=book_data)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == "Böcker tillagda framgångsrikt"

def test_manage_book(client):
    book_data = {
        "title": "Testbok",
        "author": "Testförfattare",
        "summary": "Testsummering",
        "genre": "Testgenre"
    }
    response = client.post('/books', json=book_data)
    assert response.status_code == 200

    book_id = response.json.get('book_id')

    # Testa GET /books/{book_id}
    response = client.get(f'/books/{book_id}')
    assert response.status_code == 200
    assert 'title' in response.json
    assert response.json['title'] == 'Testbok'

    # Testa PUT /books/{book_id}
    updated_data = {"title": "Uppdaterad testbok"}
    response = client.put(f'/books/{book_id}', json=updated_data)
    assert response.status_code == 200

    # Testa DELETE /books/{book_id}
    response = client.delete(f'/books/{book_id}')
    assert response.status_code == 200

def test_add_review(client):
    # Lägg till en bok i databasen för testning
    book_data = {
        "title": "Testbok",
        "author": "Testförfattare",
        "summary": "Testsummering",
        "genre": "Testgenre"
    }
    response = client.post('/books', json=book_data)
    assert response.status_code == 200

    book_id = response.json.get('book_id')

    # Testa POST /reviews
    review_data = {
        "book_id": book_id,
        "user": "Testanvändare",
        "rating": 5,
        "review_text": "Utmärkt bok!"
    }
    response = client.post('/reviews', json=review_data)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == "Recension tillagd framgångsrikt"

def test_get_reviews(client):
    response = client.get('/reviews')
    assert response.status_code == 200
    assert 'reviews' in response.json

def test_get_reviews_for_book(client):
    # Lägg till en bok i databasen för testning
    book_data = {
        "title": "Testbok",
        "author": "Testförfattare",
        "summary": "Testsummering",
        "genre": "Testgenre"
    }
    response = client.post('/books', json=book_data)
    assert response.status_code == 200

    book_id = response.json.get('book_id')

    # Testa GET /reviews/{book_id}
    response = client.get(f'/reviews/{book_id}')
    assert response.status_code == 200
    assert 'reviews' in response.json

def test_get_top_books(client):
    response = client.get('/books/top')
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == "Topplistor hämtades framgångsrikt"

def test_get_author_info(client, mocker):
    mocker.patch('requests.get', return_value=MockedResponse(status_code=200, json_data={'extract': 'Testförfattare Sammanfattning'}))
    response = client.get('/author?author_name=Testförfattare')
    assert response.status_code == 200
    assert 'author_summary' in response.json
    assert response.json['author_summary'] == "Testförfattare Sammanfattning"

class MockedResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

