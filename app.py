from flask import Flask, jsonify, request  # Correct import for 'request'
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///llm.db"
db = SQLAlchemy(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String)
    task = db.Column(db.String)
    description = db.Column(db.String)

    def __init__(self, task_id, task, description):
        self.task_id = task_id
        self.task = task
        self.description = description

    def __repr__(self):
        return '<Task %r>' % self.task

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Tasks.query.all()
        task_list = [{'Task': task.task, 'ID': task.task_id, 'Description': task.description} for task in tasks]
        return jsonify({'tasks': task_list})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/models', methods=['GET'])
def get_models():
    try:
        # Extract the 'filter' and 'author' query parameters if provided
        filter_param = request.args.get('filter')
        author_param = request.args.get('author')

        # Construct the API URL with the parameters if they exist
        api_url = 'https://huggingface.co/api/models?'
        if filter_param:
            api_url += f'filter={filter_param}&'
        if author_param:
            api_url += f'author={author_param}'

        # Make a request to the Hugging Face API with the constructed URL
        response = requests.get(api_url)

        if response.status_code == 200:
            models_data = response.json()
            return jsonify(models_data)
        else:
            return jsonify({'error': f'Request failed with status code {response.status_code}'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
