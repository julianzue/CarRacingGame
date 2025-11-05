import pygame
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from classes.game import Game


class WindowSizeSelector:
    """Window size selection screen"""
    
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Select Window Size - Car Racing Game")
        
        # Initialize font
        pygame.font.init()
        try:
            self.font_large = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 24)
            self.font_medium = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 18)
            self.font_small = pygame.font.Font("C:/Windows/Fonts/consolab.ttf", 14)
        except:
            try:
                self.font_large = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 24)
                self.font_medium = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 18)
                self.font_small = pygame.font.Font("C:/Windows/Fonts/courbd.ttf", 14)
            except:
                self.font_large = pygame.font.SysFont("monospacebold", 24)
                self.font_medium = pygame.font.SysFont("monospacebold", 18)
                self.font_small = pygame.font.SysFont("monospacebold", 14)
        
        self.selected_size = "normal"  # Default to normal size
        self.running = True
        self.clock = pygame.time.Clock()
    
    def handle_events(self):
        """Handle events for size selection"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return None
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    # Toggle between small and normal
                    self.selected_size = "small" if self.selected_size == "normal" else "normal"
                    print(f"Selected: {self.selected_size.upper()} size")
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Confirm selection
                    return self.selected_size
        return "continue"
    
    def draw(self):
        """Draw the size selection screen"""
        self.screen.fill((20, 20, 30))  # Dark blue background
        
        # Title
        title_text = "SELECT WINDOW SIZE"
        title_surface = self.font_large.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width//2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Instructions
        instruction_text = "Use ← → arrows to select, ENTER/SPACE to confirm"
        instruction_surface = self.font_small.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(self.width//2, 80))
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Size option boxes
        box_width = 200
        box_height = 120
        small_x = self.width//2 - 120
        normal_x = self.width//2 + 120
        box_y = self.height//2
        
        # Small size box
        small_color = (0, 100, 0) if self.selected_size == "small" else (40, 40, 40)
        small_border_color = (0, 200, 0) if self.selected_size == "small" else (100, 100, 100)
        
        small_rect = pygame.Rect(small_x - box_width//2, box_y - box_height//2, box_width, box_height)
        pygame.draw.rect(self.screen, small_color, small_rect)
        pygame.draw.rect(self.screen, small_border_color, small_rect, 3 if self.selected_size == "small" else 1)
        
        # Small size label and info
        small_label = "SMALL"
        small_label_surface = self.font_medium.render(small_label, True, (255, 255, 255))
        small_label_rect = small_label_surface.get_rect(center=(small_x, box_y - 35))
        self.screen.blit(small_label_surface, small_label_rect)
        
        small_info = ["800 x 600", "30° view", "Compact"]
        for i, info in enumerate(small_info):
            info_surface = self.font_small.render(info, True, (200, 200, 200))
            info_rect = info_surface.get_rect(center=(small_x, box_y + i * 15))
            self.screen.blit(info_surface, info_rect)
        
        # Normal size box
        normal_color = (0, 100, 0) if self.selected_size == "normal" else (40, 40, 40)
        normal_border_color = (0, 200, 0) if self.selected_size == "normal" else (100, 100, 100)
        
        normal_rect = pygame.Rect(normal_x - box_width//2, box_y - box_height//2, box_width, box_height)
        pygame.draw.rect(self.screen, normal_color, normal_rect)
        pygame.draw.rect(self.screen, normal_border_color, normal_rect, 3 if self.selected_size == "normal" else 1)
        
        # Normal size label and info
        normal_label = "NORMAL"
        normal_label_surface = self.font_medium.render(normal_label, True, (255, 255, 255))
        normal_label_rect = normal_label_surface.get_rect(center=(normal_x, box_y - 35))
        self.screen.blit(normal_label_surface, normal_label_rect)
        
        normal_info = ["1200 x 800", "45° view", "Full size"]
        for i, info in enumerate(normal_info):
            info_surface = self.font_small.render(info, True, (200, 200, 200))
            info_rect = info_surface.get_rect(center=(normal_x, box_y + i * 15))
            self.screen.blit(info_surface, info_rect)
        
        # Selection indicator
        if self.selected_size == "small":
            arrow_points = [
                (small_x - box_width//2 - 20, box_y),
                (small_x - box_width//2 - 5, box_y - 10),
                (small_x - box_width//2 - 5, box_y + 10)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 0), arrow_points)
        else:
            arrow_points = [
                (normal_x + box_width//2 + 20, box_y),
                (normal_x + box_width//2 + 5, box_y - 10),
                (normal_x + box_width//2 + 5, box_y + 10)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 0), arrow_points)
        
        # Current selection at bottom
        current_text = f"SELECTED: {self.selected_size.upper()} ({self.get_size_info()})"
        current_surface = self.font_medium.render(current_text, True, (255, 255, 0))
        current_rect = current_surface.get_rect(center=(self.width//2, self.height - 50))
        self.screen.blit(current_surface, current_rect)
        
        pygame.display.flip()
    
    def get_size_info(self):
        """Get size information string"""
        if self.selected_size == "small":
            return "800x600, 30° view"
        else:
            return "1200x800, 45° view"
    
    def run(self):
        """Run the size selection loop"""
        print("\n=== WINDOW SIZE SELECTION ===")
        print("SMALL: 800x600 with 30° perspective")
        print("NORMAL: 1200x800 with 45° perspective")
        print("Use LEFT/RIGHT arrows to select, ENTER/SPACE to confirm")
        
        while self.running:
            result = self.handle_events()
            if result == "continue":
                self.draw()
                self.clock.tick(60)
            elif result is not None:
                # Size selected
                pygame.quit()
                return result
            else:
                # User quit
                pygame.quit()
                return None


def main():
    try:
        # First, show window size selection
        size_selector = WindowSizeSelector()
        selected_size = size_selector.run()
        
        if selected_size is None:
            print("Window size selection cancelled.")
            return
        
        print(f"Selected window size: {selected_size.upper()}")
        
        # Create game with selected size
        if selected_size == "small":
            game = Game(width=800, height=600, fov=30)
        else:
            game = Game(width=1200, height=800, fov=45)
        
        print("Game initialized successfully!")
        print("Starting night racing game...")
        game.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
