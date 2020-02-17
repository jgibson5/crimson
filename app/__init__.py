from flask import Flask
from config import Config

from flask.cli import with_appcontext, click
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_user import UserManager


import yaml
import io

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

Bootstrap(app)


from app import routes, models

# Setup Flask-User
user_manager = UserManager(app, db, models.User)




@click.command("seed_db")
@with_appcontext
def item_seed():
    """Seed the database."""
    stream = io.open('items.yaml', 'r')
    items_to_seed = yaml.safe_load(stream)
    for item_name in items_to_seed['items']:
        existing_item = models.Item().query.filter_by(name=item_name).first()
        if not existing_item:
            item = models.Item(name=item_name)
            db.session.add(item)
    db.session.commit()

    for role_name in ('raider', 'council', 'initiate'):
        role = models.Role.query.filter_by(name=role_name).first()
        if not role:
            db.session.add(models.Role(name=role_name))
    db.session.commit()

    if not models.User.query.filter(models.User.username=='lucky').first():
        user1 = models.User(username='lucky', email='lucky@example.com', active=True,
                password=user_manager.hash_password('asdf'))
        council_role = models.Role.query.filter_by(name='council').first()
        user1.roles.append(council_role)
        user1.construct_new_lists()
        db.session.add(user1)
        db.session.commit()
    db.session.commit()
app.cli.add_command(item_seed)