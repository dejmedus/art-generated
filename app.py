from flask import Flask, render_template, request, session, redirect, url_for

import openai
import base64

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# os: get operating system / re: regex out unwanted name chars
import os
import re

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
# initialize the app with the extension
db.init_app(app)

# initialize flask-migrate with the application instance (app) and the Flask-SQLAlchemy database instance (db)
migrate = Migrate(app, db)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")
app.secret_key = os.getenv("KEY")


# define a model class
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    prompt = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)


# create the table schema in the database
with app.app_context():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def index():
    current_prompt = None
    image_src = None

    if request.method == "POST":
        # create image with generate image form data
        if 'generate_image' in request.form:
            prompt = request.form["prompt"]
            movement = request.form['movement']
            current_prompt = f'{prompt}, {movement}'

            try:
                # create image with DALLE
                response = openai.Image.create(
                    prompt=current_prompt,
                    n=1,
                    size="256x256",
                    response_format='b64_json'
                )
                image_data = response['data'][0]['b64_json']
                image_src = f'data:image/png;base64,{image_data}'

                # save image to db
                add_to_db = History(
                    prompt=current_prompt,
                    image=image_data
                )
                # add image to the session
                db.session.add(add_to_db)
                # commit and insert image into the database
                db.session.commit()

                # save image db id as session cookie
                session['image_id'] = add_to_db.id

            except openai.error.OpenAIError as e:
                print(e.http_status)
                print(e.error)

        else:
            # clicked button of type='submit' will be named either 'save', 'cancel', or 'rerun' - others are set to None
            # save goes straight to the Homepage create image form
            # cancel, or re-run queries the database
            save_data = request.form.get('save', None)
            cancel_data = request.form.get('cancel', None)
            rerun_data = request.form.get('rerun', None)

            if save_data == None:
                try:
                    # get image from database by querying its id, which is stored as session cookie
                    query = query_image(session['image_id'])

                    if cancel_data != None:
                        # delete image from database
                        db.session.delete(query)
                        db.session.commit()

                    # elif rerun_data != None:
                        # regenerate prompt
                        # rerun prompt

                except Exception as e:
                    print('ERROR db')
                    print(e)

    return render_template('index.html', image_src=image_src, prompt=current_prompt)


@app.route("/history", methods=['GET', 'POST'])
def history():
    delete_img = './static/images/trash.svg'
    download_img = './static/images/download.svg'
    data = db.session.execute(
        db.select(History).order_by(History.date.desc())).scalars()
    src = 'data:image/png;base64,'

    return render_template('history.html', src=src, data=data, delete_img=delete_img, download_img=download_img)


@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    try:
        data = query_image(session['image_id'])

        db.session.delete(data)
        db.session.commit()
    except:
        print(f'ERROR deleting data row {id}')

    return redirect(url_for('history'))


@app.route("/download/<int:id>", methods=['GET', 'POST'])
def download(id):
    try:
        # download image
        data = query_image(session['image_id'])
        path = path_name(data)
        with open(path, 'wb') as image:
            image.write(base64.urlsafe_b64decode(data.image))

    except:
        print(f'ERROR downloading data row {id}')

    return redirect(url_for('history'))


# return download path
def path_name(data):
    download_folder = None
    operating_system = os.name

    # MacOS/Linux
    if operating_system == 'posix':
        download_folder = f"{os.getenv('HOME')}/Downloads"
    # Windows
    else:
        download_folder = f"{os.getenv('USERPROFILE')}\Downloads"

    # create name for image
    prompt = data.prompt.replace(' ', '-')
    prompt = re.sub('[!,./+=?]+', '', prompt)

    return f"{download_folder}/{prompt}[{data.id}]"


# return exactly one scalar result (the image with id of image_id) or raise an exception
def query_image(image_id):
    return db.session.execute(db.select(History).filter_by(
        id=image_id)).scalar_one()
