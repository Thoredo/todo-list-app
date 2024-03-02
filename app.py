from flask import Flask, render_template, flash
from forms.register_form import RegisterForm
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


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
        first_name = form.first_name.data
        form.first_name.data = ""

        last_name = form.last_name.data
        form.last_name.data = ""

        email = form.email.data
        form.email.data = ""
        flash("Successfully registered")

    return render_template(
        "register.html",
        first_name=first_name,
        last_name=last_name,
        email=email,
        form=form,
    )


if __name__ == "__main__":
    app.run(debug=True)
