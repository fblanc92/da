from flask import render_template, request, Blueprint
from Defect_analyzer_front.defect_app.models import Post
from Defect_analyzer_back.resources.config.configs_utils import get_current_config_json
from Defect_analyzer_front.defect_app.models import Coil_post
from Defect_analyzer_front.defect_app.main.forms import SearchForm

from flask import Flask, render_template, Response,redirect,url_for
from random import randint

import json

main = Blueprint('main', __name__)


@main.route("/data")
def chart_data(data=None):
    data_set = []
    for x in range(0, 12):
        y = randint(1, 12)
        data_set.append(y)
    data = {}
    data['set'] = data_set
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    # {"set": [9, 9, 12, 6, 9, 8, 7, 10, 2, 5, 2, 7]}
    return resp


@main.route("/",methods=['GET','POST'])
@main.route("/home",methods=['GET','POST'])
def home(data=None):
    def get_categories_and_areas():
        area_dicts_for_all_coilposts = [eval(el.areas) for el in Coil_post.query.order_by(Coil_post.date_posted.desc())]
        categories = [[categ for categ in area_dict] for area_dict in area_dicts_for_all_coilposts]
        areas = [[int(mydict[val]) for val in mydict] for mydict in area_dicts_for_all_coilposts]
        return categories, areas

    form=SearchForm()
    if form.validate_on_submit():
        post = Coil_post.query.filter_by(coil_id=form.coil_to_search_id.data).first()
        return redirect(url_for('coilposts_blueprint.post', post_id=post.id))

    page = request.args.get('page', 1, type=int)
    post_per_page = get_current_config_json()['config']['post_per_page']
    posts = Coil_post.query.order_by(Coil_post.date_posted.desc()).paginate(page=page, per_page=post_per_page)
    categories_per_coil, areas_per_coil = get_categories_and_areas()
    data = {}
    data['title'] = 'Chart'
    return render_template('home.html', data=data, posts=posts, title='Defect Analyzer',form=form)

@main.route("/search",methods=['POST','GET'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        post = Coil_post.query.filter_by(post_id=form.coil_to_search_id.data)
        return redirect(url_for('coilposts_blueprint.post', post_id=post.coil_id))
    data={}
    data['title']='Chart'

    page = request.args.get('page', 1, type=int)
    post_per_page = get_current_config_json()['config']['post_per_page']
    posts = Coil_post.query.order_by(Coil_post.date_posted.desc()).paginate(page=page, per_page=post_per_page)

    return render_template('home.html', data=data, posts=posts, title='Defect Analyzer',form=form)

@main.route('/about')
def about():
    return render_template('about.html', title='About')
