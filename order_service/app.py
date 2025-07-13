from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import uuid
import requests

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données simulée pour les commandes
orders_db = {}

# URLs des services
CART_SERVICE_URL = "http://cart-service:5004"
STOCK_SERVICE_URL = "http://stock-service:5002"

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_id = data.get("customer_id")
    
    # Récupérer le panier
    try:
        cart_response = requests.get(f"{CART_SERVICE_URL}/cart/{customer_id}")
        if cart_response.status_code != 200:
            return jsonify({"error": "Cart not found"}), 4002
        cart = cart_response.json()
    except:
        return jsonify({"error": "Unable to retrieve cart"}), 500
    
    if not cart["items"]:
        return jsonify({"error": "Cart is empty"}), 400
    
    # Créer la commande
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "customer_id": customer_id,
        "items": cart["items"],
        "status": "pending",
        "total": cart["total"],
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    # Réserver le stock pour chaque produit
    for item in cart["items"]:
        try:
            reserve_response = requests.post(
                f"{STOCK_SERVICE_URL}/stock/{item['product_id']}/reserve",
                json={"quantity": item["quantity"]}
            )
            if reserve_response.status_code != 200:
                logger.warning(f"Impossible de réserver le stock pour {item['product_id']}")
        except:
            logger.warning(f"Erreur lors de la réservation du stock pour {item['product_id']}")
    
    orders_db[order_id] = order
    
    # Vider le panier
    try:
        requests.delete(f"{CART_SERVICE_URL}/cart/{customer_id}/clear")
    except:
        logger.warning("Impossible de vider le panier")
    
    logger.info(f"Commande créée: {order_id} pour client {customer_id}")
    return jsonify(order), 201

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    logger.info(f"Récupération commande {order_id}")
    order = orders_db.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")
    
    if order_id in orders_db:
        orders_db[order_id]["status"] = new_status
        logger.info(f"Statut commande {order_id} mis à jour: {new_status}")
        return jsonify(orders_db[order_id])
    
    return jsonify({"error": "Order not found"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "orders"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
