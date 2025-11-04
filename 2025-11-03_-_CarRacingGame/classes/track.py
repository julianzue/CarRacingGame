"""
Track module for 3D Car Racing Game
Contains the Track class that manages road layout, buildings, and lighting.
"""
import random
from OpenGL.GL import *
from classes.building import Building
from classes.lighting import StreetLight, TrafficLight


class Track:
    """Track class that manages the cross-shaped road with buildings and lighting"""
    
    def __init__(self, pos_x=0, pos_y=0):
        self.track_width = 4.0
        self.arm_length = 30.0  # Extended to reach the edges
        self.center_size = 6.0  # Size of center intersection
        # Position of track in world coordinates
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        # Create buildings
        self.buildings = []
        self.create_buildings()
        
        # Create street lights
        self.street_lights = []
        self.create_street_lights()
        
        # Create traffic lights at intersections
        self.traffic_lights = []
        self.create_traffic_lights()
    
    def create_buildings(self):
        """Create buildings with varied positions and sizes"""
        # Northeast quadrant - Multiple buildings
        for i in range(3):
            x = random.uniform(8, 25) + self.pos_x
            z = random.uniform(8, 25) + self.pos_y
            width = random.uniform(2, 6)
            height = random.uniform(4, 12)
            depth = random.uniform(2, 6)
            building = Building(x, 0, z, width, height, depth)
            self.buildings.append(building)

        # Northwest quadrant - Multiple buildings
        for i in range(3):
            x = random.uniform(-25, -8) + self.pos_x
            z = random.uniform(8, 25) + self.pos_y
            width = random.uniform(2, 6)
            height = random.uniform(4, 12)
            depth = random.uniform(2, 6)
            building = Building(x, 0, z, width, height, depth)
            self.buildings.append(building)

        # Southeast quadrant - Multiple buildings
        for i in range(3):
            x = random.uniform(8, 25) + self.pos_x
            z = random.uniform(-25, -8) + self.pos_y
            width = random.uniform(2, 6)
            height = random.uniform(4, 12)
            depth = random.uniform(2, 6)
            building = Building(x, 0, z, width, height, depth)
            self.buildings.append(building)

        # Southwest quadrant - Multiple buildings
        for i in range(3):
            x = random.uniform(-25, -8) + self.pos_x
            z = random.uniform(-25, -8) + self.pos_y
            width = random.uniform(2, 6)
            height = random.uniform(4, 12)
            depth = random.uniform(2, 6)
            building = Building(x, 0, z, width, height, depth)
            self.buildings.append(building)

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
            
            # Left side of horizontal arm - closer to road
            z_pos = -self.track_width/2 - 0.8 + self.pos_y
            light = StreetLight(x_pos, 0, z_pos, light_id)
            self.street_lights.append(light)
            light_id += 1
            
            if light_id <= 7:
                # Right side of horizontal arm - closer to road
                z_pos = self.track_width/2 + 0.8 + self.pos_y
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
                
            # Left side of vertical arm - closer to road
            x_pos = -self.track_width/2 - 0.8 + self.pos_x
            if light_id <= 7:
                light = StreetLight(x_pos, 0, z_pos, light_id)
                self.street_lights.append(light)
                light_id += 1
            
            # Right side of vertical arm - closer to road
            x_pos = self.track_width/2 + 0.8 + self.pos_x
            if light_id <= 7:
                light = StreetLight(x_pos, 0, z_pos, light_id)
                self.street_lights.append(light)
                light_id += 1

    def create_traffic_lights(self):
        """Create traffic lights at the intersection"""
        # Only create traffic lights for the center track (pos_x=0, pos_y=0)
        if self.pos_x == 0 and self.pos_y == 0:
            # For horizontal traffic (east-west movement)
            # Right side when traveling east (north side of road)
            traffic_light = TrafficLight(3.0, 0, self.track_width/2 + 0.8, "horizontal", 6, 0)
            traffic_light.state = "red"  # Start with red light
            self.traffic_lights.append(traffic_light)
            
            # Right side when traveling west (south side of road)
            traffic_light2 = TrafficLight(-3.0, 0, -self.track_width/2 - 0.8, "horizontal", 7, 180)
            traffic_light2.state = "red"  # Start with red light
            self.traffic_lights.append(traffic_light2)
            
            # For vertical traffic (north-south movement)
            # Right side when traveling south (east side of road)
            traffic_light3 = TrafficLight(self.track_width/2 + 0.3, 0, -3.0, "vertical", 6, 90)
            traffic_light3.state = "green"  # Start with green light
            self.traffic_lights.append(traffic_light3)
               
            # Right side when traveling north (west side of road)
            traffic_light4 = TrafficLight(-self.track_width/2 - 0.3, 0, 3.0, "vertical", 7, 270)
            traffic_light4.state = "green"  # Start with green light
            self.traffic_lights.append(traffic_light4)
            

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
        
    def draw(self, is_day=False):
        """Draw the complete track with roads, buildings, and lighting"""
        # Draw ground first (large plane) - darker for night
        glColor3f(0.15, 0.15, 0.2)  # Dark blue-gray ground for night
        glBegin(GL_QUADS)
        size = 30.0
        glVertex3f(-size + self.pos_x, -0.01, -size + self.pos_y)
        glVertex3f(size + self.pos_x, -0.01, -size + self.pos_y)
        glVertex3f(size + self.pos_x, -0.01, size + self.pos_y)
        glVertex3f(-size + self.pos_x, -0.01, size + self.pos_y)
        glEnd()
        
        # Draw cross-shaped track surface - slightly lighter for visibility
        glColor3f(0.3, 0.3, 0.35)  # Slightly lighter gray track for night
        
        # Horizontal arm (left-right)
        glBegin(GL_QUADS)
        glVertex3f(-self.arm_length + self.pos_x, 0.01, -self.track_width/2 + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, 0.01, -self.track_width/2 + self.pos_y)
        glVertex3f(self.arm_length + self.pos_x, 0.01, self.track_width/2 + self.pos_y)
        glVertex3f(-self.arm_length + self.pos_x, 0.01, self.track_width/2 + self.pos_y)
        glEnd()
        
        # Vertical arm (up-down)
        glBegin(GL_QUADS)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.01, -self.arm_length + self.pos_y)
        glVertex3f(self.track_width/2 + self.pos_x, 0.01, -self.arm_length + self.pos_y)
        glVertex3f(self.track_width/2 + self.pos_x, 0.01, self.arm_length + self.pos_y)
        glVertex3f(-self.track_width/2 + self.pos_x, 0.01, self.arm_length + self.pos_y)
        glEnd()
        
        # Draw road markings (center lines and edge lines)
        self.draw_road_markings()
        
        # Draw all buildings that belong to this track
        for building in self.buildings:
            building.draw()
            
        # Setup and draw all street lights that belong to this track
        for light in self.street_lights:
            light.setup_light()  # Configure the OpenGL light
            light.draw(is_day)  # Draw the physical street light (glow only at night)
            
        # Setup and draw all traffic lights that belong to this track
        for light in self.traffic_lights:
            light.setup_light()  # Configure the OpenGL light
            light.draw()  # Draw the physical traffic light