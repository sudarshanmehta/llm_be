import os
import json
from models import *
import importlib

class LLMWrapper:
    def __init__(self, model_id, dataset_id, hyperparameters):
        self.config_path = 'config.json'
        self.model_id = model_id
        self.models = self.load_config()
        self.dataset_id = dataset_id
        self.hyperparameters = hyperparameters
        self.run_model()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file '{self.config_path}' not found.")

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        llms = config[0]['Config']['MultiLLM']['llms']
    
        for item in llms:
            if item['model'] == self.model_id:
                return item
        return "Error: Model ID not found in config."

    def run_model(self):
        
        script_path = self.models['file']
        class_name = self.models['class_name']
        
        # Remove .py extension and replace / with .
        module_path = script_path.replace('/', '.')[:-3]
        
        spec = importlib.util.spec_from_file_location(module_path, script_path)
        # Import the module dynamically
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get the class from the module
        ModelClass = getattr(module, class_name)
        
        # Instantiate the model and run it
        ModelClass(self.dataset_id,self.model_id,self.hyperparameters)
        return