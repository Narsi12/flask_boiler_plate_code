import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from service.models import db
from wsgi import create_app

config_name = os.environ['FLASK_ENV']
app = create_app(config_name)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
