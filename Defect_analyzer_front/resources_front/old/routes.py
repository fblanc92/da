import secrets, os
from PIL import Image
from defect_app.forms import RegistrationForm, LoginForm, ConfigurationForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from defect_app.models import User, Post
from defect_app import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message




# posts_default = [
# 	{	'bobina':'1234567',
# 		'fecha':'04-08-20',
# 		'hora':'13:14:15',
# 		'linea':'TRL',
# 		'imagen':'IMG_000.JPG',
# 		'nota':'Esta es la primera bobina'
# 	},
# 	{
# 		'bobina':'1234567_2',
# 		'fecha':'05-08-20',
#                 'hora':'14:15:16',
# 		'linea':'TRL',
# 		'imagen':'IMG_001.JPG',
# 		'nota':'Esta es la segunda bobina'
# 	}
# ]



@app.route('/config', methods=['GET','POST'])
def config():
    form = ConfigurationForm()
    if form.validate_on_submit():
        flash('Configuracion creada','success')
    return render_template('config.html', title='Configuración',form=form)






# @app.route("/post/<int:posts_default>")
# def post(post_id):
# 	post = Post.query.get_or_404(post_id)
# 	return render_template('post.html', title=post.title, post=post)
