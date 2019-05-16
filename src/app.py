from flask import Flask
from flask_restful import Api
import db.mongoengine
from resources.asset.history import AssetHistory
from resources.asset.returns import AssetReturns

app = Flask(__name__)
api = Api(app)

api.add_resource(AssetHistory, '/asset/<string:ticker>/history')
api.add_resource(AssetReturns, '/asset/<string:ticker>/returns')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
