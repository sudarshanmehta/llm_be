from flask import jsonify, request
from auth_service import AuthenticatorService
from functools import wraps
# Initialize AuthenticatorService with Supabase credentials
auth = AuthenticatorService()

def AuthenticationController(app):

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        success, token = auth.signup(email, password)
        if success:
            return jsonify({'message': 'Signup successful', 'token': token}), 200
        else:
            return jsonify({'error': 'Signup failed'}), 400

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        success, token = auth.login(email, password)
        if success:
            return jsonify({'message': 'Login successful', 'token': token}), 200
        else:
            return jsonify({'error': 'Login failed'}), 401
    
    @app.route('/logout', methods=['POST'])
    def logout():
        success = auth.logout()
        if success:
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'error': 'Logout failed'}), 401


def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')

            if not token:
                return jsonify({'message': 'Token is missing'}), 401

            # Validate the token using your AuthenticatorService
            if not auth.verify_access_token(token):
                return jsonify({'message': 'Token is invalid'}), 401

            return func(*args, **kwargs)

    return decorated_function