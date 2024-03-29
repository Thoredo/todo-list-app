from flask import Flask, render_template, flash, request, redirect, url_for
from flask_migrate import Migrate
from flask_login import (
    login_required,
    LoginManager,
    current_user,
)
from forms.add_task import AddTaskForm
from forms.edit_tasks import EditTaskForm
from forms.add_group_member import AddGroupMemberForm
from dotenv import load_dotenv
import os
from datetime import datetime
from database.tables import db, Users, Lists, GroupMembers, Tasks, GroupInvites
from auth.views import auth_bp
from lists.views import lists_bp

load_dotenv()

app = Flask(__name__)
# MYSQL db
mysql_pass = os.getenv("MYSQL_PASS")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://root:{mysql_pass}@localhost/jurgenst_flask_users"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.app_context().push()

db.init_app(app)
migrate = Migrate(app, db)

# Flask_login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(lists_bp, url_prefix="/lists")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


@app.route("/invites/<int:list_id>/accept")
@login_required
def accept_invite(list_id):
    # See if invite exists
    invite = GroupInvites.query.filter_by(
        list_id=list_id, recipient_id=current_user.id
    ).first()

    if invite:
        # join group of the list
        list = db.session.get(Lists, list_id)
        new_group_member = GroupMembers(group_id=list.group_id, user_id=current_user.id)
        db.session.add(new_group_member)
        db.session.commit()
        # remove invite
        db.session.delete(invite)
        db.session.commit()
        flash("Invite Accepted!")

    return redirect(url_for("group_invites"))


@app.route("/lists/<int:list_id>/group/add_member", methods=["GET", "POST"])
@login_required
def add_group_member(list_id):
    form = AddGroupMemberForm()
    list = db.session.get(Lists, list_id)

    if form.validate_on_submit():
        recipient = Users.query.filter_by(username=form.username.data).first()
        if recipient:
            if GroupMembers.query.filter_by(
                user_id=recipient.id, group_id=list.group_id
            ).first():
                flash("This user is already a member of the group!", "danger")
            elif GroupInvites.query.filter_by(
                recipient_id=recipient.id, list_id=list_id
            ).first():
                flash("This user is already has an invite to this group!", "danger")
            else:
                new_invite = GroupInvites(
                    sender_id=current_user.id,
                    recipient_id=recipient.id,
                    list_id=list_id,
                )
                db.session.add(new_invite)
                db.session.commit()

                form.username.data = ""
                flash("Invite sent successfully!", "success")
        else:
            flash("User not found!", "danger")
    return render_template("add_member.html", form=form, list_id=list_id)


@app.route("/lists/<int:list_id>/add_task", methods=["GET", "POST"])
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


@app.route("/lists/<int:list_id>/<int:task_id>/delete", methods=["GET", "POST"])
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
        return render_template(
            "view_list.html",
            list=list,
            group_members_ids=group_members_ids,
            list_id=list_id,
            tasks=tasks,
            today=today,
        )
    except:
        flash("Error! Looks like there was a problem.... Try Again!")
        return render_template(
            "view_list.html",
            list=list,
            group=group,
            list_id=list_id,
            tasks=tasks,
            today=today,
        )


@app.route("/invites/<int:list_id>/deny")
@login_required
def deny_invite(list_id):
    # See if invite exists
    invite = GroupInvites.query.filter_by(
        list_id=list_id, recipient_id=current_user.id
    ).first()

    if invite:
        # remove invite
        db.session.delete(invite)
        db.session.commit()
        flash("Invite Denied!")

    return redirect(url_for("group_invites"))


@app.route("/lists/<int:list_id>/<int:task_id>/edit", methods=["GET", "POST"])
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
            return redirect(url_for("view_list", list_id=list_id))
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


@app.route("/invites")
@login_required
def group_invites():
    active_page = "invites"
    invites = GroupInvites.query.filter_by(recipient_id=current_user.id).all()
    all_lists = []
    if invites:
        for invite in invites:
            list = db.session.get(Lists, invite.list_id)
            list_name = list.list_name
            list_id = list.list_id
            user = db.session.get(Users, list.list_owner_id)
            sender_name = user.full_name
            all_lists.append(
                {"list_name": list_name, "sender_name": sender_name, "list_id": list_id}
            )
    return render_template("invites.html", active_page=active_page, all_lists=all_lists)


@app.route("/")
def index():
    active_page = "index"

    return render_template("index.html", active_page=active_page)


@app.route("/lists/<int:list_id>/group/leave")
@login_required
def leave_group(list_id):
    list = db.session.get(Lists, list_id)
    member_leaving = GroupMembers.query.filter_by(
        user_id=current_user.id, group_id=list.group_id
    ).first()
    try:
        db.session.delete(member_leaving)
        db.session.commit()
        flash("Succesfully Left Group!!")
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
    except:
        flash("There was an error leaving the group, try again!!")
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


@app.route("/lists/<int:list_id>/group/remove_member/<int:user_id>")
@login_required
def remove_member(list_id, user_id):
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members.append(user_info)

    user_to_remove = GroupMembers.query.filter_by(
        user_id=user_id, group_id=list.group_id
    ).first()

    try:
        db.session.delete(user_to_remove)
        db.session.commit()
        flash("User Removed Successfully!!")
        group_members = []
        for member in group:
            user_info = db.session.get(Users, member.user_id)
            group_members.append(user_info)
        return render_template(
            "view_list_group.html",
            group_members=group_members,
            list_id=list_id,
            list=list,
        )
    except:
        flash("Error! Looks like there was a problem.... Try Again!")
        return render_template(
            "view_list_group.html",
            group_members=group_members,
            list_id=list_id,
            list=list,
        )


@app.route("/lists/<int:list_id>/group")
@login_required
def view_list_group(list_id):
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
    group_members = []
    for member in group:
        user_info = db.session.get(Users, member.user_id)
        group_members.append(user_info)
    return render_template(
        "view_list_group.html", group_members=group_members, list_id=list_id, list=list
    )


if __name__ == "__main__":
    app.run(debug=True)
