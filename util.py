import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from config import Config
from io import BytesIO

class ModelMemoryUtil:
    @staticmethod
    def estimate_model_memory(model_id):
        try:
            url = f"https://huggingface.co/{model_id}/tree/main"
            response = requests.get(url)
            size_value = 0
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                files = soup.find_all('a', href=True)
                for file in files:
                    if file['href'].endswith(('.safetensors', '.pth', '.pt', '.h5', '.onnx', '.bin')):
                        file_url = f"https://huggingface.co{file['href'].replace('/blob/', '/raw/')}"
                        file_response = requests.get(file_url)
                        if file_response.status_code == 200:
                            file_size_match = re.search(r"size\s+(\d+)", file_response.text)
                            if file_size_match:
                                file_size = float(file_size_match.group(1))
                                size_value = size_value + int(file_size / 1000000)  # Convert bytes to MB and add to size_value
                return size_value
            else:
                print("Failed to fetch the URL")
                return None
            # Disable logging to prevent unnecessary output
         
        except Exception as e:
            print(f"Error occurred while estimating model memory usage: {e}")
            return None

class FileHandlingUtil:
    @staticmethod
    def validate_data(df):
        if 'text' in df.columns and 'label' in df.columns:
            # Perform additional validation if needed
            return True
        else:
            return False
    
    @staticmethod
    def download_file(file_path):
        bucket_name = 'user_data'
        url = f"{Config.SUPABASE_URL}/storage/v1/object/{bucket_name}/{file_path}"
        headers = {
            "authorization": Config.SUPABASE_KEY
        }
        response = requests.get(url, headers=headers, stream=True)
        return response

    @staticmethod
    def parse_file(response, file_path):
        if response.status_code == 200:
            content = response.content
            if file_path.endswith('.xlsx'):
                return pd.read_excel(BytesIO(content))
            elif file_path.endswith('.csv'):
                return pd.read_csv(BytesIO(content))
            else:
                return None  # Unsupported file format
        else:
            return None  # File not found