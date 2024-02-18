import shutil
import tempfile
from transformers import MarianMTModel, logging

class ModelMemoryUtil:
    @staticmethod
    def estimate_model_memory(model_id):
        try:
            # Disable logging to prevent unnecessary output
            logging.set_verbosity_error()

            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()

            # Load the model into the temporary directory
            model = MarianMTModel.from_pretrained(model_id, cache_dir=temp_dir)

            # Get the number of parameters
            num_params = model.num_parameters()

            # Assuming each parameter takes 4 bytes (32 bits), calculate the memory usage in MB
            memory_usage = num_params * 4 / (1024 ** 2)

            # Delete the temporary directory to free up space
            shutil.rmtree(temp_dir)

            return memory_usage

        except Exception as e:
            print(f"Error occurred while estimating model memory usage: {e}")
            return None
