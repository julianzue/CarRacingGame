#!/usr/bin/env python3
"""
Test script to demonstrate building textures
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from classes.building import Building

def init_pygame_opengl():
    """Initialize pygame and OpenGL for testing"""
    pygame.init()
    
    # Set up display
    width, height = 800, 600
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Building Texture Test")
    
    # Set up OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Set up projection
    gluPerspective(45, (width/height), 0.1, 50.0)
    
    # Set up lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 0, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

def main():
    """Test the building textures"""
    init_pygame_opengl()
    
    # Create test buildings with different positions to get different texture types
    buildings = [
        Building(0, 0, 0, 2, 4, 2),      # Center building
        Building(-5, 0, 0, 2, 3, 2),     # Left building  
        Building(5, 0, 0, 2, 5, 2),      # Right building
        Building(0, 0, -5, 3, 6, 3),     # Back building
        Building(0, 0, 5, 1.5, 2.5, 1.5) # Front building
    ]
    
    print("Building Texture Types:")
    for i, building in enumerate(buildings):
        print(f"Building {i+1}: {building.texture_type}")
    
    clock = pygame.time.Clock()
    rotation = 0
    
    print("\nControls:")
    print("- Mouse: Look around")
    print("- W/S: Move forward/backward") 
    print("- A/D: Move left/right")
    print("- Q/E: Move up/down")
    print("- ESC: Exit")
    
    camera_pos = [0, 3, 10]
    camera_rot = [0, 0]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    camera_rot[0] += event.rel[1] * 0.5
                    camera_rot[1] += event.rel[0] * 0.5
                    camera_rot[0] = max(-90, min(90, camera_rot[0]))
        
        # Handle continuous key input
        keys = pygame.key.get_pressed()
        speed = 0.1
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
        
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set camera
        glLoadIdentity()
        glRotatef(camera_rot[0], 1, 0, 0)
        glRotatef(camera_rot[1], 0, 1, 0)
        glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
        
        # Draw ground plane
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(-20, 0, -20)
        glVertex3f(20, 0, -20)
        glVertex3f(20, 0, 20)
        glVertex3f(-20, 0, 20)
        glEnd()
        
        # Draw buildings
        for building in buildings:
            building.draw(is_day_time=True)  # Test with daytime
        
        rotation += 1
        
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    for building in buildings:
        building.cleanup()
    Building.cleanup_texture_cache()
    
    pygame.quit()

if __name__ == "__main__":
    main()