## Description
Ce projet implémente une architecture microservices pour un système d'e-commerce, évoluant d'une architecture monolithique vers une approche distribuée avec API Gateway et load balancing.

### Services
- **API Gateway** (Port 8080) : Point d'entrée unique avec load balancing
- **Products Service** (2 instances) : Gestion des produits
- **Stock Service** (Port 5002) : Gestion des stocks
- **Customers Service** (Port 5003) : Gestion des comptes clients
- **Cart Service** (Port 5004) : Gestion des paniers
- **Order Service** (Port 5005) : Validation des commandes

### Monitoring
- **Prometheus** (Port 9090) : Collecte des métriques
- **Grafana** (Port 3000) : Visualisation des métriques

### Architecture

lab5/
├── README.md
├── docker-compose.yml
├── load_test.py
├── docs/
│   ├── architecture.md
│   └── adr/
│       ├── 001-api-gateway-choice.md
│       └── 002-load-balancing-strategy.md
├── gateway/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── products_service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── stock_service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── customers_service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── cart_service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── order_service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── monitoring/
    ├── prometheus.yml
    └── grafana/
        └── dashboards/

## Déploiement

### Prérequis
- Docker et Docker Compose
- Python 3.9+
- Git

### Installation
```bash
# Cloner le repository
git clone <https://github.com/minutmaidman/lab5.git>
cd lab5
docker-compose up --build
```

## Monitoring

### Prometheus
- URL: http://localhost:9090
- Collecte automatique des métriques de tous les services

### Grafana
- URL: http://localhost:3000
- Utilisateur: admin
- Mot de passe: admin

- **Service Health**: Statut et disponibilité des services
- **API Gateway Metrics**: Latence, taux d'erreur, throughput
- **Load Balancing**: Distribution des requêtes entre instances

## Tests et éxécution des charges
```bash
pip install requests
python load_test.py
```