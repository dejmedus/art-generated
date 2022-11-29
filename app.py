from flask import Flask, render_template, request
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

# prompt = 'mermaid sitting on a rocky beach'
# movement_arr = ['art deco, René Lalique, Jean Dunand, Émile-Jacques Ruhlmann', 'abstract art', 'art nouveau', 'baroque', 'constructivism', 'cubism', 'digital art', 'expressionism', 'fauvism', 'figurative art', 'folk art', 'funk art', 'futurism', 'graffiti art', 'gothic', 'geometric', 'hyperrealism', 'impressionism', 'kitsch', 'pop art', 'pre-raphaelitism', 'primitivism', 'purism', 'pointillism', 'photorealism', 'psychedelic art', 'renaissance', 'realism', 'rococo', 'romanticism']
yes = ['yes', 'y']
no = ['no', 'n']


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    prompt = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)
    
    def __repr__(self):
        return '<Task %r>' % self.id
    
# with app.app_context():
#     db.create_all()

@app.route("/", methods=['GET', 'POST'])
def index():
    imageSrc = None
    current_prompt = None
    
    # if request is made
    print('REQUEST MADE')
    if request.method == "POST":
        try:
            prompt=request.form["prompt"]
            movement=request.form['movement']
            current_prompt = f'{prompt}, {movement}'
        except:
            print("Error: form post")
            
        try:
            print('CREATE IMAGE')
            response = openai.Image.create(
                prompt=current_prompt,
                n=1,
                size="256x256",
                response_format='b64_json'
            )
            imageData = response['data'][0]['b64_json']
            imageSrc = f'data:image/png;base64,{imageData}'
            print(imageSrc[0:100])
        except openai.error.OpenAIError as e:
            print(e.http_status)
            print(e.error)
        # except:
        #     print('Error DALLE 2 API')

        # while True:
        #     save_image = input(f'\nSave {current_prompt} (yes/no): ')
        #     if save_image.lower() in yes:
        #         prompt = History(
        #             prompt=current_prompt,
        #             image=imageData
        #         )
        #         db.session.add(prompt)
        #         db.session.commit()
        #         break
        #     elif save_image.lower() in no:
        #         break
        #     else:
        #         print('Please input yes or no')
        #         continue

    return render_template('index.html', imageSrc=imageSrc, prompt=current_prompt)


