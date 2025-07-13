# VRP Optimization Library

A comprehensive Python library for solving Vehicle Routing Problems (VRP) using various optimization algorithms.

## Features

- **Multiple Algorithms**: Nearest Neighbor, Genetic Algorithm, Simulated Annealing, OR-Tools
- **VRP Variants**: Basic VRP, Capacitated VRP (CVRP), VRP with Time Windows (VRPTW)
- **Visualization**: Interactive plotting of solutions with matplotlib
- **Benchmarking**: Compare different algorithms on the same problem
- **Extensible**: Easy to add new algorithms and constraints

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. For OR-Tools support (optional but recommended):
```bash
pip install ortools
```

## Quick Start

```python
from vrp_optimizer import *
from vrp_examples import VRPDataGenerator

# Generate test data
locations = VRPDataGenerator.generate_random_locations(15, seed=42)
vehicles = VRPDataGenerator.generate_vehicles(3, (40, 60))

# Create solver and optimizer
solver = NearestNeighborSolver()
optimizer = VRPOptimizer(solver)

# Solve the problem
result = optimizer.optimize(locations, vehicles)

# Print results
print(f"Total Distance: {result['total_distance']:.2f}")
print(f"Vehicles Used: {result['num_vehicles_used']}")

# Visualize solution
optimizer.visualize_solution(locations, result['routes'])
```

## Algorithms

### 1. Nearest Neighbor Heuristic
Simple greedy algorithm that always visits the nearest unvisited customer.

```python
solver = NearestNeighborSolver()
```

### 2. Genetic Algorithm
Evolutionary algorithm that evolves a population of solutions.

```python
solver = GeneticAlgorithmSolver(
    population_size=100,
    generations=500,
    mutation_rate=0.1,
    elite_size=20
)
```

### 3. Simulated Annealing
Metaheuristic that accepts worse solutions with decreasing probability.

```python
solver = SimulatedAnnealingSolver(
    initial_temp=1000.0,
    cooling_rate=0.95,
    min_temp=1.0,
    max_iterations=10000
)
```

### 4. OR-Tools (Google)
Professional optimization solver with advanced constraints.

```python
solver = ORToolsSolver(
    time_limit=30,
    first_solution_strategy='PATH_CHEAPEST_ARC'
)
```

## VRP Variants

### Basic VRP
```python
# Standard VRP with distance minimization
locations = [Location(x, y, demand) for x, y, demand in data]
vehicles = [Vehicle(capacity) for capacity in capacities]
```

### VRP with Time Windows
```python
# Add time windows to locations
location.time_window = (earliest_time, latest_time)
location.service_time = service_duration

# Use time window solver
base_solver = NearestNeighborSolver()
solver = VRPTimeWindowSolver(base_solver)
```

### Capacitated VRP
```python
# Vehicles have capacity constraints
vehicles = [Vehicle(capacity=50) for _ in range(num_vehicles)]

# Customers have demands
locations = [Location(x, y, demand=5) for x, y in coordinates]
```

## Data Classes

### Location
```python
@dataclass
class Location:
    x: float                    # X coordinate
    y: float                    # Y coordinate
    demand: float = 0.0         # Customer demand
    time_window: Optional[Tuple[float, float]] = None  # (earliest, latest)
    service_time: float = 0.0   # Service duration
```

### Vehicle
```python
@dataclass
class Vehicle:
    capacity: float             # Vehicle capacity
    start_location: int = 0     # Starting depot
    end_location: Optional[int] = None  # Ending depot (optional)
```

### Route
```python
@dataclass
class Route:
    vehicle_id: int             # Vehicle identifier
    locations: List[int]        # Sequence of location indices
    total_distance: float       # Total route distance
    total_demand: float         # Total demand served
```

## Examples

### Basic Example
```python
from vrp_examples import example_basic_vrp
example_basic_vrp()
```

### Genetic Algorithm Example
```python
from vrp_examples import example_genetic_algorithm
example_genetic_algorithm()
```

### Benchmark Multiple Algorithms
```python
from vrp_examples import example_benchmark
example_benchmark()
```

### Run All Examples
```python
python vrp_examples.py
```

## Data Generation

The library includes utilities for generating test data:

```python
from vrp_examples import VRPDataGenerator

# Random locations
locations = VRPDataGenerator.generate_random_locations(20, seed=42)

# Clustered locations
locations = VRPDataGenerator.generate_clustered_locations(30, num_clusters=4)

# Add time windows
locations = VRPDataGenerator.add_time_windows(locations, time_window_ratio=0.5)

# Generate vehicles
vehicles = VRPDataGenerator.generate_vehicles(5, capacity_range=(40, 80))
```

## Benchmarking

Compare different algorithms on the same problem:

```python
from vrp_examples import VRPBenchmark

# Create benchmark
benchmark = VRPBenchmark()

# Run comparison
results = benchmark.run_benchmark(locations, vehicles, 
                                  ['nearest_neighbor', 'genetic_algorithm', 'ortools'])

# Print results
benchmark.print_results()

# Plot comparison
benchmark.plot_comparison()
```

## Visualization

The library provides built-in visualization:

```python
optimizer.visualize_solution(locations, routes, title="My VRP Solution")
```

Features:
- Depot shown as red square
- Customers shown as blue circles
- Routes shown in different colors
- Customer labels and annotations
- Equal axis scaling

## Extending the Library

### Adding New Algorithms

1. Create a new solver class inheriting from `VRPSolver`:

```python
class MyCustomSolver(VRPSolver):
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        # Implement your algorithm here
        routes = []
        # ... algorithm implementation ...
        return routes
```

2. Use your solver:

```python
solver = MyCustomSolver()
optimizer = VRPOptimizer(solver)
result = optimizer.optimize(locations, vehicles)
```

### Adding New Constraints

1. Extend the `Location` or `Vehicle` classes:

```python
@dataclass
class ExtendedLocation(Location):
    priority: int = 1
    location_type: str = "customer"
```

2. Modify solver logic to handle new constraints.

## Performance Tips

1. **OR-Tools**: Best for complex problems with many constraints
2. **Genetic Algorithm**: Good balance of quality and speed
3. **Simulated Annealing**: Effective for medium-sized problems
4. **Nearest Neighbor**: Fast but lower quality solutions

## Algorithm Comparison

| Algorithm | Speed | Quality | Scalability | Constraints |
|-----------|-------|---------|-------------|-------------|
| Nearest Neighbor | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Genetic Algorithm | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Simulated Annealing | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| OR-Tools | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Common Use Cases

1. **Delivery Services**: Route optimization for package delivery
2. **Waste Collection**: Optimize garbage collection routes
3. **Service Technicians**: Route field service workers
4. **Supply Chain**: Optimize distribution from warehouses
5. **Emergency Services**: Optimize ambulance/fire truck routing

## Troubleshooting

### OR-Tools Import Error
```bash
pip install ortools
```

### Visualization Not Working
```bash
pip install matplotlib
```

### Performance Issues
- Reduce problem size for testing
- Use simpler algorithms for large problems
- Adjust algorithm parameters (population size, iterations)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## References

- Toth, P., & Vigo, D. (2014). Vehicle routing: problems, methods, and applications.
- Golden, B. L., Raghavan, S., & Wasil, E. A. (2008). The vehicle routing problem: latest advances and new challenges.
- OR-Tools documentation: https://developers.google.com/optimization