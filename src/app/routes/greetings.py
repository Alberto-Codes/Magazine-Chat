from flask_restx import Resource

class Greetings(Resource):
    def get(self):
        return {"greeting": "Hello, world!"}