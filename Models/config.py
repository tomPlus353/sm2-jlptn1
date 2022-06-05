from orator import DatabaseManager, Model, Schema

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
schema = Schema(db)
Model.set_connection_resolver(db)