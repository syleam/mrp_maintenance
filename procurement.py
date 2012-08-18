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


class procuremen_order(osv.osv):
    _inherit = 'procurement.order'

    def test_maintenance(self, cr, uid, ids):
        """ Tests whether type of sale order is maintenance or not.
        @return: True or False
        """
        for record in self.browse(cr, uid, ids):
            if record.move_id and \
               record.move_id.sale_line_id and \
               record.move_id.sale_line_id.order_id and \
               record.move_id.sale_line_id.order_id.type == 'maintenance':
                return True
        return False

procuremen_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: