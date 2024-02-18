import requests
from bs4 import BeautifulSoup
import re

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
