import os

class Config():
    SECRET_KEY = '287aa0d2cf3f20e0e9c91ca1c052ac74'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    #SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = "287aa0d2cf3f20e0e9c91ca1c052ac74"
    #SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    # SQLALCHEMY_TRACK_MODIFICATIONS = False
