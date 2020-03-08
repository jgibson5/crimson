from flask import render_template, flash, redirect, url_for, request
from app import app, db
from flask_user import current_user, login_required, roles_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os

from app.forms import ItemListForm, ItemDropForm, ItemAssignForm, UserManageForm, GlobalItemLockForm, sort_item_choices, WorkbookForm
from app.models import User, ItemList, ItemRank, Item, Role, LockedItemList, ItemRankAudit

from app.workbook_manager import read_workbook


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

                list_lock_update = False
                list_locked_field = user_manage_form.list_locked_fields[username]
                selected_list_locked = getattr(user_manage_form, list_locked_field).data

                if selected_list_locked != user.item_list_locked:
                    user.item_list_locked = selected_list_locked
                    if selected_list_locked:
                        user.locked_item_list = LockedItemList(item_list=user.item_list)
                    list_lock_update = True

                if role_update or active_update or list_lock_update:
                    db.session.add(user)
                    db.session.commit()
                    changes_made = True
            if changes_made:
                flash("Changes to users have been saved.")

        return render_template('user_manager.html', form=user_manage_form)
    else:
        return redirect(url_for('index'))


@app.route('/item_list_lock', methods=['GET', 'POST'])
@roles_required('council')
def item_list_lock():
    if current_user.is_authenticated and current_user.has_role('council'):
        global_item_lock_form = GlobalItemLockForm()
        if global_item_lock_form.validate_on_submit():
            lock_lists = None
            lock_text = ""
            if global_item_lock_form.force_lock_lists.data:
                lock_lists = True
                lock_text = "locked"
            elif global_item_lock_form.force_unlock_lists.data:
                lock_lists = False
                lock_text = "unlocked"
            users = User.query.all()
            for user in users:
                user.item_list_locked = lock_lists
                if lock_lists:
                    user.locked_item_list = LockedItemList(item_list=user.item_list)
                db.session.add(user)
            db.session.commit()
            flash(f"Item lists have been {lock_text}.")
        return render_template('global_item_list_lock.html', form=global_item_lock_form)
    else:
        return redirect(url_for('index'))


@app.route('/item_list', methods=['GET', 'POST'])
@login_required
def item_list():
    if current_user.is_authenticated:
        if current_user.item_list_locked:
            return render_template('locked_item_list.html', item_ranks=current_user.item_list.items)
        else:
            if current_user.has_role('initiate'):
                return edit_list_route(current_user, current_user, as_user_type='initiate')
            return edit_list_route(current_user, current_user)
    else:
        return redirect(url_for('index'))


@app.route('/item_list/<username>', methods=['GET', 'POST'])
@roles_required('council')
def user_item_list(username):
    if current_user.is_authenticated and current_user.has_role('council'):
        user = User.query.filter_by(username=username).first()
        return edit_list_route(user, current_user, as_user_type='council')
    else:
        return redirect(url_for('index'))


def edit_list_route(list_user, edit_user, as_user_type='raider'):
    item_list_form = ItemListForm(list_user.item_list, list_user.locked_item_list_id, as_user_type=as_user_type)

    if item_list_form.validate_on_submit():
        item_rank_fields = item_list_form.item_rank_fields
        new_item_ids = []
        for field in item_rank_fields:
            new_item_ids.append(getattr(item_list_form, field).data)
        update_item_list(new_item_ids, list_user, edit_user)
    return render_template('item_list.html', form=item_list_form)

def update_item_list(new_item_ids, list_user, edit_user):
    current_item_ranks = sorted(list_user.item_list.items, key=lambda x: x.rank)

    for new_item_id, old_item_rank in zip(new_item_ids, current_item_ranks):
        if new_item_id != old_item_rank.item_id:
            item_rank = ItemRank.query.get(old_item_rank.id)
            item_rank_audit = ItemRankAudit(
                item_rank_id=item_rank.id,
                old_item_id=item_rank.item_id,
                new_item_id=new_item_id,
                user=edit_user,
            )
            db.session.add(item_rank_audit)
            item_rank.item_id = new_item_id
            db.session.add(item_rank)
    db.session.commit()
    flash("Wish list has been updated.")


@app.route('/assign_item', methods=['GET', 'POST'])
@roles_required('council')
def assign_item():
    if current_user.is_authenticated and current_user.has_role('council'):
        item_assign_form = ItemAssignForm(current_form=request.form)

        all_items = sort_item_choices(Item.query.all())
        item_assign_form.item_drop.choices = all_items

        item_drop_check_results = []
        item_check_error = ''

        if item_assign_form.validate_on_submit():

            item_id = item_assign_form.item_drop.data
            active_users = User.query.filter_by(active=True).all()

            item_ranks = ItemRank.query.filter(ItemRank.item_id==item_id, ItemRank.item_list_id.in_(user.item_list_id for user in active_users)).all()

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
                    default_item = Item.query.filter_by(name=Item.default_name).first()
                    user = User.query.filter_by(username=item_rank['username']).first()
                    item_rank_to_update = ItemRank.query.filter_by(rank=item_rank['rank'], item_list_id=user.item_list_id).first()
                    item_rank_to_update.item_id = default_item.id
                    item_rank_audit = ItemRankAudit(
                        item_rank_id=item_rank_to_update.id,
                        old_item_id=item_id,
                        new_item_id=default_item.id,
                        user=current_user,
                    )
                    db.session.add(item_rank_audit)
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

@app.route('/workbook', methods=['GET', 'POST'])
@roles_required('council')
def workbook():
    form = WorkbookForm()
    if form.validate_on_submit():
        f = form.workbook.data
        filename = secure_filename(f.filename)
        filepath = os.path.join(
            app.instance_path, 'workbooks', filename
        )
        f.save(filepath)
        item_map = Item.item_name_to_id_map()
        lists = read_workbook(filepath, item_map)
        create_new_users = form.add_new_users.data
        for character in lists.keys():
            print(character)
            list_user = User.query.filter_by(username=character).first()
            if not list_user and not create_new_users:
                flash(f"Unable to find a wish list for {character}.")
                continue
            elif not list_user:
                list_user = create_temp_user(character)
                flash(f"Creating a new account and wishlist for {character}.")
            update_item_list(lists[character] , list_user, current_user)

        print(lists)
        return redirect(url_for('index'))

    return render_template('workbook.html', form=form)

def create_temp_user(username):
    from app import user_manager # TODO remove this once users aren't created by the workbook upload
    user = User(username=username, active=True, password=app.user_manager.hash_password('asdf'))
    initiate_role = Role.query.filter_by(name='initiate').first()
    user.roles.append(initiate_role)
    return user

