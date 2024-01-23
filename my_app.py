from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import json
from functools import wraps
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_reviews.db'
db = SQLAlchemy(app)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    genre = db.Column(db.String(255), nullable=True)

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    review_text = db.Column(db.Text, nullable=True)

# Funktion för att hämta data från databasen och strukturera den
def fetch_data_from_db():
    books = Books.query.outerjoin(Reviews).all()
    
    books_data = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "summary": book.summary,
            "genre": book.genre,
            "reviews": [{"id": review.id, "user": review.user, "rating": review.rating, "review_text": review.review_text} for review in book.reviews]
        }
        books_data.append(book_data)

    return books_data

# Funktion för att spara data till en JSON-fil
def save_to_json(data):
    with open('request.json', 'w') as json_file:
        json_file.write(json.dumps(data, indent=4))

# Dekorator för att skriva ut SQL-query vid varje anrop till en funktion
def print_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        query = str(db.session.query(Books))
        print(f"Executing query: {query}")
        return result

    return wrapper

# Krav: GET /books - Hämtar alla böcker i databasen.
@app.route('/books', methods=['GET'])
@print_query
def get_books():
    search_query = request.args.get('genre')
    if search_query:
        books = Books.query.filter_by(genre=search_query).all()
    else:
        books = Books.query.all()

    return jsonify({"books": [{"id": book.id, "title": book.title, "author": book.author, "summary": book.summary, "genre": book.genre} for book in books]})

# Krav: POST /books - Lägger till en eller flera böcker i databasen.
@app.route('/books', methods=['POST'])
@print_query
def add_books():
    data = request.json
    new_book = Books(**data)
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Books added successfully"})

# Krav: GET /books/{book_id} - Hämtar en enskild bok.
# Krav: PUT /books/{book_id} - Uppdaterar information om en enskild bok.
# Krav: DELETE /books/{book_id} - Tar bort en enskild bok
@app.route('/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
@print_query
def manage_book(book_id):
    book = Books.query.get_or_404(book_id)

    if request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            setattr(book, key, value)
        db.session.commit()

    elif request.method == 'DELETE':
        db.session.delete(book)
        db.session.commit()

    return jsonify({"message": "Operation successful"})

# Krav: POST /reviews - Lägger till en ny recension till en bok.
@app.route('/reviews', methods=['POST'])
@print_query
def add_review():
    data = request.json
    new_review = Reviews(**data)
    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message": "Review added successfully"})

# Krav: GET /reviews - Hämtar alla recensioner som finns i databasen
@app.route('/reviews', methods=['GET'])
@print_query
def get_reviews():
    reviews = Reviews.query.all()
    return jsonify({"reviews": [{"id": review.id, "user": review.user, "rating": review.rating, "review_text": review.review_text} for review in reviews]})

# Krav: GET /reviews/{book_id} - Hämtar alla recensioner för en enskild bok.
@app.route('/reviews/<int:book_id>', methods=['GET'])
@print_query
def get_reviews_for_book(book_id):
    reviews = Reviews.query.filter_by(book_id=book_id).all()
    return jsonify({"reviews": [{"id": review.id, "user": review.user, "rating": review.rating, "review_text": review.review_text} for review in reviews]})

# Krav: GET /books/top - Hämtar de fem böckerna med högst genomsnittliga recensioner.
@app.route('/books/top', methods=['GET'])
@print_query
def get_top_books():
    # Implementera logiken för att hämta de fem böckerna med högst genomsnittliga recensioner här.
    return jsonify({"message": "Top books retrieved successfully"})

# Krav: GET /author - Hämtar en kort sammanfattning om författaren och författarens mest kända verk.
@app.route('/author', methods=['GET'])
def get_author_info():
    author_name = request.args.get('author_name')

    if not author_name:
        abort(400, "Missing author_name parameter")

    # Krav: Ett externt API för att hämta författarens korta sammanfattning
    summary_url = f'https://book/rest_v1/page/summary/{author_name}'
    summary_response = requests.get(summary_url)

    if summary_response.status_code != 200:
        abort(500, f"Failed to retrieve author summary from Wikipedia API. Status code: {summary_response.status_code}")

    author_summary = summary_response.json().get('extract', '')
    print(f"Author Summary: {author_summary}")

    return jsonify({"author_summary": author_summary})

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
