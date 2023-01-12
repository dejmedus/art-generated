from flask import Flask, render_template, request, redirect, url_for

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
    if request.method == "POST":
        # create image with generate image form data
        prompt = f'{request.form["prompt"]}, {request.form["movement"]}'

        # generate_image takes in a prompt, generates an image, saves image to db
        # and returns an object with keys id and image
        generated = generate_image(prompt)

        return render_template('index.html', image_src=generated["image"], prompt=prompt, image_id=generated["id"])

    return render_template('index.html', image_src=None, prompt=None, image_id=None)


@app.route("/image/<int:id>", methods=['GET', 'POST'])
def image(id):
    # clicked button of type='submit' will be named either 'return', 'cancel', or 'rerun' - others are set to None
    # return_to_homepage goes straight to the Homepage create image form
    # cancel, or re-run queries the database
    return_to_homepage = request.form.get('return', None)
    cancel_data = request.form.get('cancel', None)
    rerun_data = request.form.get('rerun', None)

    if return_to_homepage == None:
        try:
            query = query_image(id)

            if cancel_data != None:
                # delete image from database
                db.session.delete(query)
                db.session.commit()

            elif rerun_data != None:
                # rerun prompt, generate_image returns dict with image and id
                generated = generate_image(query.prompt)
                print(generated)

                return render_template('index.html', image_src=generated["image"], prompt=query.prompt, image_id=generated["id"])

        except Exception as e:
            print('ERROR in route /image')
            print(e)

    return redirect(url_for('index'))


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
        data = query_image(id)

        db.session.delete(data)
        db.session.commit()
    except Exception as e:
        print(f'ERROR deleting data row {id}')
        print(e)

    return redirect(url_for('history'))


@app.route("/download/<int:id>", methods=['GET', 'POST'])
def download(id):
    try:
        # download image
        data = query_image(id)
        path = path_name(data)
        with open(path, 'wb') as image:
            image.write(base64.urlsafe_b64decode(data.image))

    except Exception as e:
        print(f'ERROR downloading data row {id}')
        print(e)

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


def generate_image(current_prompt):
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

        image_id = add_to_db.id

    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)

    return {
        "id": image_id,
        "image": image_src
    }
