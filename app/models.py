from app import db
from flask_user import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin,):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    email_confirmed_at = db.Column('confirmed_at', db.DateTime())
    password = db.Column(db.String(128))

    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')

    item_list_id = db.Column(db.Integer, db.ForeignKey('item_list.id'))
    item_list = db.relationship('ItemList', backref=db.backref('user', uselist=False))

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.construct_new_list()
        if not self.roles:
            initiate_role = Role.query.filter_by(name='initiate').first()
            self.roles.append(initiate_role)

    def has_role(self, role):
        return role in (role.name for role in self.roles)

    def construct_new_list(self):
        self.item_list = ItemList()
        default_item = Item.query.filter_by(name=Item.default_name).first()
        for slot in range(15):
            self.item_list.items.append(ItemRank(rank=slot+1, item_id=default_item.id))


# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    default_name = 'empty'
    
    def __repr__(self):
        return '<Item {}>'.format(self.name)


class ItemRank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, index=True)
    item_list_id = db.Column(db.Integer, db.ForeignKey('item_list.id'), index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), index=True)
    item = db.relationship('Item', backref=db.backref('item', uselist=False))

    def __repr__(self):
        return '<ItemRank {}:{}:{}>'.format(self.item_list_id, self.rank, self.item)


class ItemList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship("ItemRank", backref='list', lazy='dynamic')

    def __repr__(self):
        return '<List {}>'.format(self.id)

