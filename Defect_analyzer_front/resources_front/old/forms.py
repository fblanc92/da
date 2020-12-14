from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from defect_app.models import User



class ConfigurationForm(FlaskForm):
    config_1 = StringField('config_1', validators=[DataRequired()])
    config_2 = StringField('config_2', validators=[DataRequired()])
    config_3 = StringField('config_3', validators=[DataRequired()])
    config_4 = StringField('config_4', validators=[DataRequired()])
    config_5 = StringField('config_5', validators=[DataRequired()])
    config_6 = StringField('config_6', validators=[DataRequired()])
    config_7 = StringField('config_7', validators=[DataRequired()])
    config_8 = StringField('config_8', validators=[DataRequired()])
    config_9 = StringField('config_9', validators=[DataRequired()])
    config_10 = StringField('config_10', validators=[DataRequired()])
    config_11 = StringField('config_11', validators=[DataRequired()])
    submit = SubmitField('Configure')
