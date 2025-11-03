"""
Game module for 3D Car Racing Game
Contains the main Game class with rendering, HUD, camera, and game loop logic.
"""
import math
import random
import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from classes.car import Car, NPCCar, Motorcycle
from classes.track import Track


class Game:
    """Main game engine class handling rendering, input, and game logic"""
    
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("3D Car Racing Game")
        
        # Initialize font for HUD display
        pygame.font.init()
        
        # Sound system disabled - removed all sound initialization
        
        try:
            # Try to use Consolas monospace font (Windows) - smaller sizes

            self.font_large = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 30)     # Consolas monospace (reduced from 48)
            self.font_medium = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 20)    # Consolas monospace (reduced from 36)
            self.font_small = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 16)     # Consolas monospace (reduced from 24)
        except:
            try:
                # Fallback to Courier New (also monospace)
                self.font_large = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 30)
                self.font_medium = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 20)
                self.font_small = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 16)
            except:
                # Final fallback to system monospace font
                self.font_large = pygame.font.SysFont("monospacebold", 30)
                self.font_medium = pygame.font.SysFont("monospacebold", 20)
                self.font_small = pygame.font.SysFont("monospacebold", 16)

        # OpenGL setup - enable lighting for night scene
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue night sky
        
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)  # Main ambient light
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up ambient lighting (reduced for better headlight visibility)
        ambient_light = [0.05, 0.05, 0.1, 1.0]  # Much darker ambient light
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
        
        # Reduced diffuse light for better headlight contrast
        diffuse_light = [0.1, 0.1, 0.15, 1.0]  # Much darker diffuse light
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
        
        # Set up perspective
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Game objects - Vehicle selection system
        self.vehicle_selection = True  # Start in vehicle selection mode
        self.selected_vehicle = "car"  # Default selection
        self.vehicle = None  # Will be created after selection
        
        # Game stats
        self.score = 0

        # Create multiple tracks for larger area 3x3
        self.tracks = []
        
        # Center track
        track_center = Track(0, 0)
        self.tracks.append(track_center)

        # Top track
        track_top = Track(0, track_center.arm_length * 2)
        self.tracks.append(track_top)

        # Bottom track  
        track_bottom = Track(0, -track_center.arm_length * 2)
        self.tracks.append(track_bottom)

        # Left track
        track_left = Track(-track_center.arm_length * 2, 0)
        self.tracks.append(track_left)

        # Right track
        track_right = Track(track_center.arm_length * 2, 0)
        self.tracks.append(track_right)

        # Top-left track
        track_top_left = Track(-track_center.arm_length * 2, track_center.arm_length * 2)
        self.tracks.append(track_top_left)

        # Top-right track
        track_top_right = Track(track_center.arm_length * 2, track_center.arm_length * 2)
        self.tracks.append(track_top_right)

        # Bottom-left track
        track_bottom_left = Track(-track_center.arm_length * 2, -track_center.arm_length * 2)
        self.tracks.append(track_bottom_left)

        # Bottom-right track
        track_bottom_right = Track(track_center.arm_length * 2, -track_center.arm_length * 2)
        self.tracks.append(track_bottom_right)

        # NPC cars - DISABLED
        self.npc_cars = []
        self.npc_spawn_timer = 0.0
        self.npc_spawn_interval = 3.0  # Spawn a new car every 3 seconds
        self.max_npc_cars = 8  # Maximum number of NPC cars
        
        # Spawn initial NPC cars - DISABLED
        # self.spawn_initial_npc_cars()

        # Camera
        self.camera_distance = 8.0
        self.camera_height = 3.0
        
        # Camera lag system for smooth following
        self.camera_lag_factor = 0.08  # Lower = more lag, Higher = more responsive
        self.camera_angle_lag = 0.1    # Camera angle lag factor
        self.camera_current_angle = 270.0  # Current camera angle (with lag) - match initial vehicle angle
        
        # Calculate initial camera position (default position before vehicle selection)
        initial_x, initial_z, initial_angle = 10.0, 0.0, 270.0
        self.camera_x = initial_x - self.camera_distance * math.sin(math.radians(initial_angle))
        self.camera_z = initial_z - self.camera_distance * math.cos(math.radians(initial_angle))
        self.camera_y = self.camera_height
        
        # HUD settings
        self.show_hud = True  # Toggle HUD display
        self.show_text_info = True  # Toggle text-based info (speed, gear, RPM)
        
        # Help menu system
        self.show_help_menu = False
        self.help_page = 0  # Current help page (0-based)
        self.max_help_pages = 3  # Total number of help pages
        
        # Timing for traffic lights and NPC cars
        self.last_time = pygame.time.get_ticks() / 1000.0
        
        # Day/Night cycle system with smooth transitions
        self.day_night_cycle_duration = 120.0  # 120 seconds for full day/night cycle
        self.game_start_time = pygame.time.get_ticks() / 1000.0
        self.time_of_day = "night"  # Start at night
        self.sky_color = [0.1, 0.1, 0.2]  # Current sky color
        self.ambient_light = [0.05, 0.05, 0.1]  # Current ambient light
        self.diffuse_light = [0.1, 0.1, 0.15]  # Current diffuse light
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Delta time tracking for traffic lights
        self.last_time = pygame.time.get_ticks() / 1000.0
    



    
    def reset_game(self):
        """Reset the game state"""
        if self.vehicle:
            self.vehicle.x = 10.0
            self.vehicle.z = 0.0
            self.vehicle.angle = 270.0  # Reset to 270 degrees rotation
            self.vehicle.speed = 0.0
            self.vehicle.steering_angle = 0.0  # Reset steering angle
            self.vehicle.current_gear = 1  # Reset to first gear
            self.vehicle.rpm = self.vehicle.idle_rpm  # Reset RPM
        self.score = 0
        
        # Reset camera lag system
        self.camera_current_angle = 270.0  # Reset to match vehicle's new starting angle
        if self.vehicle:
            self.camera_x = self.vehicle.x - self.camera_distance * math.sin(math.radians(self.vehicle.angle))
            self.camera_z = self.vehicle.z - self.camera_distance * math.cos(math.radians(self.vehicle.angle))
        self.camera_y = self.camera_height
        
    def update_camera(self):
        """Update camera position with lag system for smooth following"""
        if not self.vehicle:  # Skip if no vehicle selected yet
            return
            
        # Calculate target camera position based on vehicle position and angle
        target_camera_x = self.vehicle.x - self.camera_distance * math.sin(math.radians(self.vehicle.angle))
        target_camera_z = self.vehicle.z - self.camera_distance * math.cos(math.radians(self.vehicle.angle))
        
        # Apply lag to camera angle for smoother turning
        angle_diff = self.vehicle.angle - self.camera_current_angle
        
        # Handle angle wrapping (when crossing 0/360 boundary)
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
            
        self.camera_current_angle += angle_diff * self.camera_angle_lag
        
        # Normalize camera angle
        if self.camera_current_angle > 360:
            self.camera_current_angle -= 360
        elif self.camera_current_angle < 0:
            self.camera_current_angle += 360
        
        # Apply lag to camera position for smooth following
        self.camera_x += (target_camera_x - self.camera_x) * self.camera_lag_factor
        self.camera_z += (target_camera_z - self.camera_z) * self.camera_lag_factor
        self.camera_y = self.camera_height  # Keep height constant
        
        # Look at vehicle (if one is selected)
        if self.vehicle:
            look_x = self.vehicle.x
            look_y = self.vehicle.y + 0.65  # Vehicle is raised, so look higher
            look_z = self.vehicle.z
        else:
            # Default look position during vehicle selection
            look_x, look_y, look_z = 10.0, 0.65, 0.0
        
        # Set up the camera
        glLoadIdentity()
        gluLookAt(self.camera_x, self.camera_y, self.camera_z,
                  look_x, look_y, look_z,
                  0, 1, 0)
        
    def handle_events(self):
        """Handle pygame events and keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.vehicle_selection:
                    # Handle vehicle selection input
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        # Toggle between car and motorcycle
                        self.selected_vehicle = "motorcycle" if self.selected_vehicle == "car" else "car"
                        print(f"Selected: {self.selected_vehicle.upper()}")
                        # Reset instruction flag so it prints the new selection
                        if hasattr(self, 'selection_instructions_shown'):
                            delattr(self, 'selection_instructions_shown')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Confirm selection
                        self.confirm_vehicle_selection()
                elif event.key == pygame.K_r:
                    # Reset car position and game state
                    print("Resetting game...")
                    self.reset_game()
                elif event.key == pygame.K_h:
                    # Toggle help menu
                    self.show_help_menu = not self.show_help_menu
                    if self.show_help_menu:
                        self.help_page = 0  # Reset to first page
                elif event.key == pygame.K_LEFT and self.show_help_menu:
                    # Previous help page
                    self.help_page = max(0, self.help_page - 1)
                elif event.key == pygame.K_RIGHT and self.show_help_menu:
                    # Next help page
                    self.help_page = min(self.max_help_pages - 1, self.help_page + 1)
                elif event.key == pygame.K_1:
                    # Increase camera lag (more delay)
                    self.camera_lag_factor = max(0.02, self.camera_lag_factor - 0.01)
                    self.camera_angle_lag = max(0.02, self.camera_angle_lag - 0.01)
                    print(f"Camera lag increased - Position: {self.camera_lag_factor:.3f}, Angle: {self.camera_angle_lag:.3f}")
                elif event.key == pygame.K_2:
                    # Decrease camera lag (less delay, more responsive)
                    self.camera_lag_factor = min(0.3, self.camera_lag_factor + 0.01)
                    self.camera_angle_lag = min(0.3, self.camera_angle_lag + 0.01)
                    print(f"Camera lag decreased - Position: {self.camera_lag_factor:.3f}, Angle: {self.camera_angle_lag:.3f}")
                elif event.key == pygame.K_3:
                    # Reset camera lag to default
                    self.camera_lag_factor = 0.08
                    self.camera_angle_lag = 0.1
                    print("Camera lag reset to default")
                elif event.key == pygame.K_c:
                    # Show camera info
                    print(f"Camera Lag - Position: {self.camera_lag_factor:.3f}, Angle: {self.camera_angle_lag:.3f}")
                elif event.key == pygame.K_g:
                    # Show gear info
                    self.show_gear_info()
                elif event.key == pygame.K_TAB:
                    # Toggle HUD display
                    self.show_hud = not self.show_hud
                    print(f"HUD: {'ON' if self.show_hud else 'OFF'}")
                elif event.key == pygame.K_i:
                    # Toggle text-based info display
                    self.show_text_info = not self.show_text_info
                    print(f"Text Info: {'ON' if self.show_text_info else 'OFF'}")
    
    def show_help(self):
        """Display current game stats"""
        if not self.vehicle:
            print("\n=== VEHICLE SELECTION MODE ===")
            print("Select your vehicle first!")
            return
            
        gear_info = self.vehicle.get_gear_info()
        print("\n=== GAME STATUS ===")
        print(f"Score: {self.score}")
        print(f"Vehicle: {self.vehicle.vehicle_type.upper()}")
        print(f"Position: ({self.vehicle.x:.1f}, {self.vehicle.z:.1f})")
        print(f"Speed: {self.vehicle.speed:.2f}")
        print(f"Current Gear: {gear_info['gear']}")
        print(f"RPM: {gear_info['rpm']}")
        print(f"Transmission: {'Auto' if gear_info['auto'] else 'Manual'}")
        print("==================\n")
    
    def draw_help_menu(self):
        """Draw the help menu overlay"""
        # Create help surface with semi-transparent background
        help_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 180))  # Semi-transparent black background (180/255 opacity)
        
        # Title
        title = "GAME HELP MENU"
        title_surface = self.font_large.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect()
        help_surface.blit(title_surface, (self.width//2 - title_rect.width//2, 50))
        
        # Page indicator
        page_info = f"Page {self.help_page + 1} of {self.max_help_pages}"
        page_surface = self.font_small.render(page_info, True, (255, 255, 255))
        page_rect = page_surface.get_rect()
        help_surface.blit(page_surface, (self.width//2 - page_rect.width//2, 100))
        
        # Help content based on current page
        if self.help_page == 0:
            self.draw_help_page_controls(help_surface)
        elif self.help_page == 1:
            self.draw_help_page_features(help_surface)
        elif self.help_page == 2:
            self.draw_help_page_advanced(help_surface)
        
        # Navigation instructions
        nav_text = "← Previous Page  |  → Next Page  |  H to Close"
        nav_surface = self.font_small.render(nav_text, True, (255, 255, 255))
        nav_rect = nav_surface.get_rect()
        help_surface.blit(nav_surface, (self.width//2 - nav_rect.width//2, self.height - 50))
        
        # Display the help surface
        self.display_surface_as_texture(help_surface)
    
    def draw_help_page_controls(self, surface):
        """Draw the controls help page"""
        y_offset = 150
        line_height = 20
        
        controls = [
            "BASIC CONTROLS:",
            "",
            "↑ Arrow Key     - Accelerate",
            "↓ Arrow Key     - Brake / Reverse",
            "← Arrow Key     - Turn Left (when moving)",
            "→ Arrow Key     - Turn Right (when moving)",
            "",
            "TRANSMISSION:",
            "",
            "T               - Toggle Auto/Manual transmission",
            "Q               - Shift Down (Manual mode)",
            "E               - Shift Up (Manual mode)",
            "",
            "LIGHTING:",
            "",
            "L               - Toggle Headlights",
            "                  (Auto on/off at night/day)",
            "",
            "GENERAL:",
            "",
            "H               - Toggle this Help Menu",
            "TAB             - Toggle HUD display",
            "R               - Reset game position",
            "ESC             - Exit game"
        ]
        
        for i, line in enumerate(controls):
            if line == "":
                continue
            color = (255, 255, 255) if line.endswith(":") else (255, 255, 255)
            font = self.font_medium if line.endswith(":") else self.font_small
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (100, y_offset + i * line_height))
    
    def draw_help_page_features(self, surface):
        """Draw the features help page"""
        y_offset = 150
        line_height = 20
        
        features = [
            "GAME FEATURES:",
            "",
            "• 6-Speed Transmission System",
            "  - Each gear has different acceleration/speed",
            "  - Lower gears: High acceleration, low speed",
            "  - Higher gears: Lower acceleration, high speed",
            "",
            "• Realistic Night Scene",
            "  - Dark environment with street lighting",
            "  - Traffic lights at intersections",
            "  - Car headlights for visibility",
            "",
            "• AI Traffic System",
            "  - NPC cars disabled",
            "  - Peaceful solo driving experience",
            "",
            "",
            "• Physics & Steering",
            "  - Front wheels rotate when turning",
            "  - Realistic car physics",
            "  - Building collision detection"
        ]
        
        for i, line in enumerate(features):
            if line == "":
                continue
            color = (255, 255, 255) if line.endswith(":") else (255, 255, 255)
            font = self.font_medium if line.endswith(":") else self.font_small
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (100, y_offset + i * line_height))
    
    def draw_help_page_advanced(self, surface):
        """Draw the advanced features help page"""
        y_offset = 150
        line_height = 20

        advanced = [
            "ADVANCED FEATURES:",
            "",
            "CAMERA CONTROLS:",
            "",
            "1               - Increase camera lag (more delay)",
            "2               - Decrease camera lag (less delay)",
            "3               - Reset camera lag to default",
            "C               - Show camera settings",
            "",
            "INFORMATION COMMANDS:",
            "",
            "G               - Show gear information",
            "",
            "HUD DISPLAY:",
            "",
            "• Speed in KM/H (bottom right)",
            "• Current gear and transmission mode",
            "• RPM indicator (red when high)",
            "• Instructions when stationary",
            "",
            "TRAFFIC LIGHT SYSTEM:",
            "",
            "• Green (5s) → Yellow (2s) → Red (5s)",
            "• Perpendicular directions alternate"
        ]
        
        for i, line in enumerate(advanced):
            if line == "":
                continue
            color = (255, 255, 255) if line.endswith(":") else (255, 255, 255)
            font = self.font_medium if line.endswith(":") else self.font_small
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (100, y_offset + i * line_height))
    
    def show_gear_info(self):
        """Display current gear and transmission info"""
        gear_info = self.car.get_gear_info()
        print(f"Gear: {gear_info['gear']}/6 | RPM: {gear_info['rpm']} | Mode: {'Auto' if gear_info['auto'] else 'Manual'} | Speed: {gear_info['speed']:.3f}")
    
    def speed_to_kmh(self, speed):
        """Convert game speed units to km/h for display"""
        # Assuming game speed of 1.0 = 100 km/h (adjust this multiplier as needed)
        return abs(speed) * 200.0
    
    def draw_hud(self):
        """Draw the HUD overlay with speedometer and gear info using surface blitting"""
        if not self.vehicle:  # Skip if no vehicle selected yet
            return
            
        # Create a temporary surface for the HUD - no transparency issues
        hud_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 0))  # Fully transparent background
        
        # Get current vehicle info
        speed_kmh = self.speed_to_kmh(self.vehicle.speed)
        gear_info = self.vehicle.get_gear_info()
        
        # Draw visual speedometer
        self.draw_speedometer(hud_surface, speed_kmh)
        
        # Draw visual RPM meter
        self.draw_rpm_meter(hud_surface, gear_info['rpm'])
        
        # Text-based speed, gear, and RPM - top left, very small (only if enabled)
        if self.show_text_info:
            # Create a very small font for the top-left text info
            try:
                font_tiny = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 12)
            except:
                try:
                    font_tiny = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 12)
                except:
                    font_tiny = pygame.font.SysFont("monospacebold", 12)
            
            # Speed text - top left
            speed_kmh_int = int(speed_kmh)
            speed_text = f"Speed: {speed_kmh_int} km/h"
            speed_surface = font_tiny.render(speed_text, True, (255, 255, 255))
            text_rect = speed_surface.get_rect()
            text_rect.topleft = (10, 10)
            pygame.draw.rect(hud_surface, (0, 0, 0), text_rect.inflate(6, 3))
            hud_surface.blit(speed_surface, (10, 10))
            
            # Vehicle type and gear indicator - top left, below speed
            vehicle_type = self.vehicle.vehicle_type.upper()
            gear_text = f"{vehicle_type} Gear: {gear_info['gear']}"
            transmission_mode = "A" if gear_info['auto'] else "M"
            gear_mode_text = f"{gear_text} ({transmission_mode})"
            gear_surface = font_tiny.render(gear_mode_text, True, (255, 255, 255))
            gear_rect = gear_surface.get_rect()
            gear_rect.topleft = (10, 28)
            pygame.draw.rect(hud_surface, (0, 0, 0), gear_rect.inflate(6, 3))
            hud_surface.blit(gear_surface, (10, 28))
            
            # RPM indicator - top left, below gear
            rpm_text = f"RPM: {gear_info['rpm']}"
            rpm_color = (255, 150, 150) if gear_info['rpm'] > 5000 else (255, 255, 255)
            rpm_surface = font_tiny.render(rpm_text, True, rpm_color)
            rpm_rect = rpm_surface.get_rect()
            rpm_rect.topleft = (10, 46)
            pygame.draw.rect(hud_surface, (0, 0, 0), rpm_rect.inflate(6, 3))
            hud_surface.blit(rpm_surface, (10, 46))
            
            # Headlight status - top left, below RPM
            headlight_text = f"Lights: {'ON' if self.vehicle.headlights_on else 'OFF'}"
            headlight_color = (255, 255, 0) if self.vehicle.headlights_on else (100, 100, 100)
            headlight_surface = font_tiny.render(headlight_text, True, headlight_color)
            headlight_rect = headlight_surface.get_rect()
            headlight_rect.topleft = (10, 64)
            pygame.draw.rect(hud_surface, (0, 0, 0), headlight_rect.inflate(6, 3))
            hud_surface.blit(headlight_surface, (10, 64))
        
        # Instructions - top center with solid background (HIDDEN)
        # if speed_kmh < 5:  # Show instructions when stationary
        #     instruction_text = "UP: Accelerate | T: Auto/Manual | TAB: Toggle HUD"
        #     instruction_surface = self.font_small.render(instruction_text, True, (255, 255, 255))
        #     text_rect = instruction_surface.get_rect()
        #     text_rect.center = (self.width//2, 20)
        #     # Add solid black background rectangle for instructions
        #     pygame.draw.rect(hud_surface, (0, 0, 0), text_rect.inflate(20,20))
        #     # Draw main text
        #     hud_surface.blit(instruction_surface, (self.width//2 - text_rect.width//2, 20))
        
        # Convert the HUD surface to OpenGL texture and display it
        self.display_surface_as_texture(hud_surface)
    
    def draw_speedometer(self, surface, speed_kmh):
        """Draw a visual speedometer gauge"""
        # Speedometer position and size
        center_x = self.width - 90
        center_y = self.height - 90
        radius = 80
        
        # Draw speedometer background circle with opaque background
        pygame.draw.circle(surface, (60, 60, 60), (center_x, center_y), radius + 5, 0)  # Solid outer background
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), radius, 3)
        pygame.draw.circle(surface, (20, 20, 20), (center_x, center_y), radius - 5, 0)
        
        # Speedometer range (0-200 km/h) - rotated by -90 degrees
        max_speed = 200
        start_angle = 135  # Start at top-left (225 - 90 = 135)
        end_angle = 225    # End at bottom-left (315 - 90 = 225)
        total_angle = 270  # 3/4 of the ring (270 degrees)
        
        # Draw speed markings
        for speed in range(0, max_speed + 1, 40):  # Changed from 20 to 40 for more spacing
            angle_deg = start_angle + (speed / max_speed) * total_angle  # Changed back to addition for proper upward movement
            angle_rad = math.radians(angle_deg)
            
            # Outer point for major markings
            outer_x = center_x + (radius - 10) * math.cos(angle_rad)
            outer_y = center_y + (radius - 10) * math.sin(angle_rad)
            
            # Inner point for major markings
            inner_x = center_x + (radius - 25) * math.cos(angle_rad)
            inner_y = center_y + (radius - 25) * math.sin(angle_rad)
            
            # Draw major speed markings
            pygame.draw.line(surface, (255, 255, 255), (outer_x, outer_y), (inner_x, inner_y), 2)
            
            # Draw speed numbers
            if speed % 40 == 0:  # Show numbers every 40 km/h (now matches major markings)
                text_x = center_x + (radius - 35) * math.cos(angle_rad)
                text_y = center_y + (radius - 35) * math.sin(angle_rad)
                speed_text = str(speed)
                # Use smaller font for speedometer numbers
                small_font = pygame.font.Font(None, 16)  # Smaller font size
                text_surface = small_font.render(speed_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(text_x, text_y))
                surface.blit(text_surface, text_rect)
        
        # Draw minor markings (every 20 km/h)
        for speed in range(0, max_speed + 1, 20):  # Changed from 10 to 20
            if speed % 40 != 0:  # Skip major markings (now every 40 instead of 20)
                angle_deg = start_angle + (speed / max_speed) * total_angle  # Changed back to addition for proper upward movement
                angle_rad = math.radians(angle_deg)
                
                outer_x = center_x + (radius - 10) * math.cos(angle_rad)
                outer_y = center_y + (radius - 10) * math.sin(angle_rad)
                inner_x = center_x + (radius - 18) * math.cos(angle_rad)
                inner_y = center_y + (radius - 18) * math.sin(angle_rad)
                
                pygame.draw.line(surface, (150, 150, 150), (outer_x, outer_y), (inner_x, inner_y), 1)
        
        # Draw speed needle
        current_speed = min(speed_kmh, max_speed)
        needle_angle_deg = start_angle + (current_speed / max_speed) * total_angle  # Changed back to addition for proper upward movement
        needle_angle_rad = math.radians(needle_angle_deg)
        
        # Needle end point
        needle_x = center_x + (radius - 15) * math.cos(needle_angle_rad)
        needle_y = center_y + (radius - 15) * math.sin(needle_angle_rad)
        
        # Needle color based on speed
        # if current_speed < 60:
        #     needle_color = (0, 255, 0)      # Green for low speed
        # elif current_speed < 120:
        #     needle_color = (255, 255, 0)    # Yellow for medium speed
        # else:
        #     needle_color = (255, 0, 0)      # Red for high speed

        needle_color = (255,180,100)
        
        # Draw needle
        pygame.draw.line(surface, needle_color, (center_x, center_y), (needle_x, needle_y), 4)
        
        # Draw center circle
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 5, 0)
        
        # Draw "KM/H" label
        small_font = pygame.font.Font(None, 16)  # Smaller font for label
        label_surface = small_font.render("KM/H", True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=(center_x, center_y + 40))
        surface.blit(label_surface, label_rect)
    
    def draw_rpm_meter(self, surface, current_rpm):
        """Draw a visual RPM meter gauge"""
        # RPM meter position and size (positioned to the left of speedometer)
        center_x = self.width - 250
        center_y = self.height - 90
        radius = 60  # Smaller than speedometer
        
        # Draw RPM meter background circle with opaque background
        pygame.draw.circle(surface, (50, 50, 50), (center_x, center_y), radius + 5, 0)  # Solid outer background
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), radius, 3)
        pygame.draw.circle(surface, (20, 20, 20), (center_x, center_y), radius - 5, 0)
        
        # RPM range (0-10000 RPM) - rotated by -90 degrees like speedometer
        max_rpm = 10000
        start_angle = 135  # Start at top-left
        end_angle = 225    # End at bottom-left
        total_angle = 270  # 3/4 of the ring (270 degrees)
        
        # Draw RPM markings
        for rpm in range(0, max_rpm + 1, 2000):  # Major markings every 2000 RPM
            angle_deg = start_angle + (rpm / max_rpm) * total_angle
            angle_rad = math.radians(angle_deg)
            
            # Outer point for major markings
            outer_x = center_x + (radius - 8) * math.cos(angle_rad)
            outer_y = center_y + (radius - 8) * math.sin(angle_rad)
            
            # Inner point for major markings
            inner_x = center_x + (radius - 18) * math.cos(angle_rad)
            inner_y = center_y + (radius - 18) * math.sin(angle_rad)
            
            # Draw major RPM markings
            pygame.draw.line(surface, (255, 255, 255), (outer_x, outer_y), (inner_x, inner_y), 2)
            
            # Draw RPM numbers
            if rpm % 2000 == 0:  # Show numbers every 2000 RPM
                text_x = center_x + (radius - 25) * math.cos(angle_rad)
                text_y = center_y + (radius - 25) * math.sin(angle_rad)
                rpm_text = str(rpm // 1000)  # Show as 0, 2, 4, 6, 8, 10
                # Use smaller font for RPM numbers
                small_font = pygame.font.Font(None, 14)  # Even smaller font
                text_surface = small_font.render(rpm_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(text_x, text_y))
                surface.blit(text_surface, text_rect)
        
        # Draw minor markings (every 1000 RPM)
        for rpm in range(0, max_rpm + 1, 1000):
            if rpm % 2000 != 0:  # Skip major markings
                angle_deg = start_angle + (rpm / max_rpm) * total_angle
                angle_rad = math.radians(angle_deg)
                
                outer_x = center_x + (radius - 8) * math.cos(angle_rad)
                outer_y = center_y + (radius - 8) * math.sin(angle_rad)
                inner_x = center_x + (radius - 14) * math.cos(angle_rad)
                inner_y = center_y + (radius - 14) * math.sin(angle_rad)
                
                pygame.draw.line(surface, (150, 150, 150), (outer_x, outer_y), (inner_x, inner_y), 1)
        
        # Draw RPM needle
        safe_rpm = min(current_rpm, max_rpm)
        needle_angle_deg = start_angle + (safe_rpm / max_rpm) * total_angle
        needle_angle_rad = math.radians(needle_angle_deg)
        
        # Needle end point
        needle_x = center_x + (radius - 12) * math.cos(needle_angle_rad)
        needle_y = center_y + (radius - 12) * math.sin(needle_angle_rad)
        
        # Needle color based on RPM (like a real tachometer)
        # if safe_rpm < 5000:
        #     needle_color = (0, 255, 0)      # Green for low RPM
        # elif safe_rpm < 8000:
        #     needle_color = (255, 255, 0)    # Yellow for medium RPM
        # else:
        #     needle_color = (255, 0, 0)      # Red for high RPM (redline)

        needle_color = (255, 255, 255)  # Default to white

        # Draw needle
        pygame.draw.line(surface, needle_color, (center_x, center_y), (needle_x, needle_y), 3)
        
        # Draw center circle
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 4, 0)
        
        # Draw "RPM x1000" label
        small_font = pygame.font.Font(None, 12)  # Very small font for label
        label_surface = small_font.render("RPM x1000", True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=(center_x, center_y + 30))
        surface.blit(label_surface, label_rect)
    
    def display_surface_as_texture(self, surface):
        """Display a pygame surface as an OpenGL texture overlay"""
        # Save current OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Switch to 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth testing for overlay
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)  # Disable lighting for text to render pure white
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        
        # Convert surface to texture
        texture_data = pygame.image.tostring(surface, "RGBA", True)
        
        # Generate and bind texture
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), 
                     surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Draw the texture as a quad covering the whole screen
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(self.width, 0)
        glTexCoord2f(1, 1); glVertex2f(self.width, self.height)
        glTexCoord2f(0, 1); glVertex2f(0, self.height)
        glEnd()
        
        # Clean up
        glDeleteTextures([texture_id])
        
        # Restore OpenGL state
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()
    
    def spawn_initial_npc_cars(self):
        """Spawn initial NPC cars on the roads"""
        spawn_positions = [
            # Horizontal roads (east-west)
            (-15, 2, "east"),
            (-10, -2, "west"),
            (10, 2, "east"),
            (15, -2, "west"),
            
            # Vertical roads (north-south)
            (2, -15, "north"),
            (-2, -10, "south"),
            (2, 10, "north"),
            (-2, 15, "south")
        ]
        
        for x, z, direction in spawn_positions[:4]:  # Start with 4 cars
            npc_car = NPCCar(x, z, direction, random.uniform(0.2, 0.4))
            self.npc_cars.append(npc_car)
    
    def spawn_npc_car(self):
        """Spawn a new NPC car at a random edge of the road network"""
        if len(self.npc_cars) >= self.max_npc_cars:
            return
            
        # Random spawn positions at edges of road network
        spawn_options = [
            # From east edge
            (30, random.choice([2, -2]), "west"),
            # From west edge  
            (-30, random.choice([2, -2]), "east"),
            # From north edge
            (random.choice([2, -2]), 30, "south"),
            # From south edge
            (random.choice([2, -2]), -30, "north")
        ]
        
        x, z, direction = random.choice(spawn_options)
        speed = random.uniform(0.15, 0.35)
        npc_car = NPCCar(x, z, direction, speed)
        self.npc_cars.append(npc_car)
    
    def update_npc_cars(self, dt):
        """Update all NPC cars"""
        # Update spawn timer
        self.npc_spawn_timer += dt
        if self.npc_spawn_timer >= self.npc_spawn_interval:
            self.spawn_npc_car()
            self.npc_spawn_timer = 0.0
        
        # Get all traffic lights for AI behavior
        all_traffic_lights = []
        for track in self.tracks:
            all_traffic_lights.extend(track.traffic_lights)
        
        # Update each NPC car
        cars_to_remove = []
        for i, npc_car in enumerate(self.npc_cars):
            if not npc_car.update_ai(all_traffic_lights):
                cars_to_remove.append(i)
        
        # Remove cars that went off screen
        for i in reversed(cars_to_remove):
            del self.npc_cars[i]
    
    def update_day_night_cycle(self, current_time):
        """Update the smooth day/night cycle with sunrise and sunset"""
        elapsed_time = current_time - self.game_start_time
        cycle_progress = (elapsed_time % self.day_night_cycle_duration) / self.day_night_cycle_duration
        
        # Define time periods (0.0 to 1.0)
        # 0.0-0.2: Night (24 seconds)
        # 0.2-0.3: Sunrise (12 seconds) 
        # 0.3-0.45: Early Morning (18 seconds) - NEW SMOOTHER TRANSITION
        # 0.45-0.7: Day (30 seconds)
        # 0.7-0.8: Sunset (12 seconds)
        # 0.8-1.0: Night (24 seconds)
        
        new_time_of_day = self.time_of_day
        
        if cycle_progress < 0.2:
            new_time_of_day = "night"
            # Deep night
            self.sky_color = [0.05, 0.05, 0.15]
            self.ambient_light = [0.02, 0.02, 0.08]
            self.diffuse_light = [0.05, 0.05, 0.1]
            
        elif cycle_progress < 0.3:
            new_time_of_day = "sunrise"
            # Sunrise transition (12 seconds) - warmer colors
            t = (cycle_progress - 0.2) / 0.1  # 0.0 to 1.0
            self.sky_color = self.lerp_color([0.05, 0.05, 0.15], [0.9, 0.5, 0.2], t)
            self.ambient_light = self.lerp_color([0.02, 0.02, 0.08], [0.6, 0.4, 0.3], t)
            self.diffuse_light = self.lerp_color([0.05, 0.05, 0.1], [0.7, 0.5, 0.4], t)
            
        elif cycle_progress < 0.45:
            new_time_of_day = "early_morning"
            # Early morning transition (18 seconds) - smooth transition to day
            t = (cycle_progress - 0.3) / 0.15  # 0.0 to 1.0
            self.sky_color = self.lerp_color([0.9, 0.5, 0.2], [0.6, 0.8, 1.0], t)
            self.ambient_light = self.lerp_color([0.6, 0.4, 0.3], [0.8, 0.8, 0.9], t)
            self.diffuse_light = self.lerp_color([0.7, 0.5, 0.4], [0.9, 0.9, 1.0], t)
            
        elif cycle_progress < 0.7:
            new_time_of_day = "day"
            # Full day
            self.sky_color = [0.6, 0.8, 1.0]
            self.ambient_light = [0.8, 0.8, 0.9]
            self.diffuse_light = [0.9, 0.9, 1.0]
            
        elif cycle_progress < 0.8:
            new_time_of_day = "sunset"
            # Sunset transition (12 seconds)
            t = (cycle_progress - 0.7) / 0.1  # 0.0 to 1.0
            self.sky_color = self.lerp_color([0.6, 0.8, 1.0], [0.8, 0.3, 0.1], t)
            self.ambient_light = self.lerp_color([0.8, 0.8, 0.9], [0.3, 0.2, 0.15], t)
            self.diffuse_light = self.lerp_color([0.9, 0.9, 1.0], [0.4, 0.3, 0.2], t)
            
        else:
            new_time_of_day = "night"
            # Evening into night
            t = (cycle_progress - 0.8) / 0.2  # 0.0 to 1.0
            self.sky_color = self.lerp_color([0.8, 0.3, 0.1], [0.05, 0.05, 0.15], t)
            self.ambient_light = self.lerp_color([0.3, 0.2, 0.15], [0.02, 0.02, 0.08], t)
            self.diffuse_light = self.lerp_color([0.4, 0.3, 0.2], [0.05, 0.05, 0.1], t)
        
        # Print time changes
        if new_time_of_day != self.time_of_day:
            self.time_of_day = new_time_of_day
            print(f"Time: {self.time_of_day.upper()}")
        
        # Apply the smooth lighting changes
        self.apply_smooth_lighting()
    
    def lerp_color(self, color1, color2, t):
        """Linear interpolation between two colors"""
        return [
            color1[0] + (color2[0] - color1[0]) * t,
            color1[1] + (color2[1] - color1[1]) * t,
            color1[2] + (color2[2] - color1[2]) * t
        ]
    
    def apply_smooth_lighting(self):
        """Apply smooth lighting changes"""
        # Update sky color
        glClearColor(self.sky_color[0], self.sky_color[1], self.sky_color[2], 1.0)
        
        # Update ambient and diffuse lighting
        ambient_light_rgba = self.ambient_light + [1.0]
        diffuse_light_rgba = self.diffuse_light + [1.0]
        
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light_rgba)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light_rgba)
    
    def is_day_time(self):
        """Check if it's day time (for street light glow)"""
        return self.time_of_day in ["day", "sunrise", "sunset", "early_morning"]
        
    def confirm_vehicle_selection(self):
        """Create the selected vehicle and start the game"""
        if self.selected_vehicle == "car":
            self.vehicle = Car()
            print("Starting with CAR - 6-speed transmission, stable handling")
        else:
            self.vehicle = Motorcycle()
            print("Starting with MOTORCYCLE - 5-speed transmission, agile handling")
        
        # Set initial position and angle
        self.vehicle.x = 10.0
        self.vehicle.angle = 270.0
        
        # Exit selection mode
        self.vehicle_selection = False
        print("Game started! Use arrow keys to drive, L for headlights, T for transmission mode")
    
    def draw_vehicle_selection(self):
        """Draw the vehicle selection screen with improved visibility"""
        # Clear screen with dark background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Only print instructions once
        if not hasattr(self, 'selection_instructions_shown'):
            print(f"\n=== VEHICLE SELECTION ===")
            print(f"Use LEFT/RIGHT arrows to select, ENTER/SPACE to confirm")
            print(f"CAR: 6-speed, stable handling")
            print(f"MOTORCYCLE: 5-speed, agile handling")
            print(f"Current selection: {self.selected_vehicle.upper()}")
            self.selection_instructions_shown = True
        
        # Create a surface for the selection UI using pygame and OpenGL texture display
        selection_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        selection_surface.fill((0, 0, 0, 255))  # Solid black background
        
        # Draw title
        title_text = "SELECT YOUR VEHICLE"
        title_surface = self.font_large.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width//2, 80))
        selection_surface.blit(title_surface, title_rect)
        
        # Instructions
        instruction_text = "Use ← → arrows to select, ENTER/SPACE to confirm"
        instruction_surface = self.font_medium.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(self.width//2, 120))
        selection_surface.blit(instruction_surface, instruction_rect)
        
        # Vehicle selection boxes
        box_width = 300
        box_height = 200
        car_x = self.width//2 - 200
        motorcycle_x = self.width//2 + 200
        box_y = self.height//2
        
        # Car selection box
        car_color = (0, 150, 0) if self.selected_vehicle == "car" else (60, 60, 60)
        car_border_color = (0, 255, 0) if self.selected_vehicle == "car" else (120, 120, 120)
        
        car_rect = pygame.Rect(car_x - box_width//2, box_y - box_height//2, box_width, box_height)
        pygame.draw.rect(selection_surface, car_color, car_rect)
        pygame.draw.rect(selection_surface, car_border_color, car_rect, 4 if self.selected_vehicle == "car" else 2)
        
        # Car label
        car_label = "CAR"
        car_label_surface = self.font_large.render(car_label, True, (255, 255, 255))
        car_label_rect = car_label_surface.get_rect(center=(car_x, box_y - 60))
        selection_surface.blit(car_label_surface, car_label_rect)
        
        # Car specs
        car_specs = ["6-Speed Transmission", "Stable Handling", "All-Weather Capable"]
        for i, spec in enumerate(car_specs):
            spec_surface = self.font_small.render(spec, True, (200, 200, 200))
            spec_rect = spec_surface.get_rect(center=(car_x, box_y + 40 + i * 20))
            selection_surface.blit(spec_surface, spec_rect)
        
        # Draw simple car icon
        car_body_rect = pygame.Rect(car_x - 40, box_y - 15, 80, 30)
        pygame.draw.rect(selection_surface, (0, 100, 255), car_body_rect)
        
        # Car wheels
        pygame.draw.circle(selection_surface, (50, 50, 50), (car_x - 25, box_y + 20), 8)
        pygame.draw.circle(selection_surface, (50, 50, 50), (car_x + 25, box_y + 20), 8)
        
        # Motorcycle selection box
        motorcycle_color = (0, 150, 0) if self.selected_vehicle == "motorcycle" else (60, 60, 60)
        motorcycle_border_color = (0, 255, 0) if self.selected_vehicle == "motorcycle" else (120, 120, 120)
        
        motorcycle_rect = pygame.Rect(motorcycle_x - box_width//2, box_y - box_height//2, box_width, box_height)
        pygame.draw.rect(selection_surface, motorcycle_color, motorcycle_rect)
        pygame.draw.rect(selection_surface, motorcycle_border_color, motorcycle_rect, 4 if self.selected_vehicle == "motorcycle" else 2)
        
        # Motorcycle label
        motorcycle_label = "MOTORCYCLE"
        motorcycle_label_surface = self.font_large.render(motorcycle_label, True, (255, 255, 255))
        motorcycle_label_rect = motorcycle_label_surface.get_rect(center=(motorcycle_x, box_y - 60))
        selection_surface.blit(motorcycle_label_surface, motorcycle_label_rect)
        
        # Motorcycle specs
        motorcycle_specs = ["5-Speed Transmission", "Agile Handling", "High Acceleration"]
        for i, spec in enumerate(motorcycle_specs):
            spec_surface = self.font_small.render(spec, True, (200, 200, 200))
            spec_rect = spec_surface.get_rect(center=(motorcycle_x, box_y + 40 + i * 20))
            selection_surface.blit(spec_surface, spec_rect)
        
        # Draw simple motorcycle icon
        bike_body_rect = pygame.Rect(motorcycle_x - 30, box_y - 8, 60, 16)
        pygame.draw.rect(selection_surface, (255, 100, 0), bike_body_rect)
        
        # Motorcycle wheels (in line)
        pygame.draw.circle(selection_surface, (50, 50, 50), (motorcycle_x - 20, box_y + 20), 10)
        pygame.draw.circle(selection_surface, (50, 50, 50), (motorcycle_x + 20, box_y + 20), 10)
        
        # Selection arrows
        if self.selected_vehicle == "car":
            # Draw arrow pointing to car
            arrow_points = [
                (car_x - box_width//2 - 40, box_y),
                (car_x - box_width//2 - 20, box_y - 20),
                (car_x - box_width//2 - 20, box_y + 20)
            ]
            pygame.draw.polygon(selection_surface, (255, 255, 0), arrow_points)
        else:
            # Draw arrow pointing to motorcycle
            arrow_points = [
                (motorcycle_x + box_width//2 + 40, box_y),
                (motorcycle_x + box_width//2 + 20, box_y - 20),
                (motorcycle_x + box_width//2 + 20, box_y + 20)
            ]
            pygame.draw.polygon(selection_surface, (255, 255, 0), arrow_points)
        
        # Current selection indicator at bottom
        current_text = f"SELECTED: {self.selected_vehicle.upper()}"
        current_surface = self.font_medium.render(current_text, True, (255, 255, 0))
        current_rect = current_surface.get_rect(center=(self.width//2, self.height - 80))
        selection_surface.blit(current_surface, current_rect)
        
        # Display the selection surface using OpenGL texture
        self.display_surface_as_texture(selection_surface)

    def draw_text_surface(self, surface, x, y):
        """Helper method to draw pygame text surface using OpenGL"""
        text_data = pygame.image.tostring(surface, "RGBA", True)
        
        glRasterPos2f(x, y)
        glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time for traffic lights
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - self.last_time
            self.last_time = current_time
            
            self.handle_events()
            
            if self.vehicle_selection:
                # Vehicle selection screen
                self.draw_vehicle_selection()
            else:
                # Update day/night cycle
                self.update_day_night_cycle(current_time)
                
                # Get pressed keys for continuous input
                keys = pygame.key.get_pressed()
                
                # Update game objects
                # Update player vehicle with day/night status for auto headlights
                self.vehicle.update(keys, self.is_day_time())
                
                # Check for building collisions
                all_buildings = []
                for track in self.tracks:
                    all_buildings.extend(track.buildings)
                
                if self.vehicle.check_building_collision(all_buildings):
                    self.vehicle.resolve_collision(self.vehicle.prev_x, self.vehicle.prev_z)
                
                # Update traffic lights
                for track in self.tracks:
                    track.update_traffic_lights(dt)
                
                # Update NPC cars - DISABLED
                # self.update_npc_cars(dt)
                
                # Clear screen
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
                # Update camera
                self.update_camera()
                
                # Draw everything
                for track in self.tracks:
                    track.draw(self.is_day_time())  # Draw all tracks with their buildings (pass day/night status)
                self.vehicle.draw()
                
                # Draw NPC cars - DISABLED
                # for npc_car in self.npc_cars:
                #     npc_car.draw()
                
                # Draw HUD on top (if enabled)
            if self.show_hud:
                self.draw_hud()
            
            # Draw help menu on top of everything (if enabled)
            if self.show_help_menu:
                self.draw_help_menu()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # Increased to 60 FPS for smoother HUD
        
        # Cleanup
        pygame.quit()
        sys.exit()