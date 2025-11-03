"""
Lighting module for 3D Car Racing Game
Contains StreetLight and TrafficLight classes for realistic night scene lighting.
"""
import math
from OpenGL.GL import *


class StreetLight:
    """Street light class with OpenGL lighting and visual effects"""
    
    def __init__(self, x, y, z, light_id):
        self.x = x
        self.y = y
        self.z = z
        self.light_id = light_id  # OpenGL light ID (GL_LIGHT1, GL_LIGHT2, etc.)
        self.pole_height = 2.0  # Reduced from 4.0 to 2.0
        self.light_radius = 5.0  # Reduced from 8.0 to 5.0 to prevent overlap
        
    def setup_light(self):
        """Configure the OpenGL light for this street light"""
        if self.light_id <= 7:  # OpenGL supports up to 8 lights (0-7)
            light_enum = GL_LIGHT0 + self.light_id
            glEnable(light_enum)
            
            # Position the light at the top of the pole
            light_position = [self.x, self.y + self.pole_height, self.z, 1.0]  # Point light
            glLightfv(light_enum, GL_POSITION, light_position)
            
            # Set light properties - brighter and more focused
            light_diffuse = [1.5, 1.3, 1.0, 1.0]  # Brighter warm white light
            light_specular = [1.0, 0.9, 0.7, 1.0]  # Bright specular
            light_ambient = [0.2, 0.2, 0.2, 1.0]   # More ambient light
            
            glLightfv(light_enum, GL_DIFFUSE, light_diffuse)
            glLightfv(light_enum, GL_SPECULAR, light_specular)
            glLightfv(light_enum, GL_AMBIENT, light_ambient)
            
            # Adjust attenuation for better road coverage
            glLightf(light_enum, GL_CONSTANT_ATTENUATION, 0.5)  # Reduced from 1.0
            glLightf(light_enum, GL_LINEAR_ATTENUATION, 0.05)   # Reduced from 0.1
            glLightf(light_enum, GL_QUADRATIC_ATTENUATION, 0.01) # Reduced from 0.02
    
    def draw(self, is_day=False):
        """Draw the street light pole and lamp"""
        # Draw pole
        glColor3f(0.3, 0.3, 0.3)  # Dark gray pole
        glPushMatrix()
        glTranslatef(self.x, self.y + self.pole_height/2, self.z)
        glScalef(0.1, self.pole_height, 0.1)  # Thin tall pole
        self.draw_pole()
        glPopMatrix()
        
        # Draw light fixture
        glColor3f(1.0, 0.9, 0.7)  # Warm light color
        glPushMatrix()
        glTranslatef(self.x, self.y + self.pole_height - 0.2, self.z)
        glScalef(0.3, 0.2, 0.3)  # Light fixture size
        self.draw_light_fixture()
        glPopMatrix()
        
        # Draw light glow effect (only at night)
        self.draw_light_glow(is_day)
    
    def draw_pole(self):
        """Draw a simple rectangular pole"""
        glBegin(GL_QUADS)
        # All faces of the pole
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glEnd()
    
    def draw_light_fixture(self):
        """Draw the light fixture on top of pole"""
        glBegin(GL_QUADS)
        # Simple box for light fixture
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glEnd()
    
    def draw_light_glow(self, is_day=False):
        """Draw a realistic glow effect with proper spatial distribution in 4 directions"""
        # Skip glow during day time
        if is_day:
            return
            
        # Enable blending for glow effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)  # Disable lighting for glow effect
        
        # Draw glow layers at different distances from the light source
        # Only 2 glow circles: small bright core and large dim outer (reduced sizes)
        glow_layers = [
            (0.8, 0.15, 0.15),   # Medium, dim, outer glow (reduced from 1.5)
            (0.3, 0.35, 0.05)    # Small, bright, inner core (reduced from 0.6)
        ]
        
        # Draw glow in 4 directions: North, South, East, West
        rotations = [0, 90, 180, 270]  # Rotation angles for 4 directions
        
        for rotation in rotations:
            for size, alpha, z_offset in glow_layers:
                glPushMatrix()
                glTranslatef(self.x, self.y + self.pole_height - 0.2, self.z)
                glRotatef(rotation, 0, 1, 0)  # Rotate around Y-axis
                glTranslatef(0, 0, z_offset)  # Move forward in the rotated direction
                glColor4f(1.0, 0.9, 0.6, alpha)
                # Draw low poly circle
                segments = 6  # Low poly circle with 6 sides
                glBegin(GL_TRIANGLE_FAN)
                glVertex3f(0, 0, 0)  # Center
                for i in range(segments + 1):
                    angle = i * 2.0 * 3.14159 / segments
                    x = size * math.cos(angle)
                    y = size * math.sin(angle)
                    glVertex3f(x, y, 0)
                glEnd()
                glPopMatrix()
        
        glEnable(GL_LIGHTING)  # Re-enable lighting
        glDisable(GL_BLEND)


class TrafficLight:
    """Traffic light class with realistic timing and coordinated behavior"""
    
    def __init__(self, x, y, z, direction, light_id, rotation=0):
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction  # 'horizontal' or 'vertical' - which road this light controls
        self.light_id = light_id
        self.pole_height = 2.0  # Match street light height
        self.rotation = rotation  # Rotation angle in degrees
        
        # Traffic light states
        self.state = "green"  # "green", "yellow", "red"
        self.state_timer = 0.0
        
        # Traffic light timing (in seconds)
        self.green_duration = 5.0
        self.yellow_duration = 2.0
        self.red_duration = 5.0
        
        # Start with offset based on direction
        if direction == "vertical":
            self.state_timer = self.green_duration + self.yellow_duration  # Start at red
            self.state = "red"
        elif direction == "horizontal":
            self.state_timer = 0.0
            self.state = "green"
    
    def update(self, dt):
        """Update traffic light state based on time"""
        self.state_timer += dt
        
        if self.state == "green":
            if self.state_timer >= self.green_duration:
                self.state = "yellow"
                self.state_timer = 0.0

        elif self.state == "yellow":
            if self.state_timer >= self.yellow_duration:
                self.state = "red"
                self.state_timer = 0.0

        elif self.state == "red":
            if self.state_timer >= self.red_duration:
                self.state = "red-yellow"
                self.state_timer = 0.0

        elif self.state == "red-yellow":
            if self.state_timer >= self.yellow_duration:
                self.state = "green"
                self.state_timer = 0.0
    
    def get_light_color(self):
        """Get the current light color as RGB"""
        if self.state == "green":
            return (0.0, 1.0, 0.0)  # Green
        elif self.state == "yellow":
            return (1.0, 1.0, 0.0)  # Yellow
        elif self.state == "red-yellow":
            return (1.0, 0.5, 0.0)  # Red-yellow mix (orange)
        else:  # red
            return (1.0, 0.0, 0.0)  # Red
    
    def setup_light(self):
        """Configure the OpenGL light for this traffic light"""
        if self.light_id <= 7:
            light_enum = GL_LIGHT0 + self.light_id
            glEnable(light_enum)
            
            # Position the light at the top of the pole
            light_position = [self.x, self.y + self.pole_height, self.z, 1.0]
            glLightfv(light_enum, GL_POSITION, light_position)
            
            # Get current color
            r, g, b = self.get_light_color()

            # Set light properties based on current state
            light_diffuse = [r * 0.8, g * 0.8, b * 0.8, 1.0]
            light_specular = [r * 0.5, g * 0.5, b * 0.5, 1.0]
            light_ambient = [r * 0.1, g * 0.1, b * 0.1, 1.0]
            
            glLightfv(light_enum, GL_DIFFUSE, light_diffuse)
            glLightfv(light_enum, GL_SPECULAR, light_specular)
            glLightfv(light_enum, GL_AMBIENT, light_ambient)
            
            # Set attenuation
            glLightf(light_enum, GL_CONSTANT_ATTENUATION, 0.8)
            glLightf(light_enum, GL_LINEAR_ATTENUATION, 0.1)
            glLightf(light_enum, GL_QUADRATIC_ATTENUATION, 0.05)
    
    def draw(self):
        """Draw the traffic light pole and lights"""
        # Apply rotation for the entire traffic light
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)  # Rotate around Y-axis
        glTranslatef(-self.x, -self.y, -self.z)
        
        # Draw pole
        glColor3f(0.2, 0.2, 0.2)  # Dark gray pole
        glPushMatrix()
        glTranslatef(self.x, self.y + self.pole_height/2, self.z)
        glScalef(0.15, self.pole_height, 0.15)  # Slightly thicker pole
        self.draw_pole()
        glPopMatrix()
        
        # Draw traffic light housing
        glColor3f(0.1, 0.1, 0.1)  # Black housing
        glPushMatrix()
        glTranslatef(self.x, self.y + self.pole_height - 0.3, self.z)
        glScalef(0.4, 0.8, 0.2)  # Traffic light box
        self.draw_box()
        glPopMatrix()
        
        # Draw individual lights
        self.draw_traffic_lights()
        
        # Draw light glow effect
        self.draw_light_glow()
        
        # Reset color to white for other objects
        glColor3f(1.0, 1.0, 1.0)
        
        # Restore matrix
        glPopMatrix()
    
    def draw_pole(self):
        """Draw the traffic light pole"""
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glEnd()
    
    def draw_box(self):
        """Draw the traffic light housing box"""
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Back face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # Left face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        # Right face
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        # Top face
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glEnd()
    
    def draw_traffic_lights(self):
        """Draw the three colored circles (red, yellow, green)"""
        glDisable(GL_LIGHTING)  # Disable lighting for bright light colors
        
        base_y = self.y + self.pole_height - 0.3
        
        # Red light (top)
        if self.state == "red" or self.state == "red-yellow":
            glColor3f(1.0, 0.0, 0.0)  # Bright red
        else:
            glColor3f(0.3, 0.0, 0.0)  # Dim red
        glPushMatrix()
        glTranslatef(self.x, base_y + 0.2, self.z + 0.11)
        self.draw_light_circle()
        glPopMatrix()
        
        # Yellow light (middle)
        if self.state == "yellow" or self.state == "red-yellow":
            glColor3f(1.0, 1.0, 0.0)  # Bright yellow
        else:
            glColor3f(0.3, 0.3, 0.0)  # Dim yellow
        glPushMatrix()
        glTranslatef(self.x, base_y, self.z + 0.11)
        self.draw_light_circle()
        glPopMatrix()
        
        # Green light (bottom)
        if self.state == "green":
            glColor3f(0.0, 1.0, 0.0)  # Bright green
        else:
            glColor3f(0.0, 0.3, 0.0)  # Dim green
        glPushMatrix()
        glTranslatef(self.x, base_y - 0.2, self.z + 0.11)
        self.draw_light_circle()
        glPopMatrix()
        
        # Reset color to prevent affecting other objects
        glColor3f(1.0, 1.0, 1.0)  # White
        glEnable(GL_LIGHTING)  # Re-enable lighting
    
    def draw_light_circle(self):
        """Draw a simple circle for traffic light"""
        segments = 8
        radius = 0.08
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)  # Center
        for i in range(segments + 1):
            angle = i * 2.0 * 3.14159 / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
    
    def draw_light_glow(self):
        """Draw glow effect for active light"""
        if self.state == "red" or self.state == "yellow" or self.state == "green" or self.state == "red-yellow":
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_LIGHTING)
            
            # Position glow at current active light
            base_y = self.y + self.pole_height - 0.3
            
            if self.state == "red-yellow":
                # Draw glow for both red and yellow lights with very small gaps
                # Red glow layers at different distances (very small z_offset gaps)
                red_layers = [
                    (0.08, 0.5, 0.01),   # Core bright spot, closest
                    (0.15, 0.35, 0.03), # Inner bright glow, close
                    (0.25, 0.2, 0.06),  # Medium glow, medium distance
                    (0.4, 0.1, 0.10)   # Outer dim glow, furthest
                ]
                for size, alpha, z_offset in red_layers:
                    glPushMatrix()
                    glTranslatef(self.x, base_y + 0.2, self.z + 0.12 + z_offset)
                    glColor4f(1.0, 0.0, 0.0, alpha)
                    # Draw low poly circle
                    segments = 6  # Low poly circle with 6 sides
                    glBegin(GL_TRIANGLE_FAN)
                    glVertex3f(0, 0, 0)  # Center
                    for i in range(segments + 1):
                        angle = i * 2.0 * 3.14159 / segments
                        x = size * math.cos(angle)
                        y = size * math.sin(angle)
                        glVertex3f(x, y, 0)
                    glEnd()
                    glPopMatrix()
                
                # Yellow glow layers at different distances (very small z_offset gaps)
                yellow_layers = [
                    (0.08, 0.5, 0.01),   # Core bright spot, closest
                    (0.15, 0.35, 0.03), # Inner bright glow, close
                    (0.25, 0.2, 0.06),  # Medium glow, medium distance
                    (0.4, 0.1, 0.10)   # Outer dim glow, furthest
                ]
                for size, alpha, z_offset in yellow_layers:
                    glPushMatrix()
                    glTranslatef(self.x, base_y, self.z + 0.12 + z_offset)
                    glColor4f(1.0, 1.0, 0.0, alpha)
                    # Draw low poly circle
                    segments = 6  # Low poly circle with 6 sides
                    glBegin(GL_TRIANGLE_FAN)
                    glVertex3f(0, 0, 0)  # Center
                    for i in range(segments + 1):
                        angle = i * 2.0 * 3.14159 / segments
                        x = size * math.cos(angle)
                        y = size * math.sin(angle)
                        glVertex3f(x, y, 0)
                    glEnd()
                    glPopMatrix()
            else:
                # Handle single color states (red, yellow, green)
                r, g, b = self.get_light_color()
                
                if self.state == "red":
                    glow_y = base_y + 0.2
                elif self.state == "yellow":
                    glow_y = base_y
                else:  # green
                    glow_y = base_y - 0.2
                
                # Draw glow with very small gaps between layers
                glow_layers = [
                    (0.08, 0.5, 0.01),   # Core bright spot, closest to source
                    (0.15, 0.35, 0.03), # Inner bright glow, close
                    (0.25, 0.2, 0.06),  # Medium glow, medium distance
                    (0.4, 0.1, 0.10)   # Outer dim glow, furthest away
                ]
                
                for size, alpha, z_offset in glow_layers:
                    glPushMatrix()
                    glTranslatef(self.x, glow_y, self.z + 0.12 + z_offset)
                    glColor4f(r, g, b, alpha)
                    # Draw low poly circle
                    segments = 6  # Low poly circle with 6 sides
                    glBegin(GL_TRIANGLE_FAN)
                    glVertex3f(0, 0, 0)  # Center
                    for i in range(segments + 1):
                        angle = i * 2.0 * 3.14159 / segments
                        x = size * math.cos(angle)
                        y = size * math.sin(angle)
                        glVertex3f(x, y, 0)
                    glEnd()
                    glPopMatrix()
            
            glEnable(GL_LIGHTING)
            glDisable(GL_BLEND)