"""
Building module for 3D Car Racing Game
Contains the Building class with collision detection and window lighting effects.
"""
from OpenGL.GL import *
import pygame
import numpy as np
import random
from classes.physics import Physics


class Building(Physics):
    """Building class with collision detection and glowing window effects"""
    
    # Class-level texture cache to avoid recreating textures
    _texture_cache = {}
    
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
        
        # Texture properties
        self.texture_id = None
        self.texture_type = self._choose_texture_type()
        self._generate_texture()
    
    def _choose_texture_type(self):
        """Choose a random texture type for building variety"""
        # Use building position as seed for consistent textures
        # Use a more complex hash to get better distribution
        seed_value = int((self.x * 73 + self.z * 97 + self.width * 127 + self.height * 151) % 10000)
        random.seed(seed_value)
        texture_types = ['brick', 'concrete', 'glass_modern', 'stone']
        return random.choice(texture_types)
    
    def _generate_texture(self):
        """Generate or retrieve cached texture"""
        # Use the same improved hashing for cache key
        hash_value = int((self.x * 73 + self.z * 97 + self.width * 127 + self.height * 151) % 1000)
        cache_key = f"{self.texture_type}_{hash_value}"
        
        if cache_key in Building._texture_cache:
            self.texture_id = Building._texture_cache[cache_key]
            return
        
        # Generate new texture
        if self.texture_type == 'brick':
            surface = self._create_brick_texture()
        elif self.texture_type == 'concrete':
            surface = self._create_concrete_texture()
        elif self.texture_type == 'glass_modern':
            surface = self._create_glass_texture()
        elif self.texture_type == 'stone':
            surface = self._create_stone_texture()
        else:
            surface = self._create_concrete_texture()  # fallback
        
        # Convert pygame surface to OpenGL texture
        self.texture_id = self._surface_to_texture(surface)
        Building._texture_cache[cache_key] = self.texture_id
    
    def _create_brick_texture(self, size=128):
        """Create a brick pattern texture"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use position-based random seed for consistency
        random.seed(int(self.x * 100 + self.z * 100))
        
        # Base brick color (reddish brown)
        base_colors = [
            (120, 60, 40),    # Dark red-brown
            (140, 80, 50),    # Medium red-brown  
            (100, 50, 35),    # Dark brown
        ]
        base_color = random.choice(base_colors)
        
        brick_width = size // 8
        brick_height = size // 16
        mortar_color = (220, 220, 210)  # Light mortar
        
        # Fill with mortar color
        surface.fill(mortar_color)
        
        # Draw bricks
        for row in range(0, size, brick_height + 2):
            offset = (brick_width // 2) if (row // (brick_height + 2)) % 2 else 0
            for col in range(-offset, size + brick_width, brick_width + 2):
                if col + brick_width > 0 and col < size:
                    # Add slight color variation to each brick
                    variation = random.randint(-15, 15)
                    brick_color = tuple(max(0, min(255, c + variation)) for c in base_color)
                    
                    pygame.draw.rect(surface, brick_color, 
                                   (col, row, brick_width, brick_height))
                    
                    # Add some texture to the brick
                    for _ in range(3):
                        spot_x = col + random.randint(0, brick_width - 1)
                        spot_y = row + random.randint(0, brick_height - 1)
                        spot_color = tuple(max(0, min(255, c + random.randint(-20, 20))) 
                                         for c in brick_color)
                        pygame.draw.circle(surface, spot_color, (spot_x, spot_y), 1)
        
        return surface
    
    def _create_concrete_texture(self, size=128):
        """Create a concrete texture"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use position-based random seed
        random.seed(int(self.x * 100 + self.z * 100))
        
        # Base concrete colors (gray variations)
        base_colors = [
            (120, 120, 125),  # Cool gray
            (130, 125, 120),  # Warm gray
            (110, 115, 120),  # Blue-gray
        ]
        base_color = random.choice(base_colors)
        surface.fill(base_color)
        
        # Add concrete texture with noise
        for _ in range(size * 2):
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            variation = random.randint(-25, 25)
            noise_color = tuple(max(0, min(255, c + variation)) for c in base_color)
            pygame.draw.circle(surface, noise_color, (x, y), random.randint(1, 3))
        
        # Add some darker streaks for weathering
        for _ in range(5):
            start_y = random.randint(0, size)
            end_y = random.randint(start_y, size)
            x = random.randint(0, size - 1)
            dark_color = tuple(max(0, c - 30) for c in base_color)
            pygame.draw.line(surface, dark_color, (x, start_y), (x, end_y), 1)
        
        return surface
    
    def _create_glass_texture(self, size=128):
        """Create a modern glass building texture"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use position-based random seed
        random.seed(int(self.x * 100 + self.z * 100))
        
        # Glass colors (blue-tinted)
        base_colors = [
            (40, 60, 120),    # Blue tint
            (30, 70, 100),    # Darker blue
            (50, 50, 90),     # Purple-blue
        ]
        base_color = random.choice(base_colors)
        
        # Create glass panel grid
        panel_size = size // 6
        frame_color = (60, 60, 70)  # Dark frame
        
        # Fill with frame color
        surface.fill(frame_color)
        
        # Draw glass panels
        for row in range(0, size, panel_size + 4):
            for col in range(0, size, panel_size + 4):
                # Glass panel with gradient effect
                panel_rect = (col + 2, row + 2, panel_size, panel_size)
                pygame.draw.rect(surface, base_color, panel_rect)
                
                # Add reflective highlight
                highlight_color = tuple(min(255, c + 40) for c in base_color)
                highlight_rect = (col + 2, row + 2, panel_size // 3, panel_size)
                pygame.draw.rect(surface, highlight_color, highlight_rect)
                
                # Add subtle reflection pattern
                for i in range(0, panel_size, 8):
                    reflection_color = tuple(min(255, c + 20) for c in base_color)
                    pygame.draw.line(surface, reflection_color, 
                                   (col + 2 + i, row + 2), 
                                   (col + 2 + i, row + 2 + panel_size), 1)
        
        return surface
    
    def _create_stone_texture(self, size=128):
        """Create a stone texture"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use position-based random seed
        random.seed(int(self.x * 100 + self.z * 100))
        
        # Stone colors
        base_colors = [
            (100, 90, 80),    # Tan stone
            (90, 85, 75),     # Gray stone
            (80, 75, 70),     # Dark stone
        ]
        base_color = random.choice(base_colors)
        
        stone_width = size // 6
        stone_height = size // 8
        mortar_color = (160, 150, 140)
        
        # Fill with mortar
        surface.fill(mortar_color)
        
        # Draw irregular stones
        for row in range(0, size, stone_height + 3):
            offset = random.randint(-stone_width//4, stone_width//4) if row % (stone_height*2) else 0
            for col in range(offset, size, stone_width + 3):
                if col + stone_width > 0 and col < size:
                    # Vary stone size slightly
                    actual_width = stone_width + random.randint(-stone_width//4, stone_width//4)
                    actual_height = stone_height + random.randint(-stone_height//4, stone_height//4)
                    
                    # Stone color with variation
                    variation = random.randint(-20, 20)
                    stone_color = tuple(max(0, min(255, c + variation)) for c in base_color)
                    
                    pygame.draw.rect(surface, stone_color,
                                   (col, row, actual_width, actual_height))
                    
                    # Add texture spots
                    for _ in range(5):
                        spot_x = col + random.randint(0, actual_width - 1)
                        spot_y = row + random.randint(0, actual_height - 1)
                        spot_variation = random.randint(-15, 15)
                        spot_color = tuple(max(0, min(255, c + spot_variation)) 
                                         for c in stone_color)
                        pygame.draw.circle(surface, spot_color, (spot_x, spot_y), 1)
        
        return surface
    
    def _surface_to_texture(self, surface):
        """Convert pygame surface to OpenGL texture"""
        texture_data = pygame.image.tostring(surface, "RGBA", True)
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), 
                     surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        # Set texture parameters for tiling
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        return texture_id
        
    def draw(self, is_day_time=True):
        """Draw the building with textures and windows"""
        if self.destroyed:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y + self.height/2, self.z)  # Center the building
        glScalef(self.width, self.height, self.depth)
        
        # Enable texturing
        glEnable(GL_TEXTURE_2D)
        if self.texture_id:
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Set color to white so texture shows properly
        glColor3f(1.0, 1.0, 1.0)
        self.draw_textured_box()
        
        # Disable texturing before drawing windows
        glDisable(GL_TEXTURE_2D)
        
        # Draw windows on the building
        self.draw_windows(is_day_time)
        
        glPopMatrix()
        
    def draw_windows(self, is_day_time=True):
        """Draw realistic windows positioned according to building type and architecture"""
        # Save current OpenGL state
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configure for proper blending
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        
        # Use consistent random seed for window placement
        import random
        random.seed(int(self.x * 73 + self.z * 97 + self.width * 127))
        
        # Get building-specific window parameters based on texture type
        window_params = self._get_window_parameters()
        
        # Draw windows on each face
        self._draw_face_windows('front', is_day_time, window_params, random)
        if self.width > 1.5 or self.depth > 1.5:  # Only larger buildings get side windows
            self._draw_face_windows('back', is_day_time, window_params, random)
        if self.width > 2:  # Only wide buildings get left/right windows
            self._draw_face_windows('left', is_day_time, window_params, random)
            self._draw_face_windows('right', is_day_time, window_params, random)
        
        # Restore OpenGL state
        glPopAttrib()
    
    def _get_window_parameters(self):
        """Get uniform window layout parameters for all building types"""
        # All buildings use the same window size and regular grid spacing
        return {
            'rows': max(2, min(6, int(self.height * 2.5))),
            'cols_width': max(2, min(8, int(self.width * 3))),
            'cols_depth': max(2, min(8, int(self.depth * 3))),
            'window_width': 0.08,  # Standard window width for all buildings
            'window_height': 0.10,  # Standard window height for all buildings
            'spacing_x': 0.15,  # Uniform horizontal spacing
            'spacing_y': 0.15,  # Uniform vertical spacing
            'start_floor': 1,  # Skip ground floor for all buildings
            'frame_width': 0.008,  # Standard frame width
            'window_style': 'uniform'  # All buildings use same style
        }
    
    def _draw_face_windows(self, face, is_day_time, params, random):
        """Draw windows in uniform grid on a specific building face"""
        if face == 'front':
            z_offset = 0.52
            cols = params['cols_width']
            use_width = True
        elif face == 'back':
            z_offset = -0.52
            cols = params['cols_width'] 
            use_width = True
        elif face == 'left':
            x_offset = -0.52
            cols = params['cols_depth']
            use_width = False
        else:  # right
            x_offset = 0.52
            cols = params['cols_depth']
            use_width = False
        
        rows = params['rows']
        
        # Calculate uniform window positions in a perfect grid
        for row in range(params['start_floor'], rows):
            # Calculate floor position - evenly distributed
            floor_height = (row + 0.5) / rows - 0.5
            
            for col in range(cols):
                # At night, randomly decide if window is lit (50% chance)
                window_lit = True
                if not is_day_time:
                    window_lit = random.random() < 0.5  # 50% lit, 50% dark
                
                # Calculate horizontal position - evenly distributed
                col_position = (col + 0.5) / cols - 0.5
                
                # Set window appearance based on whether it's lit or dark
                if window_lit:
                    self._set_window_appearance(is_day_time, params['window_style'])
                else:
                    # Dark unlit window at night
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                    glColor4f(0.05, 0.05, 0.08, 1.0)  # Very dark gray for unlit windows
                
                # Use uniform window dimensions for all windows
                window_width = params['window_width']
                window_height = params['window_height']
                
                # Draw the window based on face orientation
                if face in ['front', 'back']:
                    self._draw_single_window(col_position, floor_height, z_offset if face == 'front' else z_offset,
                                           window_width, window_height, params['frame_width'], 'front_back')
                else:
                    # Side faces (left/right)
                    self._draw_single_window(floor_height, col_position, x_offset,
                                           window_width, window_height, params['frame_width'], 'left_right')
    
    def _set_window_appearance(self, is_day_time, window_style):
        """Set uniform window appearance for all building types"""
        if is_day_time:
            # Daytime windows - uniform dark reflective appearance
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            # light whiter color
            glColor4f(0.25, 0.35, 0.45, 1.0)  # Standard dark blue-gray windows
        else:
            # Nighttime windows - uniform warm glow
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for glow
            glColor4f(1.0, 0.9, 0.5, 1.0)  # Standard warm yellow light
    
    def _draw_single_window(self, x_pos, y_pos, z_pos, width, height, frame_width, orientation):
        """Draw a single window with frame"""
        if orientation == 'front_back':
            # Windows on front/back faces
            glBegin(GL_QUADS)
            # Main window
            glVertex3f(x_pos - width/2, y_pos - height/2, z_pos)
            glVertex3f(x_pos + width/2, y_pos - height/2, z_pos)
            glVertex3f(x_pos + width/2, y_pos + height/2, z_pos)
            glVertex3f(x_pos - width/2, y_pos + height/2, z_pos)
            glEnd()
            
            # Window frame (slightly darker)
            #glColor4f(0.1, 0.1, 0.1, 0.8)
            #glBegin(GL_LINE_LOOP)
            #glVertex3f(x_pos - width/2 - frame_width, y_pos - height/2 - frame_width, z_pos + 0.001)
            #glVertex3f(x_pos + width/2 + frame_width, y_pos - height/2 - frame_width, z_pos + 0.001)
            #glVertex3f(x_pos + width/2 + frame_width, y_pos + height/2 + frame_width, z_pos + 0.001)
            #glVertex3f(x_pos - width/2 - frame_width, y_pos + height/2 + frame_width, z_pos + 0.001)
            #glEnd()
            
        else:  # left_right orientation
            # Windows on left/right faces
            glBegin(GL_QUADS)
            # Main window
            glVertex3f(z_pos, x_pos - width/2, y_pos - height/2)
            glVertex3f(z_pos, x_pos - width/2, y_pos + height/2)
            glVertex3f(z_pos, x_pos + width/2, y_pos + height/2)
            glVertex3f(z_pos, x_pos + width/2, y_pos - height/2)
            glEnd()
            
            # Window frame
            #glColor4f(0.1, 0.1, 0.1, 0.8)
            #glBegin(GL_LINE_LOOP)
            #glVertex3f(z_pos + 0.001, x_pos - width/2 - frame_width, y_pos - height/2 - frame_width)
            #glVertex3f(z_pos + 0.001, x_pos + width/2 + frame_width, y_pos - height/2 - frame_width)
            #glVertex3f(z_pos + 0.001, x_pos + width/2 + frame_width, y_pos + height/2 + frame_width)
            #glVertex3f(z_pos + 0.001, x_pos - width/2 - frame_width, y_pos + height/2 + frame_width)
            #glEnd()

    def draw_textured_box(self):
        """Draw a textured box shape with proper UV coordinates"""
        # Calculate texture scale based on building size for consistent texture appearance
        tex_scale_x = max(1.0, self.width / 2.0)
        tex_scale_y = max(1.0, self.height / 2.0)
        tex_scale_z = max(1.0, self.depth / 2.0)
        
        glBegin(GL_QUADS)
        
        # Front face
        glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, 0.5)
        glTexCoord2f(tex_scale_x, 0); glVertex3f(0.5, -0.5, 0.5)
        glTexCoord2f(tex_scale_x, tex_scale_y); glVertex3f(0.5, 0.5, 0.5)
        glTexCoord2f(0, tex_scale_y); glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, -0.5)
        glTexCoord2f(0, tex_scale_y); glVertex3f(-0.5, 0.5, -0.5)
        glTexCoord2f(tex_scale_x, tex_scale_y); glVertex3f(0.5, 0.5, -0.5)
        glTexCoord2f(tex_scale_x, 0); glVertex3f(0.5, -0.5, -0.5)
        
        # Left face
        glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, -0.5)
        glTexCoord2f(tex_scale_z, 0); glVertex3f(-0.5, -0.5, 0.5)
        glTexCoord2f(tex_scale_z, tex_scale_y); glVertex3f(-0.5, 0.5, 0.5)
        glTexCoord2f(0, tex_scale_y); glVertex3f(-0.5, 0.5, -0.5)
        
        # Right face
        glTexCoord2f(0, 0); glVertex3f(0.5, -0.5, -0.5)
        glTexCoord2f(0, tex_scale_y); glVertex3f(0.5, 0.5, -0.5)
        glTexCoord2f(tex_scale_z, tex_scale_y); glVertex3f(0.5, 0.5, 0.5)
        glTexCoord2f(tex_scale_z, 0); glVertex3f(0.5, -0.5, 0.5)
        
        # Top face (roof)
        glTexCoord2f(0, 0); glVertex3f(-0.5, 0.5, -0.5)
        glTexCoord2f(tex_scale_x, 0); glVertex3f(0.5, 0.5, -0.5)
        glTexCoord2f(tex_scale_x, tex_scale_z); glVertex3f(0.5, 0.5, 0.5)
        glTexCoord2f(0, tex_scale_z); glVertex3f(-0.5, 0.5, 0.5)
        
        # Bottom face (usually not visible, but included for completeness)
        glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, -0.5)
        glTexCoord2f(0, tex_scale_z); glVertex3f(-0.5, -0.5, 0.5)
        glTexCoord2f(tex_scale_x, tex_scale_z); glVertex3f(0.5, -0.5, 0.5)
        glTexCoord2f(tex_scale_x, 0); glVertex3f(0.5, -0.5, -0.5)
        
        glEnd()
    
    def cleanup(self):
        """Clean up OpenGL resources"""
        if self.texture_id:
            # Only delete if we created this texture (not from cache)
            hash_value = int((self.x * 73 + self.z * 97 + self.width * 127 + self.height * 151) % 1000)
            cache_key = f"{self.texture_type}_{hash_value}"
            if cache_key not in Building._texture_cache:
                glDeleteTextures([self.texture_id])
            self.texture_id = None
    
    @classmethod
    def cleanup_texture_cache(cls):
        """Clean up all cached textures - call when exiting game"""
        for texture_id in cls._texture_cache.values():
            glDeleteTextures([texture_id])
        cls._texture_cache.clear()