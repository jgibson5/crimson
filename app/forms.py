from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.widgets.core import ListWidget, CheckboxInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.models import User, Item, Role


def UserManageForm():
    class UserManageForm(FlaskForm):
        submit = SubmitField('Update Users')

    all_users = User.query.all()
    all_roles = Role.query.all()

    UserManageForm.role_fields = {}
    UserManageForm.active_fields = {}
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
        UserManageForm.users.append(user.username)
        UserManageForm.role_fields[user.username] = f"{user.username}_roles"
        UserManageForm.active_fields[user.username] = f"{user.username}_is_active"

    return UserManageForm()


class MultiCheckboxField(SelectMultipleField):

    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

    def pre_validate(self, form):
        pass


class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass


class ItemListFormFactory():
    slot_name = "item_rank_"

    class ItemListForm(FlaskForm):
        submit = SubmitField('Update List')

        # def validate

    def construct(self, current_item_list):
        all_items = sorted([(i.id, i.name) for i in Item.query.all()], key=lambda x: x[1] if x[1] != 'empty' else 'AAAA')

        self.ItemListForm.item_rank_fields = []

        for item_rank in current_item_list.items:
            item_rank_field_name = self.slot_name + str(item_rank.rank)
            setattr(
                self.ItemListForm,
                item_rank_field_name,
                NonValidatingSelectField(f"Item Rank {item_rank.rank}", choices=all_items, default=item_rank.item_id, validators=[]) # validators=[DataRequired()]
            )
            self.ItemListForm.item_rank_fields.append(item_rank_field_name)

        return self.ItemListForm


class ItemDropForm(FlaskForm):
    item_drop = NonValidatingSelectField("Item")
    submit = SubmitField("Check")

    def __init__(self):
        super().__init__()
        all_items = sorted([(i.id, i.name) for i in Item.query.all()], key=lambda x: x[1] if x[1] != 'empty' else 'AAAA')
        self.item_drop.choices = all_items


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


