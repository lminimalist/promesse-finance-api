from flask import Flask
from flask_restful import Api
import db.mongoengine
from resources.asset.history import AssetHistory

app = Flask(__name__)
api = Api(app)

api.add_resource(AssetHistory, '/asset/<string:ticker>/history')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
