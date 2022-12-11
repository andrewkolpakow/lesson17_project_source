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

if __name__ == '__main__':
    app.run(debug=True)
