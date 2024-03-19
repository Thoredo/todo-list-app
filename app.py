from flask import Flask, render_template, flash, request, redirect, url_for
from flask_migrate import Migrate
from flask_login import (
    login_user,
    login_required,
    logout_user,
    LoginManager,
    current_user,
)
from forms.register_form import RegisterForm
from forms.login import LoginForm
from forms.new_list import NewListForm
from forms.add_task import AddTaskForm
from forms.edit_tasks import EditTaskForm
from forms.add_group_member import AddGroupMemberForm
from dotenv import load_dotenv
import os
from datetime import datetime
from database.tables import Users, Lists, Groups, GroupMembers, Tasks, db
from werkzeug.security import generate_password_hash, check_password_hash

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
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    active_page = "account"

    return render_template("account.html", active_page=active_page)


@app.route("/lists/<int:list_id>/group/add_member", methods=["GET", "POST"])
@login_required
def add_group_member(list_id):
    form = AddGroupMemberForm()
    list = db.session.get(Lists, list_id)
    user = Users.query.filter_by(username=form.username.data).first()
    if form.validate_on_submit():
        new_group_member = GroupMembers(group_id=list.group_id, user_id=user.id)
        db.session.add(new_group_member)
        db.session.commit()

        form.username.data = ""

        flash("Member Added!")
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
        return redirect(url_for("view_list", list_id=list_id))
    return render_template(
        "add_task.html",
        form=form,
        list=list,
        group_members_ids=group_members_ids,
        list_id=list_id,
    )


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_account(id):
    user_to_delete = Users.query.get_or_404(id)

    if current_user.id == user_to_delete.id:
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!!")

            return render_template("delete.html")
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return render_template("delete.html")
    else:
        flash("Please Don't Try To Delete Other Peoples Account. That Is Not Nice!")
        return render_template("delete.html")


@app.route("/lists/delete_list/<int:list_id>", methods=["GET", "POST"])
def delete_list(list_id):
    list_to_delete = Lists.query.get_or_404(list_id)

    if current_user.id == list_to_delete.list_owner_id:
        try:
            db.session.delete(list_to_delete)
            db.session.commit()
            flash("List Deleted Successfully!!")

            return redirect(url_for("personal_lists"))
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return redirect(url_for("personal_lists"))
    else:
        flash("Please Don't Try To Delete Other Peoples Lists. That Is Not Nice!")
        return redirect(url_for("personal_lists"))


@app.route("/lists/<int:list_id>/<int:task_id>/delete")
@login_required
def delete_task(list_id, task_id):
    task_to_delete = Tasks.query.get_or_404(task_id)
    list = db.session.get(Lists, list_id)
    group = GroupMembers.query.filter_by(group_id=list.group_id)
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
            group=group,
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


@app.route("/lists/<int:list_id>/edit_name", methods=["GET", "POST"])
@login_required
def edit_list_name(list_id):
    form = NewListForm()
    list_to_edit = Lists.query.get_or_404(list_id)
    if request.method == "POST":
        list_to_edit.list_name = request.form["list_name"]
        try:
            db.session.commit()
            flash("List Name Updated Successfully!")
            return redirect(url_for("personal_lists"))
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return redirect(url_for("personal_lists"))
    else:
        return render_template(
            "edit_list_name.html", form=form, list_to_edit=list_to_edit
        )


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


@app.route("/edit_user/<int:id>", methods=["GET", "POST"])
@login_required
def edit_user(id):
    form = RegisterForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        user_to_update.first_name = request.form["first_name"]
        user_to_update.last_name = request.form["last_name"]
        user_to_update.email = request.form["email"]
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template(
                "edit_user.html", form=form, user_to_update=user_to_update, id=id
            )
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return render_template(
                "edit_user.html", form=form, user_to_update=user_to_update
            )
    else:
        return render_template(
            "edit_user.html", form=form, user_to_update=user_to_update, id=id
        )


@app.route("/")
def index():
    active_page = "index"

    return render_template("index.html", active_page=active_page)


@app.route("/lists")
def lists():
    active_page = "lists"
    return render_template("/lists.html", active_page=active_page)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    active_page = "login"

    if form.validate_on_submit():
        # Lookup user
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for("account"))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That Username Doesn't Exist! Try Again!")

    return render_template("login.html", form=form, active_page=active_page)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You Logged Out!")
    return redirect(url_for("login"))


@app.route("/lists/new_list", methods=["GET", "POST"])
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


@app.route("/lists/personal_lists")
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


@app.route("/register", methods=["GET", "POST"])
def register():
    first_name = None
    last_name = None
    email = None
    form = RegisterForm()
    active_page = "register"

    # Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            full_name = form.first_name.data + " " + form.last_name.data
            # Hash password
            hashed_pw = generate_password_hash(
                form.password_hash.data, method="pbkdf2:sha256"
            )

            user = Users(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                full_name=full_name,
                email=form.email.data,
                password_hash=hashed_pw,
            )
            db.session.add(user)
            db.session.commit()
            flash("Successfully registered")

            form.first_name.data = ""
            form.last_name.data = ""
            form.username.data = ""
            form.email.data = ""
            form.password_hash.data = ""
        else:
            flash("Email adress already in use")

    our_users = Users.query.order_by(Users.date_added)
    return render_template(
        "register.html",
        first_name=first_name,
        last_name=last_name,
        email=email,
        form=form,
        our_users=our_users,
        active_page=active_page,
    )


@app.route("/lists/shared_lists")
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
        "personal_lists.html",
        lists_with_active_tasks=lists_with_active_tasks,
    )


@app.route("/lists/<int:list_id>")
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
        "view_list_group.html", group_members=group_members, list_id=list_id
    )


if __name__ == "__main__":
    app.run(debug=True)
