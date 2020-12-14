from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    coil_to_search_id = StringField('Search Coil', validators=[DataRequired()])
    submit = SubmitField('Search')
