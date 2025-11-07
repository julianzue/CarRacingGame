"""
Sky module for 3D Car Racing Game
Contains the Sky class for rendering procedurally generated sky with different times of day.
"""
import pygame
import math
from OpenGL.GL import *


class Sky:
    """Sky class that renders a procedurally generated sky dome with time-of-day variations"""
    
    # Class-level texture cache for sky textures
    _sky_texture_cache = {}
    
    def __init__(self):
        self.sky_mode = 'night'  # 'night', 'sunrise', 'day', 'sunset'
        self.transition_progress = 0.0  # 0.0 to 1.0 for smooth transitions
        self.sky_radius = 500.0  # Increased from 100.0 to cover entire map
        self.dome_segments = 32  # Reduced from 64 for better performance
        self.dome_rings = 16  # Reduced from 32 for better performance
    
    @staticmethod
    def _create_sky_texture(sky_type):
        """Create a procedurally generated sky texture"""
        if sky_type in Sky._sky_texture_cache:
            return Sky._sky_texture_cache[sky_type]
        
        width, height = 512, 256
        surface = pygame.Surface((width, height))
        
        if sky_type == 'night':
            Sky._generate_night_sky(surface)
        elif sky_type == 'sunrise':
            Sky._generate_sunrise_sky(surface)
        elif sky_type == 'day':
            Sky._generate_day_sky(surface)
        elif sky_type == 'sunset':
            Sky._generate_sunset_sky(surface)
        
        # Convert surface to OpenGL texture
        texture_data = pygame.image.tostring(surface, "RGB", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        
        Sky._sky_texture_cache[sky_type] = texture_id
        return texture_id
    
    @staticmethod
    def _generate_night_sky(surface):
        """Generate a night sky with stars"""
        width, height = surface.get_size()
        
        # Dark blue gradient background (bottom darker)
        for y in range(height):
            # Gradient from dark blue at horizon to darker blue at top
            t = y / height
            r = int(5 + t * 15)
            g = int(5 + t * 15)
            b = int(20 + t * 40)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Add stars
        import random
        random.seed(42)  # Consistent star pattern
        for _ in range(200):
            x = random.randint(0, width - 1)
            y = random.randint(0, height // 2)  # Stars mostly in upper half
            
            brightness = random.randint(150, 255)
            size = random.choice([1, 1, 1, 2])
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)
        
        # Add some nebula clouds
        for _ in range(30):
            x = random.randint(0, width - 50)
            y = random.randint(0, height // 3)
            size = random.randint(20, 60)
            color = random.choice([
                (100, 50, 150),   # Purple nebula
                (50, 100, 150),   # Blue nebula
                (150, 50, 100)    # Pink nebula
            ])
            pygame.draw.circle(surface, color, (x, y), size)
    
    @staticmethod
    def _generate_sunrise_sky(surface):
        """Generate a sunrise sky with warm orange and pink hues"""
        width, height = surface.get_size()
        
        # Gradient from orange at horizon to light blue at top
        for y in range(height):
            t = y / height
            
            if t < 0.3:
                # Lower part: warm orange to yellow gradient
                r = int(255 - t * 50)
                g = int(200 + t * 30)
                b = int(50 + t * 100)
            elif t < 0.6:
                # Middle: orange to pink gradient
                t_mid = (t - 0.3) / 0.3
                r = int(255 - t_mid * 30)
                g = int(130 - t_mid * 50)
                b = int(150 + t_mid * 50)
            else:
                # Upper: pink to light blue gradient
                t_top = (t - 0.6) / 0.4
                r = int(220 - t_top * 100)
                g = int(80 + t_top * 120)
                b = int(200 + t_top * 55)
            
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Add some cloud textures with warm colors
        import random
        random.seed(42)
        for _ in range(15):
            x = random.randint(0, width - 100)
            y = random.randint(0, height // 2)
            size = random.randint(30, 80)
            color = random.choice([
                (255, 150, 100),  # Light orange
                (255, 200, 150),  # Light peach
                (255, 180, 120)   # Coral
            ])
            pygame.draw.circle(surface, color, (x, y), size)
    
    @staticmethod
    def _generate_day_sky(surface):
        """Generate a bright day sky with light blue and white clouds"""
        width, height = surface.get_size()
        
        # Gradient from light blue at horizon to darker blue at top
        for y in range(height):
            t = y / height
            
            # Lighter blue at bottom, slightly darker at top
            r = int(200 - t * 40)
            g = int(220 - t * 40)
            b = int(255 - t * 50)
            
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Add white clouds
        import random
        random.seed(42)
        for _ in range(20):
            x = random.randint(0, width - 120)
            y = random.randint(20, height // 2)
            size = random.randint(40, 100)
            
            # Draw cloud clusters
            color = (255, 255, 255)
            pygame.draw.circle(surface, color, (x, y), size)
            pygame.draw.circle(surface, color, (x + size // 2, y - size // 3), size // 1.5)
            pygame.draw.circle(surface, color, (x - size // 2, y - size // 3), size // 1.5)
        
        # Add sun
        sun_x = width // 4
        sun_y = height // 3
        pygame.draw.circle(surface, (255, 240, 100), (sun_x, sun_y), 40)
        pygame.draw.circle(surface, (255, 250, 150), (sun_x, sun_y), 35)
    
    @staticmethod
    def _generate_sunset_sky(surface):
        """Generate a sunset sky with deep orange, red, and purple hues"""
        width, height = surface.get_size()
        
        # Gradient from deep orange at horizon to purple at top
        for y in range(height):
            t = y / height
            
            if t < 0.3:
                # Lower part: deep orange to red gradient
                r = int(255)
                g = int(150 - t * 150)
                b = int(50 + t * 50)
            elif t < 0.6:
                # Middle: red to purple gradient
                t_mid = (t - 0.3) / 0.3
                r = int(255 - t_mid * 50)
                g = int(0 + t_mid * 50)
                b = int(100 + t_mid * 80)
            else:
                # Upper: purple to deep blue gradient
                t_top = (t - 0.6) / 0.4
                r = int(200 - t_top * 150)
                g = int(50 - t_top * 30)
                b = int(180 + t_top * 40)
            
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Add dark cloud silhouettes
        import random
        random.seed(42)
        for _ in range(12):
            x = random.randint(0, width - 150)
            y = random.randint(height // 4, height // 2)
            size = random.randint(50, 120)
            color = random.choice([
                (80, 30, 60),      # Dark purple
                (100, 40, 80),     # Dark magenta
                (60, 20, 40)       # Very dark purple
            ])
            pygame.draw.circle(surface, color, (x, y), size)
        
        # Add sunset sun
        sun_x = width * 3 // 4
        sun_y = height // 3
        pygame.draw.circle(surface, (255, 100, 50), (sun_x, sun_y), 45)
        pygame.draw.circle(surface, (255, 150, 80), (sun_x, sun_y), 40)
    
    def set_sky_mode(self, mode, progress=0.0):
        """
        Set the sky mode with optional transition progress
        
        Args:
            mode: 'night', 'sunrise', 'day', or 'sunset'
            progress: 0.0 to 1.0 for smooth transitions between modes
        """
        self.sky_mode = mode
        self.transition_progress = progress
    
    def draw(self):
        """Draw the sky dome with texture"""
        glPushMatrix()
        glDisable(GL_LIGHTING)
        
        # Create sky dome
        glColor3f(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        
        sky_texture = self._create_sky_texture(self.sky_mode)
        glBindTexture(GL_TEXTURE_2D, sky_texture)
        
        # Draw sky dome as a sphere
        glRotatef(-90, 1, 0, 0)  # Rotate so we look up
        
        for ring in range(self.dome_rings):
            glBegin(GL_QUAD_STRIP)
            
            ring_angle = (ring / self.dome_rings) * math.pi
            next_ring_angle = ((ring + 1) / self.dome_rings) * math.pi
            
            for segment in range(self.dome_segments + 1):
                segment_angle = (segment / self.dome_segments) * 2 * math.pi
                
                # Current ring vertex
                x = self.sky_radius * math.sin(ring_angle) * math.cos(segment_angle)
                y = self.sky_radius * math.cos(ring_angle)
                z = self.sky_radius * math.sin(ring_angle) * math.sin(segment_angle)
                
                u = segment / self.dome_segments
                v = ring / self.dome_rings
                
                glTexCoord2f(u, v)
                glVertex3f(x, y, z)
                
                # Next ring vertex
                x = self.sky_radius * math.sin(next_ring_angle) * math.cos(segment_angle)
                y = self.sky_radius * math.cos(next_ring_angle)
                z = self.sky_radius * math.sin(next_ring_angle) * math.sin(segment_angle)
                
                v = (ring + 1) / self.dome_rings
                
                glTexCoord2f(u, v)
                glVertex3f(x, y, z)
            
            glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()
