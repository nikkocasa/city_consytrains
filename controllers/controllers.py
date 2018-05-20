# -*- coding: utf-8 -*-
from odoo import http

# class City(http.Controller):
#     @http.route('/city/city/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/city/city/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('city.listing', {
#             'root': '/city/city',
#             'objects': http.request.env['city.city'].search([]),
#         })

#     @http.route('/city/city/objects/<model("city.city"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('city.object', {
#             'object': obj
#         })