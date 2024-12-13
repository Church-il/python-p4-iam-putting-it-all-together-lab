# server/app.py
#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            if not username or not password:
                return {"error": "Invalid input"}, 422

            user = User(
                username=username,
                bio=data.get('bio', '').strip(),
                image_url=data.get('image_url', '').strip()
            )
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already exists."}, 422
        except Exception as e:
            return {"error": str(e)}, 400

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get(user_id)
        if user:
            return user.to_dict(), 200
        return {"error": "User not found"}, 404

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return {"error": "Invalid input"}, 400

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid credentials"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return '', 204
        return {"error": "Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        title = data.get('title', '').strip()
        instructions = data.get('instructions', '').strip()
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or minutes_to_complete is None:
            return {"error": "Invalid input"}, 422

        if len(instructions) < 50:
            return {"error": "Instructions must be at least 50 characters long."}, 422

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Recipe with this title already exists."}, 422
        except Exception as e:
            return {"error": str(e)}, 400


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
