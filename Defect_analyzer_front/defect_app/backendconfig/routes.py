from flask_login import current_user, login_required
from flask import render_template, request, Blueprint, flash, redirect, url_for, abort
from Defect_analyzer_front.defect_app import db
from Defect_analyzer_front.defect_app.models import Backend_config, Coil_post
from Defect_analyzer_front.defect_app.backendconfig.forms import BackendConfigForm
from Defect_analyzer_back.resources.config.configs_utils import get_all_the_configs_list
from Defect_analyzer_back.resources.config.configs_utils import update_config, get_current_config_json, revert_config

backend_config_blueprint = Blueprint('backend_config_blueprint', __name__)


@backend_config_blueprint.route('/backend_config')
@login_required
def backend_config():  # Home | About | Analyzer Configs | Configurations
    page = request.args.get('page', 1, type=int)
    backend_config_list = get_all_the_configs_list()
    # configs = Backend_config.query.order_by(Backend_config.date_created.desc()).paginate(page=page, per_page=5)
    return render_template('backend_config.html', configs=backend_config_list)


@backend_config_blueprint.route("/backend_config/revert")
@login_required
def revert_backend_config():
    revert_config()
    backend_config_list = get_all_the_configs_list()
    return render_template('backend_config.html', configs=backend_config_list)


@backend_config_blueprint.route('/backend_config/new', methods=['GET', 'POST'])
@login_required
def edit_backend_config():  # no argument config_id argument because the idea is edit the ONLY config

    form = BackendConfigForm()
    if form.validate_on_submit():
        new_config = Backend_config(input_images_formats=form.input_images_formats.data,
                                    path_coils_folder=form.path_coils_folder.data,
                                    output_folder_suffix=form.output_folder_suffix.data,
                                    scan_timer_delay=form.scan_timer_delay.data,
                                    path_to_labels=form.path_to_labels.data,
                                    path_to_frozen_graph=form.path_to_frozen_graph.data,
                                    path_to_current_coil_register_folder=form.path_to_current_coil_register_folder.data,
                                    path_to_current_coil_register_json=form.path_to_current_coil_register_json.data,
                                    path_to_output_folders=form.path_to_output_folders.data,
                                    path_to_current_config_folder=form.path_to_current_config_folder.data,
                                    path_to_current_config_json=form.path_to_current_config_json.data,
                                    path_to_previous_config_folder=form.path_to_previous_config_folder.data,
                                    path_to_previous_config_file=form.path_to_previous_config_file.data,
                                    path_to_default_config_folder=form.path_to_default_config_folder.data,
                                    path_to_default_config_json=form.path_to_default_config_json.data,
                                    post_per_page=form.post_per_page.data,
                                    starting_date=form.starting_date.data,
                                    starting_time=form.starting_time.data,
                                    const_px_cm=form.const_px_cm.data,
                                    emails=form.emails.data,
                                    thresholds=form.thresholds.data)

        update_config(new_config.__dict__)
        flash('The configuration has been updated', 'success')
        return redirect(url_for('backend_config_blueprint.backend_config'))

    current_config_json = get_current_config_json()
    form.input_images_formats.data = current_config_json['config']['input_images_formats']
    form.path_coils_folder.data = current_config_json['config']['path_coils_folder']
    form.output_folder_suffix.data = current_config_json['config']['output_folder_suffix']
    form.scan_timer_delay.data = current_config_json['config']['scan_timer_delay']
    form.path_to_labels.data = current_config_json['config']['path_to_labels']
    form.path_to_frozen_graph.data = current_config_json['config']['path_to_frozen_graph']
    form.path_to_current_coil_register_folder.data = current_config_json['config'][
        'path_to_current_coil_register_folder']
    form.path_to_current_coil_register_json.data = current_config_json['config']['path_to_current_coil_register_json']
    form.path_to_output_folders.data = current_config_json['config']['path_to_output_folders']
    form.path_to_current_config_folder.data = current_config_json['config']['path_to_current_config_folder']
    form.path_to_current_config_json.data = current_config_json['config']['path_to_current_config_json']
    form.path_to_previous_config_folder.data = current_config_json['config']['path_to_previous_config_folder']
    form.path_to_previous_config_file.data = current_config_json['config']['path_to_previous_config_file']
    form.path_to_default_config_folder.data = current_config_json['config']['path_to_default_config_folder']
    form.path_to_default_config_json.data = current_config_json['config']['path_to_default_config_json']
    form.post_per_page.data = current_config_json['config']['post_per_page']
    form.starting_date.data = current_config_json['config']['starting_date']
    form.starting_time.data = current_config_json['config']['starting_time']
    form.const_px_cm.data = current_config_json['config']['const_px_cm']
    form.emails.data = current_config_json['emails']
    form.thresholds.data = current_config_json['thresholds']

    return render_template('edit_backend_config.html', title='Edit Config', form=form, legend='Edit Config')
