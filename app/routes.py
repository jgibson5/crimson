from flask import render_template, flash, redirect, url_for, request
from app import app, db
from flask_user import current_user, login_required, roles_required
from werkzeug.urls import url_parse

from app.forms import ItemListFormFactory, ItemDropForm, ItemAssignForm, UserManageForm
from app.models import User, ItemList, ItemRank, Item, Role


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/user/manage', methods=['GET', 'POST'])
@roles_required('council')
def manage_users():
    if current_user.is_authenticated and current_user.has_role('council'):
        user_manage_form = UserManageForm()
        if user_manage_form.validate_on_submit():
            changes_made = False
            for username in user_manage_form.users:
                user = User.query.filter_by(username=username).first()
                role_field = user_manage_form.role_fields[username]
                selected_roles = getattr(user_manage_form, role_field).data
                role_update = False
                for role_id in selected_roles:
                    if role_id not in (role.id for role in user.roles):
                        role_update = True
                for role in user.roles:
                    if role.id not in (selected_roles):
                        role_update = True
                if role_update:
                    roles = [Role.query.get(role_id) for role_id in selected_roles]
                    user.roles = roles

                active_update = False
                active_field = user_manage_form.active_fields[username]
                selected_active = getattr(user_manage_form, active_field).data

                if selected_active != user.active:
                    user.active = selected_active
                    active_update = True

                if role_update or active_update:
                    db.session.add(user)
                    db.session.commit()
                    changes_made = True
            if changes_made:
                flash("Changes to users have been saved.")

        return render_template('user_manager.html', form=user_manage_form)
    else:
        return redirect(url_for('index'))


@app.route('/item_list', methods=['GET', 'POST'])
@login_required
def item_list():
    if current_user.is_authenticated:
        item_list_form = ItemListFormFactory().construct(current_user.item_list)(request.form)

        if item_list_form.validate_on_submit():
            for form_item, old_item_rank in zip(item_list_form.item_rank_fields, current_user.item_list.items):
                new_item_id = getattr(item_list_form, form_item).data
                if new_item_id != old_item_rank.item_id:
                    item_rank = ItemRank.query.get(old_item_rank.id)
                    item_rank.item_id = new_item_id
                    db.session.add(item_rank)
            db.session.commit()
            flash("Wish list has been updated.")
        return render_template('item_list.html', form=item_list_form)
    else:
        return redirect(url_for('index'))


@app.route('/assign_item', methods=['GET', 'POST'])
@roles_required('council')
def assign_item():
    if current_user.is_authenticated and current_user.has_role('council'):
        item_assign_form = ItemAssignForm(current_form=request.form)

        all_items = sorted([(i.id, i.name) for i in Item.query.all()], key=lambda x: x[1] if x[1] != 'empty' else 'AAAA')
        item_assign_form.item_drop.choices = all_items

        item_drop_check_results = []
        item_check_error = ''

        if item_assign_form.validate_on_submit():

            item_id = item_assign_form.item_drop.data
            active_users = User.query.filter_by(active=True).all()
            print(item_id)
            print(active_users)
            item_ranks = ItemRank.query.filter(ItemRank.item_id==item_id, ItemRank.item_list_id.in_(user.item_list_id for user in active_users)).all()
            print(item_ranks)
            for item_rank in item_ranks:
                user = User.query.filter_by(item_list_id=item_rank.item_list_id).first()
                item_drop_check_results.append({'rank': item_rank.rank, 'username': user.username})

            if not item_drop_check_results:
                item_check_error = 'Item not found in any Wish Lists.'

            item_drop_check_results.sort(key=lambda x: x['rank'])
            item_assign_form = ItemAssignForm(item_ranks=item_drop_check_results, current_form=request.form)
            item_assign_form.item_drop.choices = all_items
            item_assign_form.item_drop.default = item_id

            assign_click = False
            for field_name in item_assign_form.assign_fields:
                field = getattr(item_assign_form, field_name)
                if field.data:
                    assign_click = True
                    item_rank = item_assign_form.parse_label(field_name)
                    default_item = Item.query.filter_by(name='empty').first()
                    user = User.query.filter_by(username=item_rank['username']).first()
                    item_rank_to_update = ItemRank.query.filter_by(rank=item_rank['rank'], item_list_id=user.item_list_id).first()
                    item_rank_to_update.item_id = default_item.id
                    db.session.add(item_rank_to_update)
                    db.session.commit()

            if assign_click:
                item_assign_form = ItemAssignForm()
                item_assign_form.item_drop.choices = all_items
                item_assign_form.item_drop.default = item_id

        return render_template(
            'item_drop.html',
            form=item_assign_form,
            item_check_error=item_check_error,
        )
    else:
        return redirect(url_for('index'))
