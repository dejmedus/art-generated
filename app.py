from config import API_Key, Org_ID, Secret_Key
from flask import Flask, render_template, request, session
import openai
# from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import base64
import os
import re


db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///picas.db"
db.init_app(app)

migrate = Migrate(app, db)

# load_dotenv()

openai.organization = Org_ID
openai.api_key = API_Key
app.secret_key = Secret_Key

# movement_arr = [
# 'art deco, René Lalique, Jean Dunand, Émile-Jacques Ruhlmann'
# , 'abstract art', 'art nouveau', 'baroque', 'constructivism', 'cubism', 'digital art', 'expressionism', 'fauvism', 'figurative art', 'folk art, by Ammi Phillips', 'funk art', 'futurism', 'graffiti art', 'gothic', 'geometric', 'hyperrealism', 'impressionism', 'kitsch', 'pop art', 'pre-raphaelitism', 'primitivism', 'purism', 'pointillism', 'photorealism', 'psychedelic art', 'renaissance', 'realism', 'rococo', 'romanticism']


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
    print('REQUEST MADE')
    if request.method == "POST":
        if 'generate_image' in request.form:
            prompt = request.form["prompt"]
            movement = request.form['movement']
            current_prompt = f'{prompt}, {movement}'

            try:
                print('CREATE IMAGE')
                response = openai.Image.create(
                    prompt=current_prompt,
                    n=1,
                    size="256x256",
                    response_format='b64_json'
                )
                image_data = response['data'][0]['b64_json']
                image_src = f'data:image/png;base64,{image_data}'

                print('save image to database')
                add_to_db = History(
                    prompt=current_prompt,
                    image=image_data
                )
                db.session.add(add_to_db)
                db.session.commit()

                print('save images database id as session cookie')
                session['image_id'] = add_to_db.id

            except openai.error.OpenAIError as e:
                print(e.http_status)
                print(e.error)
        else:
            try:
                print('SAVE OR CANCEL')
                save_data = request.form.get('save', None)
                cancel_data = request.form.get('cancel', None)
                rerun_data = request.form.get('rerun', None)
                if save_data != None:
                    print('save image')
                    # save image
                    query = History.query.get(session['image_id'])
                    with open(f"photos/{query.prompt}{query.id}.png", "wb") as image:
                        image.write(base64.urlsafe_b64decode(query.image))

                elif cancel_data != None:
                    print('cancel image')
                    # get image from database by querying its id
                    #   stored as a session cookie
                    query = History.query.get(session['image_id'])
                    # delete image from database
                    db.session.delete(query)
                    db.session.commit()

                elif rerun_data != None:
                    print('generate again - not set up yet')
                    query = History.query.get(session['image_id'])
                    # rerun prompt

            except Exception as e:
                print('ERROR db')
                print(e)

    # old way: saved_images = History.query.order_by(History.date).all()
    # new way: saved_images = db.session.execute(db.select(History).order_by(History.date)).scalars()
    return render_template('index.html', image_src=image_src, prompt=current_prompt)


@app.route("/history", methods=['GET', 'POST'])
def history():
    data = db.session.execute(
        db.select(History).order_by(History.date.desc())).scalars()
    src = 'data:image/png;base64,'

    return render_template('history.html', src=src, data=data)


@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    try:
        data = db.get_or_404(History, id)
        print(data)
        db.session.delete(data)
        db.session.commit()
    except:
        print(f'ERROR deleting data row {id}')

    data = db.session.execute(
        db.select(History).order_by(History.date.desc())).scalars()
    src = 'data:image/png;base64,'

    return render_template('history.html', src=src, data=data)


@app.route("/download/<int:id>", methods=['GET', 'POST'])
def download(id):
    try:
        print('download image')
        data = db.get_or_404(History, id)
        path = path_name(data)
        print(path)
        with open(path, 'wb') as image:
            image.write(base64.urlsafe_b64decode(data.image))

    except:
        print(f'ERROR downloading data row {id}')

    data = db.session.execute(
        db.select(History).order_by(History.date.desc())).scalars()
    src = 'data:image/png;base64,'

    return render_template('history.html', src=src, data=data)


def path_name(data):
    download_folder = None

    if os.name == 'posix':
        download_folder = f"{os.getenv('HOME')}/Downloads"
    # else:
    #     download_folder = f"{os.getenv('USERPROFILE')}\\Downloads"

    prompt = data.prompt.replace(' ', '-')
    prompt = re.sub('[!,./+=?]+', '', prompt)

    return f"{download_folder}/{prompt}[{data.id}]"
