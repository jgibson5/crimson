from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.widgets.core import ListWidget, CheckboxInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileRequired

from app.models import User, Item, Role, LockedItemRank


def UserManageForm():
    class UserManageForm(FlaskForm):
        submit = SubmitField('Update Users')

    all_users = User.query.all()
    all_roles = Role.query.all()

    UserManageForm.role_fields = {}
    UserManageForm.active_fields = {}
    UserManageForm.list_locked_fields = {}
    UserManageForm.users = []
    for user in all_users:
        setattr(
            UserManageForm,
            f"{user.username}_roles",
            MultiCheckboxField("Roles", choices=[(role.id, role.name) for role in all_roles], default=[user_role.id for user_role in user.roles]),
        )
        setattr(
            UserManageForm,
            f"{user.username}_is_active",
            BooleanField("Is Active", false_values=[False], default=user.active),
        )
        setattr(
            UserManageForm,
            f"{user.username}_list_locked",
            BooleanField("List is Locked", false_values=[False], default=user.item_list_locked),
        )
        UserManageForm.users.append(user.username)
        UserManageForm.role_fields[user.username] = f"{user.username}_roles"
        UserManageForm.active_fields[user.username] = f"{user.username}_is_active"
        UserManageForm.list_locked_fields[user.username] = f"{user.username}_list_locked"

    return UserManageForm()


class MultiCheckboxField(SelectMultipleField):

    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

    def pre_validate(self, form):
        pass


class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass


def ItemListForm(current_item_list, locked_item_list_id, as_user_type='raider'):
    slot_name = "item_rank_"

    class ItemListForm(FlaskForm):
        submit = SubmitField('Update List')

    all_items = sort_item_choices(Item.query.all())

    ItemListForm.item_rank_fields = []

    for item_rank in sorted(current_item_list.items, key=lambda x:x.rank):
        item_rank_field_name = slot_name + str(item_rank.rank)
        item_choices = []
        restricted_slots = tuple()
        if as_user_type == 'initiate':
            restricted_slots = (1, 2, 3)
        elif as_user_type == 'raider':
            restricted_slots = (1, 2)

        if item_rank.rank in restricted_slots:
            default_item = Item.query.filter_by(name=Item.default_name).first()
            current_rank = LockedItemRank.query.filter_by(rank=item_rank.rank, locked_item_list_id=locked_item_list_id).first()
            promotable_rank = LockedItemRank.query.filter_by(rank=item_rank.rank+1, locked_item_list_id=locked_item_list_id).first()
            unsorted_choices = [default_item, current_rank.item, promotable_rank.item]
            item_choices = sort_item_choices(unsorted_choices)
        else:
            item_choices = all_items
        setattr(
            ItemListForm,
            item_rank_field_name,
            NonValidatingSelectField(f"Item Rank {item_rank.rank}", choices=item_choices, default=item_rank.item_id, validators=[])
        )
        ItemListForm.item_rank_fields.append(item_rank_field_name)

    return ItemListForm()


class ItemDropForm(FlaskForm):
    item_drop = NonValidatingSelectField("Item")
    submit = SubmitField("Check")

    def __init__(self):
        super().__init__()
        self.item_drop.choices = sort_item_choices(Item.query.all())


def sort_item_choices(item_choices):
    return sorted(list(set((i.id, i.name) for i in item_choices)), key=lambda x: x[1] if x[1] != Item.default_name else 'AAAA')


def ItemAssignForm(item_ranks=None, current_form=None):
    if item_ranks == None:
        item_ranks = []

    class ItemAssignForm(FlaskForm):
        item_drop = NonValidatingSelectField("Item")
        submit = SubmitField("Check")

        def parse_label(self, label):
            parts = label.split(':')
            return {'rank': parts[0], 'username': parts[1].strip()}

    ItemAssignForm.assign_fields = []
    for item_rank in item_ranks:
        label = f"{item_rank['rank']}: {item_rank['username']}"
        setattr(ItemAssignForm, label, SubmitField('Assign'))
        ItemAssignForm.assign_fields.append(label)

    return ItemAssignForm(current_form) if current_form else ItemAssignForm()


class GlobalItemLockForm(FlaskForm):
    force_lock_lists = SubmitField('Lock')
    force_unlock_lists = SubmitField('Unlock')


class WorkbookForm(FlaskForm):
    workbook = FileField(validators=[FileRequired()])
    add_new_users = BooleanField("Add New Characters", false_values=[False], default=False)
    submit = SubmitField("Upload Workbook")


class PasswordForm(FlaskForm):
    password = StringField("New password")
    submit = SubmitField("Change password")

