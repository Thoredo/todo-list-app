from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, RadioField
from wtforms.validators import DataRequired


class AddTaskForm(FlaskForm):
    task_name = StringField("Task Name:", validators=[DataRequired()])
    priority = SelectField(
        "Priority:", choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")]
    )
    due_date = DateField("Due Date:", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Submit")
