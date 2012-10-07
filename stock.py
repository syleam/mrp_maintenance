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


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns = {
        'maintenance_type_id': fields.many2one('mrp.maintenance.type', 'Maintenance Type', domain=[('type', 'in', ['all', 'lot'])], help='Type of maintenance for know if this maintenance will be invoice or not'),
        'partner_id': fields.many2one('res.partner', 'Partner', help='Product form this partner'),
    }

stock_production_lot()


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Fill partner_id in stock.production.lot
        """
        if move.prodlot_id and not move.prodlot_id.partner_id \
           and move.picking_id and move.picking_id.type == 'out' \
           and move.sale_line_id:
            self.pool.get('stock.production.lot').write(cr, uid, [move.prodlot_id.id], {'partner_id': move.sale_line_id.order_id.partner_id.id}, context=context)
        return super(stock_move, self)._create_product_valuation_moves(cr, uid, move, context=context)

stock_move()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
