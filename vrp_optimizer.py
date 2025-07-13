import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import math
from collections import defaultdict

@dataclass
class Location:
    """Represents a location with coordinates and optional time window."""
    x: float
    y: float
    demand: float = 0.0
    time_window: Optional[Tuple[float, float]] = None
    service_time: float = 0.0
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate Euclidean distance to another location."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Vehicle:
    """Represents a vehicle with capacity constraints."""
    capacity: float
    start_location: int = 0
    end_location: Optional[int] = None
    
    def __post_init__(self):
        if self.end_location is None:
            self.end_location = self.start_location

@dataclass
class Route:
    """Represents a route for a vehicle."""
    vehicle_id: int
    locations: List[int]
    total_distance: float = 0.0
    total_demand: float = 0.0
    
    def is_feasible(self, vehicle: Vehicle, locations: List[Location]) -> bool:
        """Check if route is feasible given vehicle capacity."""
        return self.total_demand <= vehicle.capacity

class VRPSolver(ABC):
    """Abstract base class for VRP solvers."""
    
    @abstractmethod
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Solve the VRP and return optimized routes."""
        pass

class NearestNeighborSolver(VRPSolver):
    """Simple nearest neighbor heuristic for VRP."""
    
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Solve VRP using nearest neighbor heuristic."""
        if not locations or not vehicles:
            return []
        
        depot = locations[0]
        customers = list(range(1, len(locations)))
        routes = []
        
        for vehicle_id, vehicle in enumerate(vehicles):
            if not customers:
                break
                
            route = Route(vehicle_id=vehicle_id, locations=[0])  # Start at depot
            current_location = 0
            current_demand = 0.0
            
            while customers:
                # Find nearest unvisited customer
                min_distance = float('inf')
                nearest_customer = None
                
                for customer in customers:
                    if current_demand + locations[customer].demand <= vehicle.capacity:
                        distance = locations[current_location].distance_to(locations[customer])
                        if distance < min_distance:
                            min_distance = distance
                            nearest_customer = customer
                
                if nearest_customer is None:
                    break
                
                # Add customer to route
                route.locations.append(nearest_customer)
                current_demand += locations[nearest_customer].demand
                current_location = nearest_customer
                customers.remove(nearest_customer)
            
            # Return to depot
            route.locations.append(0)
            route.total_demand = current_demand
            route.total_distance = self._calculate_route_distance(route, locations)
            routes.append(route)
        
        return routes
    
    def _calculate_route_distance(self, route: Route, locations: List[Location]) -> float:
        """Calculate total distance for a route."""
        total_distance = 0.0
        for i in range(len(route.locations) - 1):
            total_distance += locations[route.locations[i]].distance_to(locations[route.locations[i + 1]])
        return total_distance

class GeneticAlgorithmSolver(VRPSolver):
    """Genetic Algorithm solver for VRP."""
    
    def __init__(self, population_size: int = 100, generations: int = 500, 
                 mutation_rate: float = 0.1, elite_size: int = 20):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
    
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Solve VRP using genetic algorithm."""
        if not locations or not vehicles:
            return []
        
        customers = list(range(1, len(locations)))
        population = self._create_initial_population(customers, len(vehicles))
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [(individual, self._evaluate_fitness(individual, locations, vehicles)) 
                            for individual in population]
            fitness_scores.sort(key=lambda x: x[1])
            
            # Select elite
            elite = [individual for individual, _ in fitness_scores[:self.elite_size]]
            
            # Create new population
            new_population = elite.copy()
            
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(fitness_scores)
                parent2 = self._tournament_selection(fitness_scores)
                child = self._crossover(parent1, parent2)
                
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population
        
        # Convert best solution to routes
        best_individual = min(population, key=lambda x: self._evaluate_fitness(x, locations, vehicles))
        return self._convert_to_routes(best_individual, locations, vehicles)
    
    def _create_initial_population(self, customers: List[int], num_vehicles: int) -> List[List[int]]:
        """Create initial population for genetic algorithm."""
        population = []
        for _ in range(self.population_size):
            individual = customers.copy()
            random.shuffle(individual)
            population.append(individual)
        return population
    
    def _evaluate_fitness(self, individual: List[int], locations: List[Location], vehicles: List[Vehicle]) -> float:
        """Evaluate fitness of an individual (lower is better)."""
        routes = self._convert_to_routes(individual, locations, vehicles)
        total_distance = sum(route.total_distance for route in routes)
        
        # Add penalty for constraint violations
        penalty = 0.0
        for route in routes:
            vehicle = vehicles[route.vehicle_id]
            if route.total_demand > vehicle.capacity:
                penalty += 1000 * (route.total_demand - vehicle.capacity)
        
        return total_distance + penalty
    
    def _tournament_selection(self, fitness_scores: List[Tuple[List[int], float]]) -> List[int]:
        """Select parent using tournament selection."""
        tournament_size = 3
        tournament = random.sample(fitness_scores, tournament_size)
        return min(tournament, key=lambda x: x[1])[0]
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """Perform order crossover (OX)."""
        if len(parent1) < 2:
            return parent1.copy()
        
        start = random.randint(0, len(parent1) - 2)
        end = random.randint(start + 1, len(parent1))
        
        child = [-1] * len(parent1)
        child[start:end] = parent1[start:end]
        
        pointer = end
        for gene in parent2[end:] + parent2[:end]:
            if gene not in child:
                child[pointer % len(child)] = gene
                pointer += 1
        
        return child
    
    def _mutate(self, individual: List[int]) -> List[int]:
        """Perform mutation by swapping two random genes."""
        if len(individual) < 2:
            return individual
        
        mutated = individual.copy()
        i, j = random.sample(range(len(mutated)), 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
        return mutated
    
    def _convert_to_routes(self, individual: List[int], locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Convert individual to routes."""
        routes = []
        customer_index = 0
        
        for vehicle_id, vehicle in enumerate(vehicles):
            if customer_index >= len(individual):
                break
            
            route = Route(vehicle_id=vehicle_id, locations=[0])
            current_demand = 0.0
            
            while customer_index < len(individual):
                customer = individual[customer_index]
                customer_demand = locations[customer].demand
                
                if current_demand + customer_demand <= vehicle.capacity:
                    route.locations.append(customer)
                    current_demand += customer_demand
                    customer_index += 1
                else:
                    break
            
            route.locations.append(0)  # Return to depot
            route.total_demand = current_demand
            route.total_distance = self._calculate_route_distance(route, locations)
            routes.append(route)
        
        return routes
    
    def _calculate_route_distance(self, route: Route, locations: List[Location]) -> float:
        """Calculate total distance for a route."""
        total_distance = 0.0
        for i in range(len(route.locations) - 1):
            total_distance += locations[route.locations[i]].distance_to(locations[route.locations[i + 1]])
        return total_distance

class VRPOptimizer:
    """Main VRP optimizer class."""
    
    def __init__(self, solver: VRPSolver):
        self.solver = solver
    
    def optimize(self, locations: List[Location], vehicles: List[Vehicle]) -> Dict:
        """Optimize VRP and return results."""
        routes = self.solver.solve(locations, vehicles)
        
        # Calculate statistics
        total_distance = sum(route.total_distance for route in routes)
        total_demand = sum(route.total_demand for route in routes)
        vehicle_utilization = [route.total_demand / vehicles[route.vehicle_id].capacity 
                             for route in routes if route.vehicle_id < len(vehicles)]
        
        return {
            'routes': routes,
            'total_distance': total_distance,
            'total_demand': total_demand,
            'num_vehicles_used': len(routes),
            'vehicle_utilization': vehicle_utilization,
            'average_utilization': np.mean(vehicle_utilization) if vehicle_utilization else 0.0
        }
    
    def visualize_solution(self, locations: List[Location], routes: List[Route], 
                          title: str = "VRP Solution"):
        """Visualize the VRP solution."""
        plt.figure(figsize=(12, 8))
        
        # Plot locations
        depot_x, depot_y = locations[0].x, locations[0].y
        customer_x = [loc.x for loc in locations[1:]]
        customer_y = [loc.y for loc in locations[1:]]
        
        plt.scatter(depot_x, depot_y, c='red', s=200, marker='s', label='Depot', zorder=5)
        plt.scatter(customer_x, customer_y, c='blue', s=100, marker='o', label='Customers', zorder=5)
        
        # Plot routes
        colors = plt.cm.Set3(np.linspace(0, 1, len(routes)))
        
        for i, route in enumerate(routes):
            if len(route.locations) > 2:  # Only plot routes with customers
                route_x = [locations[loc].x for loc in route.locations]
                route_y = [locations[loc].y for loc in route.locations]
                plt.plot(route_x, route_y, color=colors[i], linewidth=2, alpha=0.7, 
                        label=f'Vehicle {route.vehicle_id + 1}', zorder=1)
        
        # Add customer labels
        for i, loc in enumerate(locations):
            if i == 0:
                plt.annotate('Depot', (loc.x, loc.y), xytext=(5, 5), textcoords='offset points')
            else:
                plt.annotate(f'C{i}', (loc.x, loc.y), xytext=(5, 5), textcoords='offset points')
        
        plt.title(title)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()