# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Translate mode',
    'category': 'Hidden',
    'summary': 'Activates translation mode on the whole database',
    'description': """TODO: module description""",
    'depends': ['web',],
    'auto_install': True,
    'data': [],
    'assets': {
        'web.assets_backend': [
            'translate_mode/static/src/**/*',
        ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
