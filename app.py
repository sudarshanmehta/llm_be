from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
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
        # Retrieve data from the Tasks table
        tasks = Tasks.query.all()

        # Convert data to a list of dictionaries
        task_list = [{'Task': task.task, 'ID': task.task_id, 'Description': task.description} for task in tasks]

        # Return data as JSON
        return jsonify({'tasks': task_list})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
