"""
Track module for 3D Car Racing Game
Contains the Track class that manages road layout, buildings, and lighting.
"""
import random
import pygame
import numpy as np
from OpenGL.GL import *
from classes.building import Building
from classes.lighting import StreetLight, TrafficLight
from classes.signs import Sign, create_intersection_signs


class Track:
    """Track class that manages the cross-shaped road with buildings and lighting"""
    
    # Class-level grass texture cache
    _grass_texture_cache = {}
    _stone_texture_cache = {}
    _pavement_texture_cache = {}
    
    def __init__(self, pos_x=0, pos_y=0):
        self.track_width = 4.0
        self.arm_length = 30.0  # Extended to reach the edges
        self.center_size = 6.0  # Size of center intersection
        # Position of track in world coordinates
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        # Pavement properties
        self.pavement_width = 2.0  # Width of sidewalks
        self.pavement_height = 0.15  # Height above road surface (increased from 0.05)
        
        # Create buildings
        self.buildings = []
        self.create_buildings()
        
        # Create street lights
        self.street_lights = []
        self.create_street_lights()
        
        # Create traffic lights at intersections
        self.traffic_lights = []
        self.create_traffic_lights()
        
        # Create street signs
        self.signs = []
        self.create_street_signs()
    
    def create_buildings(self):
        """Create buildings with varied positions and sizes, ensuring no overlap"""
        # Set random seed based on track position for consistent building placement
        random.seed(int(self.pos_x * 100 + self.pos_y * 100))
        
        # Northeast quadrant - Multiple buildings
        self._place_buildings_in_quadrant(8, 25, 8, 25, 3)
        
        # Northwest quadrant - Multiple buildings  
        self._place_buildings_in_quadrant(-25, -8, 8, 25, 3)
        
        # Southeast quadrant - Multiple buildings
        self._place_buildings_in_quadrant(8, 25, -25, -8, 3)
        
        # Southwest quadrant - Multiple buildings
        self._place_buildings_in_quadrant(-25, -8, -25, -8, 3)
    
    def _place_buildings_in_quadrant(self, min_x, max_x, min_z, max_z, count):
        """Place buildings in a quadrant without overlap"""
        attempts_per_building = 50  # Maximum attempts to place each building
        min_spacing = 1.5  # Minimum distance between building edges
        
        for i in range(count):
            placed = False
            
            for attempt in range(attempts_per_building):
                # Generate random building properties
                width = random.uniform(2, 6)
                height = random.uniform(4, 12)
                depth = random.uniform(2, 6)
                
                # Generate random position within quadrant bounds
                # Account for building size to keep it fully within bounds
                x = random.uniform(min_x + width/2, max_x - width/2) + self.pos_x
                z = random.uniform(min_z + depth/2, max_z - depth/2) + self.pos_y
                
                # Check if this position would overlap with existing buildings
                if self._is_position_valid(x, z, width, depth, min_spacing):
                    building = Building(x, 0, z, width, height, depth)
                    self.buildings.append(building)
                    placed = True
                    break
            
            # If we couldn't place the building after all attempts, skip it
            if not placed:
                print(f"Warning: Could not place building {i+1} in quadrant ({min_x},{max_x},{min_z},{max_z}) after {attempts_per_building} attempts")
    
    def _is_position_valid(self, x, z, width, depth, min_spacing):
        """Check if a building position would overlap with existing buildings"""
        # Calculate the bounds of the proposed building
        new_left = x - width/2
        new_right = x + width/2
        new_front = z - depth/2
        new_back = z + depth/2
        
        # Check against all existing buildings
        for existing_building in self.buildings:
            # Calculate bounds of existing building
            existing_left = existing_building.x - existing_building.width/2
            existing_right = existing_building.x + existing_building.width/2
            existing_front = existing_building.z - existing_building.depth/2
            existing_back = existing_building.z + existing_building.depth/2
            
            # Add minimum spacing buffer to existing building bounds
            existing_left -= min_spacing
            existing_right += min_spacing
            existing_front -= min_spacing
            existing_back += min_spacing
            
            # Check for overlap (if any of these conditions are false, buildings don't overlap)
            if not (new_right < existing_left or   # New building is completely to the left
                   new_left > existing_right or    # New building is completely to the right
                   new_back < existing_front or    # New building is completely in front
                   new_front > existing_back):     # New building is completely behind
                return False  # Overlap detected
        
        return True  # No overlap

    def create_street_lights(self):
        """Create street lights along the roads"""
        light_id = 1  # Start from 1 since 0 is used for ambient lighting
        
        # Street lights along horizontal arms of the track - increased spacing
        for i in range(-3, 4):  # Fewer lights with wider spacing (7 instead of 9)
            if light_id > 7:  # OpenGL limit
                break
            x_pos = i * 10 + self.pos_x  # Increased spacing back to 10 units
            
            # Skip lights that would be in the intersection area
            if abs(x_pos - self.pos_x) < self.track_width:  # Skip if within track width of center
                continue
            
            # Left side of horizontal arm - on pavement
            z_pos = -self.track_width/2 - self.pavement_width/2 + self.pos_y
            light = StreetLight(x_pos, 0, z_pos, light_id)
            self.street_lights.append(light)
            light_id += 1
            
            if light_id <= 7:
                # Right side of horizontal arm - on pavement
                z_pos = self.track_width/2 + self.pavement_width/2 + self.pos_y
                light = StreetLight(x_pos, 0, z_pos, light_id)
                self.street_lights.append(light)
                light_id += 1
        
        # Street lights along vertical arms of the track - increased spacing
        for i in range(-3, 4):  # Fewer lights with wider spacing
            if light_id > 7:  # OpenGL limit
                break
            z_pos = i * 10 + self.pos_y  # Increased spacing back to 10 units
            
            # Skip lights that would be in the intersection area
            if abs(z_pos - self.pos_y) < self.track_width:  # Skip if within track width of center
                continue
                
            # Left side of vertical arm - on pavement
            x_pos = -self.track_width/2 - self.pavement_width/2 + self.pos_x
            if light_id <= 7:
                light = StreetLight(x_pos, 0, z_pos, light_id)
                self.street_lights.append(light)
                light_id += 1
            
            # Right side of vertical arm - on pavement
            x_pos = self.track_width/2 + self.pavement_width/2 + self.pos_x
            if light_id <= 7:
                light = StreetLight(x_pos, 0, z_pos, light_id)
                self.street_lights.append(light)
                light_id += 1

    def create_traffic_lights(self):
        """Create traffic lights at the intersection"""
        # Only create traffic lights for the center track (pos_x=0, pos_y=0)
        if self.pos_x == 0 and self.pos_y == 0:
            # For horizontal traffic (east-west movement)
            # Right side when traveling east (north side of road) - positioned on pavement
            traffic_light = TrafficLight(3.0, 0, self.track_width/2 + self.pavement_width/3, "horizontal", 6, 0)
            traffic_light.state = "red"  # Start with red light
            self.traffic_lights.append(traffic_light)
            
            # Right side when traveling west (south side of road) - positioned on pavement
            traffic_light2 = TrafficLight(-3.0, 0, -self.track_width/2 - self.pavement_width/3, "horizontal", 7, 180)
            traffic_light2.state = "red"  # Start with red light
            self.traffic_lights.append(traffic_light2)
            
            # For vertical traffic (north-south movement)
            # Right side when traveling south (east side of road) - positioned on pavement
            traffic_light3 = TrafficLight(self.track_width/2 + self.pavement_width/3, 0, -3.0, "vertical", 6, 90)
            traffic_light3.state = "green"  # Start with green light
            self.traffic_lights.append(traffic_light3)
               
            # Right side when traveling north (west side of road) - positioned on pavement
            traffic_light4 = TrafficLight(-self.track_width/2 - self.pavement_width/3, 0, 3.0, "vertical", 7, 270)
            traffic_light4.state = "green"  # Start with green light
            self.traffic_lights.append(traffic_light4)
            
    def create_street_signs(self):
        """Create only traffic light ahead signs at intersections"""
        # Only create traffic light ahead signs for intersection warnings
        # All other street signs along roads have been removed per user request
        
        # Add intersection signs for center track only
        if self.pos_x == 0 and self.pos_y == 0:
            # Add traffic light ahead signs at the exact same positions as the traffic lights
            # Traffic light positions from the lighting setup:
            # traffic_light = TrafficLight(3.0, 0, self.track_width/2 + 0.8, "horizontal", 6, 0)
            # traffic_light2 = TrafficLight(-3.0, 0, -self.track_width/2 - 0.8, "horizontal", 7, 180)
            # traffic_light3 = TrafficLight(self.track_width/2 + 0.3, 0, -3.0, "vertical", 6, 90)
            # traffic_light4 = TrafficLight(-self.track_width/2 - 0.3, 0, 3.0, "vertical", 7, 270)
            
            # Traffic light ahead sign at position of first horizontal traffic light
            sign_east = Sign(3.0, self.track_width/2 + 20.0, 'traffic_light_ahead', rotation=0)
            self.signs.append(sign_east)
            
            # Traffic light ahead sign at position of second horizontal traffic light
            sign_west = Sign(-3.0, -self.track_width/2 - 20.0, 'traffic_light_ahead', rotation=180)
            self.signs.append(sign_west)
            
            # Traffic light ahead sign at position of first vertical traffic light
            sign_south = Sign(self.track_width/2 + 20.0, -3.0, 'traffic_light_ahead', rotation=90)
            self.signs.append(sign_south)
            
            # Traffic light ahead sign at position of second vertical traffic light
            sign_north = Sign(-self.track_width/2 - 20.0, 3.0, 'traffic_light_ahead', rotation=270)
            self.signs.append(sign_north)
            

    def update_traffic_lights(self, dt):
        """Update all traffic lights with coordinated timing"""
        if not self.traffic_lights:
            return
            
        # Use the first horizontal light as the master timer
        master_light = None
        for light in self.traffic_lights:
            if light.direction == "horizontal":
                master_light = light
                break
        
        if master_light is None:
            return
            
        # Update master timer
        master_light.state_timer += dt
        
        # Determine master state based on timer
        if master_light.state == "green":
            if master_light.state_timer >= master_light.green_duration:
                master_light.state = "yellow"
                master_light.state_timer = 0.0
        elif master_light.state == "yellow":
            if master_light.state_timer >= master_light.yellow_duration:
                master_light.state = "red"
                master_light.state_timer = 0.0
        elif master_light.state == "red":
            if master_light.state_timer >= master_light.red_duration:
                master_light.state = "red-yellow"
                master_light.state_timer = 0.0
        elif master_light.state == "red-yellow":
            if master_light.state_timer >= master_light.yellow_duration:
                master_light.state = "green"
                master_light.state_timer = 0.0
        
        # Synchronize all traffic lights based on master
        for light in self.traffic_lights:
            light.state_timer = master_light.state_timer
            
            if light.direction == "horizontal":
                # Horizontal lights follow master
                light.state = master_light.state
            else:
                # Vertical lights are opposite to horizontal
                if master_light.state == "green":
                    light.state = "red"
                elif master_light.state == "yellow":
                    light.state = "red-yellow"
                elif master_light.state == "red":
                    light.state = "green"
                elif master_light.state == "red-yellow":
                    light.state = "yellow"

    @staticmethod
    def _create_grass_texture():
        """Create a procedural grass texture"""
        if 'grass' in Track._grass_texture_cache:
            return Track._grass_texture_cache['grass']
        
        width, height = 256, 256
        surface = pygame.Surface((width, height))
        
        # Base grass green colors
        base_green = (34, 139, 34)  # Dark green
        light_green = (50, 180, 50)  # Light green
        dark_green = (20, 100, 20)  # Very dark green
        
        # Fill with base color
        surface.fill(base_green)
        
        # Add grass blade patterns
        random.seed(42)  # Consistent pattern
        for _ in range(800):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # Draw small grass tufts
            color = random.choice([light_green, base_green, dark_green])
            pygame.draw.line(surface, color, (x, y), (x + random.randint(-2, 2), y - random.randint(2, 5)), 1)
        
        # Add some variation with noise patches
        for _ in range(300):
            x = random.randint(0, width - 16)
            y = random.randint(0, height - 16)
            size = random.randint(3, 8)
            color = random.choice([light_green, dark_green])
            pygame.draw.circle(surface, color, (x, y), size)
        
        # Convert surface to OpenGL texture
        texture_data = pygame.image.tostring(surface, "RGB", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        Track._grass_texture_cache['grass'] = texture_id
        return texture_id

    @staticmethod
    def _create_stone_texture():
        """Create a dark stone texture for the track surface with subtle details"""
        if 'stone' in Track._stone_texture_cache:
            return Track._stone_texture_cache['stone']
        
        width, height = 256, 256
        surface = pygame.Surface((width, height))
        
        # Dark stone base colors with less contrast
        dark_stone = (70, 70, 70)  # Base dark gray
        medium_dark = (75, 75, 75)  # Very subtle variation
        lighter_stone = (80, 80, 80)  # Minimal lighter shade
        
        # Fill with base dark stone color
        surface.fill(dark_stone)
        
        # Add subtle stone texture with very small details
        random.seed(42)  # Consistent pattern
        
        # Add tiny pebble-like stones with reduced size
        for _ in range(80):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            size = random.randint(1, 2)  # Much smaller pebbles
            
            # Vary stone color very slightly
            color = random.choice([dark_stone, medium_dark, lighter_stone])
            pygame.draw.circle(surface, color, (x, y), size)
        
        # Add very fine cracks with minimal visibility
        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            # Draw thin lines for crack effect
            length = random.randint(2, 6)  # Much shorter cracks
            angle = random.randint(0, 360)
            
            # Calculate end point
            import math
            end_x = x + int(length * math.cos(math.radians(angle)))
            end_y = y + int(length * math.sin(math.radians(angle)))
            
            # Draw very subtle crack lines with minimal color difference
            crack_color = (68, 68, 68)  # Barely darker
            pygame.draw.line(surface, crack_color, (x, y), (end_x, end_y), 1)
        
        # Add few subtle light spots for very minimal effect
        for _ in range(40):
            x = random.randint(0, width - 16)
            y = random.randint(0, height - 16)
            size = 1  # Very small spots
            spot_color = (72, 72, 72)  # Barely lighter spots
            pygame.draw.circle(surface, spot_color, (x, y), size)
        
        # Convert surface to OpenGL texture
        texture_data = pygame.image.tostring(surface, "RGB", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        Track._stone_texture_cache['stone'] = texture_id
        return texture_id

    @staticmethod
    def _create_pavement_texture():
        """Create a concrete pavement texture for sidewalks"""
        if 'pavement' in Track._pavement_texture_cache:
            return Track._pavement_texture_cache['pavement']
        
        width, height = 256, 256
        surface = pygame.Surface((width, height))
        
        # Light gray concrete colors
        base_concrete = (150, 150, 150)  # Light gray
        lighter_concrete = (160, 160, 160)  # Slightly lighter
        darker_concrete = (140, 140, 140)  # Slightly darker
        
        # Fill with base concrete color
        surface.fill(base_concrete)
        
        # Add concrete texture with subtle patterns
        random.seed(123)  # Different seed from other textures
        
        # Add small aggregate spots
        for _ in range(200):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            size = random.randint(1, 3)
            
            # Vary concrete color slightly
            color = random.choice([base_concrete, lighter_concrete, darker_concrete])
            pygame.draw.circle(surface, color, (x, y), size)
        
        # Add subtle expansion joints (lines across pavement)
        joint_color = (135, 135, 135)  # Darker for joints
        for i in range(4):  # 4 joints across the texture
            y_pos = (i + 1) * (height // 5)
            pygame.draw.line(surface, joint_color, (0, y_pos), (width, y_pos), 2)
        
        # Add some weathering spots
        for _ in range(50):
            x = random.randint(0, width - 10)
            y = random.randint(0, height - 10)
            size = random.randint(2, 6)
            weather_color = (145, 145, 145)  # Slightly weathered color
            pygame.draw.circle(surface, weather_color, (x, y), size)
        
        # Convert surface to OpenGL texture
        texture_data = pygame.image.tostring(surface, "RGB", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        Track._pavement_texture_cache['pavement'] = texture_id
        return texture_id

    def draw_road_markings(self):
        """Draw road markings including center lines and edge lines"""
        glColor3f(1.0, 1.0, 1.0)  # White color for road markings
        glLineWidth(3.0)  # Make lines more visible
        
        # Center line markings for horizontal road
        glBegin(GL_LINES)
        # Dashed center line - horizontal road
        dash_length = 1.0
        gap_length = 0.5
        current_x = -self.arm_length + self.pos_x
        while current_x < self.arm_length + self.pos_x:
            # Draw dash
            glVertex3f(current_x, 0.02, self.pos_y)
            glVertex3f(min(current_x + dash_length, self.arm_length + self.pos_x), 0.02, self.pos_y)
            current_x += dash_length + gap_length
        
        # Dashed center line - vertical road
        current_z = -self.arm_length + self.pos_y
        while current_z < self.arm_length + self.pos_y:
            # Draw dash
            glVertex3f(self.pos_x, 0.02, current_z)
            glVertex3f(self.pos_x, 0.02, min(current_z + dash_length, self.arm_length + self.pos_y))
            current_z += dash_length + gap_length
        glEnd()
        
        # Edge lines for roads
        glBegin(GL_LINES)
        # Horizontal road edge lines
        # Left edge
        glVertex3f(-self.arm_length + self.pos_x, 0.02, -self.track_width/2 + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, 0.02, -self.track_width/2 + self.pos_y)
        # Right edge
        glVertex3f(-self.arm_length + self.pos_x, 0.02, self.track_width/2 + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, 0.02, self.track_width/2 + self.pos_y)
        
        # Vertical road edge lines
        # Left edge (when facing north)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.02, -self.arm_length + self.pos_y)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.02, self.arm_length + self.pos_y)
        # Right edge (when facing north)
        glVertex3f(self.track_width/2 + self.pos_x, 0.02, -self.arm_length + self.pos_y)
        glVertex3f(self.track_width/2 + self.pos_x, 0.02, self.arm_length + self.pos_y)
        glEnd()
        
        # Cross marking in the center of the intersection
        cross_size = 1.5  # Size of the cross arms
        glBegin(GL_LINES)
        # Horizontal line of the cross
        glVertex3f(-cross_size + self.pos_x, 0.02, self.pos_y)
        glVertex3f(cross_size + self.pos_x, 0.02, self.pos_y)
        
        # Vertical line of the cross
        glVertex3f(self.pos_x, 0.02, -cross_size + self.pos_y)
        glVertex3f(self.pos_x, 0.02, cross_size + self.pos_y)
        glEnd()
        
        glLineWidth(1.0)  # Reset line width

    def draw_pavements(self):
        """Draw concrete pavements (sidewalks) alongside the roads with curb cuts at intersections"""
        pavement_texture = self._create_pavement_texture()
        glColor3f(1.0, 1.0, 1.0)  # White to show full texture color
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, pavement_texture)
        
        road_height = 0.01  # Road surface height
        pavement_surface_height = road_height + self.pavement_height
        
        # Calculate pavement positions
        # For horizontal road (left-right), pavements are above and below the road
        pavement_outer_north = self.track_width/2 + self.pavement_width  # North side outer edge
        pavement_inner_north = self.track_width/2  # North side inner edge (road edge)
        pavement_inner_south = -self.track_width/2  # South side inner edge (road edge)
        pavement_outer_south = -self.track_width/2 - self.pavement_width  # South side outer edge
        
        # For vertical road (up-down), pavements are left and right of the road
        pavement_outer_east = self.track_width/2 + self.pavement_width  # East side outer edge
        pavement_inner_east = self.track_width/2  # East side inner edge (road edge)
        pavement_inner_west = -self.track_width/2  # West side inner edge (road edge)
        pavement_outer_west = -self.track_width/2 - self.pavement_width  # West side outer edge
        
        # Define crosswalk interruption zones - horizontal and vertical roads have different gaps to avoid overlapping
        horizontal_gap = 2.0  # Shorter gap for horizontal road (north-south sidewalks)
        vertical_gap = 4.0    # Longer gap for vertical road (east-west sidewalks)
        
        # Horizontal road pavements (north and south sides) - with shorter gap at vertical crossings
        # North side pavement - west section (left of vertical road)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glTexCoord2f(7.5, 0.0)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glTexCoord2f(7.5, 2.0)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glTexCoord2f(0.0, 2.0)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glEnd()
        
        # North side pavement - east section (right of vertical road)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glTexCoord2f(7.5, 0.0)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glTexCoord2f(7.5, 2.0)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glTexCoord2f(0.0, 2.0)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glEnd()
        
        # South side pavement - west section (left of vertical road)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(7.5, 0.0)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(7.5, 2.0)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glTexCoord2f(0.0, 2.0)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glEnd()
        
        # South side pavement - east section (right of vertical road)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(7.5, 0.0)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(7.5, 2.0)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glTexCoord2f(0.0, 2.0)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glEnd()
        
        # Vertical road pavements (east and west sides) - with longer gap at horizontal crossings
        # East side pavement - north section (above horizontal road intersection)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glTexCoord2f(2.0, 0.0)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glTexCoord2f(2.0, 7.5)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glTexCoord2f(0.0, 7.5)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glEnd()
        
        # East side pavement - south section (below horizontal road intersection)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glTexCoord2f(2.0, 0.0)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glTexCoord2f(2.0, 7.5)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glTexCoord2f(0.0, 7.5)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glEnd()
        
        # West side pavement - north section (above horizontal road intersection)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glTexCoord2f(2.0, 0.0)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glTexCoord2f(2.0, 7.5)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glTexCoord2f(0.0, 7.5)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glEnd()
        
        # West side pavement - south section (below horizontal road intersection)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glTexCoord2f(2.0, 0.0)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glTexCoord2f(2.0, 7.5)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glTexCoord2f(0.0, 7.5)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Draw curb sides (vertical faces of the pavement)
        self.draw_curb_sides(pavement_surface_height, pavement_inner_north, pavement_outer_north, 
                            pavement_inner_south, pavement_outer_south, pavement_inner_east, 
                            pavement_outer_east, pavement_inner_west, pavement_outer_west,
                            horizontal_gap, vertical_gap)
    
    def draw_curb_sides(self, pavement_surface_height, pavement_inner_north, pavement_outer_north,
                        pavement_inner_south, pavement_outer_south, pavement_inner_east,
                        pavement_outer_east, pavement_inner_west, pavement_outer_west,
                        horizontal_gap, vertical_gap):
        """Draw the vertical curb sides of the pavements"""
        road_height = 0.01  # Road surface height
        glColor3f(0.9, 0.9, 0.9)  # Light gray color for curb sides
        
        # Horizontal road curb sides - inner edges (next to the road)
        # North side inner curb - west section
        glBegin(GL_QUADS)
        glVertex3f(-self.arm_length + self.pos_x, road_height, pavement_inner_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_inner_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glEnd()
        
        # North side inner curb - east section
        glBegin(GL_QUADS)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_inner_north + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, road_height, pavement_inner_north + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glEnd()
        
        # South side inner curb - west section
        glBegin(GL_QUADS)
        glVertex3f(-self.arm_length + self.pos_x, road_height, pavement_inner_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_inner_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glEnd()
        
        # South side inner curb - east section
        glBegin(GL_QUADS)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_inner_south + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, road_height, pavement_inner_south + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glEnd()
        
        # Horizontal road curb sides - outer edges (away from the road)
        # North side outer curb - west section
        glBegin(GL_QUADS)
        glVertex3f(-self.arm_length + self.pos_x, road_height, pavement_outer_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_outer_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glEnd()
        
        # North side outer curb - east section
        glBegin(GL_QUADS)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_outer_north + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, road_height, pavement_outer_north + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glEnd()
        
        # South side outer curb - west section
        glBegin(GL_QUADS)
        glVertex3f(-self.arm_length + self.pos_x, road_height, pavement_outer_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_outer_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glVertex3f(-self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glEnd()
        
        # South side outer curb - east section
        glBegin(GL_QUADS)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_outer_south + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, road_height, pavement_outer_south + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glEnd()
        
        # Vertical road curb sides - inner edges (next to the road)
        # East side inner curb - north section
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_east + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, road_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glEnd()
        
        # East side inner curb - south section
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_east + self.pos_x, road_height, -self.arm_length + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glEnd()
        
        # West side inner curb - north section
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_west + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, road_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glEnd()
        
        # West side inner curb - south section
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_west + self.pos_x, road_height, -self.arm_length + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glEnd()
        
        # Vertical road curb sides - outer edges (away from the road)
        # East side outer curb - north section
        glBegin(GL_QUADS)
        glVertex3f(pavement_outer_east + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, road_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glEnd()
        
        # East side outer curb - south section
        glBegin(GL_QUADS)
        glVertex3f(pavement_outer_east + self.pos_x, road_height, -self.arm_length + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glEnd()
        
        # West side outer curb - north section
        glBegin(GL_QUADS)
        glVertex3f(pavement_outer_west + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, road_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, self.arm_length + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glEnd()
        
        # West side outer curb - south section
        glBegin(GL_QUADS)
        glVertex3f(pavement_outer_west + self.pos_x, road_height, -self.arm_length + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, -self.arm_length + self.pos_y)
        glEnd()
        
        # End faces for horizontal road pavements (at left and right gaps)
        # North side end faces - west gap
        glBegin(GL_QUADS)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_inner_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_outer_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glEnd()
        
        # North side end faces - east gap
        glBegin(GL_QUADS)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_inner_north + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_outer_north + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_north + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_north + self.pos_y)
        glEnd()
        
        # South side end faces - west gap
        glBegin(GL_QUADS)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_inner_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, road_height, pavement_outer_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glVertex3f(-horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glEnd()
        
        # South side end faces - east gap
        glBegin(GL_QUADS)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_inner_south + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, road_height, pavement_outer_south + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_outer_south + self.pos_y)
        glVertex3f(horizontal_gap + self.pos_x, pavement_surface_height, pavement_inner_south + self.pos_y)
        glEnd()
        
        # End faces for vertical road pavements (at top and bottom gaps)
        # East side end faces - north gap
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_east + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glEnd()
        
        # East side end faces - south gap
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_east + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_east + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_east + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glEnd()
        
        # West side end faces - north gap
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_west + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, road_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, vertical_gap + self.pos_y)
        glEnd()
        
        # West side end faces - south gap
        glBegin(GL_QUADS)
        glVertex3f(pavement_inner_west + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, road_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_outer_west + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glVertex3f(pavement_inner_west + self.pos_x, pavement_surface_height, -vertical_gap + self.pos_y)
        glEnd()
        
    def draw(self, is_day=False, camera_x=0, camera_z=0):
        """Draw the complete track with roads, buildings, and lighting"""
        # Draw ground with grass texture at sidewalk height - split into 4 quadrants
        grass_texture = self._create_grass_texture()
        glColor3f(1.0, 1.0, 1.0)  # White to show full texture color
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, grass_texture)
        
        grass_height = 0.01 + self.pavement_height  # Same height as sidewalk
        
        # Calculate the inner boundary (where sidewalks end)
        pavement_outer_north = self.track_width/2 + self.pavement_width  # 4.0
        pavement_outer_south = -self.track_width/2 - self.pavement_width  # -4.0
        pavement_outer_east = self.track_width/2 + self.pavement_width  # 4.0
        pavement_outer_west = -self.track_width/2 - self.pavement_width  # -4.0
        
        # Track extends from -arm_length to arm_length
        arm_length = self.arm_length  # 30.0
        
        # Draw 4 grass sections - one for each quadrant
        # Northeast quadrant grass
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(pavement_outer_east + self.pos_x, grass_height, pavement_outer_north + self.pos_y)
        glTexCoord2f(3.0, 0.0)
        glVertex3f(arm_length + self.pos_x, grass_height, pavement_outer_north + self.pos_y)
        glTexCoord2f(3.0, 3.0)
        glVertex3f(arm_length + self.pos_x, grass_height, arm_length + self.pos_y)
        glTexCoord2f(0.0, 3.0)
        glVertex3f(pavement_outer_east + self.pos_x, grass_height, arm_length + self.pos_y)
        glEnd()
        
        # Northwest quadrant grass
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-arm_length + self.pos_x, grass_height, pavement_outer_north + self.pos_y)
        glTexCoord2f(3.0, 0.0)
        glVertex3f(pavement_outer_west + self.pos_x, grass_height, pavement_outer_north + self.pos_y)
        glTexCoord2f(3.0, 3.0)
        glVertex3f(pavement_outer_west + self.pos_x, grass_height, arm_length + self.pos_y)
        glTexCoord2f(0.0, 3.0)
        glVertex3f(-arm_length + self.pos_x, grass_height, arm_length + self.pos_y)
        glEnd()
        
        # Southeast quadrant grass
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(pavement_outer_east + self.pos_x, grass_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(3.0, 0.0)
        glVertex3f(arm_length + self.pos_x, grass_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(3.0, 3.0)
        glVertex3f(arm_length + self.pos_x, grass_height, -arm_length + self.pos_y)
        glTexCoord2f(0.0, 3.0)
        glVertex3f(pavement_outer_east + self.pos_x, grass_height, -arm_length + self.pos_y)
        glEnd()
        
        # Southwest quadrant grass
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-arm_length + self.pos_x, grass_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(3.0, 0.0)
        glVertex3f(pavement_outer_west + self.pos_x, grass_height, pavement_outer_south + self.pos_y)
        glTexCoord2f(3.0, 3.0)
        glVertex3f(pavement_outer_west + self.pos_x, grass_height, -arm_length + self.pos_y)
        glTexCoord2f(0.0, 3.0)
        glVertex3f(-arm_length + self.pos_x, grass_height, -arm_length + self.pos_y)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Draw cross-shaped track surface with light stone texture
        stone_texture = self._create_stone_texture()
        glColor3f(1.0, 1.0, 1.0)  # White to show full stone texture color
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, stone_texture)
        
        # Horizontal arm (left-right) - extends from edge to edge
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.arm_length + self.pos_x, 0.01, -self.track_width/2 + self.pos_y)
        glTexCoord2f(15.0, 0.0)
        glVertex3f(self.arm_length + self.pos_x, 0.01, -self.track_width/2 + self.pos_y)
        glTexCoord2f(15.0, 1.0)
        glVertex3f(self.arm_length + self.pos_x, 0.01, self.track_width/2 + self.pos_y)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-self.arm_length + self.pos_x, 0.01, self.track_width/2 + self.pos_y)
        glEnd()
        
        # Vertical arm (up-down) - only draw the parts that don't overlap with horizontal
        # Left side of vertical arm
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.01, -self.arm_length + self.pos_y)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.01, -self.track_width/2 + self.pos_y)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(self.track_width/2 + self.pos_x, 0.01, -self.track_width/2 + self.pos_y)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(self.track_width/2 + self.pos_x, 0.01, -self.arm_length + self.pos_y)
        glEnd()
        
        # Right side of vertical arm
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.01, self.track_width/2 + self.pos_y)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.01, self.arm_length + self.pos_y)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(self.track_width/2 + self.pos_x, 0.01, self.arm_length + self.pos_y)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(self.track_width/2 + self.pos_x, 0.01, self.track_width/2 + self.pos_y)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Draw pavements (sidewalks)
        self.draw_pavements()
        
        # Draw road markings (center lines and edge lines)
        self.draw_road_markings()
        
        # Draw all buildings that belong to this track (with distance culling for performance)
        # Dynamically adjust render distance based on viewport size for performance
        max_render_distance = 60.0  # Reduced from 100.0 for better performance
        for building in self.buildings:
            # Calculate distance from camera to building
            distance = ((building.x - camera_x) ** 2 + (building.z - camera_z) ** 2) ** 0.5
            if distance <= max_render_distance:
                building.draw(is_day)  # Pass is_day parameter to buildings
            
        # Setup and draw all street lights that belong to this track (with distance culling)
        for light in self.street_lights:
            # Calculate distance from camera to light
            distance = ((light.x - camera_x) ** 2 + (light.z - camera_z) ** 2) ** 0.5
            if distance <= max_render_distance:
                light.setup_light()  # Configure the OpenGL light
                light.draw(is_day)  # Draw the physical street light (glow only at night)
            
        # Setup and draw all traffic lights that belong to this track (with distance culling)
        for light in self.traffic_lights:
            # Calculate distance from camera to light
            distance = ((light.x - camera_x) ** 2 + (light.z - camera_z) ** 2) ** 0.5
            if distance <= max_render_distance:
                light.setup_light()  # Configure the OpenGL light
                light.draw()  # Draw the physical traffic light
        
        # Draw all street signs that belong to this track (with distance culling)
        for sign in self.signs:
            # Calculate distance from camera to sign
            distance = ((sign.x - camera_x) ** 2 + (sign.z - camera_z) ** 2) ** 0.5
            if distance <= max_render_distance:
                sign.draw()  # Draw the street sign