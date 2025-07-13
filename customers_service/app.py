from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import uuid
import hashlib

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données simulée pour les clients
customers_db = {}

@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    customer_id = str(uuid.uuid4())
    
    # Hash du mot de passe (simplification)
    password_hash = hashlib.sha256(data.get("password", "").encode()).hexdigest()
    
    customer = {
        "id": customer_id,
        "email": data.get("email"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "password_hash": password_hash,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    customers_db[customer_id] = customer
    logger.info(f"Client créé: {customer_id}")
    
    # Retourner sans le mot de passe
    response = customer.copy()
    del response["password_hash"]
    return jsonify(response), 201

@app.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    logger.info(f"Récupération client {customer_id}")
    customer = customers_db.get(customer_id)
    if customer:
        response = customer.copy()
        del response["password_hash"]
        return jsonify(response)
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    for customer in customers_db.values():
        if customer["email"] == email and customer["password_hash"] == password_hash:
            response = customer.copy()
            del response["password_hash"]
            logger.info(f"Connexion réussie pour {email}")
            return jsonify({"success": True, "customer": response})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "customers"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)