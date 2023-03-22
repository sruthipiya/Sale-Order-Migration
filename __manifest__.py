{
    'name': 'Data Migration 15 to 16',
    'version': '16.0.1.0.0',
    'category': 'Data Migration',
    'summary': 'Migrate sale order from odoo 15 to odoo 16',
    'sequence': -6,
    'installable': True,
    'application': True,
    'depends': ['base'],
    'data': ['security/ir.model.access.csv',
             'views/data_migration.xml',
             'views/data_migration_menu.xml'],
}
