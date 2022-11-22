from flask import Flask
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()

@app.route("/")
def index():
    return "<p>flask</p>"

@app.route('/history')
def history():
    return '<p>history</p>'