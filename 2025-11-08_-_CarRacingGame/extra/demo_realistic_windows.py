#!/usr/bin/env python3
"""
Enhanced test to showcase realistic window positioning for different building types
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from classes.building import Building

def init_pygame_opengl():
    """Initialize pygame and OpenGL for testing"""
    pygame.init()
    
    # Set up display
    width, height = 1200, 800
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Realistic Building Windows Test")
    
    # Set up OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Set up projection
    gluPerspective(45, (width/height), 0.1, 50.0)
    
    # Set up lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 5, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

def create_demo_buildings():
    """Create buildings designed to showcase different texture types and window styles"""
    buildings = []
    
    # Create specific buildings to demonstrate each texture type
    # Brick building (traditional style)
    brick_building = Building(-8, 0, 0, 3, 4, 2)
    brick_building.texture_type = 'brick'
    brick_building._generate_texture()
    buildings.append(('Brick Building (Traditional)', brick_building))
    
    # Concrete building (utilitarian style)  
    concrete_building = Building(-3, 0, 0, 2.5, 6, 2.5)
    concrete_building.texture_type = 'concrete'
    concrete_building._generate_texture()
    buildings.append(('Concrete Building (Utilitarian)', concrete_building))
    
    # Glass modern building (contemporary style)
    glass_building = Building(2, 0, 0, 3.5, 7, 2)
    glass_building.texture_type = 'glass_modern'
    glass_building._generate_texture()
    buildings.append(('Glass Modern Building (Contemporary)', glass_building))
    
    # Stone building (traditional style)
    stone_building = Building(7, 0, 0, 2, 3.5, 3)
    stone_building.texture_type = 'stone'
    stone_building._generate_texture()
    buildings.append(('Stone Building (Traditional)', stone_building))
    
    # Mixed height buildings in background
    bg_buildings = [
        Building(-10, 0, -8, 2, 5, 2),
        Building(-5, 0, -8, 3, 4, 2),
        Building(0, 0, -8, 2.5, 6, 2.5),
        Building(5, 0, -8, 3, 3, 2),
        Building(10, 0, -8, 2, 4.5, 2),
    ]
    
    for bg_building in bg_buildings:
        buildings.append(('Background Building', bg_building))
    
    return buildings

def draw_info_text():
    """Draw information about building types (conceptual - would need text rendering)"""
    # This would require implementing text rendering in OpenGL
    # For now, we'll print to console
    pass

def main():
    """Enhanced test showing realistic window positioning"""
    init_pygame_opengl()
    
    buildings = create_demo_buildings()
    
    print("=== UNIFORM BUILDING WINDOWS DEMO ===")
    print("\nBuilding Types with Uniform Windows:")
    print("• BRICK: Textured brick walls with uniform window grid")
    print("• CONCRETE: Textured concrete walls with uniform window grid") 
    print("• GLASS MODERN: Textured glass panels with uniform window grid")
    print("• STONE: Textured stone walls with uniform window grid")
    print("\nFeatures:")
    print("• All windows are the same size and evenly spaced")
    print("• Perfect grid layout on all building faces")
    print("• Uniform window frames and proportions")
    print("• Consistent day/night appearance")
    print("• Different building textures with identical window patterns")
    
    for name, building in buildings[:4]:  # First 4 are the showcase buildings
        print(f"\n{name}: {building.texture_type}")
        params = building._get_window_parameters()
        print(f"  - Window Style: {params['window_style']} (all buildings use same style)")
        print(f"  - Floors with windows: {params['rows'] - params['start_floor']}")
        print(f"  - Windows per floor: {params['cols_width']}")
        print(f"  - Window size: {params['window_width']:.3f} x {params['window_height']:.3f} (uniform for all)")
    
    clock = pygame.time.Clock()
    camera_pos = [0, 4, 12]
    camera_rot = [0, 0]
    is_day = True
    
    print(f"\n=== CONTROLS ===")
    print("• WASD: Move camera")
    print("• QE: Move up/down") 
    print("• Mouse + Left Click: Look around")
    print("• SPACE: Toggle day/night (see window lighting changes)")
    print("• ESC: Exit")
    print("• Use mouse to rotate view and see windows on different building faces")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    is_day = not is_day
                    print(f"Switched to {'DAY' if is_day else 'NIGHT'} mode - notice window lighting changes")
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    camera_rot[0] += event.rel[1] * 0.5
                    camera_rot[1] += event.rel[0] * 0.5
                    camera_rot[0] = max(-90, min(90, camera_rot[0]))
        
        # Handle continuous key input
        keys = pygame.key.get_pressed()
        speed = 0.15
        if keys[pygame.K_w]:
            camera_pos[2] -= speed
        if keys[pygame.K_s]:
            camera_pos[2] += speed
        if keys[pygame.K_a]:
            camera_pos[0] -= speed
        if keys[pygame.K_d]:
            camera_pos[0] += speed
        if keys[pygame.K_q]:
            camera_pos[1] -= speed
        if keys[pygame.K_e]:
            camera_pos[1] += speed
        
        # Clear screen with appropriate background
        if is_day:
            glClearColor(0.7, 0.8, 1.0, 1.0)  # Light blue sky
        else:
            glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark night sky
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set camera
        glLoadIdentity()
        glRotatef(camera_rot[0], 1, 0, 0)
        glRotatef(camera_rot[1], 0, 1, 0)
        glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
        
        # Draw ground plane
        glDisable(GL_TEXTURE_2D)
        if is_day:
            glColor3f(0.3, 0.4, 0.2)  # Grass green
        else:
            glColor3f(0.1, 0.1, 0.1)  # Dark ground
        glBegin(GL_QUADS)
        glVertex3f(-30, 0, -30)
        glVertex3f(30, 0, -30)
        glVertex3f(30, 0, 30)
        glVertex3f(-30, 0, 30)
        glEnd()
        
        # Draw buildings with appropriate lighting
        for name, building in buildings:
            building.draw(is_day_time=is_day)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    for name, building in buildings:
        building.cleanup()
    Building.cleanup_texture_cache()
    
    pygame.quit()

if __name__ == "__main__":
    main()