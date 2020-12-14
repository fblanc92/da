from flask import render_template, request, Blueprint
from Defect_analyzer_back.resources.config.configs_utils import get_current_config_json
from Defect_analyzer_front.defect_app.models import Coil_post
from Defect_analyzer_front.defect_app.main.forms import SearchForm
from flask import Flask, render_template, Response, redirect, url_for
import os
from random import randint

import json

captcha_blueprint = Blueprint('captcha_blueprint', __name__)


def get_images_in_captcha_folder():
    captcha_folder_path = r'c:/code/DA/Defect_analyzer_back/project_data/captcha'
    if not os.path.isdir(captcha_folder_path):
        os.makedirs(captcha_folder_path)
    img_filepaths = [os.path.join(captcha_folder_path, img_file) for img_file in os.listdir(captcha_folder_path)
                     if any(img_file.endswith(ext)
                            for ext in eval(get_current_config_json()['config']['input_images_formats']))
                     and os.path.isfile(
            os.path.join(captcha_folder_path, img_file.replace(img_file.split('.')[-1], 'xml')))]
    print(img_filepaths)


@captcha_blueprint.route("/captcha")
def captcha():
    get_images_in_captcha_folder()
    return render_template("captcha.html", title="Captcha")
