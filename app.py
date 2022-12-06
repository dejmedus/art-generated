from flask import Flask, render_template, request, redirect
# from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import openai

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///picas.db"
db.init_app(app)

# load_dotenv()
from config import API_Key, Org_ID

openai.organization = Org_ID
openai.api_key = API_Key

# movement_arr = [
    # 'art deco, René Lalique, Jean Dunand, Émile-Jacques Ruhlmann'
    # , 'abstract art', 'art nouveau', 'baroque', 'constructivism', 'cubism', 'digital art', 'expressionism', 'fauvism', 'figurative art', 'folk art, by Ammi Phillips', 'funk art', 'futurism', 'graffiti art', 'gothic', 'geometric', 'hyperrealism', 'impressionism', 'kitsch', 'pop art', 'pre-raphaelitism', 'primitivism', 'purism', 'pointillism', 'photorealism', 'psychedelic art', 'renaissance', 'realism', 'rococo', 'romanticism']

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    prompt = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    
with app.app_context():
    db.create_all()
    

@app.route("/", methods=['GET', 'POST'])
def index():
    
    # if request is made
    print('REQUEST MADE')
    if request.method == "POST":
        if 'generate_image' in request.form:
            prompt=request.form["prompt"]
            movement=request.form['movement']
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
            except openai.error.OpenAIError as e:
                  print(e.http_status)
                  print(e.error)
        else:
            try:
                print('SAVE OR CANCEL')
                save_data = request.form.get('save', None)
                cancel_data = request.form.get('cancel', None)
                if save_data != None:
                    print('save image')
                    add_to_db = History(
                        prompt=current_prompt,
                        image=image_data
                    )
                    db.session.add(add_to_db)
                    db.session.commit()

                elif cancel_data != None:
                    print('cancel image')
                    
            except Exception as e:
                print('ERROR db')
                print(e)
    else:
        current_prompt = None
        image_src = None
                   
    saved_images = History.query.order_by(History.date).all()
    print(saved_images)
    return render_template('index.html', image_src=image_src, prompt=current_prompt)

