from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données simulée pour les paniers
carts_db = {}

# URLs des services (à adapter selon votre configuration)
PRODUCTS_SERVICE_URL = "http://products-service:5001"
STOCK_SERVICE_URL = "http://stock-service:5002"

@app.route('/cart/<customer_id>', methods=['GET'])
def get_cart(customer_id):
    logger.info(f"Récupération panier pour client {customer_id}")
    cart = carts_db.get(customer_id, {"items": [], "total": 0})
    return jsonify(cart)

@app.route('/cart/<customer_id>/add', methods=['POST'])
def add_to_cart(customer_id):
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    
    # Vérifier la disponibilité du produit
    try:
        stock_response = requests.get(f"{STOCK_SERVICE_URL}/stock/{product_id}")
        if stock_response.status_code != 200:
            return jsonify({"error": "Product not available"}), 400
            
        stock_data = stock_response.json()
        if stock_data["quantity"] - stock_data["reserved"] < quantity:
            return jsonify({"error": "Insufficient stock"}), 400
    except:
        logger.warning("Impossible de vérifier le stock")
    
    # Ajouter au panier
    if customer_id not in carts_db:
        carts_db[customer_id] = {"items": [], "total": 0}
    
    cart = carts_db[customer_id]
    
    # Chercher si le produit existe déjà dans le panier
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart["items"].append({
            "product_id": product_id,
            "quantity": quantity
        })
    
    # Recalculer le total (simplifié)
    cart["total"] = len(cart["items"])
    
    logger.info(f"Ajout au panier {customer_id}: produit {product_id}, quantité {quantity}")
    return jsonify(cart)

@app.route('/cart/<customer_id>/clear', methods=['DELETE'])
def clear_cart(customer_id):
    if customer_id in carts_db:
        carts_db[customer_id] = {"items": [], "total": 0}
    logger.info(f"Panier vidé pour client {customer_id}")
    return jsonify({"success": True})

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "cart"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)