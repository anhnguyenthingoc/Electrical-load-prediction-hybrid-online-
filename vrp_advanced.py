from vrp_optimizer import *
import numpy as np
from typing import List, Tuple, Dict, Optional
import time

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("OR-Tools not available. Install with: pip install ortools")

class ORToolsSolver(VRPSolver):
    """OR-Tools based VRP solver with advanced constraints."""
    
    def __init__(self, time_limit: int = 30, first_solution_strategy: str = 'PATH_CHEAPEST_ARC'):
        self.time_limit = time_limit
        self.first_solution_strategy = first_solution_strategy
        
        if not ORTOOLS_AVAILABLE:
            raise ImportError("OR-Tools not available. Install with: pip install ortools")
    
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Solve VRP using OR-Tools."""
        if not locations or not vehicles:
            return []
        
        # Create distance matrix
        distance_matrix = self._create_distance_matrix(locations)
        
        # Create demand array
        demands = [int(loc.demand) for loc in locations]
        
        # Create vehicle capacities
        vehicle_capacities = [int(vehicle.capacity) for vehicle in vehicles]
        
        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(len(locations), len(vehicles), 0)
        
        # Create routing model
        routing = pywrapcp.RoutingModel(manager)
        
        # Add distance constraint
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)  # Scale for integer arithmetic
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add capacity constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return demands[from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity'
        )
        
        # Add time window constraints if available
        if any(loc.time_window for loc in locations):
            self._add_time_window_constraints(routing, manager, locations)
        
        # Set first solution heuristic
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            getattr(routing_enums_pb2.FirstSolutionStrategy, self.first_solution_strategy)
        )
        search_parameters.time_limit.seconds = self.time_limit
        
        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._extract_routes(solution, routing, manager, locations, vehicles)
        else:
            return []
    
    def _create_distance_matrix(self, locations: List[Location]) -> List[List[float]]:
        """Create distance matrix from locations."""
        n = len(locations)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = locations[i].distance_to(locations[j])
        
        return matrix
    
    def _add_time_window_constraints(self, routing, manager, locations: List[Location]):
        """Add time window constraints to the routing model."""
        time_windows = []
        for loc in locations:
            if loc.time_window:
                time_windows.append((int(loc.time_window[0]), int(loc.time_window[1])))
            else:
                time_windows.append((0, 1000000))  # Large time window if not specified
        
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = int(locations[from_node].distance_to(locations[to_node]))
            service_time = int(locations[from_node].service_time)
            return travel_time + service_time
        
        time_callback_index = routing.RegisterTransitCallback(time_callback)
        
        time_dimension = routing.AddDimension(
            time_callback_index,
            1000000,  # allow waiting time
            1000000,  # maximum time per vehicle
            False,  # don't force start cumul to zero
            'Time'
        )
        
        # Add time window constraints for each location
        for location_idx, time_window in enumerate(time_windows):
            if location_idx == 0:
                continue  # Skip depot
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    
    def _extract_routes(self, solution, routing, manager, locations: List[Location], 
                       vehicles: List[Vehicle]) -> List[Route]:
        """Extract routes from OR-Tools solution."""
        routes = []
        
        for vehicle_id in range(len(vehicles)):
            route_locations = []
            index = routing.Start(vehicle_id)
            
            while not routing.IsEnd(index):
                route_locations.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            
            route_locations.append(manager.IndexToNode(index))  # Add depot end
            
            # Calculate route statistics
            total_distance = 0.0
            total_demand = 0.0
            
            for i in range(len(route_locations) - 1):
                total_distance += locations[route_locations[i]].distance_to(locations[route_locations[i + 1]])
            
            for loc_idx in route_locations[1:-1]:  # Exclude depot
                total_demand += locations[loc_idx].demand
            
            route = Route(
                vehicle_id=vehicle_id,
                locations=route_locations,
                total_distance=total_distance,
                total_demand=total_demand
            )
            
            if len(route_locations) > 2:  # Only include routes with customers
                routes.append(route)
        
        return routes

class SimulatedAnnealingSolver(VRPSolver):
    """Simulated Annealing solver for VRP."""
    
    def __init__(self, initial_temp: float = 1000.0, cooling_rate: float = 0.95, 
                 min_temp: float = 1.0, max_iterations: int = 10000):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations
    
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Solve VRP using simulated annealing."""
        if not locations or not vehicles:
            return []
        
        # Start with nearest neighbor solution
        nn_solver = NearestNeighborSolver()
        current_solution = nn_solver.solve(locations, vehicles)
        current_cost = self._calculate_total_cost(current_solution)
        
        best_solution = [self._copy_route(route) for route in current_solution]
        best_cost = current_cost
        
        temp = self.initial_temp
        
        for iteration in range(self.max_iterations):
            if temp < self.min_temp:
                break
            
            # Generate neighbor solution
            neighbor_solution = self._generate_neighbor(current_solution, locations, vehicles)
            neighbor_cost = self._calculate_total_cost(neighbor_solution)
            
            # Accept or reject neighbor
            if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temp):
                current_solution = neighbor_solution
                current_cost = neighbor_cost
                
                if current_cost < best_cost:
                    best_solution = [self._copy_route(route) for route in current_solution]
                    best_cost = current_cost
            
            temp *= self.cooling_rate
        
        return best_solution
    
    def _calculate_total_cost(self, routes: List[Route]) -> float:
        """Calculate total cost of solution."""
        return sum(route.total_distance for route in routes)
    
    def _generate_neighbor(self, routes: List[Route], locations: List[Location], 
                          vehicles: List[Vehicle]) -> List[Route]:
        """Generate neighbor solution using various operators."""
        neighbor_routes = [self._copy_route(route) for route in routes]
        
        # Choose random operator
        operators = [self._swap_customers, self._relocate_customer, self._reverse_segment]
        operator = random.choice(operators)
        
        return operator(neighbor_routes, locations, vehicles)
    
    def _swap_customers(self, routes: List[Route], locations: List[Location], 
                       vehicles: List[Vehicle]) -> List[Route]:
        """Swap two customers between routes."""
        if len(routes) < 2:
            return routes
        
        route1, route2 = random.sample(routes, 2)
        
        if len(route1.locations) > 2 and len(route2.locations) > 2:
            # Get customer indices (excluding depot)
            customers1 = [i for i, loc in enumerate(route1.locations) if loc != 0]
            customers2 = [i for i, loc in enumerate(route2.locations) if loc != 0]
            
            if customers1 and customers2:
                idx1 = random.choice(customers1)
                idx2 = random.choice(customers2)
                
                # Swap customers
                route1.locations[idx1], route2.locations[idx2] = route2.locations[idx2], route1.locations[idx1]
                
                # Recalculate route statistics
                self._recalculate_route_stats(route1, locations)
                self._recalculate_route_stats(route2, locations)
        
        return routes
    
    def _relocate_customer(self, routes: List[Route], locations: List[Location], 
                          vehicles: List[Vehicle]) -> List[Route]:
        """Relocate customer to different position."""
        if not routes:
            return routes
        
        route = random.choice(routes)
        
        if len(route.locations) > 3:  # Need at least depot-customer-depot
            # Get customer indices (excluding depot)
            customers = [i for i, loc in enumerate(route.locations) if loc != 0]
            
            if len(customers) >= 2:
                customer_idx = random.choice(customers)
                customer = route.locations[customer_idx]
                
                # Remove customer
                route.locations.pop(customer_idx)
                
                # Insert at new position
                valid_positions = [i for i in range(1, len(route.locations))]
                if valid_positions:
                    new_pos = random.choice(valid_positions)
                    route.locations.insert(new_pos, customer)
                
                # Recalculate route statistics
                self._recalculate_route_stats(route, locations)
        
        return routes
    
    def _reverse_segment(self, routes: List[Route], locations: List[Location], 
                        vehicles: List[Vehicle]) -> List[Route]:
        """Reverse a segment of a route."""
        if not routes:
            return routes
        
        route = random.choice(routes)
        
        if len(route.locations) > 4:  # Need enough customers to reverse
            # Get customer indices (excluding depot)
            customers = [i for i, loc in enumerate(route.locations) if loc != 0]
            
            if len(customers) >= 2:
                start_idx = random.choice(customers[:-1])
                end_idx = random.choice(customers[start_idx:])
                
                # Reverse segment
                route.locations[start_idx:end_idx + 1] = reversed(route.locations[start_idx:end_idx + 1])
                
                # Recalculate route statistics
                self._recalculate_route_stats(route, locations)
        
        return routes
    
    def _copy_route(self, route: Route) -> Route:
        """Create a copy of a route."""
        return Route(
            vehicle_id=route.vehicle_id,
            locations=route.locations.copy(),
            total_distance=route.total_distance,
            total_demand=route.total_demand
        )
    
    def _recalculate_route_stats(self, route: Route, locations: List[Location]):
        """Recalculate route statistics."""
        # Calculate total distance
        total_distance = 0.0
        for i in range(len(route.locations) - 1):
            total_distance += locations[route.locations[i]].distance_to(locations[route.locations[i + 1]])
        route.total_distance = total_distance
        
        # Calculate total demand
        total_demand = 0.0
        for loc_idx in route.locations[1:-1]:  # Exclude depot
            total_demand += locations[loc_idx].demand
        route.total_demand = total_demand

class VRPTimeWindowSolver(VRPSolver):
    """VRP solver with time window constraints."""
    
    def __init__(self, base_solver: VRPSolver):
        self.base_solver = base_solver
    
    def solve(self, locations: List[Location], vehicles: List[Vehicle]) -> List[Route]:
        """Solve VRP with time window constraints."""
        # Get base solution
        routes = self.base_solver.solve(locations, vehicles)
        
        # Check and repair time window violations
        for route in routes:
            self._repair_time_windows(route, locations)
        
        return routes
    
    def _repair_time_windows(self, route: Route, locations: List[Location]):
        """Repair time window violations in a route."""
        current_time = 0.0
        
        for i in range(len(route.locations) - 1):
            current_loc = route.locations[i]
            next_loc = route.locations[i + 1]
            
            # Add travel time
            travel_time = locations[current_loc].distance_to(locations[next_loc])
            current_time += travel_time
            
            # Check time window
            if locations[next_loc].time_window:
                earliest, latest = locations[next_loc].time_window
                if current_time < earliest:
                    current_time = earliest  # Wait
                elif current_time > latest:
                    # Time window violation - need to reschedule or remove
                    pass
            
            # Add service time
            current_time += locations[next_loc].service_time