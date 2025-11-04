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
        
    def draw(self):
        """Draw the building with windows"""
        if self.destroyed:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y + self.height/2, self.z)  # Center the building
        glScalef(self.width, self.height, self.depth)
        
        glColor3f(self.color_r, self.color_g, self.color_b)  # Random colored building
        self.draw_box()
        
        # Draw windows on the building
        self.draw_windows()
        
        glPopMatrix()
        
    def draw_windows(self):
        """Draw simple windows on all sides of the building with light emission"""
        # Save current OpenGL state
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configure for proper blending
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)  # Don't write to depth buffer for transparent objects
        
        window_size = 0.12
        window_spacing = 0.25
        
        # Calculate number of windows based on building dimensions
        rows = max(1, int(self.height * 2))
        cols_width = max(1, int(self.width * 3))
        cols_depth = max(1, int(self.depth * 3))
        
        # Front face windows (Z = 0.55) - emit light
        glColor4f(1.0, 0.9, 0.6, 0.4)  # Semi-transparent warm glow
        for row in range(rows):
            for col in range(cols_width):
                if row % 2 == 0 and col % 2 == 0:  # Every other window
                    x_offset = (col - cols_width/2 + 0.5) * window_spacing / cols_width
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    glow_size = window_size * 1.5
                    glBegin(GL_QUADS)
                    glVertex3f(x_offset - glow_size/2, y_offset - glow_size/2, 0.55)
                    glVertex3f(x_offset + glow_size/2, y_offset - glow_size/2, 0.55)
                    glVertex3f(x_offset + glow_size/2, y_offset + glow_size/2, 0.55)
                    glVertex3f(x_offset - glow_size/2, y_offset + glow_size/2, 0.55)
                    glEnd()
        
        # Back face windows (Z = -0.55) - emit light
        for row in range(rows):
            for col in range(cols_width):
                if row % 2 == 0 and col % 2 == 0:
                    x_offset = (col - cols_width/2 + 0.5) * window_spacing / cols_width
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    glow_size = window_size * 1.5
                    glBegin(GL_QUADS)
                    glVertex3f(x_offset - glow_size/2, y_offset - glow_size/2, -0.55)
                    glVertex3f(x_offset + glow_size/2, y_offset - glow_size/2, -0.55)
                    glVertex3f(x_offset + glow_size/2, y_offset + glow_size/2, -0.55)
                    glVertex3f(x_offset - glow_size/2, y_offset + glow_size/2, -0.55)
                    glEnd()
        
        # Left face windows (X = -0.55) - emit light
        for row in range(rows):
            for col in range(cols_depth):
                if row % 2 == 0 and col % 2 == 0:
                    z_offset = (col - cols_depth/2 + 0.5) * window_spacing / cols_depth
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    glow_size = window_size * 1.5
                    glBegin(GL_QUADS)
                    glVertex3f(-0.55, y_offset - glow_size/2, z_offset - glow_size/2)
                    glVertex3f(-0.55, y_offset - glow_size/2, z_offset + glow_size/2)
                    glVertex3f(-0.55, y_offset + glow_size/2, z_offset + glow_size/2)
                    glVertex3f(-0.55, y_offset + glow_size/2, z_offset - glow_size/2)
                    glEnd()
        
        # Right face windows (X = 0.55) - emit light
        for row in range(rows):
            for col in range(cols_depth):
                if row % 2 == 0 and col % 2 == 0:
                    z_offset = (col - cols_depth/2 + 0.5) * window_spacing / cols_depth
                    y_offset = (row - rows/2 + 0.5) * window_spacing / rows
                    
                    glow_size = window_size * 1.5
                    glBegin(GL_QUADS)
                    glVertex3f(0.55, y_offset - glow_size/2, z_offset - glow_size/2)
                    glVertex3f(0.55, y_offset + glow_size/2, z_offset - glow_size/2)
                    glVertex3f(0.55, y_offset + glow_size/2, z_offset + glow_size/2)
                    glVertex3f(0.55, y_offset - glow_size/2, z_offset + glow_size/2)
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