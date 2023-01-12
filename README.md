## Create AI Art 🤖🎨

Flask app to generate images with the OpenAI [DALL·E Images API](https://openai.com/api/).

### Built with
- [DALL·E Images API](https://beta.openai.com/docs/api-reference/images/create) creates images from a text prompt
- [Flask](https://flask.palletsprojects.com/en/2.2.x/) a python web framework
  - Uses the [Jinja](https://palletsprojects.com/p/jinja/) template engine
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/), which simplifies [SQLAlchemy](https://www.sqlalchemy.org) for Flask
    - SQLAlchemy is an SQL toolkit and Object-Relational Mapper for Python
    - Connects to a [SQLite](https://www.sqlite.org/index.html) database
- [Flask Migrate](https://flask-migrate.readthedocs.io) to configure [Alembic](https://alembic.sqlalchemy.org/en/latest/) for Flask-SQLAlchemy
  - Alembic is a lightweight database migration tool for SQLAlchemy

### Get Started
#### Prerequisites
- [Python 3](https://www.python.org/downloads/)

#### Setup

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) art-generated
2. [Create a local clone](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository) of the forked repository
3. Using the terminal, move into your local copy
```
cd art-generated
```
4. Create a [virtual environment](https://docs.python.org/3/library/venv.html#module-venv)
   
*MacOS/Linux*
```
python3 -m venv venv
. venv/bin/activate
```
*Windows*
```
py -3 -m venv venv
venv\Scripts\activate
```
5. Install dependencies
```
pip3 install -r requirements.txt
```
6. Rename .env-copy to .env
```
mv .env-copy .env
```
7. Create an [OpenAI](https://beta.openai.com) account and fill in .env
```
OPENAI_API_KEY='<your api key>'
OPENAI_ORG_ID='<your organization>'
```
8. Create initial database migration
```
flask db init
flask db migrate -m "Initial migration."
```
> When changes are made to the database model, run ```flask db upgrade```<sup>[1](https://flask-migrate.readthedocs.io/en/latest/)</sup>
9.   Run the app
```
flask --debug run
```
10. Generate images on the [browser!](http://localhost:5000) 🎉


### Screenshots
<details><summary>Homepage</summary>
<img width="1280" alt="homepage" src="https://user-images.githubusercontent.com/59973863/211992466-7df0be36-0d65-460e-9ad4-3b9ec266efb0.png">
</details>

<details><summary>Generated Image</summary>
<img width="1280" alt="image" src="https://user-images.githubusercontent.com/59973863/211992507-9d02d8ed-9d51-4f43-a8b9-4bd85031ae3f.png">
</details>

<details><summary>Image History</summary>
<img width="1280" alt="history" src="https://user-images.githubusercontent.com/59973863/211992574-3c955b28-bc5c-46ef-a207-7c819e7a870a.png">
</details>
