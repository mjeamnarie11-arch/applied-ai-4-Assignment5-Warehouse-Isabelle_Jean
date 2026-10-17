#!/usr/bin/env python3
"""
Skeleton Optimization Agent - Template for students to implement optimization algorithms

IMPORTANT: This is NOT an RL agent - it's a template for 
students to implement their own optimization algorithms (greedy, Hungarian, etc.)

This agent currently makes terrible decisions:
- Random staffing decisions
- No layout optimization 
- Ignores order priorities
- No intelligent assignment logic

Students should replace the naive methods with proper optimization algorithms.
"""

import numpy as np
from typing import Dict, Optional
from .standardized_agents import BaselineAgent
from environment.employee import EmployeeState
from environment.warehouse_grid import CellType

class SkeletonOptimizationAgent(BaselineAgent):
    """
    Template for students to implement their own optimization algorithms.
    
    Students should replace the naive methods with:
    - Economic models for staffing decisions
    - Hungarian algorithm for order assignment  
    - Greedy search for layout optimization
    - Multi-objective optimization techniques
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.name = "StudentOptimization"
        
        # Enable unlimited hiring for true economic optimization
        self.env._unlimited_hiring = True
        
        # Students can add their own state tracking here
        self.performance_metrics = []
        self.decision_history = []
        
        # Students can add algorithm parameters here
        # Example: Hungarian algorithm matrices, greedy search parameters, etc.
        self.staffing_parameters = {
            'hire_threshold_ratio': 3.0,
            'fire_threshold_ratio': 2.0,
            'profit_threshold': 0
        }
        
        # Students can implement adaptive parameters that change based on performance
        self.adaptive_optimization_enabled = False
        
    def reset(self):
        """Reset agent state - students should expand this"""
        self.action_history = []
        self.reward_history = []
        # TODO: Reset any neural network states, replay buffers, etc.
    
    def get_action(self, observation: Dict) -> Dict:
        """
        Generate action based on observation.
        Current implementation is intentionally terrible - students should improve!
        """
        
        # Extract basic info from observation
        current_timestep = observation['time'][0]
        financial_state = observation['financial']  # [profit, revenue, costs, burn_rate]
        queue_info = observation['order_queue']
        employee_info = observation['employees']
        
        action = {
            'staffing_action': self._get_naive_staffing_action(financial_state, employee_info),
            'layout_swap': self._get_naive_layout_action(current_timestep),
            'order_assignments': self._get_naive_order_assignments(queue_info, employee_info)
        }
        
        # TODO: Students should implement proper action recording for optimization
        self.action_history.append(action.copy())
        
        return action
    
    def _get_naive_staffing_action(self, financial_state, employee_info) -> int:
        """
        WEEK 2 STEP 1: Staffing decisions - students should improve this!
        
        Current problems:
        - Ignores queue length and workload
        - Random decisions regardless of profit
        - No consideration of employee efficiency
        """
        
        # TODO WEEK 2 STEP 1: Students should implement intelligent staffing logic
        # Current approach: Make random decisions based on "vibes"
        
        num_employees = len(self.env.employees)
        has_manager = any(
            employee.is_manager for employee in self.env.employees
        )
        can_hire = num_employees < self.env.max_employees

        if np.random.random() < 0.3:
            if can_hire:
                return 1  # Hire worker

        elif np.random.random() < 0.1:
            if num_employees > 1:
                return 2  # Fire employee

        elif np.random.random() < 0.2:
            if can_hire and not has_manager:
                return 3  # Hire manager only when none exists

        return 0  # No staffing change
    
    def _get_naive_layout_action(self, current_timestep) -> list:
        """
        Retain the template's random staffing decisions while correcting
        employee counting, manager detection, and hiring limits.
        """
        
        # TODO WEEK 1 STEP 1: Students should implement intelligent layout optimization
        # Current approach: Occasionally make random swaps
        
        if current_timestep == 0 or current_timestep % 100 != 0:
            return [0, 0]

        grid = self.env.warehouse_grid
        frequencies = grid.item_access_frequency

        print(
            f"[Layout step {current_timestep}] "
            f"Recorded accesses: {frequencies.sum():.0f}, "
            f"Employees: {len(self.env.employees)}"
        )

        # The environment uses the first manager for relocation requests.
        manager = next(
            (employee for employee in self.env.employees
             if employee.is_manager),
            None
        )

        if manager is None:
            print("  Skipped: no manager available.")
            return [0, 0]

        if manager.state != EmployeeState.IDLE:
            print(f"  Skipped: manager is busy ({manager.state.name}).")
            return [0, 0]

        if not np.any(frequencies > 0):
            print("  Skipped: no product retrievals recorded yet.")
            return [0, 0]

        # Only accessible permanent storage cells are valid swap locations.
        positions = [
            (x, y)
            for y in range(grid.height)
            for x in range(grid.width)
            if grid.cell_types[y, x] == CellType.STORAGE.value
            and grid.can_access_storage(x, y)
        ]

        distances = {
            position: self._distance_to_delivery(position)
            for position in positions
        }

        # Estimate demand per copy of each product.
        copy_counts = np.bincount(
            grid.item_grid[grid.item_grid >= 0],
            minlength=len(frequencies)
        )

        best_score = 0.0
        best_swap = [0, 0]

        for source in positions:
            source_item = grid.get_item_at_position(*source)
            if source_item is None:
                continue

            source_frequency = (
                frequencies[source_item] / max(1, copy_counts[source_item])
            )
            if source_frequency <= 0:
                continue

            for target in positions:
                distance_saved = distances[source] - distances[target]

                # Require at least two steps of delivery-distance improvement.
                if distance_saved < 2:
                    continue

                target_item = grid.get_item_at_position(*target)
                if target_item == source_item:
                    continue

                target_frequency = 0.0
                if target_item is not None:
                    target_frequency = (
                        frequencies[target_item]
                        / max(1, copy_counts[target_item])
                    )

                # Account for moving the other product farther from delivery.
                net_benefit = (
                    source_frequency - target_frequency
                ) * distance_saved

                if net_benefit <= 0:
                    continue

                # Favor beneficial swaps with shorter manager travel.
                relocation_distance = (
                    grid.manhattan_distance(manager.position, source)
                    + grid.manhattan_distance(source, target)
                )
                score = net_benefit / (1 + relocation_distance)

                if score > best_score:
                    best_score = score
                    best_swap = [
                        source[1] * grid.width + source[0],
                        target[1] * grid.width + target[0]
                    ]

        print(
            f"  Selected swap: {best_swap}, "
            f"Estimated score: {best_score:.2f}"
        )

        if best_swap == [0, 0]:
            print("  No beneficial swap found.")

        return best_swap

    def _distance_to_delivery(self, position) -> int:
        """Return Manhattan distance to the nearest truck bay."""
        grid = self.env.warehouse_grid
        return min(
            grid.manhattan_distance(position, bay)
            for bay in grid.truck_bay_positions
        )
    
    def _get_naive_order_assignments(self, queue_info, employee_info) -> list:
        """
        WEEK 2 STEP 2: Order assignment - students should improve this!
        
        Current problems:
        - Ignores employee locations
        - No consideration of order priority/value
        - Random assignments regardless of efficiency
        - Doesn't check if employees are actually available
        """
        
        # TODO WEEK 2 STEP 2: Students should implement intelligent order assignment
        # Current approach: Random assignments
        
        assignments = [0] * 20  # No assignments by default
        
        # Count how many employees we have (very naive)
        num_employees = int(np.sum(employee_info[:, 0] > 0))
        
        # Randomly assign first few orders to first few employees
        if num_employees > 0:
            for i in range(min(3, num_employees)):  # Only assign 3 orders max
                if np.random.random() < 0.6:  # 60% chance to assign
                    assignments[i] = (i % num_employees) + 1  # Random employee
        
        return assignments
    
    def record_reward(self, reward: float):
        """
        WEEK 3 STEP 1: Reward tracking and learning - students should expand this
        
        TODO WEEK 3 STEP 1: Students should implement:
        - Proper reward tracking
        - Performance analysis
        - Adaptive parameter adjustment
        - Multi-objective optimization
        """
        self.reward_history.append(reward)
        
        # Skeleton optimization - doesn't actually learn anything useful
        if len(self.reward_history) > 10:
            # "Update" weights randomly (this doesn't actually improve performance)
            if reward > 0:
                self.staffing_weights += np.random.randn(4) * 0.01
                self.layout_weights += np.random.randn(3) * 0.01
    
    def should_update_policy(self) -> bool:
        """
        WEEK 3 STEP 2: Policy updates and adaptation - students should improve this
        
        TODO WEEK 3 STEP 2: Students should implement proper update schedules
        """
        return len(self.action_history) % 50 == 0  # Arbitrary update frequency
    
    def get_performance_metrics(self) -> Dict:
        """
        Get agent performance metrics for analysis
        Students can use this to debug their improvements
        """
        if not self.reward_history:
            return {"avg_reward": 0, "total_actions": 0}
        
        return {
            "avg_reward": np.mean(self.reward_history[-100:]),  # Last 100 rewards
            "total_actions": len(self.action_history),
            "exploration_rate": self.exploration_rate,
            "recent_performance": np.mean(self.reward_history[-10:]) if len(self.reward_history) >= 10 else 0
        }


def create_skeleton_optimization_agent(env) -> SkeletonOptimizationAgent:
    """Factory function to create skeleton Optimization agent"""
    return SkeletonOptimizationAgent(env)


# TODO: Students should implement these advanced components:

class StudentOptimizationAgent(SkeletonOptimizationAgent):
    """
    Template for students to implement their improved Optimization agent
    
    Suggested improvements:
    1. Replace random staffing with demand-based hiring
    2. Implement proper layout optimization using item frequencies
    3. Add distance-based order assignment
    4. Implement basic Q-optimization or policy gradients
    5. Add proper exploration vs exploitation balance
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.name = "StudentOptimization"
        
        # TODO: Students implement these
        # self.q_table = {}
        # self.policy_network = SimpleNeuralNetwork()
        # self.experience_buffer = []
        # self.target_network = None
        
    def _get_improved_staffing_action(self, financial_state, employee_info, queue_info):
        """
        WEEK 2 STEP 1: Students implement intelligent staffing:
        - Hire when queue is growing
        - Fire when queue is empty for extended periods
        - Consider profit margins before hiring
        - Balance managers vs workers
        """
        pass
    
    def _get_improved_layout_action(self, observation):
        """
        WEEK 1 STEP 1: Students implement smart layout optimization:
        - Move frequently accessed items closer to delivery
        - Group items that are often ordered together
        - Only optimize when queue is manageable
        - Track swap effectiveness
        """
        pass
    
    def _get_improved_order_assignments(self, queue_info, employee_info):
        """
        WEEK 2 STEP 2: Students implement efficient order assignment:
        - Assign orders to closest available employees
        - Prioritize high-value or urgent orders
        - Consider employee current locations
        - Balance workload across employees
        """
        pass
    
    def learn_from_experience(self, state, action, reward, next_state, done):
        """
        WEEK 3 STEP 3: Students implement multi-objective optimization:
        - Performance trend analysis
        - Adaptive parameter tuning
        - Multi-objective trade-off handling
        - Robust optimization techniques
        """
        pass