# server/models.py
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)
    image_url = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user', lazy=True)

    serialize_rules = ('-recipes.user',)

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be accessed directly.')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates('username')
    def validate_username(self, key, value):
        if not value:
            raise ValueError("Username is required.")
        return value

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self, key, value):
        if not value:
            raise ValueError("Title is required.")
        return value

    @validates('instructions')
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value

    @validates('minutes_to_complete')
    def validate_minutes_to_complete(self, key, value):
        if value is None or value < 1:
            raise ValueError("Minutes to complete must be a positive integer.")
        return value
