#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 15:16:24 2017

@author: tony
"""

import logmodel
import nonlinear

from flask import Flask
from flask_restful import Resource, Api
from flask_restful.utils import cors
from flask import jsonify
from collections import OrderedDict

app = Flask(__name__)
api = Api(app)

# for log model
class HCG(Resource):
    @cors.crossdomain(origin='*')
    def get(self, id):
        weeks_str = []
        weeks = list(logmodel.getHcgValues(id)[0])
        for week in weeks:
            weeks_str.append(str(week))

        hcgs = list(logmodel.getHcgValues(id)[1])
        relative_error = round(logmodel.getHcgValues(id)[2], 2)

        hcg_int = [round(x) for x in hcgs]
        res = OrderedDict(zip(weeks_str,hcg_int))

        res['error'] = relative_error
        return jsonify(res)

# for non-linear model
class HCG2(Resource):
    @cors.crossdomain(origin='*')
    def get(self, id):
        weeks_str = []
        weeks = list(nonlinear.getHcgValues2(id)[0])
        for week in weeks:
            weeks_str.append(str(week))

        hcgs = list(nonlinear.getHcgValues2(id)[1])
        hcg_int = [round(x) for x in hcgs]
        res = OrderedDict(zip(weeks_str, hcg_int))

        return jsonify(res)


api.add_resource(HCG, '/api/hcgs/<int:id>')
api.add_resource(HCG2, '/api/hcgs2/<int:id>')

if __name__ == '__main__':
    app.run(port=5000)