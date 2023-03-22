from odoo import models, fields
import xmlrpc.client as client


class DataMigration(models.Model):
    _name = "data.migrate"
    _description = "Data migration"
    _rec_name = "source_db"

    source_db = fields.Char(string="Source DB in Odoo 15")
    source_db_user = fields.Char(string="Source DB Username")
    source_db_pwd = fields.Char(string="Source DB Password")
    source_db_url = fields.Char(string="Source DB URL")
    destination_db = fields.Char(string="Destination DB in odoo 16")
    destination_db_user = fields.Char(string="Destination DB Username")
    destination_db_pwd = fields.Char(string="Destination DB Password")
    destination_db_url = fields.Char(string="Destination DB URL")

    def action_fetch_data(self):
        '''This code connecting the odoo 15 database '''
        common_1 = client.ServerProxy('{}/xmlrpc/2/common'.format(self.source_db_url))
        models_1 = client.ServerProxy('{}/xmlrpc/2/object'.format(self.source_db_url))

        '''This code connecting the odoo 16 database '''
        common_2 = client.ServerProxy('{}/xmlrpc/2/common'.format(self.destination_db_url))
        models_2 = client.ServerProxy('{}/xmlrpc/2/object'.format(self.destination_db_url))

        '''Validating the databases in different version'''
        uid_db1 = common_1.authenticate(self.source_db, self.source_db_user, self.source_db_pwd, {})
        uid_db2 = common_2.authenticate(self.destination_db, self.destination_db_user, self.destination_db_pwd, {})

        '''Fetching all the data in the sale.order from odoo 15'''
        db_1_orders = models_1.execute_kw(self.source_db, uid_db1, self.source_db_pwd,
                                          'sale.order',
                                          'search_read', [[]], {
                                              'fields': ['name', 'partner_id',
                                                         'pricelist_id',
                                                         'state',
                                                         'order_line']})

        '''Fetching all the data in the sale.order from odoo 16 to check it with 
        odoo 15 data to get identical data'''
        db_2_orders = models_2.execute_kw(self.destination_db, uid_db2, self.destination_db_pwd,
                                          'sale.order',
                                          'search_read', [[]], {
                                              'fields': ['name', 'partner_id',
                                                         'state',
                                                         'order_line']})

        '''Creating a list with odoo 16 data'''
        migration_data_16 = []
        for orders_16 in db_2_orders:
            order_16_partner = orders_16['partner_id'][0]
            order_16_state = orders_16['state']
            order_16_orderline = orders_16['order_line']
            data_16 = [order_16_partner, order_16_state, order_16_orderline]
            migration_data_16.append(data_16)

        '''Creating a list with odoo 15 data and checking it with 
        odoo 16 data'''
        migration_data_15 = []
        for orders_15 in db_1_orders:
            order_15_partner = orders_15['partner_id'][0]
            order_15_state = orders_15['state']
            order_15_orderline = orders_15['order_line']
            data_15 = [order_15_partner, order_15_state, order_15_orderline]
            if data_15 not in migration_data_16:
                migration_data_15.append(orders_15)
        print(migration_data_15, 'mmmm')

        if migration_data_15:
            '''Fetching sale order line from odoo 15'''
            db_1_order_line = models_1.execute_kw(self.source_db, uid_db1, self.source_db_pwd,
                                                  'sale.order.line',
                                                  'search_read', [[]], {
                                                      'fields': ['order_id',
                                                                 'product_id',
                                                                 'name',
                                                                 'product_uom_qty',
                                                                 'price_unit']})
            order_dict = {}
            for order in migration_data_15:
                for key in order:
                    if key == 'order_line':
                        continue
                    elif key == 'partner_id':
                        customer = order[key][0]
                        order_dict.update({key: customer})
                    elif key == 'pricelist_id':
                        pricelist = order[key][0]
                        order_dict.update({key: pricelist})
                    else:
                        order_dict.update({key: order[key]})

            '''Creating sale order in odoo 16 using the data from odoo 15'''
            new_order = models_2.execute_kw(self.destination_db, uid_db2, self.destination_db_pwd,
                                            'sale.order',
                                            'create', [order_dict])

            '''Creating the corresponding sale order line in odoo 16'''
            for so in migration_data_15:
                for sol in db_1_order_line:
                    if sol['order_id'][0] == so['id']:
                        new_order = models_2.execute_kw(self.destination_db, uid_db2,
                                                        self.destination_db_pwd,
                                                        'sale.order.line',
                                                        'create',
                                                        [{
                                                            'order_id': so[
                                                                'id'],
                                                            'product_id': sol[
                                                                'product_id'][
                                                                0],
                                                            'name': sol[
                                                                'name'],
                                                            'product_uom_qty':
                                                                sol[
                                                                    'product_uom_qty'],
                                                            'price_unit': sol[
                                                                'price_unit'],
                                                        }])
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Transfer Complete',
                    'type': 'rainbow_man',
                }
            }
        else:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'No Data to Transfer',
                    'type': 'rainbow_man',
                }
            }







