import unittest
from flask import json
from my_app import app, db, Books, Reviews

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_book_reviews.db'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_books(self):
        # Test GET /books
        response = self.app.get('/books')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('books', data)

    def test_add_books(self):
        # Test POST /books
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "summary": "Test Summary",
            "genre": "Test Genre"
        }

        response = self.app.post('/books', json=book_data)
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Books added successfully')

    def test_manage_book(self):
        # Test GET /books/{book_id}
        book = Books(title="Test Book", author="Test Author", genre="Test Genre")
        db.session.add(book)
        db.session.commit()

        response = self.app.get(f'/books/{book.id}')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('title', data)
        self.assertEqual(data['title'], 'Test Book')

        # Test PUT /books/{book_id}
        updated_data = {"title": "Updated Test Book"}
        response = self.app.put(f'/books/{book.id}', json=updated_data)
        updated_book = Books.query.get(book.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_book.title, 'Updated Test Book')

        # Test DELETE /books/{book_id}
        response = self.app.delete(f'/books/{book.id}')
        deleted_book = Books.query.get(book.id)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(deleted_book)

    def test_add_review(self):
        # Test POST /reviews
        book = Books(title="Test Book", author="Test Author", genre="Test Genre")
        db.session.add(book)
        db.session.commit()

        review_data = {
            "book_id": book.id,
            "user": "Test User",
            "rating": 5,
            "review_text": "Excellent book!"
        }

        response = self.app.post('/reviews', json=review_data)
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Review added successfully')

    def test_get_reviews(self):
        # Test GET /reviews
        response = self.app.get('/reviews')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('reviews', data)

    def test_get_reviews_for_book(self):
        # Test GET /reviews/{book_id}
        book = Books(title="Test Book", author="Test Author", genre="Test Genre")
        db.session.add(book)
        db.session.commit()

        response = self.app.get(f'/reviews/{book.id}')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('reviews', data)

    def test_get_top_books(self):
        # Test GET /books/top
        response = self.app.get('/books/top')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Top books retrieved successfully')

    def test_get_author_info(self):
        # Test GET /author
        response = self.app.get('/author?author_name=TestAuthor')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertIn('author_summary', data)

if __name__ == '__main__':
    unittest.main()
