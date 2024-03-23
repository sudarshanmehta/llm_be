from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import text
import requests
from models import *
from util import *
from train_script import Seq2SeqTrainerWrapper
from auth_controller import *
from config import Config

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
Initialize.initialize(app)
AuthenticationController(app)


@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks():
    try:
        tasks = Tasks.query.all()
        task_list = [{'Task': task.task, 'ID': task.task_id, 'Description': task.description} for task in tasks]
        return jsonify({'tasks': task_list})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/models', methods=['GET'])
@token_required
def get_models():
    try:
        filter_param = request.args.get('filter')
        author_param = request.args.get('author')
        taskid = Tasks.query.filter_by(task_id = filter_param).first().id
        # Check if there are any entries in the Models table
        models = Models.query.filter_by(task_id = taskid).order_by(Models.hits.desc()).limit(10).all()

        if models:
            # If there are entries, return the data from the database
            model_data = [{'model_id': model.model_id,
                           'memory': model.memory,
                           'hits': model.hits} for model in models]
            return jsonify(model_data)
        else:
            # If there are no entries, fetch data from the Hugging Face API
           
            api_url = 'https://huggingface.co/api/models?'
            if filter_param:
                api_url += f'filter={filter_param}&'
                api_url += f'sort=downloads&'
                api_url += f'direction=-1&'
                api_url += f'limit=10&'
            if author_param:
                api_url += f'author={author_param}'


            response = requests.get(api_url)

            if response.status_code == 200:
                models_data = response.json()
                model_data = []
                # Store data in the Models table
                for model in models_data:
                    memory = ModelMemoryUtil.estimate_model_memory(model['modelId'])
                    new_model = Models(task_id=taskid,
                                       model_id=model['modelId'],
                                       memory=memory,
                                       hits=model['downloads'])
                    db.session.add(new_model)
                    model_data.append(new_model)
            
                db.session.commit()
                top_models = Models.query.filter_by(task_id = taskid).order_by(Models.hits.desc()).limit(10).all()
                if not top_models:
                    top_models = model_data
                # Convert the query results to a list of dictionaries

                res_data = []
                for model in top_models:
                    res_data.append({
                        'model_id': model.model_id,
                        'memory': model.memory,
                        'hits': model.hits
                    })

                return jsonify(res_data)
            else:
                    return jsonify({'error': f'Request failed with status code {response.status_code}'})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/datasets', methods=['GET'])
def get_datasets():
    try:
        # Extract filter parameter from the query string
        filter_param = request.args.get('task_id')

        # Construct the API URL
        api_url = 'https://huggingface.co/api/datasets?'
        if filter_param:
            api_url += f'filter={filter_param}&'
            api_url += f'sort=downloads&'
            api_url += f'direction=-1&'
            api_url += f'limit=20&'

        # Send GET request to the Hugging Face API
        response = requests.get(api_url)
        
        # Check if the request was successful
        if response.status_code == 200:
        # Parse the JSON response
            datasets = response.json()
        # Extract only the dataset IDs from the response
            dataset_ids = [dataset['id'] for dataset in datasets]
            return jsonify({'datasets': dataset_ids})
        else:
            return jsonify({'error': 'Failed to fetch datasets from Hugging Face API'})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/hyperparameters', methods=['GET'])
@token_required
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


@app.route('/train_model', methods=['POST'])
@token_required
def train_model():
    try:
        # Get data from the request's JSON payload
        data = request.json

        # Extract required parameters
        dataset = data.get('dataset')
        model_id = data.get('model_id')
        training_args = data.get('training_args')

        # Check if all required parameters are provided
        if not dataset or not model_id:
            return jsonify({'error': 'Missing required parameters. Please provide dataset, model_id, and training_args'})

        # Create an instance of Seq2SeqTrainerWrapper if not already created
        seq2seq_trainer_instance = Seq2SeqTrainerWrapper(dataset_id=dataset, model_id=model_id, training_args=training_args)
        # Trigger training using the exposed instance
        seq2seq_trainer_instance.train_model()

        return jsonify({'success': f'Training model with dataset'})
    
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
