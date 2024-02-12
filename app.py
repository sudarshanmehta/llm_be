from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
import requests
from train_script import Seq2SeqTrainerWrapper

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

class Hyperparameters(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_id = db.Column(db.String)
    hyper_param = db.Column(db.String)
    hyper_value = db.Column(db.String)

    def __init__(self, model_id, hyper_param, hyper_value):
        self.model_id = model_id
        self.hyper_param = hyper_param
        self.hyper_value = hyper_value

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

@app.route('/datasets', methods=['GET'])
def get_datasets():
    try:
        # Extract task_id from the query parameters
        task_id = request.args.get('task_id')

        if task_id:
            # Query the Datasets table for dataset_name based on task_id
            query = text("SELECT dataset_name FROM Datasets WHERE task_id = :task_id")
           
            result = db.session.execute(query, {'task_id': task_id})
            dataset_names = [row[0] for row in result.fetchall()]

            if dataset_names:
                return jsonify({'datasets': dataset_names})
            else:
                return jsonify({'error': 'Dataset not found for the given task_id'})

        else:
            return jsonify({'error': 'task_id parameter is required'})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/train_model', methods=['POST'])
def train_model():
    try:
        # Get data from the request's JSON payload
        data = request.json

        # Extract required parameters
        dataset = data.get('dataset')
        model_id = data.get('model_id')
        #training_args = data.get('training_args')

        # Check if all required parameters are provided
        if not dataset or not model_id:
            return jsonify({'error': 'Missing required parameters. Please provide dataset, model_id, and training_args'})

        # Create an instance of Seq2SeqTrainerWrapper if not already created
        seq2seq_trainer_instance = Seq2SeqTrainerWrapper(dataset_id=dataset, model_id=model_id, training_args=None)
        # Trigger training using the exposed instance
        seq2seq_trainer_instance.train_model()

        return jsonify({'success': f'Training model with dataset'})
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/hyperparameters', methods=['GET'])
def get_hyperparameters():
    try:
        # Extract the 'model_id' parameter from the request
        model_id = request.args.get('model_id')

        if model_id:
            # Query the Hyperparameters table for all entries with the specified model_id
            hyperparameters_data = Hyperparameters.query.filter_by(model_id = model_id).all()

            if hyperparameters_data:
                # If the model_id exists, return its hyperparameters
                hyperparameters_list = [{'model_id': hyper.model_id,
                                        'hyper_param': hyper.hyper_param,
                                        'hyper_value': hyper.hyper_value} for hyper in hyperparameters_data]
            else:
                # If the model_id does not exist, return standard hyperparameters
                standard_hyperparameters_data = Hyperparameters.query.filter_by(model_id = 'standard').all()
                hyperparameters_list = [{'model_id': standard_hyperparameters.model_id,
                                'hyper_param': standard_hyperparameters.hyper_param,
                                'hyper_value': standard_hyperparameters.hyper_value}for standard_hyperparameters in standard_hyperparameters_data]
            return jsonify(hyperparameters_list)
        else:
            return jsonify({'error': 'model_id parameter is required'})

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
