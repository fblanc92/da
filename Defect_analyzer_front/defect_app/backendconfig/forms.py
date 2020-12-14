from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class BackendConfigForm(FlaskForm):
    input_images_formats = StringField('Input Images Fomats', validators=[DataRequired()])
    path_coils_folder = StringField('Input Path', validators=[DataRequired()])
    output_folder_suffix = StringField('Output Forder Suffix', validators=[DataRequired()])
    # pasar a float
    scan_timer_delay = StringField('Scan Timer [sec]', validators=[DataRequired()])
    path_to_labels = StringField('Labelmap Path', validators=[DataRequired()])
    path_to_frozen_graph = StringField('Graph Path', validators=[DataRequired()])
    path_to_current_coil_register_folder = StringField('Coil Register Path', validators=[DataRequired()])
    path_to_current_coil_register_json = StringField('Coil Register File [.json]', validators=[DataRequired()])
    path_to_output_folders = StringField('Output Path', validators=[DataRequired()])
    path_to_current_config_folder = StringField('Current Config Path', validators=[DataRequired()])
    path_to_current_config_json = StringField('Current Config File[.json]', validators=[DataRequired()])
    path_to_previous_config_folder = StringField('Previous Config Path', validators=[DataRequired()])
    path_to_previous_config_file = StringField('Previous Config File [.json]', validators=[DataRequired()])
    path_to_default_config_folder = StringField('Default Config Folder', validators=[DataRequired()])
    path_to_default_config_json = StringField('Default Config File [.json]', validators=[DataRequired()])
    post_per_page = StringField('Post Per Page', validators=[DataRequired()])
    starting_date = StringField('Starting Date to Analyze yyyy/mm/dd', validators=[DataRequired()])
    starting_time = StringField('Starting Time to Analyze hh:mm:ss', validators=[DataRequired()])
    const_px_cm = StringField('Const px/cm', validators=[DataRequired()])
    emails = StringField('Emails', validators=[DataRequired()])
    thresholds = StringField('Thresholds', validators=[DataRequired()])
    submit = SubmitField('Create')
