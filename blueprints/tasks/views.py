from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_required
from forms.add_task import AddTaskForm
from forms.edit_tasks import EditTaskForm
from database.tables import db, Lists, GroupMembers, Users, Tasks
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__, template_folder="templates")


@tasks_bp.route("/<int:list_id>/add_task", methods=["GET", "POST"])
@login_required
def add_task(list_id):
    form = AddTaskForm()
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members_ids = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members_ids.append(user_info.id)
    if form.validate_on_submit():
        new_task = Tasks(
            list_id=list_id,
            task_name=form.task_name.data,
            created_at=datetime.now(),
            priority=form.priority.data,
            due_date=form.due_date.data,
        )
        db.session.add(new_task)
        db.session.commit()

        form.task_name.data = ""
        form.priority.data = ""

        flash("Task Added!")
        return redirect(url_for("lists.view_list", list_id=list_id))
    return render_template(
        "add_task.html",
        form=form,
        list=list,
        group_members_ids=group_members_ids,
        list_id=list_id,
    )


@tasks_bp.route("/<int:list_id>/<int:task_id>/delete", methods=["GET", "POST"])
@login_required
def delete_task(list_id, task_id):
    task_to_delete = Tasks.query.get_or_404(task_id)
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members_ids = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members_ids.append(user_info.id)
    tasks = Tasks.query.filter_by(list_id=list.list_id)
    date = datetime.now()
    today = date.date()

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash("Task Deleted Successfully!!")
        return redirect(url_for("lists.view_list", list_id=list_id))
    except:
        flash("Error! Looks like there was a problem.... Try Again!")
        return redirect(url_for("lists.view_list", list_id=list_id))


@tasks_bp.route("/<int:list_id>/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(list_id, task_id):
    form = EditTaskForm()
    task_to_edit = Tasks.query.get_or_404(task_id)
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members_ids = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members_ids.append(user_info.id)
    if request.method == "POST":
        task_to_edit.task_name = request.form["task_name"]
        task_to_edit.priority = request.form["priority"]
        task_to_edit.due_date = request.form["due_date"]
        if request.form["finished"] == "True":
            task_to_edit.finished = True
        else:
            task_to_edit.finished = False
        try:
            db.session.commit()
            flash("Task Updated Successfully!")
            return redirect(url_for("lists.view_list", list_id=list_id))
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return render_template(
                "edit_task.html",
                form=form,
                list_id=list_id,
                task_id=task_id,
                task_to_edit=task_to_edit,
                group_members_ids=group_members_ids,
            )
    return render_template(
        "edit_task.html",
        form=form,
        list_id=list_id,
        task_id=task_id,
        task_to_edit=task_to_edit,
        group_members_ids=group_members_ids,
    )
