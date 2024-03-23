import requests
from supabase_py import create_client
from config import Config

class AuthenticatorService:
    def __init__(self, supabase_url, supabase_key):
        self.supabase = create_client(supabase_url, supabase_key)

    def signup(self, email, password):
        # Sign up user with email and password
        signup_response = self.supabase.auth.sign_up(email=email, password=password)
        return signup_response['status_code'] == 200, signup_response['access_token'] if signup_response['status_code'] == 200 else None

    def login(self, email, password):
        # Login user with email and password
        login_response = self.supabase.auth.sign_in(email=email, password=password)
        return login_response['status_code'] == 200, login_response['access_token'] if login_response['status_code'] == 200 else None

    def validate_token(self,token):
        auth_response = self.verify_access_token(token)
        return auth_response

    def verify_access_token(self,token):
        """Verifies the access token using the Supabase REST API."""
        headers = {
            'Authorization': f'{token}',
            'apiKey' : Config.SUPABASE_KEY
        }
        response = requests.get(Config.SUPABASE_URL+'/auth/v1/user', headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False