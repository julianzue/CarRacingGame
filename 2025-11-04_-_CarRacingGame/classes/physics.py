"""
Physics module for 3D Car Racing Game
Contains the base Physics class with collision detection and physics parameters.
"""


class Physics:
    """Base physics class with collision detection and physics parameters"""
    
    def __init__(self):
        self.gravity = 9.81  # m/s^2
        self.friction_coefficient = 0.1  # arbitrary friction coefficient
        self.collision_distance = 0.5  # distance to consider a collision

    def check_collision(self, other):
        """Enhanced collision detection between car and any obstacle"""
        # Car dimensions (approximate)
        car_width = 0.6
        car_depth = 1.2
        
        # Check if car is within obstacle's bounding box
        dx = abs(self.x - other.x)
        dz = abs(self.z - other.z)
        
        # Calculate collision boundaries with a small buffer
        collision_x = (car_width + other.width) / 2 + 0.1
        collision_z = (car_depth + other.depth) / 2 + 0.1
        
        # Check for collision
        is_colliding = dx < collision_x and dz < collision_z
        
        if is_colliding:
            # Calculate collision severity based on distance
            collision_severity = 1.0 - (dx / collision_x + dz / collision_z) / 2
            return collision_severity
        
        return 0.0  # No collision