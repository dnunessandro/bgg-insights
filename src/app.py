from flask import Flask, request
from json import loads
from flask_restful import Resource, Api, reqparse
import requests
from classes.collection import Collection
from utils import getCurveFit, getBestCurveFit


# Config (TEMP)
API_ROOT_URL = 'http://localhost:3000'

app = Flask(__name__)
api = Api(app)


class InsightsPost(Resource):
    def post(self, type):
        try:
            collection = Collection(request.get_json())
        except:
            return {'error': 'Collection could not be parsed.'}, 500

        if type == 'all':
            response = collection.genAllInsights()
        else:
            response = collection.genInsight(type).data
        return response, 200


class InsightsGet(Resource):
    def get(self, id, type):
        response = requests.get(
            '{}/collections/{}/enrich?filter=boardgames,plays'.format(API_ROOT_URL, id))

        collection = Collection(loads(response.content))

        if type == 'all':
            insights = collection.genAllInsights()
        else:
            insights = collection.genInsight(type).data
        return insights, 200


class PolyFit(Resource):
    def post(self):

        try:
            args = request.args
            fitDomainMin = args['min']
            fitDomainMax = args['max']
            if 'polyparams' in args.keys():
                polyParams = [int(x) for x in args['polyparams'].split(',')]
            else:
                polyParams = [0,0,0,0,1]
            
            requestBody = request.get_json()
            x = requestBody['x']
            y = requestBody['y']
            fitObj = getCurveFit(x, y, fitDomainMin, fitDomainMax, polyParams)
            return fitObj, 200
        except:
            return {'error': 'Could not compute fit curve'}, 500

class BestPolyFit(Resource):
        def post(self):

            # try:
            args = request.args
            fitDomainMin = args['min']
            fitDomainMax = args['max']
            
            requestBody = request.get_json()
            x = requestBody['x']
            y = requestBody['y']
            
            fitObject = getBestCurveFit(x, y, fitDomainMin, fitDomainMax)
            
            return fitObject, 200
            # except e:
            #     print(e)
            #     return {'error': 'Could not compute fit curve'}, 500


api.add_resource(InsightsPost, '/insights/<string:type>')
api.add_resource(InsightsGet, '/insights/<string:id>/<string:type>')
api.add_resource(PolyFit, '/utils/fit')
api.add_resource(BestPolyFit, '/utils/bestfit')

if __name__ == '__main__':
    app.run(debug=True)
