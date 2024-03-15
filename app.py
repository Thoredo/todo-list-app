from flask import Flask, render_template, flash, request, redirect, url_for
from flask_migrate import Migrate
from flask_login import (
    login_user,
    login_required,
    logout_user,
    LoginManager,
)
from forms.register_form import RegisterForm
from forms.login import LoginForm
from dotenv import load_dotenv
import os
from database.tables import Users, db
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
    return Users.query.get(int(user_id))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    active_page = "account"

    return render_template("account.html", active_page=active_page)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")

        return render_template("/delete.html")
    except:
        flash("Error! Looks like there was a problem.... Try Again!")
        return render_template("/delete.html")


@app.route("/")
def index():
    active_page = "index"

    return render_template("index.html", active_page=active_page)


@app.route("/lists")
def lists():
    return render_template("/lists.html")


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


@app.route("/lists/new_list")
@login_required
def new_list():
    return render_template("new_list.html")


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
        else:
            flash("Email adress already in use")

        form.first_name.data = ""
        form.last_name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.password_hash.data = ""

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


@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
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
                "update.html", form=form, user_to_update=user_to_update, id=id
            )
        except:
            flash("Error! Looks like there was a problem.... Try Again!")
            return render_template(
                "update.html", form=form, user_to_update=user_to_update
            )
    else:
        return render_template(
            "update.html", form=form, user_to_update=user_to_update, id=id
        )


if __name__ == "__main__":
    app.run(debug=True)
