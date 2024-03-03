from flask import Flask, render_template, flash
from forms.register_form import RegisterForm
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import os


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.app_context().push()

db = SQLAlchemy(app)


# create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Name %r>" % self.first_name


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
            user = Users(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
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


if __name__ == "__main__":
    app.run(debug=True)
