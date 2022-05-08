from orator import DatabaseManager, Model

config = {
    'sqlite': {
        'driver': 'sqlite',
        #'host': '??',
        'database': '..\\n1_vocab.db',
        #'user': '??',
        #'password': '??',
        'prefix': ''
    }
}

db = DatabaseManager(config)
Model.set_connection_resolver(db)