from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    first_name = StringField("First Name:", validators=[DataRequired()])
    last_name = StringField("Last Name:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password_hash = PasswordField(
        "Password:",
        validators=[
            DataRequired(),
            EqualTo("password_hash2", message="Passwords Must Match!"),
        ],
    )
    password_hash2 = PasswordField("Confirm Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")
