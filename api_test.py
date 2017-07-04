#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 15:16:24 2017

@author: tony
"""

import logmodel

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HCG(Resource):
    def get(self, id):
        weeks = list(logmodel.getHcgValues(id)[0])
        hcgs = list(logmodel.getHcgValues(id)[1])
        hcg_int = [round(x) for x in hcgs]
        res = dict(zip(weeks,hcg_int))
        return res
        
api.add_resource(HCG, '/api/hcgs/<int:id>')


if __name__ == '__main__':
    app.run(port=5000)