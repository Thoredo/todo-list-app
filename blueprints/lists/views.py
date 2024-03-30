from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from database.tables import db, Lists, Tasks, GroupMembers, Groups, Users
from forms.new_list import NewListForm
from datetime import datetime

lists_bp = Blueprint("lists", __name__, template_folder="templates")


@lists_bp.route("/delete_list/<int:list_id>", methods=["GET", "POST"])
def delete_list(list_id):

    list_to_delete = Lists.query.get_or_404(list_id)

    if current_user.id == list_to_delete.list_owner_id:
        try:
            # Delete tasks
            tasks_to_delete = Tasks.query.filter_by(list_id=list_id).all()

            for task in tasks_to_delete:
                db.session.delete(task)
            db.session.commit()

            # Remove people that were in the list group
            group_members = GroupMembers.query.filter_by(
                group_id=list_to_delete.group_id
            ).all()
            for member in group_members:
                db.session.delete(member)
            db.session.commit()

            # Remove the list
            db.session.delete(list_to_delete)
            db.session.commit()

            # Remove the group connected to the list
            group_to_delete = Groups.query.filter_by(
                group_id=list_to_delete.group_id
            ).all()
            db.session.delete(group_to_delete)
            db.session.commit()

            flash("List Deleted Successfully!!")

            return redirect(url_for("lists.personal_lists"))
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return redirect(url_for("lists.personal_lists"))
    else:
        flash("Please Don't Try To Delete Other Peoples Lists. That Is Not Nice!")
        return redirect(url_for("lists.personal_lists"))


@lists_bp.route("/<int:list_id>/edit_name", methods=["GET", "POST"])
@login_required
def edit_list_name(list_id):
    form = NewListForm()
    list_to_edit = Lists.query.get_or_404(list_id)
    if request.method == "POST":
        list_to_edit.list_name = request.form["list_name"]
        try:
            db.session.commit()
            flash("List Name Updated Successfully!")
            return redirect(url_for("lists.personal_lists"))
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return redirect(url_for("lists.personal_lists"))
    else:
        return render_template(
            "edit_list_name.html", form=form, list_to_edit=list_to_edit
        )


@lists_bp.route("/")
@login_required
def lists():
    active_page = "lists"
    return render_template("/lists.html", active_page=active_page)


@lists_bp.route("/new_list", methods=["GET", "POST"])
@login_required
def new_list():
    form = NewListForm()
    if form.validate_on_submit():
        # Create new group
        new_group = Groups()
        db.session.add(new_group)
        db.session.commit()

        # Add creator as first member
        group_member = GroupMembers(
            group_id=new_group.group_id, user_id=current_user.id
        )
        db.session.add(group_member)
        db.session.commit()

        creator = current_user.id
        new_list = Lists(
            list_name=form.list_name.data,
            list_owner_id=creator,
            group_id=new_group.group_id,
        )
        db.session.add(new_list)
        db.session.commit()
        flash("List Created!")
    return render_template("new_list.html", form=form)


@lists_bp.route("/personal_lists")
@login_required
def personal_lists():
    lists_with_active_tasks = []
    lists = Lists.query.filter_by(list_owner_id=current_user.id)
    for list in lists:
        active_tasks_count = Tasks.query.filter_by(
            list_id=list.list_id, finished=False
        ).count()
        lists_with_active_tasks.append((list, active_tasks_count))
    return render_template(
        "personal_lists.html",
        lists_with_active_tasks=lists_with_active_tasks,
    )


@lists_bp.route("/shared_lists")
@login_required
def shared_lists():
    lists_with_active_tasks = []
    groups = GroupMembers.query.filter_by(user_id=current_user.id)
    group_ids = [group.group_id for group in groups]
    lists = Lists.query.filter(
        Lists.group_id.in_(group_ids), Lists.list_owner_id != current_user.id
    )
    for list in lists:
        active_tasks_count = Tasks.query.filter_by(
            list_id=list.list_id, finished=False
        ).count()
        lists_with_active_tasks.append((list, active_tasks_count))
    return render_template(
        "shared_lists.html",
        lists_with_active_tasks=lists_with_active_tasks,
    )


@lists_bp.route("/<int:list_id>", methods=["GET", "POST"])
@login_required
def view_list(list_id):
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members_ids = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members_ids.append(user_info.id)
    tasks = Tasks.query.filter_by(list_id=list.list_id)
    date = datetime.now()
    today = date.date()

    return render_template(
        "view_list.html",
        list=list,
        group_members_ids=group_members_ids,
        list_id=list_id,
        tasks=tasks,
        today=today,
    )
