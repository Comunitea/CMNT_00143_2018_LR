{
    'name': 'Gestor de préstamos y previsión de tesorería',
    'description':'Integra la gestión de préstamos y la previsión de tesorería',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'depends': [
        'l10n_es_loan_manager',
        'cash_forecast'
    ],
    'data':[
        'views/cash_forecast_view.xml'
    ],
    'application': True,
    'installable': True,
}
