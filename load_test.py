import requests
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        
    def make_request(self, endpoint, method='GET', data=None):
        start_time = time.time()
        try:
            url = f"{self.base_url}{endpoint}"
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            
            duration = time.time() - start_time
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'duration': duration,
                'success': response.status_code < 400
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'duration': duration,
                'success': False,
                'error': str(e)
            })
    
    def run_load_test(self, num_requests=100, concurrent_users=10):
        print(f"Démarrage du test de charge: {num_requests} requêtes avec {concurrent_users} utilisateurs concurrents")
        
        # Test scenarios
        scenarios = [
            ('/api/v1/products', 'GET'),
            ('/api/v1/products/1', 'GET'),
            ('/api/v1/stock/1', 'GET'),
            ('/api/v1/customers', 'POST', {'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User', 'password': 'password123'}),
        ]
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for i in range(num_requests):
                scenario = scenarios[i % len(scenarios)]
                endpoint, method = scenario[0], scenario[1]
                data = scenario[2] if len(scenario) > 2 else None
                
                future = executor.submit(self.make_request, endpoint, method, data)
                futures.append(future)
            
            # Attendre que tous les requests soient terminés
            for future in futures:
                future.result()
        
        self.print_results()
    
    def print_results(self):
        if not self.results:
            print("Aucun résultat à afficher")
            return
        
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        
        durations = [r['duration'] for r in self.results]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print(f"\n=== RÉSULTATS DU TEST DE CHARGE ===")
        print(f"Total des requêtes: {total_requests}")
        print(f"Requêtes réussies: {successful_requests}")
        print(f"Requêtes échouées: {failed_requests}")
        print(f"Taux de réussite: {(successful_requests/total_requests)*100:.2f}%")
        print(f"Durée moyenne: {avg_duration:.3f}s")
        print(f"Durée minimale: {min_duration:.3f}s")
        print(f"Durée maximale: {max_duration:.3f}s")
        
        # Grouper par endpoint
        endpoints = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
        
        print(f"\n=== DÉTAILS PAR ENDPOINT ===")
        for endpoint, results in endpoints.items():
            successes = sum(1 for r in results if r['success'])
            avg_dur = sum(r['duration'] for r in results) / len(results)
            print(f"{endpoint}: {successes}/{len(results)} réussies, {avg_dur:.3f}s moyenne")

if __name__ == '__main__':
    # Test direct API
    print("Test de charge - API directe")
    tester_direct = LoadTester("http://localhost:5001")  # Service direct
    tester_direct.run_load_test(50, 5)
    
    time.sleep(2)
    
    # Test via API Gateway
    print("\nTest de charge - Via API Gateway")
    tester_gateway = LoadTester("http://localhost:8080")  # Via Gateway
    tester_gateway.run_load_test(50, 5)