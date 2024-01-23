import sqlite3
import json

def fetch_data_from_db():
    connection = sqlite3.connect('book_reviews.db')
    cursor = connection.cursor()

    # Hämta data från "books" och "reviews" tabellerna
    cursor.execute('SELECT * FROM books')
    books_data = cursor.fetchall()

    cursor.execute('SELECT * FROM reviews')
    reviews_data = cursor.fetchall()

    connection.close()

    return {'books': books_data, 'reviews': reviews_data}

def save_to_json(data):
    with open('request.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    # Hämta data från både "books" och "reviews" tabellerna
    book_reviews_data = fetch_data_from_db()

    # Spara data till JSON-filen
    save_to_json(book_reviews_data)