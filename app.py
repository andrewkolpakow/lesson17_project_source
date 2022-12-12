# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int() #???
    director_id = fields.Int()
'''Создали класс для сериализации данных о фильме'''


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()
'''Создали класс для сериализации данных о режиссере'''


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()
'''Создали класс для сериализации данных о жанре'''

api = Api(app)
'''Регистрируем api'''
movies_ns = api.namespace('/movies')
directors_ns = api.namespace('/directors')
genres_ns = api.namespace('/genres')
'''Создаем неймспейсы для отображения в класс View'''

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
'''Создаем экземпляры схем сериализации'''


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)
        '''Создаем view для метода GET и получения всех фильмов'''

        director_id = request.args.get("director_id")
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)
        '''Получаем все фильмы определенного режиссера по запросу /?director_id=x'''

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)
        '''Получаем все фильмы определенного режиссера по запросу /?genre_id=x'''

        return movies_schema.dump(all_movies.all()), 200
        '''Через схему сериализации возвращаем json с фильмами'''

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)
        '''Открываем сессию с БД, добавляем фильм'''

        return 'Movie added', 201

@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "Movie not found", 404
        else:
            return movie_schema.dump(movie), 200
        '''View для получения фильма по uid'''

    def put(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        request_json = request.json

        movie.id = request_json.get("id")
        movie.title = request_json.get("title")
        movie.description = request_json.get("description")
        movie.trailer = request_json.get("trailer")
        movie.year = request_json.get("year")
        movie.rating = request_json.get("raitin")
        movie.genre_id = request_json.get("genre_id")
        movie.genre = request_json.get("genre")
        movie.director_id = request_json.get("director_id")
        movie.director = request_json.get("director")

        db.session.add(movie)
        db.session.commit()

        return "Movie updated", 204

    def delete(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "Movie not found", 404
        db.session.delete(movie)
        db.session.commit()
        return "Movie deleted", 204

@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200
    '''Создаем View для получения всех режиссеров методом GET'''

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        with db.session.begin():
            db.session.add(new_director)
        '''Открываем сессию с БД, добавляем фильм'''

        return 'Director added', 201

@directors_ns.route("/<int:uid>")
class DirectorView(Resource):
    def get(self, uid:int):
        try:
            director = db.session.query(Director).get(uid)
            return director_schema.dump(director), 200
        except Exception:
            return str(Exception), 404
    '''Создаем view для получения режиссера по ID, метод GET'''


    def put(self, uid:int):
        director = Director.query.get(uid)
        request_json = request.json
        if "name" in request_json:
            director.name = request_json.get("name")
        db.session.add(director)
        db.session.commit()

        return "Director updated", 204
    '''Создаем view для обновления данных о режиссере'''

    def delete(self, uid: int):
        director = db.session.query(Director).get(uid)
        if not director:
            return "Director not found", 404
        db.session.delete(director)
        db.session.commit()
        return 'Director deleted', 204
    '''Создаем view для удаления режиссера'''


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return directors_schema.dump(all_genres), 200

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)
        '''Открываем сессию с БД, добавляем жанр'''

        return 'Genre added', 201


if __name__ == '__main__':
    app.run(debug=True)
