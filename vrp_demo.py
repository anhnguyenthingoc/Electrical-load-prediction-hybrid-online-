#!/usr/bin/env python3
"""
VRP Optimization Demo

This script demonstrates how to use the VRP optimization library 
for a practical delivery routing problem.
"""

import time
from vrp_optimizer import *
from vrp_examples import VRPDataGenerator, VRPBenchmark
from vrp_advanced import SimulatedAnnealingSolver

def delivery_service_example():
    """Example: Delivery service routing problem."""
    
    print("="*60)
    print("DELIVERY SERVICE ROUTING OPTIMIZATION")
    print("="*60)
    
    # Problem setup
    print("\n📦 PROBLEM SETUP")
    print("- Distribution center (depot) at city center")
    print("- 20 customers scattered across the city")
    print("- 3 delivery trucks with different capacities")
    print("- Minimize total travel distance")
    
    # Generate realistic delivery locations (clustered around city areas)
    locations = VRPDataGenerator.generate_clustered_locations(
        num_customers=20, 
        num_clusters=4, 
        area_size=100, 
        seed=42
    )
    
    # Create delivery vehicles with different capacities
    vehicles = [
        Vehicle(capacity=60),  # Small truck
        Vehicle(capacity=80),  # Medium truck  
        Vehicle(capacity=100), # Large truck
    ]
    
    # Print problem details
    print(f"\n📍 LOCATIONS:")
    print(f"  Depot: ({locations[0].x:.1f}, {locations[0].y:.1f})")
    print(f"  Customers: {len(locations)-1}")
    total_demand = sum(loc.demand for loc in locations[1:])
    print(f"  Total demand: {total_demand:.1f}")
    
    print(f"\n🚚 VEHICLES:")
    total_capacity = sum(v.capacity for v in vehicles)
    for i, vehicle in enumerate(vehicles):
        print(f"  Vehicle {i+1}: Capacity {vehicle.capacity}")
    print(f"  Total capacity: {total_capacity}")
    
    # Solve with different algorithms
    print(f"\n🔍 SOLVING WITH DIFFERENT ALGORITHMS...")
    
    algorithms = [
        ('Nearest Neighbor', NearestNeighborSolver()),
        ('Genetic Algorithm', GeneticAlgorithmSolver(population_size=50, generations=100)),
        ('Simulated Annealing', SimulatedAnnealingSolver(max_iterations=2000)),
    ]
    
    results = {}
    
    for name, solver in algorithms:
        print(f"\n  Running {name}...")
        optimizer = VRPOptimizer(solver)
        
        start_time = time.time()
        result = optimizer.optimize(locations, vehicles)
        end_time = time.time()
        
        results[name] = {
            'result': result,
            'time': end_time - start_time
        }
    
    # Compare results
    print(f"\n📊 RESULTS COMPARISON:")
    print(f"{'Algorithm':<20} {'Distance':<12} {'Vehicles':<10} {'Utilization':<12} {'Time':<8}")
    print("-" * 62)
    
    for name, data in results.items():
        result = data['result']
        time_taken = data['time']
        
        print(f"{name:<20} {result['total_distance']:<12.1f} "
              f"{result['num_vehicles_used']:<10} "
              f"{result['average_utilization']:<12.1%} "
              f"{time_taken:<8.2f}s")
    
    # Show best solution details
    best_algo = min(results.keys(), key=lambda x: results[x]['result']['total_distance'])
    best_result = results[best_algo]['result']
    
    print(f"\n🏆 BEST SOLUTION ({best_algo}):")
    print(f"  Total Distance: {best_result['total_distance']:.1f}")
    print(f"  Vehicles Used: {best_result['num_vehicles_used']}")
    print(f"  Average Utilization: {best_result['average_utilization']:.1%}")
    
    print(f"\n📍 ROUTE DETAILS:")
    for i, route in enumerate(best_result['routes']):
        print(f"  Route {i+1} (Vehicle {route.vehicle_id+1}):")
        print(f"    Path: {' → '.join(map(str, route.locations))}")
        print(f"    Distance: {route.total_distance:.1f}")
        print(f"    Load: {route.total_demand:.1f}/{vehicles[route.vehicle_id].capacity}")
        print(f"    Utilization: {route.total_demand/vehicles[route.vehicle_id].capacity:.1%}")
    
    # Visualize best solution
    print(f"\n📈 Generating visualization...")
    optimizer = VRPOptimizer(algorithms[0][1])  # Use first algorithm for visualization
    try:
        optimizer.visualize_solution(locations, best_result['routes'], 
                                   f"Best VRP Solution - {best_algo}")
        print("  ✓ Visualization displayed")
    except Exception as e:
        print(f"  ⚠ Visualization failed: {e}")
    
    return best_result

def capacity_analysis():
    """Analyze the impact of vehicle capacity on solution quality."""
    
    print("\n" + "="*60)
    print("CAPACITY ANALYSIS")
    print("="*60)
    
    # Generate test data
    locations = VRPDataGenerator.generate_random_locations(15, seed=42)
    total_demand = sum(loc.demand for loc in locations[1:])
    
    print(f"\nTotal customer demand: {total_demand:.1f}")
    
    # Test different capacity scenarios
    capacity_scenarios = [
        ("Low Capacity", 30),
        ("Medium Capacity", 50), 
        ("High Capacity", 80),
        ("Very High Capacity", 120)
    ]
    
    solver = NearestNeighborSolver()
    optimizer = VRPOptimizer(solver)
    
    print(f"\n{'Scenario':<20} {'Capacity':<10} {'Vehicles':<10} {'Distance':<12} {'Utilization':<12}")
    print("-" * 64)
    
    for scenario_name, capacity in capacity_scenarios:
        # Calculate minimum vehicles needed
        min_vehicles = max(3, int(total_demand / capacity) + 1)
        vehicles = [Vehicle(capacity=capacity) for _ in range(min_vehicles)]
        
        result = optimizer.optimize(locations, vehicles)
        
        print(f"{scenario_name:<20} {capacity:<10} {result['num_vehicles_used']:<10} "
              f"{result['total_distance']:<12.1f} {result['average_utilization']:<12.1%}")

def main():
    """Run the VRP optimization demo."""
    
    print("VRP OPTIMIZATION DEMO")
    print("A practical demonstration of vehicle routing optimization")
    
    try:
        # Run delivery service example
        delivery_service_example()
        
        # Run capacity analysis
        capacity_analysis()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nKey takeaways:")
        print("• Different algorithms provide different trade-offs between solution quality and speed")
        print("• Vehicle capacity significantly impacts the number of vehicles needed")
        print("• Higher capacity vehicles generally lead to better route efficiency")
        print("• Genetic Algorithm often provides the best balance of quality and speed")
        print("\nFor more advanced features, check out:")
        print("• vrp_examples.py - Comprehensive examples")
        print("• vrp_advanced.py - OR-Tools integration and time windows")
        print("• VRP_README.md - Complete documentation")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()