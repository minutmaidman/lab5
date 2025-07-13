from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données simulée pour le stock
stock_db = {
    "1": {"product_id": "1", "quantity": 50, "reserved": 0},
    "2": {"product_id": "2", "quantity": 100, "reserved": 0},
    "3": {"product_id": "3", "quantity": 75, "reserved": 0}
}

@app.route('/stock/<product_id>', methods=['GET'])
def get_stock(product_id):
    logger.info(f"Vérification stock pour produit {product_id}")
    stock = stock_db.get(product_id)
    if stock:
        return jsonify(stock)
    return jsonify({"error": "Stock not found"}), 404

@app.route('/stock/<product_id>/reserve', methods=['POST'])
def reserve_stock(product_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)
    
    if product_id in stock_db:
        stock = stock_db[product_id]
        if stock["quantity"] - stock["reserved"] >= quantity:
            stock["reserved"] += quantity
            logger.info(f"Réservation de {quantity} unités pour produit {product_id}")
            return jsonify({"success": True, "reserved": quantity})
        else:
            return jsonify({"error": "Insufficient stock"}), 400
    return jsonify({"error": "Product not found"}), 404

@app.route('/stock/<product_id>/release', methods=['POST'])
def release_stock(product_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)
    
    if product_id in stock_db:
        stock = stock_db[product_id]
        stock["reserved"] = max(0, stock["reserved"] - quantity)
        logger.info(f"Libération de {quantity} unités pour produit {product_id}")
        return jsonify({"success": True, "released": quantity})
    return jsonify({"error": "Product not found"}), 404

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "stock"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)