from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

# api.add_resource(Asset, '/asset/<string:ticker>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
