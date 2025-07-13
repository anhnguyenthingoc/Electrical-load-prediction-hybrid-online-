#!/usr/bin/env python3
"""
VRP Optimization Examples and Utilities

This module demonstrates how to use the VRP optimization library with various
algorithms and problem variants.
"""

import random
import time
import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from vrp_optimizer import *
from vrp_advanced import *

class VRPDataGenerator:
    """Utility class for generating VRP test data."""
    
    @staticmethod
    def generate_random_locations(num_customers: int, area_size: float = 100.0, 
                                 seed: int = None) -> List[Location]:
        """Generate random customer locations."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        locations = []
        
        # Add depot at center
        locations.append(Location(x=area_size/2, y=area_size/2, demand=0.0))
        
        # Add random customers
        for i in range(1, num_customers + 1):
            x = random.uniform(0, area_size)
            y = random.uniform(0, area_size)
            demand = random.uniform(1, 10)
            locations.append(Location(x=x, y=y, demand=demand))
        
        return locations
    
    @staticmethod
    def generate_clustered_locations(num_customers: int, num_clusters: int = 3, 
                                   area_size: float = 100.0, seed: int = None) -> List[Location]:
        """Generate clustered customer locations."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        locations = []
        
        # Add depot at center
        locations.append(Location(x=area_size/2, y=area_size/2, demand=0.0))
        
        # Generate cluster centers
        cluster_centers = []
        for _ in range(num_clusters):
            center_x = random.uniform(0.2 * area_size, 0.8 * area_size)
            center_y = random.uniform(0.2 * area_size, 0.8 * area_size)
            cluster_centers.append((center_x, center_y))
        
        # Add customers around cluster centers
        customers_per_cluster = num_customers // num_clusters
        for i in range(num_clusters):
            center_x, center_y = cluster_centers[i]
            
            for j in range(customers_per_cluster):
                # Add some randomness around cluster center
                x = center_x + random.gauss(0, area_size * 0.1)
                y = center_y + random.gauss(0, area_size * 0.1)
                
                # Keep within bounds
                x = max(0, min(area_size, x))
                y = max(0, min(area_size, y))
                
                demand = random.uniform(1, 10)
                locations.append(Location(x=x, y=y, demand=demand))
        
        # Add remaining customers randomly
        remaining = num_customers - len(locations) + 1
        for _ in range(remaining):
            x = random.uniform(0, area_size)
            y = random.uniform(0, area_size)
            demand = random.uniform(1, 10)
            locations.append(Location(x=x, y=y, demand=demand))
        
        return locations
    
    @staticmethod
    def add_time_windows(locations: List[Location], time_window_ratio: float = 0.5) -> List[Location]:
        """Add time windows to a fraction of locations."""
        for i, location in enumerate(locations):
            if i == 0:  # Skip depot
                continue
            
            if random.random() < time_window_ratio:
                # Generate random time window
                start_time = random.uniform(0, 480)  # 8 hours in minutes
                window_size = random.uniform(60, 180)  # 1-3 hours
                end_time = start_time + window_size
                
                location.time_window = (start_time, end_time)
                location.service_time = random.uniform(10, 30)  # 10-30 minutes service
        
        return locations
    
    @staticmethod
    def generate_vehicles(num_vehicles: int, capacity_range: Tuple[float, float] = (50, 100)) -> List[Vehicle]:
        """Generate vehicles with random capacities."""
        vehicles = []
        
        for i in range(num_vehicles):
            capacity = random.uniform(capacity_range[0], capacity_range[1])
            vehicles.append(Vehicle(capacity=capacity))
        
        return vehicles

class VRPBenchmark:
    """Benchmark different VRP solvers."""
    
    def __init__(self):
        self.results = {}
    
    def run_benchmark(self, locations: List[Location], vehicles: List[Vehicle], 
                     algorithms: List[str] = None) -> Dict:
        """Run benchmark on different algorithms."""
        if algorithms is None:
            algorithms = ['nearest_neighbor', 'genetic_algorithm', 'simulated_annealing']
        
        results = {}
        
        for algorithm in algorithms:
            print(f"Running {algorithm}...")
            
            # Create solver
            solver = self._create_solver(algorithm)
            optimizer = VRPOptimizer(solver)
            
            # Measure time
            start_time = time.time()
            result = optimizer.optimize(locations, vehicles)
            end_time = time.time()
            
            results[algorithm] = {
                'total_distance': result['total_distance'],
                'num_vehicles_used': result['num_vehicles_used'],
                'average_utilization': result['average_utilization'],
                'computation_time': end_time - start_time,
                'routes': result['routes']
            }
        
        self.results = results
        return results
    
    def _create_solver(self, algorithm: str) -> VRPSolver:
        """Create solver based on algorithm name."""
        if algorithm == 'nearest_neighbor':
            return NearestNeighborSolver()
        elif algorithm == 'genetic_algorithm':
            return GeneticAlgorithmSolver(population_size=50, generations=100)
        elif algorithm == 'simulated_annealing':
            return SimulatedAnnealingSolver(max_iterations=5000)
        elif algorithm == 'ortools' and ORTOOLS_AVAILABLE:
            return ORToolsSolver(time_limit=30)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def print_results(self):
        """Print benchmark results."""
        if not self.results:
            print("No benchmark results available.")
            return
        
        print("\n" + "="*60)
        print("VRP BENCHMARK RESULTS")
        print("="*60)
        
        # Sort by total distance
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['total_distance'])
        
        for algorithm, result in sorted_results:
            print(f"\n{algorithm.upper()}:")
            print(f"  Total Distance: {result['total_distance']:.2f}")
            print(f"  Vehicles Used: {result['num_vehicles_used']}")
            print(f"  Average Utilization: {result['average_utilization']:.2%}")
            print(f"  Computation Time: {result['computation_time']:.2f}s")
    
    def plot_comparison(self):
        """Plot comparison of different algorithms."""
        if not self.results:
            print("No benchmark results available.")
            return
        
        algorithms = list(self.results.keys())
        distances = [self.results[alg]['total_distance'] for alg in algorithms]
        times = [self.results[alg]['computation_time'] for alg in algorithms]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Distance comparison
        ax1.bar(algorithms, distances, color='skyblue', alpha=0.7)
        ax1.set_title('Total Distance Comparison')
        ax1.set_ylabel('Total Distance')
        ax1.tick_params(axis='x', rotation=45)
        
        # Time comparison
        ax2.bar(algorithms, times, color='lightcoral', alpha=0.7)
        ax2.set_title('Computation Time Comparison')
        ax2.set_ylabel('Time (seconds)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()

def example_basic_vrp():
    """Basic VRP example with nearest neighbor solver."""
    print("="*50)
    print("BASIC VRP EXAMPLE")
    print("="*50)
    
    # Generate test data
    locations = VRPDataGenerator.generate_random_locations(15, seed=42)
    vehicles = VRPDataGenerator.generate_vehicles(3, (40, 60))
    
    # Create solver and optimizer
    solver = NearestNeighborSolver()
    optimizer = VRPOptimizer(solver)
    
    # Solve
    result = optimizer.optimize(locations, vehicles)
    
    # Print results
    print(f"Total Distance: {result['total_distance']:.2f}")
    print(f"Vehicles Used: {result['num_vehicles_used']}")
    print(f"Average Utilization: {result['average_utilization']:.2%}")
    
    # Print routes
    for i, route in enumerate(result['routes']):
        print(f"\nRoute {i+1} (Vehicle {route.vehicle_id+1}):")
        print(f"  Path: {' -> '.join(map(str, route.locations))}")
        print(f"  Distance: {route.total_distance:.2f}")
        print(f"  Demand: {route.total_demand:.2f}")
    
    # Visualize
    optimizer.visualize_solution(locations, result['routes'], "Basic VRP Solution")

def example_genetic_algorithm():
    """VRP example with genetic algorithm."""
    print("="*50)
    print("GENETIC ALGORITHM VRP EXAMPLE")
    print("="*50)
    
    # Generate clustered test data
    locations = VRPDataGenerator.generate_clustered_locations(20, 4, seed=42)
    vehicles = VRPDataGenerator.generate_vehicles(4, (30, 50))
    
    # Create solver and optimizer
    solver = GeneticAlgorithmSolver(population_size=50, generations=100)
    optimizer = VRPOptimizer(solver)
    
    # Solve
    start_time = time.time()
    result = optimizer.optimize(locations, vehicles)
    end_time = time.time()
    
    # Print results
    print(f"Total Distance: {result['total_distance']:.2f}")
    print(f"Vehicles Used: {result['num_vehicles_used']}")
    print(f"Average Utilization: {result['average_utilization']:.2%}")
    print(f"Computation Time: {end_time - start_time:.2f}s")
    
    # Visualize
    optimizer.visualize_solution(locations, result['routes'], "Genetic Algorithm VRP Solution")

def example_ortools():
    """VRP example with OR-Tools (if available)."""
    if not ORTOOLS_AVAILABLE:
        print("OR-Tools not available. Skipping this example.")
        return
    
    print("="*50)
    print("OR-TOOLS VRP EXAMPLE")
    print("="*50)
    
    # Generate test data
    locations = VRPDataGenerator.generate_random_locations(25, seed=42)
    vehicles = VRPDataGenerator.generate_vehicles(5, (40, 80))
    
    # Create solver and optimizer
    solver = ORToolsSolver(time_limit=30)
    optimizer = VRPOptimizer(solver)
    
    # Solve
    start_time = time.time()
    result = optimizer.optimize(locations, vehicles)
    end_time = time.time()
    
    # Print results
    print(f"Total Distance: {result['total_distance']:.2f}")
    print(f"Vehicles Used: {result['num_vehicles_used']}")
    print(f"Average Utilization: {result['average_utilization']:.2%}")
    print(f"Computation Time: {end_time - start_time:.2f}s")
    
    # Visualize
    optimizer.visualize_solution(locations, result['routes'], "OR-Tools VRP Solution")

def example_time_windows():
    """VRP example with time windows."""
    print("="*50)
    print("VRP WITH TIME WINDOWS EXAMPLE")
    print("="*50)
    
    # Generate test data with time windows
    locations = VRPDataGenerator.generate_random_locations(12, seed=42)
    locations = VRPDataGenerator.add_time_windows(locations, time_window_ratio=0.6)
    vehicles = VRPDataGenerator.generate_vehicles(3, (50, 70))
    
    # Create solver and optimizer
    base_solver = NearestNeighborSolver()
    solver = VRPTimeWindowSolver(base_solver)
    optimizer = VRPOptimizer(solver)
    
    # Solve
    result = optimizer.optimize(locations, vehicles)
    
    # Print results
    print(f"Total Distance: {result['total_distance']:.2f}")
    print(f"Vehicles Used: {result['num_vehicles_used']}")
    print(f"Average Utilization: {result['average_utilization']:.2%}")
    
    # Print time windows
    print("\nTime Windows:")
    for i, loc in enumerate(locations):
        if loc.time_window:
            print(f"  Customer {i}: {loc.time_window[0]:.0f}-{loc.time_window[1]:.0f} (service: {loc.service_time:.0f})")
    
    # Visualize
    optimizer.visualize_solution(locations, result['routes'], "VRP with Time Windows Solution")

def example_benchmark():
    """Benchmark different VRP algorithms."""
    print("="*50)
    print("VRP ALGORITHMS BENCHMARK")
    print("="*50)
    
    # Generate test data
    locations = VRPDataGenerator.generate_clustered_locations(20, 3, seed=42)
    vehicles = VRPDataGenerator.generate_vehicles(4, (40, 60))
    
    # Run benchmark
    benchmark = VRPBenchmark()
    
    algorithms = ['nearest_neighbor', 'genetic_algorithm', 'simulated_annealing']
    if ORTOOLS_AVAILABLE:
        algorithms.append('ortools')
    
    results = benchmark.run_benchmark(locations, vehicles, algorithms)
    
    # Print and plot results
    benchmark.print_results()
    benchmark.plot_comparison()

def main():
    """Run all examples."""
    print("VRP OPTIMIZATION EXAMPLES")
    print("="*60)
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    try:
        # Run examples
        example_basic_vrp()
        input("\nPress Enter to continue to genetic algorithm example...")
        
        example_genetic_algorithm()
        input("\nPress Enter to continue to OR-Tools example...")
        
        example_ortools()
        input("\nPress Enter to continue to time windows example...")
        
        example_time_windows()
        input("\nPress Enter to continue to benchmark...")
        
        example_benchmark()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nError running examples: {e}")

if __name__ == "__main__":
    main()