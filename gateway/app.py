from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import time
import random

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration des services avec load balancing
SERVICES = {
    "products": [
        "http://products-service-1:5001",
        "http://products-service-2:5001"
    ],
    "stock": ["http://stock-service:5002"],
    "customers": ["http://customers-service:5003"],
    "cart": ["http://cart-service:5004"],
    "orders": ["http://order-service:5005"]
}

# Compteur pour round-robin
service_counters = {service: 0 for service in SERVICES}

def get_service_url(service_name):
    """Sélectionne une URL de service avec load balancing round-robin"""
    if service_name not in SERVICES:
        return None
    
    urls = SERVICES[service_name]
    if len(urls) == 1:
        return urls[0]
    
    # Round-robin
    counter = service_counters[service_name]
    url = urls[counter % len(urls)]
    service_counters[service_name] = (counter + 1) % len(urls)
    
    logger.info(f"Load balancing {service_name}: utilisation de {url}")
    return url

@app.before_request
def log_request():
    """Middleware de logging"""
    logger.info(f"Gateway: {request.method} {request.path} de {request.remote_addr}")

@app.route('/api/v1/products', methods=['GET', 'POST'])
@app.route('/api/v1/products/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_products(path=None):
    service_url = get_service_url("products")
    if not service_url:
        return jsonify({"error": "Service unavailable"}), 503
    
    url = f"{service_url}/products"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json() if request.is_json else None,
            params=request.args,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Erreur proxy products: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503

@app.route('/api/v1/stock', methods=['GET', 'POST'])
@app.route('/api/v1/stock/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_stock(path=None):
    service_url = get_service_url("stock")
    if not service_url:
        return jsonify({"error": "Service unavailable"}), 503
    
    url = f"{service_url}/stock"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json() if request.is_json else None,
            params=request.args,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Erreur proxy stock: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503

@app.route('/api/v1/customers', methods=['GET', 'POST'])
@app.route('/api/v1/customers/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_customers(path=None):
    service_url = get_service_url("customers")
    if not service_url:
        return jsonify({"error": "Service unavailable"}), 503
    
    url = f"{service_url}/customers"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json() if request.is_json else None,
            params=request.args,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Erreur proxy customers: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503

@app.route('/api/v1/cart', methods=['GET', 'POST'])
@app.route('/api/v1/cart/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_cart(path=None):
    service_url = get_service_url("cart")
    if not service_url:
        return jsonify({"error": "Service unavailable"}), 503
    
    url = f"{service_url}/cart"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json() if request.is_json else None,
            params=request.args,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Erreur proxy cart: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503

@app.route('/api/v1/orders', methods=['GET', 'POST'])
@app.route('/api/v1/orders/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_orders(path=None):
    service_url = get_service_url("orders")
    if not service_url:
        return jsonify({"error": "Service unavailable"}), 503
    
    url = f"{service_url}/orders"
    if path:
        url += f"/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json() if request.is_json else None,
            params=request.args,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Erreur proxy orders: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": time.time()
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    return "# Metrics placeholder\nservice_up 1\n", 200, {'Content-Type': 'text/plain'}

@app.route('/api/v1/health', methods=['GET'])
def health_check_all():
    """Vérifie l'état de tous les services"""
    status = {"gateway": "healthy", "services": {}}
    
    for service_name, urls in SERVICES.items():
        service_status = []
        for url in urls:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    service_status.append("healthy")
                else:
                    service_status.append("unhealthy")
            except:
                service_status.append("unreachable")
        
        status["services"][service_name] = service_status
    
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)