#!/usr/bin/env python3
"""
Test script to visualize building placement and verify no overlaps
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from classes.track import Track

def init_pygame_opengl():
    """Initialize pygame and OpenGL for testing"""
    pygame.init()
    
    # Set up display
    width, height = 1200, 800
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Building Overlap Test - No Overlapping Buildings")
    
    # Set up OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Set up projection
    gluPerspective(45, (width/height), 0.1, 100.0)
    
    # Set up lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 20, 0, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

def draw_building_bounds(building, color):
    """Draw wireframe around building to visualize its bounds"""
    glDisable(GL_TEXTURE_2D)
    glColor3f(*color)
    glLineWidth(2.0)
    
    # Calculate building corners
    left = building.x - building.width/2
    right = building.x + building.width/2
    front = building.z - building.depth/2
    back = building.z + building.depth/2
    bottom = building.y
    top = building.y + building.height
    
    # Draw wireframe box
    glBegin(GL_LINES)
    # Bottom face
    glVertex3f(left, bottom, front)
    glVertex3f(right, bottom, front)
    glVertex3f(right, bottom, front)
    glVertex3f(right, bottom, back)
    glVertex3f(right, bottom, back)
    glVertex3f(left, bottom, back)
    glVertex3f(left, bottom, back)
    glVertex3f(left, bottom, front)
    
    # Top face
    glVertex3f(left, top, front)
    glVertex3f(right, top, front)
    glVertex3f(right, top, front)
    glVertex3f(right, top, back)
    glVertex3f(right, top, back)
    glVertex3f(left, top, back)
    glVertex3f(left, top, back)
    glVertex3f(left, top, front)
    
    # Vertical edges
    glVertex3f(left, bottom, front)
    glVertex3f(left, top, front)
    glVertex3f(right, bottom, front)
    glVertex3f(right, top, front)
    glVertex3f(right, bottom, back)
    glVertex3f(right, top, back)
    glVertex3f(left, bottom, back)
    glVertex3f(left, top, back)
    glEnd()
    
    glLineWidth(1.0)

def check_building_overlaps(buildings):
    """Check for overlaps and report them"""
    overlaps = []
    for i, building1 in enumerate(buildings):
        for j, building2 in enumerate(buildings[i+1:], i+1):
            # Calculate bounds
            b1_left = building1.x - building1.width/2
            b1_right = building1.x + building1.width/2
            b1_front = building1.z - building1.depth/2
            b1_back = building1.z + building1.depth/2
            
            b2_left = building2.x - building2.width/2
            b2_right = building2.x + building2.width/2
            b2_front = building2.z - building2.depth/2
            b2_back = building2.z + building2.depth/2
            
            # Check for overlap
            if not (b1_right < b2_left or b1_left > b2_right or 
                   b1_back < b2_front or b1_front > b2_back):
                overlaps.append((i, j))
    
    return overlaps

def main():
    """Test building placement without overlaps"""
    init_pygame_opengl()
    
    # Create a track to test building placement
    track = Track(0, 0)
    
    print("=== BUILDING OVERLAP TEST ===")
    print(f"Total buildings created: {len(track.buildings)}")
    
    # Check for overlaps
    overlaps = check_building_overlaps(track.buildings)
    
    if overlaps:
        print(f"❌ OVERLAPS DETECTED: {len(overlaps)} pairs of buildings are overlapping!")
        for i, j in overlaps:
            print(f"  Building {i} overlaps with Building {j}")
    else:
        print("✅ NO OVERLAPS DETECTED: All buildings are properly spaced!")
    
    # Print building positions for verification
    print(f"\nBuilding Positions:")
    for i, building in enumerate(track.buildings):
        print(f"Building {i}: pos=({building.x:.1f}, {building.z:.1f}) size=({building.width:.1f} x {building.depth:.1f})")
        print(f"  Bounds: X=[{building.x - building.width/2:.1f} to {building.x + building.width/2:.1f}] Z=[{building.z - building.depth/2:.1f} to {building.z + building.depth/2:.1f}]")
    
    clock = pygame.time.Clock()
    camera_pos = [0, 15, 25]
    camera_rot = [-30, 0]
    show_bounds = True
    
    print(f"\n=== CONTROLS ===")
    print("• WASD: Move camera")
    print("• QE: Move up/down")
    print("• Mouse + Left Click: Look around")
    print("• B: Toggle building bounds display")
    print("• ESC: Exit")
    print("\n• Red wireframes show building boundaries")
    print("• Buildings should not overlap or touch each other")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_b:
                    show_bounds = not show_bounds
                    print(f"Building bounds display: {'ON' if show_bounds else 'OFF'}")
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    camera_rot[0] += event.rel[1] * 0.5
                    camera_rot[1] += event.rel[0] * 0.5
                    camera_rot[0] = max(-90, min(90, camera_rot[0]))
        
        # Handle continuous key input
        keys = pygame.key.get_pressed()
        speed = 0.3
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
        glClearColor(0.2, 0.3, 0.4, 1.0)  # Blue sky
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set camera
        glLoadIdentity()
        glRotatef(camera_rot[0], 1, 0, 0)
        glRotatef(camera_rot[1], 0, 1, 0)
        glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
        
        # Draw the track (ground and roads)
        track.draw(is_day=True, camera_x=camera_pos[0], camera_z=camera_pos[2])
        
        # Draw building bounds if enabled
        if show_bounds:
            for i, building in enumerate(track.buildings):
                # Use different colors to distinguish buildings
                colors = [(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1)]
                color = colors[i % len(colors)]
                draw_building_bounds(building, color)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    for building in track.buildings:
        building.cleanup()
    
    pygame.quit()

if __name__ == "__main__":
    main()