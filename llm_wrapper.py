import os
import json
from models import *
import importlib
import threading
from supabase_client import supabase_client

class LLMWrapper:
    def __init__(self, model_id, dataset_id, hyperparameters):
        self.config_path = 'config.json'
        self.model_id = model_id
        self.models = self.load_config()
        self.dataset_id = dataset_id
        self.hyperparameters = hyperparameters
        self.model_thread = threading.Thread(target=self.run_model)
        self.model_thread.start()

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
        
        self.insert_status_model()
        # Instantiate the model and run it
        ModelClass(self.dataset_id,self.model_id,self.hyperparameters)
        
        self.update_status_model()
        
        return

    def insert_status_model(self):
        model_id = supabase_client.table('models').select('id').eq('model', str(self.model_id)).execute().get('data',[])[0].get('id')
        user_id = supabase_client.auth.current_user['id']
        insert_data = { 'user_id' : user_id,
                        'model_id' : model_id,
                        'status' : False }
        supabase_client.table("trained_models").insert(insert_data).execute()

    def update_status_model(self):
        model_id = supabase_client.table('models').select('id').eq('model', str(self.model_id)).execute().get('data',[])[0].get('id')
        user_id = supabase_client.auth.current_user['id']
        id = supabase_client.table('trained_model').select('id').eq('model_id', str(model_id)).eq('user_id',user_id).execute().get('data',[])[0].get('id')
        upsert_data = {'id':id, 'status' : True}
        supabase_client.table('trained_models').upsert(upsert_data).execute()