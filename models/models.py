# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    ### Add a new column to the res.partner model, to constrains city
    # from a res_partner_city table where state_id  is mandatory and point to a country id which is mandatory too
    # original fields are : (in class res.partner (file res_partner.py)
    # see it at https: // fossies.org / dox / odoo - 8.0.0 / openerp_2addons_2base_2res_2res__partner_8py_source.html
    # line:265/:  'city': fields.char('City'),
    # line:266/:  'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
    # line:267/:  'country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
    ###

    city_id = fields.Many2one(
        comodel_name="res.city",
        string="City"
    )
    zip_id = fields.Many2one(
        comodel_name='res.zip',
        string='Zip code'
    )
    area_id_name = fields.Char(
        related="city_id.area_id.name",
        string="Area",
        index=True
    )
    state_id_name = fields.Char(
        related="city_id.area_id.state_id.name",
        string="State",
        index=True
    )
    country_id_name = fields.Char(
        related="city_id.area_id.state_id.country_id.name",
        string='Country',
        index=True
    )

    @api.onchange('city_id')
    def _onchange_city(self):
        self.ensure_one()
        self.city = ''
        if self.city_id:
            self.city = self.city_id.name
            self.area_id = self.city_id.area_id
            self.state_id = self.city_id.area_id.state_id
            self.country_id = self.city_id.area_id.state_id.country_id
            if len(self.city_id.zip_ids.ids) == 1:
                #set zip code directly
                self.zip = self.city_id.zip_ids.name
            # set zip_id to empty in case of city changes
            elif self.zip != self.zip_id.name:
                self.zip = ''
            return {'domain': {
                'zip_id': [('id', 'in', self.city_id.zip_ids.ids)],
            }}
        else: #city_id is empty : reseting domain on zip_id list
            self.city = ''
            return {'domain': {
                'zip_id': self.city_id.zip_ids.ids,
            }}

    @api.onchange('zip_id')
    def _onchange_zip(self):
        self.ensure_one()
        self.zip = ''
        if self.zip_id:
            self.zip = self.zip_id.name
            self.area_id = self.city_id.area_id
            self.state_id = self.city_id.area_id.state_id
            self.country_id = self.city_id.area_id.state_id.country_id
            if len(self.zip_id.city_ids.ids) == 1:
                #set zip code directly
                self.city = self.zip_id.city_ids.name
            # set city_id to empty in case of zip changes
            elif self.zip != self.zip_id.name:
                self.city = ''
            return {'domain': {
                'city_id': [('id', 'in', self.zip_id.city_ids.ids)],
            }}
        else:
            self.zip = ''
            return {'domain': {
                'city_id': self.zip_id.city_ids.ids,
            }}


    @api.constrains('city_id','zip')
    def set_state_country(self):
        for r in self:
            if r.city_id:
                r.city = r.city_id.name
                r.area_id = r.city_id.area_id
                r.state_id = r.city_id.area_id.state_id
                r.country_id = r.city_id.area_id.state_id.country_id

class Country(models.Model):
    _inherit = 'res.country'

    zip_name = fields.Char(
        string='Local name for ZIP code',
    )
    zip_format = fields.Char(
        string='Local Format',
        help="Empty means Anything, or give a example"
    )

class State(models.Model):
    _inherit='res.country.state'


    area_ids = fields.One2many(
        string="Area list",
        comodel_name='res.country.state.area',
        inverse_name='state_id'
    )


class Area(models.Model):
    _name = 'res.country.state.area'

    name = fields.Char(
        string='Name'
    )
    area_code = fields.Char(
        string='Code',
        size=6
    )
    state_id = fields.Many2one(
        string="State",
        comodel_name='res.country.state'
    )
    city_ids = fields.One2many(
        string='Cities list',
        comodel_name='res.city',
        inverse_name='area_id'
    )


class City(models.Model):
    _name = 'res.city'

    name = fields.Char(
        string='City Name'
    )
    airport_code = fields.Char(
        string='Airport Code',
        size=3
    )
    insee_code = fields.Char(
        string='INSEE',
        size=7
    )
    zip_ids = fields.Many2many(
        string="ZIP",
        comodel_name='res.zip',
        help="Not mandatory: leave blank if there is more than one zip code for this town"
    )
    area_id = fields.Many2one(
        string="Area",
        comodel_name='res.country.state.area'
    )
    state_id_name = fields.Char(
        related="area_id.state_id.name",
        string='State',
        index=True
    )
    country_id_name = fields.Char(
        related="area_id.state_id.country_id.name",
        string='Country',
        index=True
    )
    long = fields.Float(
        string="Longitude",
        digits=(12, 10)
    )
    lat = fields.Float(
        string="Latitude",
        digits=(12, 10)
    )
    gps_coord = fields.Char(
        string='Coord. GPS (lat, Long)',
        size=28,
        compute='_get_coord_gps()',
        store=True
    )
    population = fields.Integer(
        string='Population'
    )

    @api.onchange('long', 'lat')
    def _set_gps_coord(self):
        self.gps_coord = self._get_coord_gps()

    def _get_coord_gps(self):
        return "({0:12.10f}, {1:12.10f})".format(self.lat if self.lat else 0.0,
                                               self.long if self.long else 0.0)

class Zip(models.Model):
    _name='res.zip'

    name = fields.Char(
        string='ZIP Code'
    )
    zip_country = fields.Many2one(
        string='Country name',
        comodel_name='res.country',
    )
    zip_format = fields.Char(
        string='Format Code',
        related='zip_country.zip_format'
    )
    city_ids = fields.Many2many(
        string='Cities',
        comodel_name='res.city'
    )


