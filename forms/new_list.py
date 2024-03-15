from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewListForm(FlaskForm):
    list_name = StringField("List Name:", validators=[DataRequired()])
    create = SubmitField("Create")
