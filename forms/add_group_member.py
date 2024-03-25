from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddGroupMemberForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    invite = SubmitField("Invite")
