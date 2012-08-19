# -*- coding: utf-8 -*-
##############################################################################
#
#    mrp_maintenance module for OpenERP, Manage maintenance in production order
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of mrp_maintenance
#
#    mrp_maintenance is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    mrp_maintenance is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'sale_line_id': fields.related('move_prod_id', 'sale_line_id', type='many2one', relation='sale.order.line', readonly=True, store=True, string='Sale Line'),
        'sale_id': fields.related('sale_line_id', 'order_id', type='many2one', relation='sale.order', string='Sale Order', readonly=True, store=True, help='Sale order linked to this production order.'),
        'partner_id': fields.related('sale_id', 'partner_id', type='many2one', relation='res.partner', string='Partner', readonly=True, store=True, help='Partner linked to this production order'),
        'sale_line_notes': fields.related('sale_line_id', 'notes', type='text', string='Notes', readonly=True, store=True, help='Notes from sale order line'),
        'prodlot_id': fields.related('sale_line_id', 'prodlot_id', type='many2one', relation='stock.production.lot', string='Production Lot', readonly=True, store=True, help='Production lot is used to put a serial number on the production'),
    }

    def action_confirm_maintenance(self, cr, uid, ids, context=None):
        """
        If we do not have a product in the BOM, OpenERP will not create picking and movement of finished product.
        In the case of maintenance, we have a BOM empty so we add the movement of finished product.
        """
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids, context=context):
            if not production.move_created_ids \
               and production.sale_id \
               and production.sale_id.type == 'maintenance':
                self._make_production_produce_line(cr, uid, production, context=context)
                workcenter_line_obj.write(cr, uid, [line.id for line in production.sale_id.workcenter_line_ids], {'production_id': production.id}, context=context)
        return True

    def action_production_end(self, cr, uid, ids):
        """
        Copy raw product and workcenter in stock picking
        @return: True
        """
        picking_obj = self.pool.get('stock.picking')
        for production in self.browse(cr, uid, ids):
            vals = {'production_line_ids': []}
            if production.sale_id and production.sale_id.type == 'maintenance':
                for line in production.move_lines2:
                    vals['production_line_ids'].append((0, 0, {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'move_id': production.move_prod_id.id,
                        'price_unit': line.sale_line_id and line.sale_line_id.price_unit or line.product_id.list_price or 0.,
                        'discount': line.sale_line_id and line.sale_line_id.discount or 0.,
                        'production_id': production.id,
                    }))
                workcenter_lines = {}
                # Group by workcenter_id
                for line in production.workcenter_lines:
                    if line.workcenter_id.id in workcenter_lines:
                        workcenter_lines[line.workcenter_id.id].append(line)
                        continue
                    workcenter_lines[line.workcenter_id.id] = [line]
                pricelist_id = production.sale_id.pricelist_id.id
                partner_id = production.sale_id.partner_id.id
                for workcenter_id, lines in workcenter_lines.items():
                    nb_hour = 0.
                    for line in lines:
                        nb_hour += line.hour
                    price_unit = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                                              lines[0].workcenter_id.product_id.id, nb_hour or 1.0,
                                              partner_id,
                                              {
                                                  'uom': lines[0].workcenter_id.product_id.uom_id.id,
                                                  'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                              }
                                             )[pricelist_id]
                    vals['production_line_ids'].append((0, 0, {
                        'name': lines[0].workcenter_id.name,
                        'product_id': lines[0].workcenter_id.product_id.id,
                        'product_qty': nb_hour,
                        'product_uom': lines[0].workcenter_id.product_id.uom_id.id,
                        'move_id': production.move_prod_id.id,
                        'price_unit': price_unit or 0.,
                        'discount': 0.,
                        'production_id': production.id,
                    }))
                if vals:
                    picking_obj.write(cr, uid, [production.move_prod_id.picking_id.id], vals)
        return super(mrp_production, self).action_production_end(cr, uid, ids)

mrp_production()


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale order'),
        # Just remove required=True for possibility to add record in sale order
        'production_id': fields.many2one('mrp.production', 'Production Order', select=True, ondelete='cascade', required=False),
    }

mrp_production_workcenter_line()


class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'

    _columns = {
        'product_id': fields.many2one('product.product','Work Center Product', required=True, help="Fill this product to track easily your production costs in the analytic accounting."),
    }

mrp_workcenter()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
