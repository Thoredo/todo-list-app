from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from database.tables import db, Lists, Tasks, GroupMembers, Groups, Users
from forms.new_list import NewListForm
from datetime import datetime
from sqlalchemy import case
from active_invites import get_amount_invites

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

            # Get group id
            group_id = list_to_delete.group_id

            # Remove the list
            db.session.delete(list_to_delete)
            db.session.commit()

            # Remove the group connected to the list
            group_to_delete = Groups.query.filter_by(group_id=group_id).first()
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
        active_invites = get_amount_invites()
        return render_template(
            "edit_list_name.html",
            form=form,
            list_to_edit=list_to_edit,
            active_invites=active_invites,
        )


@lists_bp.route("/")
@login_required
def lists():
    active_page = "lists"
    active_invites = get_amount_invites()

    return render_template(
        "/lists.html", active_page=active_page, active_invites=active_invites
    )


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

        active_invites = get_amount_invites()
    return render_template("new_list.html", form=form, active_invites=active_invites)


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

    active_invites = get_amount_invites()

    return render_template(
        "personal_lists.html",
        lists_with_active_tasks=lists_with_active_tasks,
        active_invites=active_invites,
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

    active_invites = get_amount_invites()

    return render_template(
        "shared_lists.html",
        lists_with_active_tasks=lists_with_active_tasks,
        active_invites=active_invites,
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

    # Check if sorting directions are stored in session
    if "colum_directions" not in session:
        session["colum_directions"] = {
            "name_direction": "asc",
            "priority_direction": "asc",
            "date_direction": "asc",
            "status_direction": "asc",
        }

    # Retrieve sorting directions from session
    column_directions = session["colum_directions"]

    column = request.args.get("column", "task_name")
    direction = request.args.get("direction", "asc")

    date = datetime.now()
    today = date.date()

    # Fetch tasks from the database based on sorting parameters
    if column == "priority":
        tasks = handle_priority_sort(direction, column_directions, list_id)
    elif column == "due_date":
        tasks = handle_due_date_sort(direction, column_directions, list_id)
    elif column == "status":
        tasks = handle_status_sort(direction, column_directions, list_id)
    else:  # Default to sorting by task name
        tasks = handle_name_sort(direction, column_directions, list_id)

    active_invites = get_amount_invites()

    return render_template(
        "view_list.html",
        list=list,
        group_members_ids=group_members_ids,
        list_id=list_id,
        tasks=tasks,
        today=today,
        colum_directions=column_directions,
        active_invites=active_invites,
    )


def handle_priority_sort(direction, column_directions, list_id):
    # Define the custom sort orders
    descending_priority_order = {"high": 1, "medium": 2, "low": 3}
    ascending_priority_order = {"low": 1, "medium": 2, "high": 3}
    # Create a case statement for descending sort order
    descending_priority_case = case(
        descending_priority_order,
        value=Tasks.priority,
        else_=len(descending_priority_order) + 1,
    )
    # Create a case statement for ascending sort order
    ascending_priority_case = case(
        ascending_priority_order,
        value=Tasks.priority,
        else_=len(ascending_priority_order) + 1,
    )
    if direction == "asc":
        tasks = (
            Tasks.query.filter_by(list_id=list_id)
            .order_by(ascending_priority_case)
            .all()
        )
        column_directions["priority_direction"] = "asc"
    else:
        tasks = (
            Tasks.query.filter_by(list_id=list_id)
            .order_by(descending_priority_case)
            .all()
        )
        column_directions["priority_direction"] = "desc"

    return tasks


def handle_due_date_sort(direction, column_directions, list_id):
    if direction == "asc":
        tasks = (
            Tasks.query.filter_by(list_id=list_id).order_by(Tasks.due_date.asc()).all()
        )
        column_directions["date_direction"] = "asc"
    else:
        tasks = (
            Tasks.query.filter_by(list_id=list_id).order_by(Tasks.due_date.desc()).all()
        )
        column_directions["date_direction"] = "desc"

    return tasks


def handle_status_sort(direction, column_directions, list_id):
    if direction == "asc":
        tasks = (
            Tasks.query.filter_by(list_id=list_id)
            .order_by(Tasks.finished.asc(), Tasks.due_date.asc())
            .all()
        )
        column_directions["status_direction"] = "asc"
    else:
        tasks = (
            Tasks.query.filter_by(list_id=list_id)
            .order_by(Tasks.finished.desc(), Tasks.due_date.desc())
            .all()
        )
        column_directions["status_direction"] = "desc"
    return tasks


def handle_name_sort(direction, column_directions, list_id):
    if direction == "asc":
        tasks = (
            Tasks.query.filter_by(list_id=list_id).order_by(Tasks.task_name.asc()).all()
        )
        column_directions["name_direction"] == "asc"
    else:
        tasks = (
            Tasks.query.filter_by(list_id=list_id)
            .order_by(Tasks.task_name.desc())
            .all()
        )
        column_directions["name_direction"] = "desc"
    return tasks
