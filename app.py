from flask import Flask, render_template, request, session, redirect, url_for

import openai
import base64

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# os: get operating system / re: regex out unwanted name chars
import os
import re


db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db.init_app(app)

migrate = Migrate(app, db)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")
app.secret_key = os.getenv("KEY")


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    prompt = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def index():
    current_prompt = None
    image_src = None

    # if request is made
    if request.method == "POST":
        if 'generate_image' in request.form:
            prompt = request.form["prompt"]
            movement = request.form['movement']
            current_prompt = f'{prompt}, {movement}'

            try:
                # create image
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
                db.session.add(add_to_db)
                db.session.commit()

                # save image db id as session cookie
                session['image_id'] = add_to_db.id

            except openai.error.OpenAIError as e:
                print(e.http_status)
                print(e.error)
        else:
            try:
                save_data = request.form.get('save', None)
                cancel_data = request.form.get('cancel', None)
                rerun_data = request.form.get('rerun', None)
                if save_data != None:
                    # save image
                    query = History.query.get(session['image_id'])
                    with open(f"photos/{query.prompt}{query.id}.png", "wb") as image:
                        image.write(base64.urlsafe_b64decode(query.image))

                elif cancel_data != None:
                    # get image from database by querying its id
                    # stored as a session cookie
                    query = History.query.get(session['image_id'])
                    # delete image from database
                    db.session.delete(query)
                    db.session.commit()

                elif rerun_data != None:
                    # regenerate prompt
                    query = History.query.get(session['image_id'])
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
        data = db.get_or_404(History, id)

        db.session.delete(data)
        db.session.commit()
    except:
        print(f'ERROR deleting data row {id}')

    return redirect(url_for('history'))


@app.route("/download/<int:id>", methods=['GET', 'POST'])
def download(id):
    try:
        # download image
        data = db.get_or_404(History, id)
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

    # if MacOS/Linux
    if operating_system == 'posix':
        download_folder = f"{os.getenv('HOME')}/Downloads"
    # else if Windows
    else:
        download_folder = f"{os.getenv('USERPROFILE')}\Downloads"

    # create name for image
    prompt = data.prompt.replace(' ', '-')
    prompt = re.sub('[!,./+=?]+', '', prompt)

    return f"{download_folder}/{prompt}[{data.id}]"
