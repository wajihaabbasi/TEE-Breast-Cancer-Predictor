import time
import requests

LOCAL_URL = "http://127.0.0.1:8000/predict"

#sample benign data
'''
payload = {
    "radius_mean": 13.5, "texture_mean": 19, "perimeter_mean": 87.0, "area_mean": 560.0,
    "smoothness_mean": 0.095, "compactness_mean": 0.10, "concavity_mean": 0.07, 
    "concave points_mean": 0.035, "symmetry_mean": 0.180, "fractal_dimension_mean": 0.062,
    "radius_se": 0.350, "texture_se": 1.200, "perimeter_se": 2.400, "area_se": 25.0,
    "smoothness_se": 0.007, "compactness_se": 0.025, "concavity_se": 0.030, 
    "concave points_se": 0.012, "symmetry_se": 0.020, "fractal_dimension_se": 0.003,
    "radius_worst": 15.0, "texture_worst": 25.0, "perimeter_worst": 98.0, "area_worst": 700.0,
    "smoothness_worst": 0.125, "compactness_worst": 0.220, "concavity_worst": 0.190, 
    "concave points_worst": 0.090, "symmetry_worst": 0.270, "fractal_dimension_worst": 0.080
}
'''

#sample malignant data
payload = {
    "radius_mean": 20.5, "texture_mean": 20, "perimeter_mean": 135.0, "area_mean": 1260.0,
    "smoothness_mean": 0.11, "compactness_mean": 0.16, "concavity_mean": 0.19, 
    "concave points_mean": 0.105, "symmetry_mean": 0.19, "fractal_dimension_mean": 0.006,
    "radius_se": 0.60, "texture_se": 1.500, "perimeter_se": 4.500, "area_se": 75.0,
    "smoothness_se": 0.008, "compactness_se": 0.03, "concavity_se": 0.040, 
    "concave points_se": 0.015, "symmetry_se": 0.025, "fractal_dimension_se": 0.004,
    "radius_worst": 25.0, "texture_worst": 28.0, "perimeter_worst": 175.0, "area_worst": 2000.0,
    "smoothness_worst": 0.15, "compactness_worst": 0.40, "concavity_worst": 0.450, 
    "concave points_worst": 0.18, "symmetry_worst": 0.300, "fractal_dimension_worst": 0.095
}

latencies = []
num_requests = 50

print("Running local benchmark...")
for _ in range(num_requests):
    start = time.time()
    res = requests.post(LOCAL_URL, json=payload, timeout=10)
    end = time.time()
    if res.status_code == 200:
        latencies.append((end - start) * 1000)

print(f"--- Local Results ---")
print(f"Average Latency: {sum(latencies)/len(latencies):.2f} ms")
print(f"Min Latency: {min(latencies):.2f} ms")
print(f"Max Latency: {max(latencies):.2f} ms")
