from Defect_analyzer_front.defect_app import db, login_manager
from flask import current_app
from flask_login import UserMixin
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    # configs = db.relationship('Backend_config', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.datetime.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"


class Coil_post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # (post_id)
    coil_id = db.Column(db.String(15), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.datetime.now())
    time = db.Column(db.String(20), nullable=False)
    path = db.Column(db.String(300), nullable=False)
    areas = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"Coil:{self.coil_id}','Date-time:{self.date} - {self.time}','Path:{self.path}','Areas:{self.areas}')"


class Backend_config:
    def __init__(self, input_images_formats,
                 path_coils_folder,
                 output_folder_suffix,
                 scan_timer_delay,
                 path_to_labels,
                 path_to_frozen_graph,
                 path_to_current_coil_register_folder,
                 path_to_current_coil_register_json,
                 path_to_output_folders,
                 path_to_current_config_folder,
                 path_to_current_config_json,
                 path_to_previous_config_folder,
                 path_to_previous_config_file,
                 path_to_default_config_folder,
                 path_to_default_config_json,
                 post_per_page,
                 starting_date,
                 starting_time,
                 const_px_cm,
                 emails,
                 thresholds):
        self.date_created = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.input_images_formats = input_images_formats
        self.path_coils_folder = path_coils_folder
        self.output_folder_suffix = output_folder_suffix
        self.scan_timer_delay = scan_timer_delay
        self.path_to_labels = path_to_labels
        self.path_to_frozen_graph = path_to_frozen_graph
        self.path_to_current_coil_register_folder = path_to_current_coil_register_folder
        self.path_to_current_coil_register_json = path_to_current_coil_register_json
        self.path_to_output_folders = path_to_output_folders
        self.path_to_current_config_folder = path_to_current_config_folder
        self.path_to_current_config_json = path_to_current_config_json
        self.path_to_previous_config_folder = path_to_previous_config_folder
        self.path_to_previous_config_file = path_to_previous_config_file
        self.path_to_default_config_folder = path_to_default_config_folder
        self.path_to_default_config_json = path_to_default_config_json
        self.post_per_page = post_per_page
        self.starting_date = starting_date
        self.starting_time = starting_time
        self.const_px_cm = const_px_cm
        self.emails = emails
        self.thresholds = thresholds
