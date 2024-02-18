from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import text
import requests
from models import *
from util import *

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///llm.db"
Initialize.initialize(app)

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
