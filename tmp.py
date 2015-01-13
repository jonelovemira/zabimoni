#! flask/bin/python

from monitor import app
from flask_alembic import Alembic

alembic = Alembic()
alembic.init_app(app)

alembic.revision('make changes')
