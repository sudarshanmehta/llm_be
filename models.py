from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Initialize:
    @staticmethod
    def initialize(app):
        db.init_app(app)

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


class Models(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    model_id = db.Column(db.String, nullable=False, unique=True)
    memory = db.Column(db.Double, nullable=False)
    hits = db.Column(db.Double, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('task_id', 'model_id', name='_task_model_uc'),
    )

    def __init__(self, task_id=None, model_id=None, memory=None, hits=None):
        self.task_id = task_id
        self.model_id = model_id
        self.memory = memory
        self.hits = hits