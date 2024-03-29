from flask import Blueprint, render_template, flash, redirect, url_for, request
from database.tables import db, Users
from forms.register_form import RegisterForm
from forms.login import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    active_page = "account"

    return render_template("account.html", active_page=active_page)


@auth_bp.route("/delete/<int:id>", methods=["GET", "POST"])
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


@auth_bp.route("/edit_user/<int:id>", methods=["GET", "POST"])
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


@auth_bp.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("auth.account"))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That Username Doesn't Exist! Try Again!")

    return render_template("login.html", form=form, active_page=active_page)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You Logged Out!")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
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

    return render_template(
        "register.html",
        first_name=first_name,
        last_name=last_name,
        email=email,
        form=form,
        active_page=active_page,
    )
