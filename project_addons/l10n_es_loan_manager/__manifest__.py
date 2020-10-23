{
    'name': 'Gestor de préstamos',
    'description':'Crea cuadros de amortización de préstamos',
    'version': '11.0.1.0.0',
    'category': 'Partner',
    'website': 'las-rias.com',
    'author': 'Ramón Castro - Las Rías',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account'
    ],
    'data':['views/loan_line_view.xml',
            'views/loan_manager_view.xml',
            #'data/loans.xml',
            'security/loan_security.xml'
            ],
    'application': False,
    'installable': True,
}
