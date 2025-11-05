"""
Building module for 3D Car Racing Game
Contains the Building class with collision detection and window lighting effects.
"""
from OpenGL.GL import *
from classes.physics import Physics


class Building(Physics):
    """Building class with collision detection and glowing window effects"""
    
    def __init__(self, x, y, z, width, height, depth):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        self.destroyed = False
        
        self.color_r = 0.2
        self.color_g = 0.2
        self.color_b = 0.2
        
    def draw(self, is_day_time=True):
        """Draw the building with windows"""
        if self.destroyed:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y + self.height/2, self.z)  # Center the building
        glScalef(self.width, self.height, self.depth)
        
        glColor3f(self.color_r, self.color_g, self.color_b)  # Random colored building
        self.draw_box()
        
        # Draw windows on the building
        self.draw_windows(is_day_time)
        
        glPopMatrix()
        
    def draw_windows(self, is_day_time=True):
        """Draw optimized realistic windows on all sides of the building"""
        # Save current OpenGL state
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configure for proper blending
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        
        window_size = 0.1  # Slightly larger for fewer windows
        window_spacing = 0.2  # More spacing for better performance
        
        # Reduce window density for better performance
        rows = max(2, min(6, int(self.height * 2.5)))  # Cap at 6 rows
        cols_width = max(2, min(8, int(self.width * 3)))  # Cap at 8 columns
        cols_depth = max(2, min(8, int(self.depth * 3)))  # Cap at 8 columns
        
        # Debug: Force nighttime for testing
        # is_day_time = False  # Uncomment this line to test night windows
        
        # Use single random seed for consistency and performance
        import random
        random.seed(int(self.x * 100 + self.z * 100))
        
        # Front face windows (Z = 0.51)
        for row in range(1, rows):  # Start from row 1 (skip ground floor)
            for col in range(cols_width):
                # At night, show MOST windows lit (only skip 20%)
                if not is_day_time and random.random() < 0.2:  # Only 20% chance to skip
                    continue
                
                # Set color for EACH window based on time of day
                if is_day_time:
                    # Daytime: Dark reflective windows
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Normal blending
                    glColor4f(0.15, 0.25, 0.35, 0.9)  # Dark windows
                else:
                    # Nighttime: VERY bright glowing windows
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for glow
                    glColor4f(1.0, 0.9, 0.5, 1.0)  # Bright warm yellow
                
                x_offset = (col - cols_width/2 + 0.5) * window_spacing / cols_width
                y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                
                window_width = window_size
                window_height = window_size * 1.2
                
                glBegin(GL_QUADS)
                glVertex3f(x_offset - window_width/2, y_offset - window_height/2, 0.51)
                glVertex3f(x_offset + window_width/2, y_offset - window_height/2, 0.51)
                glVertex3f(x_offset + window_width/2, y_offset + window_height/2, 0.51)
                glVertex3f(x_offset - window_width/2, y_offset + window_height/2, 0.51)
                glEnd()
        
        # Back face windows (Z = -0.51) - only if building is large enough
        if self.width > 2 or self.depth > 2:
            for row in range(1, rows):
                for col in range(cols_width):
                    if not is_day_time and random.random() < 0.2:  # Only 20% chance to skip
                        continue
                    
                    # Set color for EACH window
                    if is_day_time:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                        glColor4f(0.15, 0.25, 0.35, 0.9)
                    else:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                        glColor4f(1.0, 0.9, 0.5, 1.0)
                    
                    x_offset = (col - cols_width/2 + 0.5) * window_spacing / cols_width
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    window_width = window_size
                    window_height = window_size * 1.2
                    
                    glBegin(GL_QUADS)
                    glVertex3f(x_offset - window_width/2, y_offset - window_height/2, -0.51)
                    glVertex3f(x_offset + window_width/2, y_offset - window_height/2, -0.51)
                    glVertex3f(x_offset + window_width/2, y_offset + window_height/2, -0.51)
                    glVertex3f(x_offset - window_width/2, y_offset + window_height/2, -0.51)
                    glEnd()
        
        # Side faces - only for larger buildings
        if self.width > 1.5:
            # Left face windows (X = -0.51)
            for row in range(1, rows):
                for col in range(0, cols_depth, 2):  # Every other column for performance
                    if not is_day_time and random.random() < 0.2:  # Only 20% chance to skip
                        continue
                    
                    # Set color for EACH window
                    if is_day_time:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                        glColor4f(0.15, 0.25, 0.35, 0.9)
                    else:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                        glColor4f(1.0, 0.9, 0.5, 1.0)
                    
                    z_offset = (col - cols_depth/2 + 0.5) * window_spacing / cols_depth
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    window_width = window_size
                    window_height = window_size * 1.2
                    
                    glBegin(GL_QUADS)
                    glVertex3f(-0.51, y_offset - window_height/2, z_offset - window_width/2)
                    glVertex3f(-0.51, y_offset - window_height/2, z_offset + window_width/2)
                    glVertex3f(-0.51, y_offset + window_height/2, z_offset + window_width/2)
                    glVertex3f(-0.51, y_offset + window_height/2, z_offset - window_width/2)
                    glEnd()
            
            # Right face windows (X = 0.51)
            for row in range(1, rows):
                for col in range(0, cols_depth, 2):  # Every other column for performance
                    if not is_day_time and random.random() < 0.2:  # Only 20% chance to skip
                        continue
                    
                    # Set color for EACH window
                    if is_day_time:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                        glColor4f(0.15, 0.25, 0.35, 0.9)
                    else:
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                        glColor4f(1.0, 0.9, 0.5, 1.0)
                    
                    z_offset = (col - cols_depth/2 + 0.5) * window_spacing / cols_depth
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    window_width = window_size
                    window_height = window_size * 1.2
                    
                    glBegin(GL_QUADS)
                    glVertex3f(0.51, y_offset - window_height/2, z_offset - window_width/2)
                    glVertex3f(0.51, y_offset + window_height/2, z_offset - window_width/2)
                    glVertex3f(0.51, y_offset + window_height/2, z_offset + window_width/2)
                    glVertex3f(0.51, y_offset - window_height/2, z_offset + window_width/2)
                    glEnd()
        
        # Restore OpenGL state
        glPopAttrib()

    def draw_box(self):
        """Draw a simple box shape"""
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
        
        glEnd()