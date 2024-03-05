from flask import Flask, render_template, flash, request
from flask_migrate import Migrate
from forms.register_form import RegisterForm
from dotenv import load_dotenv
import os
from database.users import Users, db

load_dotenv()

app = Flask(__name__)
# MYSQL db
mysql_pass = os.getenv("MYSQL_PASS")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://root:{mysql_pass}@localhost/jurgenst_flask_users"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.app_context().push()

db.init_app(app)  # Initialize db with the Flask app
migrate = Migrate(app, db)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register.html", methods=["GET", "POST"])
def register():
    first_name = None
    last_name = None
    email = None
    form = RegisterForm()

    # Validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            full_name = form.first_name.data + " " + form.last_name.data
            user = Users(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                full_name=full_name,
                email=form.email.data,
            )
            db.session.add(user)
            db.session.commit()
            flash("Successfully registered")
        else:
            flash("Email adress already in use")

        first_name = form.first_name.data
        form.first_name.data = ""

        last_name = form.last_name.data
        form.last_name.data = ""

        email = form.email.data
        form.email.data = ""

    our_users = Users.query.order_by(Users.date_added)
    return render_template(
        "register.html",
        first_name=first_name,
        last_name=last_name,
        email=email,
        form=form,
        our_users=our_users,
    )


@app.route("/update/<int:id>", methods=["GET", "POST"])
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
                "update.html", form=form, user_to_update=user_to_update
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


if __name__ == "__main__":
    app.run(debug=True)
