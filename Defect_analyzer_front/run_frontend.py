from Defect_analyzer_front.defect_app import create_app, db


app = create_app()  # nothing given as arg because Config class is default


def init_db():
    context = app.app_context()
    context.push()
    if 'users' not in db.get_engine(app=app, bind=None).table_names():
        db.create_all()
    return


def start_frontend():
    app.run(host='0.0.0.0', port=5000)