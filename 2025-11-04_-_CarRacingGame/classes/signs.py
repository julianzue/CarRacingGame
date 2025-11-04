"""
Signs module for 3D Car Racing Game
Contains the Sign class for creating various street signs with different types and messages.
"""
import math
from OpenGL.GL import *


class Sign:
    """Street sign class that can create different types of signs"""
    
    # Predefined sign types with their properties
    SIGN_TYPES = {
        'stop': {
            'shape': 'octagon',
            'color': (0.8, 0.1, 0.1),  # Red
            'text_color': (1.0, 1.0, 1.0),  # White
            'text': 'STOP',
            'size': 1.0
        },
        'yield': {
            'shape': 'triangle',
            'color': (1.0, 0.9, 0.0),  # Yellow
            'text_color': (0.8, 0.1, 0.1),  # Red text
            'text': 'YIELD',
            'size': 0.9
        },
        'speed_limit': {
            'shape': 'rectangle',
            'color': (1.0, 1.0, 1.0),  # White
            'text_color': (0.0, 0.0, 0.0),  # Black
            'text': 'SPEED\nLIMIT\n50',
            'size': 0.8
        },
        'no_parking': {
            'shape': 'circle',
            'color': (1.0, 1.0, 1.0),  # White
            'text_color': (0.8, 0.1, 0.1),  # Red
            'text': 'NO\nPARKING',
            'size': 0.7
        },
        'one_way': {
            'shape': 'rectangle',
            'color': (0.0, 0.0, 0.0),  # Black
            'text_color': (1.0, 1.0, 1.0),  # White
            'text': 'ONE WAY\n→',
            'size': 0.6
        },
        'pedestrian': {
            'shape': 'diamond',
            'color': (1.0, 0.9, 0.0),  # Yellow
            'text_color': (0.0, 0.0, 0.0),  # Black
            'text': 'PED\nXING',
            'size': 0.8
        },
        'school_zone': {
            'shape': 'pentagon',
            'color': (1.0, 0.9, 0.0),  # Yellow
            'text_color': (0.0, 0.0, 0.0),  # Black
            'text': 'SCHOOL\nZONE',
            'size': 0.9
        },
        'construction': {
            'shape': 'diamond',
            'color': (1.0, 0.5, 0.0),  # Orange
            'text_color': (0.0, 0.0, 0.0),  # Black
            'text': 'WORK\nZONE',
            'size': 0.8
        },
        'street_name': {
            'shape': 'rectangle',
            'color': (0.0, 0.5, 0.0),  # Green
            'text_color': (1.0, 1.0, 1.0),  # White
            'text': 'MAIN ST',
            'size': 0.5
        },
        'exit': {
            'shape': 'rectangle',
            'color': (0.0, 0.5, 0.0),  # Green
            'text_color': (1.0, 1.0, 1.0),  # White
            'text': 'EXIT\n1',
            'size': 0.7
        },
        # warning for traffic light ahead, triangle shape, german style, red and white
        'traffic_light_ahead': {
            'shape': 'triangle',
            'color': (1.0, 1.0, 1.0),  # White
            'text_color': (0.0, 0.0, 0.0),  # Black
            'text': '',  # No text, will draw traffic light circles
            'size': 0.9,
            'border_color': (0.8, 0.1, 0.1),  # Red border
            'border_width': 4.0,  # Thick border
            'draw_traffic_lights': True  # Special flag for custom drawing
        }
    }
    
    def __init__(self, x, z, sign_type='stop', custom_text=None, rotation=0.0):
        """
        Initialize a street sign
        
        Args:
            x, z: Position coordinates
            sign_type: Type of sign from SIGN_TYPES or 'custom'
            custom_text: Custom text for the sign (overrides default text)
            rotation: Rotation angle in degrees
        """
        self.x = x
        self.y = 0.0  # Ground level
        self.z = z
        self.rotation = rotation
        
        # Set sign properties based on type
        if sign_type in self.SIGN_TYPES:
            self.sign_data = self.SIGN_TYPES[sign_type].copy()
            self.sign_type = sign_type
        else:
            # Default to stop sign if unknown type
            self.sign_data = self.SIGN_TYPES['stop'].copy()
            self.sign_type = 'stop'
        
        # Override text if custom text provided
        if custom_text:
            self.sign_data['text'] = custom_text
            
        # Sign post properties
        self.post_height = 1.8
        self.post_width = 0.1
        self.sign_height_offset = 1.8  # Height of sign on post
        
    @classmethod
    def create_street_name_sign(cls, x, z, street_name, rotation=0.0):
        """Create a street name sign with custom text"""
        return cls(x, z, 'street_name', custom_text=street_name, rotation=rotation)
    
    @classmethod
    def create_speed_limit_sign(cls, x, z, speed_limit=50, rotation=0.0):
        """Create a speed limit sign with custom speed"""
        text = f"SPEED\nLIMIT\n{speed_limit}"
        return cls(x, z, 'speed_limit', custom_text=text, rotation=rotation)
    
    def draw(self):
        """Draw the street sign"""
        glPushMatrix()
        
        # Move to sign position
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        
        # Draw the post
        self._draw_post()
        
        # Draw the sign
        glTranslatef(0, self.sign_height_offset, 0)
        self._draw_sign_shape()
        
        glPopMatrix()
    
    def _draw_post(self):
        """Draw the sign post behind the sign"""
        glPushMatrix()
        
        # Move post behind the sign (negative Z direction)
        glTranslatef(0, 0, -0.05)  # Move post 0.1 units behind the sign
        
        glColor3f(0.5, 0.5, 0.5)  # Gray post
        
        # Draw post as a rectangular prism
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-self.post_width/2, 0, self.post_width/2)
        glVertex3f(self.post_width/2, 0, self.post_width/2)
        glVertex3f(self.post_width/2, self.post_height, self.post_width/2)
        glVertex3f(-self.post_width/2, self.post_height, self.post_width/2)
        
        # Back face
        glVertex3f(-self.post_width/2, 0, -self.post_width/2)
        glVertex3f(-self.post_width/2, self.post_height, -self.post_width/2)
        glVertex3f(self.post_width/2, self.post_height, -self.post_width/2)
        glVertex3f(self.post_width/2, 0, -self.post_width/2)
        
        # Left face
        glVertex3f(-self.post_width/2, 0, -self.post_width/2)
        glVertex3f(-self.post_width/2, 0, self.post_width/2)
        glVertex3f(-self.post_width/2, self.post_height, self.post_width/2)
        glVertex3f(-self.post_width/2, self.post_height, -self.post_width/2)
        
        # Right face
        glVertex3f(self.post_width/2, 0, -self.post_width/2)
        glVertex3f(self.post_width/2, self.post_height, -self.post_width/2)
        glVertex3f(self.post_width/2, self.post_height, self.post_width/2)
        glVertex3f(self.post_width/2, 0, self.post_width/2)
        
        glEnd()
        
        glPopMatrix()  # Close the post transformation
    
    def _draw_sign_shape(self):
        """Draw the sign shape based on its type"""
        size = self.sign_data['size']
        color = self.sign_data['color']
        shape = self.sign_data['shape']
        
        # Set sign color
        glColor3f(*color)
        
        if shape == 'rectangle':
            self._draw_rectangle(size)
        elif shape == 'circle':
            self._draw_circle(size)
        elif shape == 'triangle':
            self._draw_triangle(size)
        elif shape == 'octagon':
            self._draw_octagon(size)
        elif shape == 'diamond':
            self._draw_diamond(size)
        elif shape == 'pentagon':
            self._draw_pentagon(size)
    
    def _draw_rectangle(self, size):
        """Draw a rectangular sign"""
        width = size * 0.8
        height = size * 0.6
        
        glBegin(GL_QUADS)
        glVertex3f(-width/2, -height/2, 0.01)
        glVertex3f(width/2, -height/2, 0.01)
        glVertex3f(width/2, height/2, 0.01)
        glVertex3f(-width/2, height/2, 0.01)
        glEnd()
        
        # Draw border
        glColor3f(0.0, 0.0, 0.0)  # Black border
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-width/2, -height/2, 0.02)
        glVertex3f(width/2, -height/2, 0.02)
        glVertex3f(width/2, height/2, 0.02)
        glVertex3f(-width/2, height/2, 0.02)
        glEnd()
    
    def _draw_circle(self, size):
        """Draw a circular sign"""
        radius = size * 0.4
        segments = 16
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0.01)
        for i in range(segments + 1):
            angle = 2.0 * 3.14159 * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.01)
        glEnd()
        
        # Draw border
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * 3.14159 * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.02)
        glEnd()
    
    def _draw_triangle(self, size):
        """Draw a triangular sign (pointing up)"""
        height = size * 0.7
        width = size * 0.8
        
        glBegin(GL_TRIANGLES)
        glVertex3f(0, height/2, 0.01)           # Top
        glVertex3f(-width/2, -height/2, 0.01)  # Bottom left
        glVertex3f(width/2, -height/2, 0.01)   # Bottom right
        glEnd()
        
        # Draw border - check for special border properties
        if 'border_color' in self.sign_data and 'border_width' in self.sign_data:
            # Use custom border color and width (for traffic_light_ahead)
            glColor3f(*self.sign_data['border_color'])
            glLineWidth(self.sign_data['border_width'])
        else:
            # Default black border
            glColor3f(0.0, 0.0, 0.0)
            glLineWidth(2.0)
            
        glBegin(GL_LINE_LOOP)
        glVertex3f(0, height/2, 0.02)
        glVertex3f(-width/2, -height/2, 0.02)
        glVertex3f(width/2, -height/2, 0.02)
        glEnd()
        
        # Draw traffic light circles if this is a traffic_light_ahead sign
        if self.sign_data.get('draw_traffic_lights', False):
            self._draw_traffic_light_circles(size)
    
    def _draw_octagon(self, size):
        """Draw an octagonal sign (stop sign shape)"""
        radius = size * 0.4
        segments = 8
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0.01)
        for i in range(segments + 1):
            angle = 2.0 * 3.14159 * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.01)
        glEnd()
        
        # Draw border
        glColor3f(1.0, 1.0, 1.0)  # White border for stop sign
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * 3.14159 * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.02)
        glEnd()
    
    def _draw_diamond(self, size):
        """Draw a diamond-shaped sign"""
        half_size = size * 0.4
        
        glBegin(GL_QUADS)
        glVertex3f(0, half_size, 0.01)      # Top
        glVertex3f(half_size, 0, 0.01)      # Right
        glVertex3f(0, -half_size, 0.01)     # Bottom
        glVertex3f(-half_size, 0, 0.01)     # Left
        glEnd()
        
        # Draw border
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(0, half_size, 0.02)
        glVertex3f(half_size, 0, 0.02)
        glVertex3f(0, -half_size, 0.02)
        glVertex3f(-half_size, 0, 0.02)
        glEnd()
    
    def _draw_traffic_light_circles(self, size):
        """Draw red, yellow, and green circles for traffic light ahead sign"""
        circle_radius = size * 0.08  # Small circles
        circle_spacing = size * 0.18  # Vertical spacing between circles
        
        # Center the traffic light vertically in the triangle
        start_y = circle_spacing * 0.8  # Start a bit above center
        
        # Draw three circles vertically aligned
        circle_positions = [
            (0, start_y, (0.8, 0.1, 0.1)),      # Red (top)
            (0, start_y - circle_spacing, (1.0, 0.8, 0.0)),  # Yellow (middle)
            (0, start_y - circle_spacing * 2, (0.1, 0.8, 0.1))   # Green (bottom)
        ]
        
        segments = 12  # Smooth circles
        
        for x, y, color in circle_positions:
            # Set circle color
            glColor3f(*color)
            
            # Draw filled circle
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(x, y, 0.03)  # Center point, slightly in front
            for i in range(segments + 1):
                angle = 2.0 * 3.14159 * i / segments
                circle_x = x + circle_radius * math.cos(angle)
                circle_y = y + circle_radius * math.sin(angle)
                glVertex3f(circle_x, circle_y, 0.03)
            glEnd()
            
            # Draw black border around each circle
            glColor3f(0.0, 0.0, 0.0)
            glLineWidth(1.5)
            glBegin(GL_LINE_LOOP)
            for i in range(segments):
                angle = 2.0 * 3.14159 * i / segments
                circle_x = x + circle_radius * math.cos(angle)
                circle_y = y + circle_radius * math.sin(angle)
                glVertex3f(circle_x, circle_y, 0.04)
            glEnd()
    
    def _draw_pentagon(self, size):
        """Draw a pentagonal sign (school zone shape)"""
        radius = size * 0.4
        segments = 5
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0.01)
        for i in range(segments + 1):
            angle = 2.0 * 3.14159 * i / segments - 3.14159/2  # Start from top
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.01)
        glEnd()
        
        # Draw border
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * 3.14159 * i / segments - 3.14159/2
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.02)
        glEnd()
    
    def get_sign_info(self):
        """Return information about this sign"""
        return {
            'type': self.sign_type,
            'text': self.sign_data['text'],
            'position': (self.x, self.z),
            'rotation': self.rotation,
            'color': self.sign_data['color']
        }


# Utility functions for creating common sign arrangements
def create_intersection_signs(x, z, sign_types=['stop', 'stop', 'stop', 'stop']):
    """Create signs for a 4-way intersection"""
    signs = []
    positions = [
        (x - 3, z, 0),    # West side, facing east
        (x + 3, z, 180),  # East side, facing west  
        (x, z - 3, 90),   # South side, facing north
        (x, z + 3, 270)   # North side, facing south
    ]
    
    for i, (sign_x, sign_z, rotation) in enumerate(positions):
        if i < len(sign_types):
            sign = Sign(sign_x, sign_z, sign_types[i], rotation=rotation)
            signs.append(sign)
    
    return signs


def create_street_signs_from_list(sign_list):
    """
    Create signs from a list of sign definitions
    
    Args:
        sign_list: List of dictionaries with sign properties
                  Example: [{'x': 10, 'z': 5, 'type': 'stop', 'rotation': 0},
                           {'x': 15, 'z': 8, 'type': 'speed_limit', 'text': 'SPEED\nLIMIT\n30'}]
    """
    signs = []
    for sign_def in sign_list:
        x = sign_def.get('x', 0)
        z = sign_def.get('z', 0)
        sign_type = sign_def.get('type', 'stop')
        custom_text = sign_def.get('text', None)
        rotation = sign_def.get('rotation', 0)
        
        sign = Sign(x, z, sign_type, custom_text, rotation)
        signs.append(sign)
    
    return signs