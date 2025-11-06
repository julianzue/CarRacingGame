"""
Vehicle module for 3D Car Racing Game
Contains Vehicle base class and Car/Motorcycle classes with physics, movement, AI, and rendering.
"""
import math
import random
import pygame
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
from classes.physics import Physics


class Vehicle(Physics):
    """Base vehicle class with shared physics and lighting"""
    
    def __init__(self, vehicle_type="car"):
        super().__init__()
        self.vehicle_type = vehicle_type
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.angle = 270.0  # Start rotated 90 degrees
        self.speed = 0.0
        self.base_acceleration = 0.002  # Much slower for 68hp Golf (reduced from 0.004 to 0.002)
        self.friction = 0.95
        
        # Steering wheel angle for front wheel rotation
        self.steering_angle = 0.0
        
        # Lighting system
        self.headlights_on = False
        self.auto_headlights = True  # Automatically turn on at night
        self.braking = False
        self.turning_left = False
        self.turning_right = False
        
        # Vehicle-specific properties (will be overridden)
        self.max_speed = 0.9  # Updated to 0.9 for 180 km/h top speed (0.9 × 200 = 180 km/h)
        self.turn_speed = 6.0
        self.max_steering_angle = 60.0


class Car(Vehicle):
    # Class-level cache for environment map texture
    _env_map_texture = None
    
    @staticmethod
    def _create_env_map_texture():
        """Create a dynamic environment map texture for reflections"""
        if Car._env_map_texture is not None:
            return Car._env_map_texture
        
        # Create a sophisticated metallic environment map
        import pygame
        width, height = 512, 512
        surface = pygame.Surface((width, height))
        
        # Create a more realistic environment with sky, buildings, and reflections
        # Top section - Sky with gradient
        for y in range(height // 3):
            ratio = y / (height // 3)
            # Deep blue sky at top, lighter towards horizon
            r = int(30 + ratio * 80)
            g = int(80 + ratio * 100)
            b = int(180 + ratio * 50)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Middle section - Light reflections and atmosphere
        for y in range(height // 3, 2 * height // 3):
            ratio = (y - height // 3) / (height // 3)
            # Bright atmosphere reflections
            r = int(120 + ratio * 50)
            g = int(150 + ratio * 40)
            b = int(200 - ratio * 50)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Bottom section - Ground and building reflections
        for y in range(2 * height // 3, height):
            ratio = (y - 2 * height // 3) / (height // 3)
            # Gray urban environment reflection
            r = int(100 + ratio * 30)
            g = int(100 + ratio * 30)
            b = int(100 + ratio * 20)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Add metallic speckles and shine highlights
        import random
        random.seed(42)
        for _ in range(200):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            brightness = random.randint(200, 255)
            # Add bright metallic points
            pygame.draw.circle(surface, (brightness, brightness, brightness - 20), (x, y), random.randint(1, 3))
        
        # Convert to OpenGL texture
        texture_data = pygame.image.tostring(surface, "RGB", True)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        Car._env_map_texture = texture_id
        return texture_id
    
    @staticmethod
    def _setup_reflection_mapping():
        """Setup OpenGL for environment mapping (reflection)"""
        # Enable environment mapping
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
    
    @staticmethod
    def _disable_reflection_mapping():
        """Disable environment mapping"""
        glDisable(GL_TEXTURE_GEN_S)
        glDisable(GL_TEXTURE_GEN_T)
    
    def draw_chassis(self):
        """Draw the car's chassis (cassis) to fit the window layout, plus an inner chassis inside the windows."""
        # Setup environment mapping for reflections
        env_texture = self._create_env_map_texture()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, env_texture)
        self._setup_reflection_mapping()
        
        # Outer chassis - Metallic reflective paint with environment mapping
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.15, 0.2, 0.4, 1.0])  # Metallic dark blue base
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.95, 1.0, 1.0, 1.0])  # Bright white metallic highlights
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0)  # Maximum metallic shine for reflecting effect
        glColor4f(0.15, 0.2, 0.4, 0.9)  # Metallic dark blue with enhanced reflectivity
        glBegin(GL_QUADS)
        y_bottom = -0.1
        y_top = 0.25
        x_left = -0.5
        x_right = 0.5
        z_front = 1.2
        z_back = -1.2
        # Bottom face
        glVertex3f(x_left, y_bottom, z_back)
        glVertex3f(x_right, y_bottom, z_back)
        glVertex3f(x_right, y_bottom, z_front)
        glVertex3f(x_left, y_bottom, z_front)
        # Top face
        glVertex3f(x_left, y_top, z_back)
        glVertex3f(x_right, y_top, z_back)
        glVertex3f(x_right, y_top, z_front)
        glVertex3f(x_left, y_top, z_front)
        # Left face
        glVertex3f(x_left, y_bottom, z_back)
        glVertex3f(x_left, y_top, z_back)
        glVertex3f(x_left, y_top, z_front)
        glVertex3f(x_left, y_bottom, z_front)
        # Right face
        glVertex3f(x_right, y_bottom, z_back)
        glVertex3f(x_right, y_top, z_back)
        glVertex3f(x_right, y_top, z_front)
        glVertex3f(x_right, y_bottom, z_front)
        # Front face
        glVertex3f(x_left, y_bottom, z_front)
        glVertex3f(x_right, y_bottom, z_front)
        glVertex3f(x_right, y_top, z_front)
        glVertex3f(x_left, y_top, z_front)
        # Back face
        glVertex3f(x_left, y_bottom, z_back)
        glVertex3f(x_right, y_bottom, z_back)
        glVertex3f(x_right, y_top, z_back)
        glVertex3f(x_left, y_top, z_back)
        glEnd()

        # Add roof and pillars between windows - Glossy dark blue
        glColor3f(0.0, 0.08, 0.3)  # Glossy dark blue for roof
        glBegin(GL_QUADS)
        
        # Main roof surface (above all windows)
        glVertex3f(-0.35, 0.58, 0.1)   # Windshield top left
        glVertex3f(0.35, 0.58, 0.1)    # Windshield top right
        glVertex3f(0.35, 0.58, -0.9)   # Rear window top right
        glVertex3f(-0.35, 0.58, -0.9)  # Rear window top left
        
        # A-pillars (between windshield and side windows)
        # Left A-pillar - connecting windshield to side window
        glVertex3f(-0.4, 0.25, 0.3)    # Windshield base left
        glVertex3f(-0.35, 0.58, 0.1)   # Windshield top left
        glVertex3f(-0.35, 0.58, 0.1)   # Side window top front
        glVertex3f(-0.5, 0.25, 0.4)    # Side window base front

        # Right A-pillar - connecting windshield to side window
        glVertex3f(0.4, 0.25, 0.3)     # Windshield base right
        glVertex3f(0.35, 0.58, 0.1)    # Windshield top right
        glVertex3f(0.35, 0.58, 0.1)    # Side window top front
        glVertex3f(0.5, 0.25, 0.4)     # Side window base front
        
        # B-pillars (not needed since side windows now extend full length)
        
        # C-pillars (between side windows and rear window)
        # Left C-pillar - connecting side window to rear window
        glVertex3f(-0.5, 0.25, -0.7)   # Side window rear base
        glVertex3f(-0.35, 0.58, -0.9)  # Side window rear top
        glVertex3f(-0.35, 0.58, -0.9)  # Rear window top left
        glVertex3f(-0.4, 0.25, -1.2)   # Rear window base left
        
        # Right C-pillar - connecting side window to rear window
        glVertex3f(0.5, 0.25, -0.7)    # Side window rear base
        glVertex3f(0.35, 0.58, -0.9)   # Side window rear top
        glVertex3f(0.35, 0.58, -0.9)   # Rear window top right
        glVertex3f(0.4, 0.25, -1.2)    # Rear window base right
        
        glEnd()
        
        # Disable reflection mapping after drawing
        self._disable_reflection_mapping()
        glDisable(GL_TEXTURE_2D)

        """Player car class with 6-speed transmission and realistic physics"""


    def __init__(self):
        super().__init__("car")
        # 68hp Golf-specific properties - very low power economy car
        self.max_speed = 0.9  # Set to 0.9 for 180 km/h top speed (0.9 × 200 = 180 km/h)
        self.base_acceleration = 0.0015  # Even slower than base Vehicle class for 68hp Golf
        self.turn_speed = 7.0  # Increased from 4.5 to 7.0 for lighter steering
        self.max_steering_angle = 60.0  # Increased from 45.0 to 60.0 degrees for more wheel rotation
        
        # 6-gear transmission system
        self.current_gear = 1
        self.rpm = 0.0
        self.max_rpm = 5500.0  # Lower redline for small 68hp economy engine
        self.idle_rpm = 800.0
        self.shift_up_rpm = 4800.0  # Shift early to maintain torque (reduced from 5500)
        self.shift_down_rpm = 1800.0  # Shift down earlier to stay in power band (reduced from 2000)
        self.auto_transmission = True  # Can be toggled
        
        # Gear shifting realism - power loss during shifts
        self.is_shifting = False
        self.shift_timer = 0.0
        self.shift_duration = 0.6  # 600ms shift time for more noticeable effect
        self.shift_speed_reduction = 0.1  # Reduce speed to 10% during shift (90% power loss)
        
        # Lighting system - moved to Vehicle base class
        
        # Gear ratios for 68hp Golf - optimized for low-speed shifting
        # Ratios designed to work with automatic shifting at lower speeds
        self.gear_ratios = {
            1: 2.2,   # 1st gear - good for 0-25 km/h acceleration
            2: 1.6,   # 2nd gear - optimized for 25-45 km/h range
            3: 1.2,   # 3rd gear - for 45-70 km/h cruising/acceleration
            4: 0.9,   # 4th gear - for 70-95 km/h highway speeds
            5: 0.7,   # 5th gear - for 95-120 km/h efficient cruising
            6: 0.5    # 6th gear - overdrive for 120+ km/h fuel economy
        }
        
        # Speed limits for each gear (as fraction of max_speed) - allow reaching shift points
        self.gear_speed_limits = {
            1: 0.16,  # 1st gear max speed ~29 km/h (allows reaching 25 km/h shift point)
            2: 0.28,  # 2nd gear max speed ~50 km/h (allows reaching 45 km/h shift point)
            3: 0.42,  # 3rd gear max speed ~76 km/h (allows reaching 70 km/h shift point)
            4: 0.58,  # 4th gear max speed ~104 km/h (allows reaching 95 km/h shift point)
            5: 0.72,  # 5th gear max speed ~130 km/h (allows reaching 120 km/h shift point)
            6: 1.0    # 6th gear max speed - full 180km/h
        }
        
    def update(self, keys, is_day_time=True):
        """Update car position, physics, and transmission"""
        # Store day/night state for tail lights
        self._last_is_day_time = is_day_time
        
        # Store previous position for collision detection
        self.prev_x = self.x
        self.prev_z = self.z
        
        # Handle input
        accelerating = False
        self.braking = False
        
        if keys[pygame.K_UP]:
            accelerating = True
            # Calculate acceleration based on current gear
            gear_ratio = self.gear_ratios[self.current_gear]
            acceleration = self.base_acceleration * gear_ratio
            
            # Apply gear shifting speed reduction
            if self.is_shifting:
                acceleration *= self.shift_speed_reduction
            
            # Apply speed limit for current gear
            gear_speed_limit = self.max_speed * self.gear_speed_limits[self.current_gear]
            
            if self.speed < gear_speed_limit:
                self.speed = min(self.speed + acceleration, gear_speed_limit)
                
        if keys[pygame.K_DOWN]:
            self.braking = True
            self.speed = max(self.speed - self.base_acceleration * 3.5, -self.max_speed/3)  # Increased from *2 to *3.5 for more effective braking
        
        # Manual headlight control
        if keys[pygame.K_l]:
            # Add a small delay to prevent rapid toggling
            if not hasattr(self, 'last_headlight_toggle'):
                self.last_headlight_toggle = 0
            current_time = pygame.time.get_ticks()
            if current_time - self.last_headlight_toggle > 300:  # 300ms delay
                self.headlights_on = not self.headlights_on
                self.last_headlight_toggle = current_time
                print(f"Headlights: {'ON' if self.headlights_on else 'OFF'}")
        
        # Auto headlights based on time of day
        if self.auto_headlights:
            if not is_day_time and not self.headlights_on:
                self.headlights_on = True
                print("Auto headlights ON (nighttime)")
            elif is_day_time and self.headlights_on and not hasattr(self, 'manual_headlights'):
                self.headlights_on = False
                print("Auto headlights OFF (daytime)")
        
        # Mark if headlights were manually controlled
        if keys[pygame.K_l]:
            self.manual_headlights = True
        elif self.auto_headlights and is_day_time:
            if hasattr(self, 'manual_headlights'):
                delattr(self, 'manual_headlights')
            
        # Manual gear shifting (if auto transmission is off)
        if not self.auto_transmission:
            if keys[pygame.K_q] and self.current_gear > 1:  # Shift down
                self.shift_down()
            if keys[pygame.K_e] and self.current_gear < 6:  # Shift up
                self.shift_up()
                
        # Toggle auto transmission
        if keys[pygame.K_t]:
            # Add a small delay to prevent rapid toggling
            if not hasattr(self, 'last_transmission_toggle'):
                self.last_transmission_toggle = 0
            current_time = pygame.time.get_ticks()
            if current_time - self.last_transmission_toggle > 500:  # 500ms delay
                self.auto_transmission = not self.auto_transmission
                self.last_transmission_toggle = current_time
                print(f"Transmission: {'Auto' if self.auto_transmission else 'Manual'}")
        
        # Handle turning and turn signals
        self.turning_left = keys[pygame.K_LEFT] and abs(self.speed) > 0.01
        self.turning_right = keys[pygame.K_RIGHT] and abs(self.speed) > 0.01
        
        # Apply speed reduction during turns for more realistic handling
        turning_speed_multiplier = 1.0
        if self.turning_left or self.turning_right:
            # Reduce speed during turns (0.7 = 30% speed reduction while turning)
            turning_speed_multiplier = 0.7
        
        if self.turning_left:
            # Add minimum turning factor so steering isn't too heavy at low speeds
            turn_factor = max(0.3, abs(self.speed) / self.max_speed)  # Use abs(speed) for consistent turning
            # Invert steering when driving backwards (negative speed)
            if self.speed >= 0:
                self.angle += self.turn_speed * turn_factor  # Normal forward steering
            else:
                self.angle -= self.turn_speed * turn_factor  # Inverted steering when reversing
            # Update steering angle for visual wheel rotation
            self.steering_angle = min(self.steering_angle + 5.0, self.max_steering_angle)  # Increased from 3.0 to 5.0
        elif self.turning_right:
            # Add minimum turning factor so steering isn't too heavy at low speeds
            turn_factor = max(0.3, abs(self.speed) / self.max_speed)  # Use abs(speed) for consistent turning
            # Invert steering when driving backwards (negative speed)
            if self.speed >= 0:
                self.angle -= self.turn_speed * turn_factor  # Normal forward steering
            else:
                self.angle += self.turn_speed * turn_factor  # Inverted steering when reversing
            # Update steering angle for visual wheel rotation
            self.steering_angle = max(self.steering_angle - 5.0, -self.max_steering_angle)  # Increased from 3.0 to 5.0
        else:
            # Return steering to center when not turning
            if self.steering_angle > 0:
                self.steering_angle = max(self.steering_angle - 3.0, 0.0)  # Increased return speed from 2.0 to 3.0
            elif self.steering_angle < 0:
                self.steering_angle = min(self.steering_angle + 3.0, 0.0)  # Increased return speed from 2.0 to 3.0
        
        # Calculate RPM based on speed and gear
        self.update_rpm()
        
        # Update gear shifting timer and process realistic shift delays
        self.update_gear_shifting(1.0/60.0)  # Assuming 60 FPS
        
        # Auto transmission logic
        if self.auto_transmission:
            self.auto_shift()
            
        # Apply friction
        if not accelerating and not self.braking:
            self.speed *= self.friction
        
        # Store previous position for collision detection
        prev_x = self.x
        prev_z = self.z
        
        # Update position with turning speed reduction applied
        effective_speed = self.speed * turning_speed_multiplier
        new_x = self.x + math.sin(math.radians(self.angle)) * effective_speed
        new_z = self.z + math.cos(math.radians(self.angle)) * effective_speed
        
        # Temporarily update position
        self.x = new_x
        self.z = new_z
    
    def check_building_collision(self, buildings):
        """Check if the car collides with any building"""
        car_size = 0.6  # Reduced from 0.8 to 0.6 for narrower car collision detection
        
        for building in buildings:
            if building.destroyed:
                continue
            
            # Building boundaries
            building_left = building.x - building.width/2
            building_right = building.x + building.width/2
            building_front = building.z - building.depth/2
            building_back = building.z + building.depth/2
            
            # Car boundaries
            car_left = self.x - car_size
            car_right = self.x + car_size
            car_front = self.z - car_size
            car_back = self.z + car_size
            
            # Check for overlap
            if (car_right > building_left and car_left < building_right and
                car_back > building_front and car_front < building_back):
                return True  # Collision detected
        
        return False  # No collision
    
    def check_npc_collision(self, npc_cars):
        """Check if the player car collides with any NPC car"""
        car_size = 0.6  # Same collision size as building collision
        
        for npc_car in npc_cars:
            # NPC car boundaries (same size as player car)
            npc_left = npc_car.x - car_size
            npc_right = npc_car.x + car_size
            npc_front = npc_car.z - car_size
            npc_back = npc_car.z + car_size
            
            # Player car boundaries
            player_left = self.x - car_size
            player_right = self.x + car_size
            player_front = self.z - car_size
            player_back = self.z + car_size
            
            # Check for overlap
            if (player_right > npc_left and player_left < npc_right and
                player_back > npc_front and player_front < npc_back):
                return True  # Collision detected
        
        return False  # No collision
    
    def resolve_collision(self, prev_x, prev_z):
        """Resolve collision by moving back to previous position and stopping"""
        self.x = prev_x
        self.z = prev_z
        self.speed = 0.0
    
    def update_rpm(self):
        """Calculate RPM based on current speed and gear"""
        if abs(self.speed) < 0.001:
            self.rpm = self.idle_rpm
        else:
            # Calculate RPM based on speed and gear ratio
            speed_ratio = abs(self.speed) / (self.max_speed * self.gear_speed_limits[self.current_gear])
            self.rpm = self.idle_rpm + (self.max_rpm - self.idle_rpm) * speed_ratio
            self.rpm = min(self.rpm, self.max_rpm)
    
    def auto_shift(self):
        """Simplified automatic transmission shifting logic for 68hp Golf"""
        current_speed_kmh = abs(self.speed) * 200.0  # Convert to km/h
        
        # Simplified shift logic - shift up at specific speeds regardless of other factors
        if self.current_gear == 1 and current_speed_kmh >= 25:
            #print(f"Auto shifting 1st->2nd at {current_speed_kmh:.1f} km/h")
            self.shift_up()
        elif self.current_gear == 2 and current_speed_kmh >= 45:
            #print(f"Auto shifting 2nd->3rd at {current_speed_kmh:.1f} km/h")
            self.shift_up()
        elif self.current_gear == 3 and current_speed_kmh >= 70:
            #print(f"Auto shifting 3rd->4th at {current_speed_kmh:.1f} km/h")
            self.shift_up()
        elif self.current_gear == 4 and current_speed_kmh >= 95:
            #print(f"Auto shifting 4th->5th at {current_speed_kmh:.1f} km/h")
            self.shift_up()
        elif self.current_gear == 5 and current_speed_kmh >= 120:
            #print(f"Auto shifting 5th->6th at {current_speed_kmh:.1f} km/h")
            self.shift_up()
        
        # Shift down when speed drops significantly
        elif self.current_gear == 6 and current_speed_kmh <= 100:
            #print(f"Auto shifting 6th->5th at {current_speed_kmh:.1f} km/h")
            self.shift_down()
        elif self.current_gear == 5 and current_speed_kmh <= 75:
            #print(f"Auto shifting 5th->4th at {current_speed_kmh:.1f} km/h")
            self.shift_down()
        elif self.current_gear == 4 and current_speed_kmh <= 55:
            #print(f"Auto shifting 4th->3rd at {current_speed_kmh:.1f} km/h")
            self.shift_down()
        elif self.current_gear == 3 and current_speed_kmh <= 35:
            #print(f"Auto shifting 3rd->2nd at {current_speed_kmh:.1f} km/h")
            self.shift_down()
        elif self.current_gear == 2 and current_speed_kmh <= 20:
            #print(f"Auto shifting 2nd->1st at {current_speed_kmh:.1f} km/h")
            self.shift_down()
    
    def shift_up(self):
        """Shift to higher gear with realistic power loss during shift"""
        if self.current_gear < 6 and not self.is_shifting:
            # Start the shifting process
            self.is_shifting = True
            self.shift_timer = self.shift_duration
            self.current_gear += 1
            #print(f"Shifting up to gear {self.current_gear} - power reduced during shift")
    
    def shift_down(self):
        """Shift to lower gear with realistic power loss during shift"""
        if self.current_gear > 1 and not self.is_shifting:
            # Start the shifting process
            self.is_shifting = True
            self.shift_timer = self.shift_duration
            self.current_gear -= 1
            #print(f"Shifting down to gear {self.current_gear} - power reduced during shift")
    
    def update_gear_shifting(self, dt):
        """Update gear shifting state and timer"""
        if self.is_shifting:
            self.shift_timer -= dt
            if self.shift_timer <= 0.0:
                self.is_shifting = False
                self.shift_timer = 0.0
                #print("Gear shift completed - full power restored")
    
    def get_gear_info(self):
        """Return current gear and RPM information"""
        return {
            'gear': self.current_gear,
            'rpm': int(self.rpm),
            'auto': self.auto_transmission,
            'speed': self.speed  # Use actual current speed
        }
        
    def setup_headlights(self):
        """Setup OpenGL spotlights for car headlights (only when headlights are on)"""
        if not self.headlights_on:
            # Disable headlights when they're off
            glDisable(GL_LIGHT1)
            glDisable(GL_LIGHT2)
            return
        
        # Calculate headlight positions in world coordinates
        cos_angle = math.cos(math.radians(self.angle))
        sin_angle = math.sin(math.radians(self.angle))
        
        # Position lights AT the car's headlight locations (not ahead of car)
        # Left headlight position - on the car's front bumper (adjusted for narrower car)
        left_light_x = self.x + (-0.3 * cos_angle - 1.2 * sin_angle)
        left_light_z = self.z + (0.3 * sin_angle - 1.2 * cos_angle)
        left_light_y = self.y + 0.3  # At headlight height
        
        # Right headlight position - on the car's front bumper (adjusted for narrower car)
        right_light_x = self.x + (0.3 * cos_angle - 1.2 * sin_angle)
        right_light_z = self.z + (-0.3 * sin_angle - 1.2 * cos_angle)
        right_light_y = self.y + 0.3  # At headlight height
        
        # Light direction (forward direction of car, slightly downward)
        direction_x = sin_angle
        direction_z = cos_angle
        direction_y = -0.1  # Slight downward angle to light the road
        
        # Configure left headlight (GL_LIGHT1) - Realistic car headlight
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [left_light_x, left_light_y, left_light_z, 1.0])
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, [direction_x, direction_y, direction_z])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [1.5, 1.5, 1.2, 1.0])  # Bright but realistic white light
        glLightfv(GL_LIGHT1, GL_SPECULAR, [1.0, 1.0, 0.8, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])  # Minimal ambient
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 30.0)  # Realistic 30 degree headlight cone
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 2.0)  # Focused beam like real headlights
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.1)  # Realistic attenuation
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.01)  # Realistic falloff
        
        # Configure right headlight (GL_LIGHT2) - Realistic car headlight
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [right_light_x, right_light_y, right_light_z, 1.0])
        glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, [direction_x, direction_y, direction_z])
        glLightfv(GL_LIGHT2, GL_DIFFUSE, [1.5, 1.5, 1.2, 1.0])  # Bright but realistic white light
        glLightfv(GL_LIGHT2, GL_SPECULAR, [1.0, 1.0, 0.8, 1.0])
        glLightfv(GL_LIGHT2, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])  # Minimal ambient
        glLightf(GL_LIGHT2, GL_SPOT_CUTOFF, 30.0)  # Realistic 30 degree headlight cone
        glLightf(GL_LIGHT2, GL_SPOT_EXPONENT, 2.0)  # Focused beam like real headlights
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT2, GL_LINEAR_ATTENUATION, 0.1)  # Realistic attenuation
        glLightf(GL_LIGHT2, GL_QUADRATIC_ATTENUATION, 0.01)  # Realistic falloff

    def disable_headlights(self):
        """Disable car headlights"""
        glDisable(GL_LIGHT1)
        glDisable(GL_LIGHT2)

    def setup_camera_and_lighting(self):
        """Set up the camera perspective and lighting for the car."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800 / 600, 0.1, 50.0)  # 45-degree field of view, aspect ratio, near and far planes
        glMatrixMode(GL_MODELVIEW)

        # Position the camera
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 5.0,  # Camera position
                  0.0, 0.0, 0.0,  # Look-at point
                  0.0, 1.0, 0.0)  # Up direction

        # Enable lighting and depth testing
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)

        # Set light properties
        light_position = [1.0, 1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # White diffuse light
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # White specular light
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])  # Dim ambient light

    def draw(self):
        """Draw the player car with headlights and detailed wheels"""
        # Setup headlights before drawing
        self.setup_headlights()

        glPushMatrix()
        glTranslatef(self.x, self.y + 0.15, self.z)  # Raise car above track
        glRotatef(self.angle, 0, 1, 0)
        self.draw_chassis()

        # Car body (VW Golf style hatchback) - Glossy dark blue
        # Set glossy material properties for the car body
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.1, 0.35, 1.0])  # Glossy dark blue
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.6, 0.7, 1.0, 1.0])  # Blue-tinted specular highlight
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)  # High shininess for glossy effect
        glColor3f(0.0, 0.1, 0.35)  # Glossy dark blue
        glBegin(GL_QUADS)
        glEnd()

        # Add car headlights (visual glow only when headlights are on)
        if self.headlights_on:
            glDisable(GL_LIGHTING)  # Disable lighting for headlight glow
            # BRIGHT WHITE HEADLIGHT CORES
            glColor3f(1.0, 1.0, 1.0)  # Pure bright white headlights
            # Left headlight core - BRIGHT WHITE (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.25)  # Adjusted position for narrower car
            glScalef(0.12, 0.12, 0.12)  # Slightly bigger core
            self.draw_wheel()
            glPopMatrix()
            # Right headlight core - BRIGHT WHITE (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.25)  # Adjusted position for narrower car
            glScalef(0.12, 0.12, 0.12)  # Slightly bigger core
            self.draw_wheel()
            glPopMatrix()
            # FIRST GLOW RING - Inner white glow
            glColor3f(0.9, 0.9, 1.0)  # Slightly blue-white inner glow
            # Left headlight - inner glow ring (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.3)  # Adjusted position
            glScalef(0.18, 0.18, 0.06)  # Ring around core
            self.draw_wheel()
            glPopMatrix()
            # Right headlight - inner glow ring (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.3)  # Adjusted position
            glScalef(0.18, 0.18, 0.06)  # Ring around core
            self.draw_wheel()
            glPopMatrix()
            # SECOND GLOW RING - Middle warm glow
            glColor3f(1.0, 1.0, 0.8)  # Warm white middle glow
            # Left headlight - middle glow ring (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.35)  # Adjusted position
            glScalef(0.25, 0.25, 0.04)  # Bigger ring
            self.draw_wheel()
            glPopMatrix()
            # Right headlight - middle glow ring (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.35)  # Adjusted position
            glScalef(0.25, 0.25, 0.04)  # Bigger ring
            self.draw_wheel()
            glPopMatrix()
            # THIRD GLOW RING - Outer soft glow
            glColor3f(1.0, 1.0, 0.6)  # Soft yellow outer glow
            # Left headlight - outer glow ring (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.4)  # Adjusted position
            glScalef(0.32, 0.32, 0.03)  # Largest ring
            self.draw_wheel()
            glPopMatrix()
            # Right headlight - outer glow ring (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.4)  # Adjusted position
            glScalef(0.32, 0.32, 0.03)  # Largest ring
            self.draw_wheel()
            glPopMatrix()
            glEnable(GL_LIGHTING)  # Re-enable lighting
        else:
            # Show dim headlight housings when lights are off (adjusted for narrower car)
            glDisable(GL_LIGHTING)
            glColor3f(0.3, 0.3, 0.3)  # Dark gray housings
            # Left headlight housing
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.25)  # Adjusted position for narrower car
            glScalef(0.1, 0.1, 0.1)
            self.draw_wheel()
            glPopMatrix()
            # Right headlight housing
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.25)  # Adjusted position for narrower car
            glScalef(0.1, 0.1, 0.1)
            self.draw_wheel()
            glPopMatrix()
            glEnable(GL_LIGHTING)

        # Add brake lights (red lights at back when braking) - only when moving forward
        if self.braking and self.speed >= 0:  # Only show brake lights when braking while moving forward
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 0.0, 0.0)  # Bright red brake lights
            # Left brake light - BIGGER (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(-0.35, 0.15, -1.25)  # Adjusted position for narrower car
            glScalef(0.24, 0.24, 0.24)  # Increased from 0.06 to 0.12
            self.draw_wheel()
            glPopMatrix()
            # Right brake light - BIGGER (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(0.35, 0.15, -1.25)  # Adjusted position for narrower car
            glScalef(0.24, 0.24, 0.24)  # Increased from 0.06 to 0.12
            self.draw_wheel()
            glPopMatrix()
            # Additional glow effect for left brake light (adjusted for narrower car)
            glColor3f(1.0, 0.2, 0.2)  # Brighter red glow
            glPushMatrix()
            glTranslatef(-0.35, 0.15, -1.3)  # Adjusted position
            glScalef(0.15, 0.15, 0.08)  # Even bigger glow
            self.draw_wheel()
            glPopMatrix()
            # Additional glow effect for right brake light (adjusted for narrower car)
            glPushMatrix()
            glTranslatef(0.35, 0.15, -1.3)  # Adjusted position
            glScalef(0.15, 0.15, 0.08)  # Even bigger glow
            self.draw_wheel()
            glPopMatrix()
            glEnable(GL_LIGHTING)

        # Add reverse lights (white lights when driving backwards) - adjusted for larger car
        if self.speed < -0.01:  # Car is moving backwards
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 1.0)  # Bright white reverse lights
            # Left reverse light (adjusted for larger car)
            glPushMatrix()
            glTranslatef(-0.3, 0.1, -1.28)  # Adjusted position for larger car
            glScalef(0.08, 0.08, 0.08)
            self.draw_wheel()
            glPopMatrix()
            # Right reverse light (adjusted for larger car)
            glPushMatrix()
            glTranslatef(0.3, 0.1, -1.28)  # Adjusted position for larger car
            glScalef(0.08, 0.08, 0.08)
            self.draw_wheel()
            glPopMatrix()
            # Additional glow effect for left reverse light (adjusted for larger car)
            glColor3f(0.9, 0.9, 1.0)  # Slightly blue-white glow
            glPushMatrix()
            glTranslatef(-0.3, 0.1, -1.32)  # Adjusted position
            glScalef(0.12, 0.12, 0.06)  # Glow effect
            self.draw_wheel()
            glPopMatrix()
            # Additional glow effect for right reverse light (adjusted for larger car)
            glPushMatrix()
            glTranslatef(0.3, 0.1, -1.32)  # Adjusted position
            glScalef(0.12, 0.12, 0.06)  # Glow effect
            self.draw_wheel()
            glPopMatrix()
            glEnable(GL_LIGHTING)

        # Add turn signals (amber/orange lights)
        glDisable(GL_LIGHTING)
        # Right turn signal (blink when turning left - angle increases)
        if self.turning_left:
            # Simple blinking effect using time
            import time
            blink = int(time.time() * 3) % 2  # Blink 3 times per second
            if blink:
                glColor3f(1.0, 0.5, 0.0)  # Orange/amber turn signal
                # Front right turn signal - BIGGER (adjusted for narrower car)
                glPushMatrix()
                glTranslatef(0.55, 0.2, 1.0)  # Adjusted position for narrower car
                glScalef(0.24, 0.24, 0.24)  # Increased from 0.05 to 0.12
                self.draw_wheel()
                glPopMatrix()
                # Rear right turn signal - at right edge of car
                glPushMatrix()
                glTranslatef(0.45, 0.15, -1.25)  # Further out towards right edge
                glScalef(0.18, 0.18, 0.18)  # Slightly smaller than brake light
                self.draw_wheel()
                glPopMatrix()
                # Additional glow effect for front right (adjusted for narrower car)
                glColor3f(1.0, 0.7, 0.2)  # Brighter orange glow
                glPushMatrix()
                glTranslatef(0.55, 0.2, 1.1)  # Adjusted position
                glScalef(0.15, 0.15, 0.08)  # Even bigger glow
                self.draw_wheel()
                glPopMatrix()
                # Additional glow effect for rear right - at right edge
                glPushMatrix()
                glTranslatef(0.45, 0.15, -1.3)  # Further out towards right edge
                glScalef(0.12, 0.12, 0.06)  # Glow effect
                self.draw_wheel()
                glPopMatrix()
        # Left turn signal (blink when turning right - angle decreases)
        if self.turning_right:
            import time
            blink = int(time.time() * 3) % 2  # Blink 3 times per second
            if blink:
                glColor3f(1.0, 0.5, 0.0)  # Orange/amber turn signal
                # Front left turn signal - BIGGER (adjusted for narrower car)
                glPushMatrix()
                glTranslatef(-0.55, 0.2, 1.0)  # Adjusted position for narrower car
                glScalef(0.12, 0.12, 0.12)  # Increased from 0.05 to 0.12
                self.draw_wheel()
                glPopMatrix()
                # Rear left turn signal - at left edge of car
                glPushMatrix()
                glTranslatef(-0.45, 0.15, -1.25)  # Further out towards left edge
                glScalef(0.18, 0.18, 0.18)  # Slightly smaller than brake light
                self.draw_wheel()
                glPopMatrix()
                # Additional glow effect for front left (adjusted for narrower car)
                glColor3f(1.0, 0.7, 0.2)  # Brighter orange glow
                glPushMatrix()
                glTranslatef(-0.55, 0.2, 1.1)  # Adjusted position
                glScalef(0.15, 0.15, 0.08)  # Even bigger glow
                self.draw_wheel()
                glPopMatrix()
                # Additional glow effect for rear left - at left edge
                glPushMatrix()
                glTranslatef(-0.45, 0.15, -1.3)  # Further out towards left edge
                glScalef(0.12, 0.12, 0.06)  # Glow effect
                self.draw_wheel()
                glPopMatrix()
                # Additional glow effect for rear left (adjusted for narrower car)
                # glPushMatrix()
                # glTranslatef(-0.55, 0.2, -1.1)  # Adjusted position
                # glScalef(0.15, 0.15, 0.08)  # Even bigger glow
                # self.draw_wheel()
                # glPopMatrix()
        glEnable(GL_LIGHTING)  # Re-enable lighting

        # Add glossy car windows (draw after lights but before wheels)
        self.draw_windows()
        
        # Add red tail lights (automatically on at night)
        if not hasattr(self, '_last_is_day_time'):
            self._last_is_day_time = True  # Default to day
        
        if not self._last_is_day_time:  # If it's night, show tail lights
            glDisable(GL_LIGHTING)  # Disable lighting for tail light glow
            glColor3f(1.0, 0.1, 0.1)  # Bright red for tail lights
            
            # Left tail light
            glPushMatrix()
            glTranslatef(-0.35, 0.15, -1.25)  # Left rear position
            glScalef(0.08, 0.08, 0.08)
            self.draw_wheel()
            glPopMatrix()
            
            # Right tail light
            glPushMatrix()
            glTranslatef(0.35, 0.15, -1.25)  # Right rear position
            glScalef(0.08, 0.08, 0.08)
            self.draw_wheel()
            glPopMatrix()
            
            # Add glow effect for tail lights
            glColor3f(0.8, 0.05, 0.05)  # Darker red glow
            
            # Left tail light glow
            glPushMatrix()
            glTranslatef(-0.35, 0.15, -1.28)
            glScalef(0.12, 0.12, 0.06)
            self.draw_wheel()
            glPopMatrix()
            
            # Right tail light glow
            glPushMatrix()
            glTranslatef(0.35, 0.15, -1.28)
            glScalef(0.12, 0.12, 0.06)
            self.draw_wheel()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)  # Re-enable lighting
        
        glColor3f(0.05, 0.05, 0.05)  # Very dark gray wheel color

        # Front left wheel (adjusted for narrower car)
        glPushMatrix()
        glTranslatef(-0.45, -0.1, 0.8)  # Adjusted position for narrower car
        glRotatef(self.steering_angle, 0, 1, 0)  # Rotate around Y-axis for steering
        self.draw_wheel()
        glPopMatrix()
        # Front right wheel (adjusted for narrower car)
        glPushMatrix()
        glTranslatef(0.45, -0.1, 0.8)  # Adjusted position for narrower car
        glRotatef(self.steering_angle, 0, 1, 0)  # Rotate around Y-axis for steering
        self.draw_wheel()
        glPopMatrix()
        # Rear left wheel (adjusted for narrower car)
        glPushMatrix()
        glTranslatef(-0.45, -0.1, -0.8)  # Adjusted position for narrower car
        self.draw_wheel()
        glPopMatrix()
        # Rear right wheel (adjusted for narrower car)
        glPushMatrix()
        glTranslatef(0.45, -0.1, -0.8)  # Adjusted position for narrower car
        self.draw_wheel()
        glPopMatrix()

        glPopMatrix()
        
    def draw_windows(self):
        """Draw glossy car windows with reflective effect"""
        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        # Configure for proper window rendering
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)  # Don't write to depth buffer for transparency
        glDisable(GL_LIGHTING)  # Disable lighting for window effect

        # Offset to avoid Z-fighting with car body
        offset = 0.012

        # Windshield (front window) - more in the middle like a VW Golf
        glColor4f(0.1, 0.3, 0.5, 0.6)
        glBegin(GL_QUADS)
        glVertex3f(-0.4, 0.25 + offset, 0.4 + offset)    # Bottom left (was 0.9)
        glVertex3f(0.4, 0.25 + offset, 0.4 + offset)     # Bottom right (was 0.9)
        glVertex3f(0.35, 0.58 + offset, 0.1 + offset)    # Top right (was 0.6)
        glVertex3f(-0.35, 0.58 + offset, 0.1 + offset)   # Top left (was 0.6)
        glEnd()

        # Rear window
        glColor4f(0.1, 0.3, 0.5, 0.6)
        glBegin(GL_QUADS)
        glVertex3f(-0.35, 0.58 + offset, -0.9 - offset)  # Top left
        glVertex3f(0.35, 0.58 + offset, -0.9 - offset)   # Top right
        glVertex3f(0.4, 0.25 + offset, -1.2 - offset)    # Bottom right
        glVertex3f(-0.4, 0.25 + offset, -1.2 - offset)   # Bottom left
        glEnd()

        # Left side window (angled to match roof)
        glColor4f(0.1, 0.3, 0.5, 0.6)
        glBegin(GL_QUADS)
        glVertex3f(-0.5 - offset, 0.25 + offset, 0.4)    # Front bottom
        glVertex3f(-0.5 - offset, 0.25 + offset, -0.7)   # Rear bottom
        glVertex3f(-0.35 - offset, 0.58 + offset, -0.9)  # Rear top (aligned with roof)
        glVertex3f(-0.35 - offset, 0.58 + offset, 0.1)   # Front top (aligned with roof)
        glEnd()

        # Right side window (angled to match roof)
        glColor4f(0.1, 0.3, 0.5, 0.6)
        glBegin(GL_QUADS)
        glVertex3f(0.5 + offset, 0.25 + offset, -0.7)    # Rear bottom
        glVertex3f(0.5 + offset, 0.25 + offset, 0.4)     # Front bottom
        glVertex3f(0.35 + offset, 0.58 + offset, 0.1)    # Front top (aligned with roof)
        glVertex3f(0.35 + offset, 0.58 + offset, -0.9)   # Rear top (aligned with roof)
        glEnd()

        glPopAttrib()
    
    def draw_wheel(self):
        """Draw a simple wheel as a small cube"""

        glBegin(GL_QUADS)
        
        size = 0.08
        # Front face
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        
        # Back face  
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, -size, -size)
        
        # Left face
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        
        # Right face
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)
        
        # Top face
        glVertex3f(-size, size, -size)
        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        
        # Bottom face
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        
        glEnd()
    
    def draw_box(self):
        """Draw a simple box shape for car body"""
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
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Bottom face
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        glEnd()


class Motorcycle(Vehicle):
    """Player motorcycle class with faster acceleration and different handling"""
    
    def __init__(self):
        super().__init__("motorcycle")
        # Motorcycle-specific properties
        self.max_speed = 0.9  # Set to 0.9 for 180 km/h top speed (0.9 × 200 = 180 km/h)
        self.base_acceleration = 0.006  # Further reduced from 0.01 to 0.006 for more realistic acceleration
        self.turn_speed = 8.5  # Increased from 6.0 to 8.5 for lighter steering
        self.max_steering_angle = 45.0  # Less wheel rotation than car
        self.friction = 0.98  # Better friction (less sliding)
        
        # Simplified 5-gear transmission system
        self.current_gear = 1
        self.rpm = 0.0
        self.max_rpm = 8000.0  # Higher RPM than car
        self.idle_rpm = 1000.0
        self.shift_up_rpm = 7000.0
        self.shift_down_rpm = 2500.0
        self.auto_transmission = True
        
        # Gear ratios for motorcycle (more realistic, less aggressive)
        self.gear_ratios = {
            1: 3.2,   # 1st gear - reduced from 4.0 for more realistic acceleration
            2: 2.2,   # 2nd gear - reduced from 2.5
            3: 1.6,   # 3rd gear - reduced from 1.8
            4: 1.2,   # 4th gear - reduced from 1.3
            5: 0.9    # 5th gear - reduced from 1.0 for smoother top speed
        }
        
        # Speed limits for each gear
        self.gear_speed_limits = {
            1: 0.20,  # 1st gear max speed
            2: 0.35,  # 2nd gear max speed
            3: 0.55,  # 3rd gear max speed
            4: 0.75,  # 4th gear max speed
            5: 1.0    # 5th gear max speed (full speed)
        }
    
    def update(self, keys, is_day_time=True):
        """Update motorcycle position, physics, and transmission"""
        # Store previous position for collision detection
        self.prev_x = self.x
        self.prev_z = self.z
        
        # Handle input
        accelerating = False
        self.braking = False
        
        if keys[pygame.K_UP]:
            accelerating = True
            # Calculate acceleration based on current gear
            gear_ratio = self.gear_ratios[self.current_gear]
            acceleration = self.base_acceleration * gear_ratio
            
            # Apply speed limit for current gear
            gear_speed_limit = self.max_speed * self.gear_speed_limits[self.current_gear]
            
            if self.speed < gear_speed_limit:
                self.speed = min(self.speed + acceleration, gear_speed_limit)
                
        if keys[pygame.K_DOWN]:
            self.braking = True
            self.speed = max(self.speed - self.base_acceleration * 4.0, -self.max_speed/4)  # Increased from *2.5 to *4.0 for more effective braking
        
        # Manual headlight control
        if keys[pygame.K_l]:
            if not hasattr(self, 'last_headlight_toggle'):
                self.last_headlight_toggle = 0
            current_time = pygame.time.get_ticks()
            if current_time - self.last_headlight_toggle > 300:
                self.headlights_on = not self.headlights_on
                self.last_headlight_toggle = current_time
                print(f"Motorcycle headlight: {'ON' if self.headlights_on else 'OFF'}")
        
        # Auto headlights based on time of day
        if self.auto_headlights:
            if not is_day_time and not self.headlights_on:
                self.headlights_on = True
                print("Auto motorcycle headlight ON (nighttime)")
            elif is_day_time and self.headlights_on and not hasattr(self, 'manual_headlights'):
                self.headlights_on = False
                print("Auto motorcycle headlight OFF (daytime)")
        
        # Mark if headlights were manually controlled
        if keys[pygame.K_l]:
            self.manual_headlights = True
        elif self.auto_headlights and is_day_time:
            if hasattr(self, 'manual_headlights'):
                delattr(self, 'manual_headlights')
            
        # Manual gear shifting (if auto transmission is off)
        if not self.auto_transmission:
            if keys[pygame.K_q] and self.current_gear > 1:
                self.shift_down()
            if keys[pygame.K_e] and self.current_gear < 5:  # 5 gears for motorcycle
                self.shift_up()
                
        # Toggle auto transmission
        if keys[pygame.K_t]:
            if not hasattr(self, 'last_transmission_toggle'):
                self.last_transmission_toggle = 0
            current_time = pygame.time.get_ticks()
            if current_time - self.last_transmission_toggle > 500:
                self.auto_transmission = not self.auto_transmission
                self.last_transmission_toggle = current_time
                print(f"Motorcycle transmission: {'Auto' if self.auto_transmission else 'Manual'}")
        
        # Handle turning and turn signals
        self.turning_left = keys[pygame.K_LEFT] and abs(self.speed) > 0.01
        self.turning_right = keys[pygame.K_RIGHT] and abs(self.speed) > 0.01
        
        # Apply speed reduction during turns for more realistic handling
        turning_speed_multiplier = 1.0
        if self.turning_left or self.turning_right:
            # Reduce speed during turns (0.7 = 30% speed reduction while turning)
            turning_speed_multiplier = 0.7
        
        if self.turning_left:
            self.angle += self.turn_speed * (self.speed / self.max_speed)
            self.steering_angle = min(self.steering_angle + 6.0, self.max_steering_angle)
        elif self.turning_right:
            self.angle -= self.turn_speed * (self.speed / self.max_speed)
            self.steering_angle = max(self.steering_angle - 6.0, -self.max_steering_angle)
        else:
            # Return steering to center when not turning
            if self.steering_angle > 0:
                self.steering_angle = max(self.steering_angle - 4.0, 0.0)
            elif self.steering_angle < 0:
                self.steering_angle = min(self.steering_angle + 4.0, 0.0)
        
        # Calculate RPM based on speed and gear
        self.update_rpm()
        
        # Auto transmission logic
        if self.auto_transmission:
            self.auto_shift()
            
        # Apply friction
        if not accelerating and not self.braking:
            self.speed *= self.friction
        
        # Store previous position for collision detection
        prev_x = self.x
        prev_z = self.z
        
        # Update position with turning speed reduction applied
        effective_speed = self.speed * turning_speed_multiplier
        new_x = self.x + math.sin(math.radians(self.angle)) * effective_speed
        new_z = self.z + math.cos(math.radians(self.angle)) * effective_speed
        
        # Temporarily update position
        self.x = new_x
        self.z = new_z
    
    def check_building_collision(self, buildings):
        """Check if the motorcycle collides with any building (smaller collision box)"""
        motorcycle_size = 0.3  # Much smaller than car
        
        for building in buildings:
            if building.destroyed:
                continue
            
            # Building boundaries
            building_left = building.x - building.width/2
            building_right = building.x + building.width/2
            building_front = building.z - building.depth/2
            building_back = building.z + building.depth/2
            
            # Motorcycle boundaries
            motorcycle_left = self.x - motorcycle_size
            motorcycle_right = self.x + motorcycle_size
            motorcycle_front = self.z - motorcycle_size
            motorcycle_back = self.z + motorcycle_size
            
            # Check for overlap
            if (motorcycle_right > building_left and motorcycle_left < building_right and
                motorcycle_back > building_front and motorcycle_front < building_back):
                return True  # Collision detected
        
        return False  # No collision
    
    def check_npc_collision(self, npc_cars):
        """Check if motorcycle collides with any NPC cars"""
        if not npc_cars:
            return False
        
        # Define motorcycle boundaries with 0.6 unit collision detection
        motorcycle_size = 0.6
        motorcycle_left = self.x - motorcycle_size
        motorcycle_right = self.x + motorcycle_size
        motorcycle_front = self.z - motorcycle_size
        motorcycle_back = self.z + motorcycle_size
        
        for npc_car in npc_cars:
            # Define NPC car boundaries with 0.6 unit collision detection
            npc_size = 0.6
            npc_left = npc_car.x - npc_size
            npc_right = npc_car.x + npc_size
            npc_front = npc_car.z - npc_size
            npc_back = npc_car.z + npc_size
            
            # Check for overlap
            if (motorcycle_right > npc_left and motorcycle_left < npc_right and
                motorcycle_back > npc_front and motorcycle_front < npc_back):
                return True  # Collision detected
        
        return False  # No collision
    
    def resolve_collision(self, prev_x, prev_z):
        """Resolve collision by moving back to previous position and stopping"""
        self.x = prev_x
        self.z = prev_z
        self.speed = 0.0
    
    def update_rpm(self):
        """Calculate RPM based on current speed and gear"""
        if abs(self.speed) < 0.001:
            self.rpm = self.idle_rpm
        else:
            speed_ratio = abs(self.speed) / (self.max_speed * self.gear_speed_limits[self.current_gear])
            self.rpm = self.idle_rpm + (self.max_rpm - self.idle_rpm) * speed_ratio
            self.rpm = min(self.rpm, self.max_rpm)
    
    def auto_shift(self):
        """Automatic transmission shifting logic"""
        if self.rpm >= self.shift_up_rpm and self.current_gear < 5:  # 5 gears
            self.shift_up()
        elif self.rpm <= self.shift_down_rpm and self.current_gear > 1 and abs(self.speed) > 0.05:
            self.shift_down()
    
    def shift_up(self):
        """Shift to higher gear"""
        if self.current_gear < 5:  # 5 gears for motorcycle
            self.current_gear += 1
    
    def shift_down(self):
        """Shift to lower gear"""
        if self.current_gear > 1:
            self.current_gear -= 1
    
    def get_gear_info(self):
        """Return current gear and RPM information"""
        return {
            'gear': self.current_gear,
            'rpm': int(self.rpm),
            'auto': self.auto_transmission,
            'speed': self.speed
        }
    
    def setup_headlights(self):
        """Setup OpenGL spotlight for motorcycle headlight (single headlight)"""
        if not self.headlights_on:
            glDisable(GL_LIGHT1)
            glDisable(GL_LIGHT2)
            return
        
        # Calculate headlight position in world coordinates
        cos_angle = math.cos(math.radians(self.angle))
        sin_angle = math.sin(math.radians(self.angle))
        
        # Single centered headlight position
        light_x = self.x + (-1.0 * sin_angle)
        light_z = self.z + (-1.0 * cos_angle)
        light_y = self.y + 0.25  # Slightly higher than car headlights
        
        # Light direction (forward direction of motorcycle, slightly downward)
        direction_x = sin_angle
        direction_z = cos_angle
        direction_y = -0.1
        
        # Configure single headlight (GL_LIGHT1) - Brighter than car
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [light_x, light_y, light_z, 1.0])
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, [direction_x, direction_y, direction_z])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [1.8, 1.8, 1.5, 1.0])  # Brighter than car
        glLightfv(GL_LIGHT1, GL_SPECULAR, [1.2, 1.2, 1.0, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 35.0)  # Wider beam than car
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 1.5)  # Less focused beam
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.08)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.008)
        
        # Disable second light since motorcycles typically have one headlight
        glDisable(GL_LIGHT2)

    def disable_headlights(self):
        """Disable motorcycle headlight"""
        glDisable(GL_LIGHT1)
        glDisable(GL_LIGHT2)

    def draw(self):
        """Draw the motorcycle with single headlight and narrow profile"""
        # Setup headlight before drawing
        self.setup_headlights()
        
        glPushMatrix()
        glTranslatef(self.x, self.y + 0.1, self.z)  # Lower than car
        glRotatef(self.angle, 0, 1, 0)
        
        # Motorcycle body (narrower and longer than car)
        glColor3f(0.0, 0.0, 1.0)  # Blue motorcycle
        glBegin(GL_QUADS)
        
        # Front face - Motorcycle is 0.4 units wide (±0.2) and 2.0 units long (±1.0)
        glVertex3f(-0.2, 0.0, 1.0)
        glVertex3f(0.2, 0.0, 1.0)
        glVertex3f(0.2, 0.4, 1.0)
        glVertex3f(-0.2, 0.4, 1.0)
        
        # Back face
        glVertex3f(-0.2, 0.0, -1.0)
        glVertex3f(-0.2, 0.4, -1.0)
        glVertex3f(0.2, 0.4, -1.0)
        glVertex3f(0.2, 0.0, -1.0)
        
        # Left face
        glVertex3f(-0.2, 0.0, -1.0)
        glVertex3f(-0.2, 0.0, 1.0)
        glVertex3f(-0.2, 0.4, 1.0)
        glVertex3f(-0.2, 0.4, -1.0)
        
        # Right face
        glVertex3f(0.2, 0.0, -1.0)
        glVertex3f(0.2, 0.4, -1.0)
        glVertex3f(0.2, 0.4, 1.0)
        glVertex3f(0.2, 0.0, 1.0)
        
        # Top face
        glVertex3f(-0.2, 0.4, -1.0)
        glVertex3f(-0.2, 0.4, 1.0)
        glVertex3f(0.2, 0.4, 1.0)
        glVertex3f(0.2, 0.4, -1.0)
        
        # Bottom face
        glVertex3f(-0.2, 0.0, -1.0)
        glVertex3f(0.2, 0.0, -1.0)
        glVertex3f(0.2, 0.0, 1.0)
        glVertex3f(-0.2, 0.0, 1.0)
        
        glEnd()
        
        # Add motorcycle windscreen (smaller than car)
        if self.headlights_on:
            glDisable(GL_LIGHTING)
            
            # BRIGHT WHITE HEADLIGHT CORE
            glColor3f(1.0, 1.0, 1.0)  # Pure bright white
            
            # Single centered headlight core
            glPushMatrix()
            glTranslatef(0.0, 0.15, 1.05)  # Centered
            glScalef(0.15, 0.15, 0.15)  # Bigger than car headlights
            self.draw_sphere()
            glPopMatrix()
            
            # INNER GLOW RING
            glColor3f(0.9, 0.9, 1.0)  # Blue-white inner glow
            glPushMatrix()
            glTranslatef(0.0, 0.15, 1.1)
            glScalef(0.22, 0.22, 0.08)
            self.draw_sphere()
            glPopMatrix()
            
            # OUTER GLOW RING
            glColor3f(1.0, 1.0, 0.8)  # Warm white outer glow
            glPushMatrix()
            glTranslatef(0.0, 0.15, 1.15)
            glScalef(0.3, 0.3, 0.06)
            self.draw_sphere()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)
        else:
            # Show dim headlight housing when light is off
            glDisable(GL_LIGHTING)
            glColor3f(0.3, 0.3, 0.3)  # Dark gray housing
            
            glPushMatrix()
            glTranslatef(0.0, 0.15, 1.05)
            glScalef(0.12, 0.12, 0.12)
            self.draw_sphere()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)
        
        # Add brake light (single centered red light at back when braking) - only when moving forward
        if self.braking and self.speed >= 0:  # Only show brake light when braking while moving forward
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 0.0, 0.0)  # Bright red brake light
            
            # Single centered brake light
            glPushMatrix()
            glTranslatef(0.0, 0.15, -1.05)
            glScalef(0.2, 0.2, 0.2)
            self.draw_sphere()
            glPopMatrix()
            
            # Glow effect
            glColor3f(1.0, 0.2, 0.2)
            glPushMatrix()
            glTranslatef(0.0, 0.15, -1.1)
            glScalef(0.12, 0.12, 0.06)
            self.draw_sphere()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)
        
        # Add reverse light (white light when driving backwards)
        if self.speed < -0.01:
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 1.0)  # Bright white reverse light
            
            glPushMatrix()
            glTranslatef(0.0, 0.08, -1.08)
            glScalef(0.06, 0.06, 0.06)
            self.draw_sphere()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)
        
        # Add turn signals (amber/orange lights on sides)
        glDisable(GL_LIGHTING)
        
        # Right turn signal (blink when turning left)
        if self.turning_left:
            import time
            blink = int(time.time() * 3) % 2
            if blink:
                glColor3f(1.0, 0.5, 0.0)  # Orange turn signal
                
                # Front right turn signal
                glPushMatrix()
                glTranslatef(0.25, 0.2, 0.8)
                glScalef(0.08, 0.08, 0.08)
                self.draw_sphere()
                glPopMatrix()
                
                # Rear right turn signal
                glPushMatrix()
                glTranslatef(0.25, 0.2, -0.8)
                glScalef(0.08, 0.08, 0.08)
                self.draw_sphere()
                glPopMatrix()
        
        # Left turn signal (blink when turning right)
        if self.turning_right:
            import time
            blink = int(time.time() * 3) % 2
            if blink:
                glColor3f(1.0, 0.5, 0.0)  # Orange turn signal
                
                # Front left turn signal
                glPushMatrix()
                glTranslatef(-0.25, 0.2, 0.8)
                glScalef(0.08, 0.08, 0.08)
                self.draw_sphere()
                glPopMatrix()
                
                # Rear left turn signal
                glPushMatrix()
                glTranslatef(-0.25, 0.2, -0.8)
                glScalef(0.08, 0.08, 0.08)
               
                self.draw_sphere()
                glPopMatrix()
        
        glEnable(GL_LIGHTING)
        
        # Add motorcycle windscreen (draw after lights but before wheels)
        self.draw_windscreen()
        
        glColor3f(0.1, 0.1, 0.1)  # Reset to wheel color
        
        # Front wheel (centered, steered)
        glPushMatrix()
        glTranslatef(0.0, -0.05, 0.6)
        glRotatef(self.steering_angle, 0, 1, 0)  # Steering
        glScalef(1.2, 1.2, 0.4)  # Thinner motorcycle wheel
        self.draw_wheel()
        glPopMatrix()
        
        # Back wheel (centered)
        glPushMatrix()
        glTranslatef(0.0, -0.05, -0.6)
        glScalef(1.2, 1.2, 0.6)  # Wider rear wheel
        self.draw_wheel()
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_windscreen(self):
        """Draw motorcycle windscreen with glossy effect"""
        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Configure for proper windscreen rendering
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)  # Don't write to depth buffer for transparency
        glDisable(GL_LIGHTING)  # Disable lighting for windscreen effect
        
        # Small motorcycle windscreen - more visible
        glColor4f(0.1, 0.3, 0.5, 0.7)  # More opaque blue tint
        glBegin(GL_QUADS)
        glVertex3f(-0.18, 0.18, 0.9)    # Bottom left (moved forward)
        glVertex3f(0.18, 0.18, 0.9)     # Bottom right
        glVertex3f(0.15, 0.48, 0.75)    # Top right (angled back)
        glVertex3f(-0.15, 0.48, 0.75)   # Top left (angled back)
        glEnd()
        
        # Restore OpenGL state
        glPopAttrib()
    
    def draw_sphere(self):
        """Draw a simple sphere for motorcycle lights"""
        # Use wheel drawing as a simple substitute for sphere
        self.draw_wheel()
    
    def draw_wheel(self):
        """Draw a simple wheel as a small cube"""
        glBegin(GL_QUADS)
        
        size = 0.08
        # Front face
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)

        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        
        # Back face  
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, -size, -size)
        
        # Left face
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        
        # Right face
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)
        
        # Top face
        glVertex3f(-size, size, -size)
        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        
        # Bottom face
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        
        glEnd()


class NPCCar(Car):
    """NPC car class with AI behavior and traffic light awareness"""
    
    def __init__(self, x, z, direction, speed=0.3):
        super().__init__()
        self.x = x
        self.z = z
        self.direction = direction  # "north", "south", "east", "west"
        self.target_speed = speed
        self.speed = speed
        self.stopped_for_light = False
        self.stop_distance = 4.0  # Distance to stop before traffic light
        
        # Lane positioning for right-side driving
        self.lane_offset = self.get_lane_offset()
        
        # Set initial angle based on direction
        if direction == "north":
            self.angle = 0.0
        elif direction == "south":
            self.angle = 180.0
        elif direction == "east":
            self.angle = 270.0
        elif direction == "west":
            self.angle = 90.0
            
        # Different colors for NPC cars
        self.color_r = random.uniform(0.3, 0.9)
        self.color_g = random.uniform(0.3, 0.9)
        self.color_b = random.uniform(0.3, 0.9)
        
        # Auto headlights for night time
        self.headlights_on = False
        self.auto_headlights = True
        
        # Acceleration delay system for realistic traffic flow
        self.acceleration_delay = 0.0  # Current delay timer
        self.max_acceleration_delay = 1.5  # Maximum delay after light turns green
        self.is_waiting_to_accelerate = False  # Flag for delay state
        
    def get_lane_offset(self):
        """Get the proper lane offset for right-side driving"""
        # Right-side driving means:
        # - East-bound traffic drives in the south lane (negative Z)
        # - West-bound traffic drives in the north lane (positive Z)  
        # - North-bound traffic drives in the west lane (negative X)
        # - South-bound traffic drives in the east lane (positive X)
        
        lane_center_offset = 1.0  # Distance from center line to lane center
        
        if self.direction == "east":
            return (0, -lane_center_offset)  # Drive in south lane
        elif self.direction == "west":
            return (0, lane_center_offset)   # Drive in north lane
        elif self.direction == "north":
            return (-lane_center_offset, 0)  # Drive in west lane
        elif self.direction == "south":
            return (lane_center_offset, 0)   # Drive in east lane
        
        return (0, 0)  # Default to center
        
    def update_ai(self, traffic_lights, is_day_time=True, other_cars=[]):
        """Update NPC car AI behavior with lane discipline, headlight control, and collision avoidance"""
        # Auto headlights based on time of day
        if self.auto_headlights:
            if not is_day_time and not self.headlights_on:
                self.headlights_on = True
            elif is_day_time and self.headlights_on:
                self.headlights_on = False
        
        # Check if we need to stop for traffic lights
        should_stop_for_light = self.check_traffic_light(traffic_lights)
        
        # Check if we need to stop for other cars
        should_stop_for_car = self.check_car_collision(other_cars)
        
        # Combine both stopping conditions
        should_stop = should_stop_for_light or should_stop_for_car
        
        if should_stop and not self.stopped_for_light:
            # Gradually slow down
            self.speed = max(0.0, self.speed - 0.015)
            if self.speed <= 0.01:
                self.stopped_for_light = True
                self.speed = 0.0
                # Reset acceleration delay when stopping
                self.acceleration_delay = 0.0
                self.is_waiting_to_accelerate = False
        elif not should_stop and self.stopped_for_light:
            # Traffic light turned green or obstacle cleared
            if not self.is_waiting_to_accelerate:
                # Start the delay timer only if we were actually stopped
                if self.speed <= 0.05:  # Only apply delay if car was truly stopped
                    self.is_waiting_to_accelerate = True
                    # Calculate delay based on position in traffic queue
                    delay = self.calculate_acceleration_delay(other_cars)
                    self.acceleration_delay = delay
                else:
                    # Car was already moving, resume immediately
                    self.stopped_for_light = False
            
        # Handle acceleration delay countdown
        if self.is_waiting_to_accelerate:
            self.acceleration_delay -= 1.0/60.0  # Assume 60 FPS
            if self.acceleration_delay <= 0.0:
                # Delay finished, resume normal driving
                self.stopped_for_light = False
                self.is_waiting_to_accelerate = False
            
        # Accelerate back to target speed if not stopping and not waiting
        if not should_stop and not self.is_waiting_to_accelerate and self.speed < self.target_speed:
            self.speed = min(self.target_speed, self.speed + 0.008)
        
        # Get lane center position
        lane_x_offset, lane_z_offset = self.lane_offset
        
        # Gentle lane correction - steer towards proper lane center
        lane_correction_strength = 0.02
        
        if self.direction in ["east", "west"]:
            # For horizontal movement, correct Z position
            target_z = lane_z_offset
            z_error = target_z - (self.z % 60)  # Use modulo to handle multiple track sections
            if abs(z_error) > 30:  # Handle wrap-around
                z_error = z_error - 60 if z_error > 0 else z_error + 60
            # Apply gentle correction to angle
            if abs(z_error) > 0.1:
                self.angle += z_error * lane_correction_strength
        else:
            # For vertical movement, correct X position  
            target_x = lane_x_offset
            x_error = target_x - (self.x % 60)  # Use modulo to handle multiple track sections
            if abs(x_error) > 30:  # Handle wrap-around
                x_error = x_error - 60 if x_error > 0 else x_error + 60
            # Apply gentle correction to angle
            if abs(x_error) > 0.1:
                self.angle += x_error * lane_correction_strength
            
        # Update position
        self.x += math.sin(math.radians(self.angle)) * self.speed
        self.z += math.cos(math.radians(self.angle)) * self.speed
        
        # Remove car if it goes too far off screen
        if abs(self.x) > 60 or abs(self.z) > 60:
            return False  # Signal to remove this car
        return True
        
    def calculate_acceleration_delay(self, other_cars):
        """Calculate how long this car should wait before accelerating after light turns green"""
        base_delay = random.uniform(0.3, 0.7)  # Random base reaction time
        
        # Count cars in front of us in the same lane
        cars_in_front = 0
        for other_car in other_cars:
            # Only count cars in same direction and lane
            if (self.direction == other_car.direction and 
                self.are_cars_in_same_lane(other_car) and 
                self.is_car_in_front(other_car)):
                
                # Only count if they're relatively close (in the same traffic queue)
                distance = math.sqrt((self.x - other_car.x)**2 + (self.z - other_car.z)**2)
                if distance < 8.0:  # Within reasonable queue distance
                    cars_in_front += 1
        
        # Each car in front adds delay (simulating chain reaction)
        queue_delay = cars_in_front * random.uniform(0.4, 0.8)
        
        # Add some randomness to make it feel natural
        random_factor = random.uniform(0.8, 1.2)
        
        total_delay = (base_delay + queue_delay) * random_factor
        
        # Cap the maximum delay to keep traffic moving
        return min(total_delay, 3.0)
        
    def check_car_collision(self, other_cars):
        """Check if car should stop to avoid collision with other cars"""
        collision_distance = 3.5  # Minimum safe distance between cars
        
        for other_car in other_cars:
            # Only check cars moving in the same direction
            if self.direction != other_car.direction:
                continue
                
            # Check if cars are in the same lane (approximately)
            if not self.are_cars_in_same_lane(other_car):
                continue
                
            # Calculate distance between cars
            distance = math.sqrt((self.x - other_car.x)**2 + (self.z - other_car.z)**2)
            
            if distance < collision_distance:
                # Check if the other car is in front of us based on direction
                if self.is_car_in_front(other_car):
                    # If the car in front is stopped or moving slower, we should stop
                    if other_car.speed < self.speed * 0.9:  # 90% threshold for more responsive stopping
                        return True
                        
        return False
    
    def are_cars_in_same_lane(self, other_car):
        """Check if two cars are in the same lane"""
        lane_tolerance = 1.5  # Allow some tolerance for lane positioning
        
        if self.direction in ["east", "west"]:
            # For horizontal movement, check Z position (lane position)
            return abs(self.z - other_car.z) < lane_tolerance
        else:
            # For vertical movement, check X position (lane position)
            return abs(self.x - other_car.x) < lane_tolerance
    
    def is_car_in_front(self, other_car):
        """Check if another car is in front of this car based on direction"""
        dx = other_car.x - self.x
        dz = other_car.z - self.z
        
        if self.direction == "east":
            return dx > 0  # Other car is further east
        elif self.direction == "west":
            return dx < 0  # Other car is further west
        elif self.direction == "north":
            return dz > 0  # Other car is further north
        elif self.direction == "south":
            return dz < 0  # Other car is further south
            
        return False
    
    def check_traffic_light(self, traffic_lights):
        """Check if car should stop for traffic light"""
        for light in traffic_lights:
            # Only check lights that control this car's direction
            # FIXED: Swapped the direction mapping - east/west cars check vertical lights
            light_controls_me = False
            
            if self.direction in ["east", "west"] and light.direction == "vertical":
                light_controls_me = True
            elif self.direction in ["north", "south"] and light.direction == "horizontal":
                light_controls_me = True
                
            if not light_controls_me:
                continue
                
            # Calculate distance to intersection center
            distance_to_light = math.sqrt((self.x - 0)**2 + (self.z - 0)**2)
            
            # Check if we're approaching the intersection and our light is red or yellow
            if distance_to_light < self.stop_distance:
                if light.state in ["red", "yellow", "red-yellow"]:
                    return True
                    
        return False
        
    def setup_headlights(self, light_id_offset=0):
        """Setup OpenGL spotlights for NPC car headlights"""
        # Use different light IDs for NPC cars to avoid conflicts
        left_light_id = GL_LIGHT3 + light_id_offset
        right_light_id = GL_LIGHT4 + light_id_offset
        
        # Only use lights 3-7 to avoid conflicts with player car (1-2) and ambient (0)
        if left_light_id > GL_LIGHT7 or right_light_id > GL_LIGHT7:
            return  # Skip if we've run out of available lights
        
        # Calculate headlight positions in world coordinates
        cos_angle = math.cos(math.radians(self.angle))
        sin_angle = math.sin(math.radians(self.angle))
        
        # Left headlight position (scaled for smaller NPC car)
        left_light_x = self.x + (-0.15 * cos_angle - 0.5 * sin_angle)
        left_light_z = self.z + (0.15 * sin_angle - 0.5 * cos_angle)
        left_light_y = self.y + 0.2
        
        # Right headlight position (scaled for smaller NPC car)
        right_light_x = self.x + (0.15 * cos_angle - 0.5 * sin_angle)
        right_light_z = self.z + (-0.15 * sin_angle - 0.5 * cos_angle)
        right_light_y = self.y + 0.2
        
        # Light direction (forward direction of car)
        direction_x = sin_angle
        direction_z = cos_angle
        
        # Configure left headlight (dimmer than player car)
        glEnable(left_light_id)
        glLightfv(left_light_id, GL_POSITION, [left_light_x, left_light_y, left_light_z, 1.0])
        glLightfv(left_light_id, GL_SPOT_DIRECTION, [direction_x, -0.1, direction_z])
        glLightfv(left_light_id, GL_DIFFUSE, [0.4, 0.4, 0.35, 1.0])  # Dimmer warm white light
        glLightfv(left_light_id, GL_SPECULAR, [0.4, 0.4, 0.35, 1.0])
        glLightfv(left_light_id, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
        glLightf(left_light_id, GL_SPOT_CUTOFF, 30.0)  # 30 degree cone
        glLightf(left_light_id, GL_SPOT_EXPONENT, 2.0)  # Focused beam
        glLightf(left_light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(left_light_id, GL_LINEAR_ATTENUATION, 0.1)
        glLightf(left_light_id, GL_QUADRATIC_ATTENUATION, 0.02)
        
        # Configure right headlight (dimmer than player car)
        glEnable(right_light_id)
        glLightfv(right_light_id, GL_POSITION, [right_light_x, right_light_y, right_light_z, 1.0])
        glLightfv(right_light_id, GL_SPOT_DIRECTION, [direction_x, -0.1, direction_z])
        glLightfv(right_light_id, GL_DIFFUSE, [0.4, 0.4, 0.35, 1.0])  # Dimmer warm white light
        glLightfv(right_light_id, GL_SPECULAR, [0.4, 0.4, 0.35, 1.0])
        glLightfv(right_light_id, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
        glLightf(right_light_id, GL_SPOT_CUTOFF, 30.0)  # 30 degree cone
        glLightf(right_light_id, GL_SPOT_EXPONENT, 2.0)  # Focused beam
        glLightf(right_light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(right_light_id, GL_LINEAR_ATTENUATION, 0.1)
        glLightf(right_light_id, GL_QUADRATIC_ATTENUATION, 0.02)

    def draw(self):
        """Draw the NPC car with different color and headlights"""
        # Setup headlights before drawing (use car index as offset)
        if hasattr(self, 'car_index'):
            self.setup_headlights(self.car_index * 2)
        
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angle, 0, 1, 0)
        
        # Car body with NPC color
        glColor3f(self.color_r, self.color_g, self.color_b)
        glPushMatrix()
        glScalef(1.0, 1.0, 1.0)  # Same size as player car
        self.draw_box()
        glPopMatrix()
        
        # Add NPC car headlights (visible when on)
        if self.headlights_on:
            glDisable(GL_LIGHTING)  # Disable lighting for headlight glow
            
            # BRIGHT WHITE HEADLIGHT CORES
            glColor3f(0.9, 0.9, 0.8)  # Slightly dimmer than player car
            
            # Left headlight core
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.0)  # Adjusted for full-size car
            glScalef(0.08, 0.08, 0.08)
            self.draw_wheel()
            glPopMatrix()
            
            # Right headlight core
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.0)  # Adjusted for full-size car
            glScalef(0.08, 0.08, 0.08)
            self.draw_wheel()
            glPopMatrix()
            
            # GLOW RINGS
            glColor3f(0.8, 0.8, 0.7)  # Warm glow
            
            # Left headlight glow
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.05)  # Adjusted for full-size car
            glScalef(0.12, 0.12, 0.06)
            self.draw_wheel()
            glPopMatrix()
            
            # Right headlight glow
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.05)  # Adjusted for full-size car
            glScalef(0.12, 0.12, 0.06)
            self.draw_wheel()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)  # Re-enable lighting
        else:
            # Show dim headlight housings when lights are off
            glDisable(GL_LIGHTING)
            glColor3f(0.2, 0.2, 0.2)  # Dark gray housings
            
            # Left headlight housing
            glPushMatrix()
            glTranslatef(-0.3, 0.15, 1.0)  # Adjusted for full-size car
            glScalef(0.06, 0.06, 0.06)
            self.draw_wheel()
            glPopMatrix()
            
            # Right headlight housing
            glPushMatrix()
            glTranslatef(0.3, 0.15, 1.0)  # Adjusted for full-size car
            glScalef(0.06, 0.06, 0.06)
            self.draw_wheel()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)
        
        # Add tail lights (automatically on at night - when headlights are on)
        if self.headlights_on:
            # Show tail lights at night
            glDisable(GL_LIGHTING)
            glColor3f(0.8, 0.1, 0.1)  # Dim red for tail lights
            
            # Left tail light
            glPushMatrix()
            glTranslatef(-0.35, 0.15, -1.0)  # Adjusted for full-size car
            glScalef(0.05, 0.05, 0.05)
            self.draw_wheel()
            glPopMatrix()
            
            # Right tail light
            glPushMatrix()
            glTranslatef(0.35, 0.15, -1.0)  # Adjusted for full-size car
            glScalef(0.05, 0.05, 0.05)
            self.draw_wheel()
            glPopMatrix()
            
            glEnable(GL_LIGHTING)
        
        # Draw wheels (very dark gray)
        glColor3f(0.05, 0.05, 0.05)
        
        # Front left wheel
        glPushMatrix()
        glTranslatef(-0.45, -0.1, 0.8)  # Adjusted for full-size car
        glScalef(1.0, 1.0, 1.0)  # Same size as player car wheels
        self.draw_wheel()
        glPopMatrix()
        
        # Front right wheel
        glPushMatrix()
        glTranslatef(0.45, -0.1, 0.8)  # Adjusted for full-size car
        glScalef(1.0, 1.0, 1.0)  # Same size as player car wheels
        self.draw_wheel()
        glPopMatrix()
        
        # Back left wheel
        glPushMatrix()
        glTranslatef(-0.45, -0.1, -0.8)  # Adjusted for full-size car
        glScalef(1.0, 1.0, 1.0)  # Same size as player car wheels
        self.draw_wheel()
        glPopMatrix()
        
        # Back right wheel
        glPushMatrix()
        glTranslatef(0.45, -0.1, -0.8)  # Adjusted for full-size car
        glScalef(1.0, 1.0, 1.0)  # Same size as player car wheels
        self.draw_wheel()
        glPopMatrix()
        
        glPopMatrix()