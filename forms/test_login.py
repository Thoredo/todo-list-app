from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class PasswordForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Login")
