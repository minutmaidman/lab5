from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import uuid

app = Flask(__name__)
CORS(app)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données simulée pour les produits
products_db = {
    "1": {"id": "1", "name": "Laptop", "price": 999.99, "stock": 50, "category": "electronics"},
    "2": {"id": "2", "name": "Mouse", "price": 29.99, "stock": 100, "category": "electronics"},
    "3": {"id": "3", "name": "Keyboard", "price": 79.99, "stock": 75, "category": "electronics"}
}

@app.route('/products', methods=['GET'])
def get_products():
    logger.info(f"Récupération de tous les produits - Instance: {app.config.get('INSTANCE_ID', 'default')}")
    return jsonify(list(products_db.values()))

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    logger.info(f"Récupération produit {product_id}")
    product = products_db.get(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product_id = str(uuid.uuid4())
    product = {
        "id": product_id,
        "name": data.get("name"),
        "price": data.get("price"),
        "stock": data.get("stock", 0),
        "category": data.get("category", "general")
    }
    products_db[product_id] = product
    logger.info(f"Produit créé: {product_id}")
    return jsonify(product), 201

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "products"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)