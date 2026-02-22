from flask import Flask, request, make_response
from flask_restful import Api, Resource, abort, reqparse
from functools import wraps

app = Flask(__name__)
api = Api(app)

BOOKS = {
    "book_1": {"title": "Harry Potter", "author": "J. K. Rowling", "year": "1999"},
    "book_2": {"title": "Lord of the Rings", "author": "J. R. R. Tolkien", "year": "1947"},
    "book_3": {"title": "In Search of Lost Time", "author": "Marcel Proust", "year": "1929"},
    "book_4": {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": "1951"},
    "book_5": {"title": "Moby Dick", "author": "Herman Melville", "year": "1909"},
}


def login_required(event):
    @wraps(event)
    def login(*args, **kwargs):
        if request.authorization and \
                request.authorization.username == "admin" and \
                request.authorization.password == "test1234":
            return event(*args, **kwargs)

        return make_response("Could not verify your credentials.", 401, {'WWW-Authenticate': 'Basic realm="Login Realm"'})
    return login


parser = reqparse.RequestParser()
parser.add_argument("title")
parser.add_argument("author")
parser.add_argument("year")

def abort_book_does_not_exist(book_id):
    if book_id not in BOOKS:
        abort(404, message="Book {} does not exist.".format(book_id))

class Book(Resource):
    @login_required
    def get(self, book_id):
        abort_book_does_not_exist(book_id)
        return BOOKS[book_id]


    def delete(self, book_id):
        abort_book_does_not_exist(book_id)
        del BOOKS[book_id]
        return "", 204

    def put(self, book_id):
        args=parser.parse_args()
        book_info = {"title": args["title"], "author": args["author"], "year": args["year"]}
        BOOKS[book_id] = book_info
        return book_info, 201

class BookList(Resource):
    def get(self):
        return BOOKS

    def post(self):
        args = parser.parse_args()

        current_book_id = 0

        if len(BOOKS)>0:
            for book in BOOKS:
                x = int(book.split("_")[-1])
                if x > current_book_id:
                    current_book_id=x

        BOOKS[f"book_{current_book_id + 1}"] = {"title": args["title"], "author": args["author"], "year": args["year"]}
        return BOOKS[f"book_{current_book_id + 1}"], 201



api.add_resource(Book, '/books/<book_id>')
api.add_resource(BookList, "/books")

# def hello():
#     return 'Hello World!'

if __name__ == '__main__':

    app.run(host=0.0.0.0, port=10000, debug=True)


