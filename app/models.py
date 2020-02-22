from app import db
from flask_user import UserMixin
import datetime

from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin,):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    email_confirmed_at = db.Column('confirmed_at', db.DateTime())
    password = db.Column(db.String(128))

    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')

    item_list_locked = db.Column(db.Boolean, default=True)

    item_list_id = db.Column(db.Integer, db.ForeignKey('item_list.id'))
    item_list = db.relationship('ItemList', backref=db.backref('user', uselist=False))

    locked_item_list_id = db.Column(db.Integer, db.ForeignKey('locked_item_list.id'))
    locked_item_list = db.relationship('LockedItemList', backref=db.backref('user', uselist=False))

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.construct_new_lists()
        if not self.roles:
            initiate_role = Role.query.filter_by(name='initiate').first()
            self.roles.append(initiate_role)

    def has_role(self, role):
        return role in (role.name for role in self.roles)

    def construct_new_lists(self):
        self.item_list = ItemList()
        default_item = Item.query.filter_by(name=Item.default_name).first()
        for slot in range(15):
            self.item_list.items.append(ItemRank(rank=slot+1, item_id=default_item.id))

        self.locked_item_list = LockedItemList(item_list=self.item_list)


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


class LockedItemRank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, index=True)
    locked_item_list_id = db.Column(db.Integer, db.ForeignKey('locked_item_list.id'), index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), index=True)
    item = db.relationship('Item', backref=db.backref('locked_item', uselist=False))

    def __repr__(self):
        return '<LockedItemRank {}:{}:{}>'.format(self.locked_item_list_id, self.rank, self.item)


class ItemList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship("ItemRank", backref='list', lazy='dynamic')

    def __init__(self, locked_item_list=None):
        super().__init__()
        if locked_item_list:
            self.items = [ItemRank(rank=item_rank.rank, item=item_rank.item) for item_rank in locked_item_list.items]

    def __repr__(self):
        return '<ItemList {}>'.format(self.id)


class LockedItemList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship("LockedItemRank", backref='list', lazy='dynamic')
    locked_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, item_list=None):
        super().__init__()
        if item_list:
            self.items = [LockedItemRank(rank=item_rank.rank, item_id=item_rank.item_id) for item_rank in item_list.items]

    def __repr__(self):
        return '<LockedItemList {}>'.format(self.id)

