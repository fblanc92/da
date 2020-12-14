import os

environ_dict = {
    "SECRET_KEY": "287aa0d2cf3f20e0e9c91ca1c052ac74",
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///site.db',
    "LC_ALL": "C.UTF-8",
    "LANG": "C.UTF-8",
    "EMAIL_USER": "defectapp.trl@gmail.com",
    "EMAIL_PASS": "hojalata"
}
for key in environ_dict:
    os.environ[key] = environ_dict[key]
    print(os.getenv(key))
print("Environment variables set")