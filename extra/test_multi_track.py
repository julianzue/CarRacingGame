#!/usr/bin/env python3
"""
Comprehensive test for building placement across multiple track sections
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from classes.track import Track

def init_pygame_opengl():
    """Initialize pygame and OpenGL"""
    pygame.init()
    
    width, height = 1400, 900
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Multi-Track Building Placement Test")
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    gluPerspective(45, (width/height), 0.1, 200.0)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 50, 0, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

def analyze_all_buildings(tracks):
    """Analyze buildings across all tracks"""
    all_buildings = []
    track_buildings = []
    
    for i, track in enumerate(tracks):
        track_buildings.append(len(track.buildings))
        all_buildings.extend(track.buildings)
    
    print(f"=== COMPREHENSIVE BUILDING ANALYSIS ===")
    print(f"Total tracks: {len(tracks)}")
    print(f"Buildings per track: {track_buildings}")
    print(f"Total buildings: {len(all_buildings)}")
    
    # Check for overlaps within each track
    total_overlaps = 0
    for i, track in enumerate(tracks):
        overlaps = check_building_overlaps(track.buildings)
        if overlaps:
            print(f"❌ Track {i}: {len(overlaps)} overlaps")
            total_overlaps += len(overlaps)
        else:
            print(f"✅ Track {i}: No overlaps ({len(track.buildings)} buildings)")
    
    # Check for overlaps between different tracks (if close enough)
    inter_track_overlaps = 0
    for i, track1 in enumerate(tracks):
        for j, track2 in enumerate(tracks[i+1:], i+1):
            # Only check if tracks are close enough that their buildings might overlap
            distance = ((track1.pos_x - track2.pos_x)**2 + (track1.pos_y - track2.pos_y)**2)**0.5
            if distance < 60:  # Only check nearby tracks
                for building1 in track1.buildings:
                    for building2 in track2.buildings:
                        if buildings_overlap(building1, building2):
                            inter_track_overlaps += 1
    
    print(f"\nOverlap Summary:")
    if total_overlaps == 0 and inter_track_overlaps == 0:
        print("🎉 SUCCESS: No building overlaps detected anywhere!")
    else:
        print(f"❌ Total intra-track overlaps: {total_overlaps}")
        print(f"❌ Total inter-track overlaps: {inter_track_overlaps}")
    
    return all_buildings

def check_building_overlaps(buildings):
    """Check for overlaps within a building list"""
    overlaps = []
    for i, building1 in enumerate(buildings):
        for j, building2 in enumerate(buildings[i+1:], i+1):
            if buildings_overlap(building1, building2):
                overlaps.append((i, j))
    return overlaps

def buildings_overlap(building1, building2):
    """Check if two buildings overlap"""
    b1_left = building1.x - building1.width/2
    b1_right = building1.x + building1.width/2
    b1_front = building1.z - building1.depth/2
    b1_back = building1.z + building1.depth/2
    
    b2_left = building2.x - building2.width/2
    b2_right = building2.x + building2.width/2
    b2_front = building2.z - building2.depth/2
    b2_back = building2.z + building2.depth/2
    
    return not (b1_right < b2_left or b1_left > b2_right or 
               b1_back < b2_front or b1_front > b2_back)

def main():
    """Test building placement across multiple tracks"""
    init_pygame_opengl()
    
    # Create multiple tracks at different positions to test the system
    tracks = [
        Track(0, 0),      # Center track
        Track(60, 0),     # East track
        Track(-60, 0),    # West track
        Track(0, 60),     # North track
        Track(0, -60),    # South track
        Track(60, 60),    # Northeast track
        Track(-60, 60),   # Northwest track  
        Track(60, -60),   # Southeast track
        Track(-60, -60),  # Southwest track
    ]
    
    # Analyze all buildings
    all_buildings = analyze_all_buildings(tracks)
    
    clock = pygame.time.Clock()
    camera_pos = [0, 40, 80]
    camera_rot = [-25, 0]
    current_track = 0
    
    print(f"\n=== CONTROLS ===")
    print("• WASD: Move camera")
    print("• QE: Move up/down")
    print("• Mouse + Left Click: Look around")
    print("• TAB: Switch focus to next track")
    print("• ESC: Exit")
    print("\n• Different colored buildings show different tracks")
    print("• Camera starts with overview, use TAB to focus on individual tracks")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    current_track = (current_track + 1) % len(tracks)
                    track = tracks[current_track]
                    camera_pos = [track.pos_x, 25, track.pos_y + 40]
                    camera_rot = [-20, 0]
                    print(f"Focused on Track {current_track} at position ({track.pos_x}, {track.pos_y})")
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    camera_rot[0] += event.rel[1] * 0.5
                    camera_rot[1] += event.rel[0] * 0.5
                    camera_rot[0] = max(-90, min(90, camera_rot[0]))
        
        # Handle continuous key input
        keys = pygame.key.get_pressed()
        speed = 1.0
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
        glClearColor(0.1, 0.2, 0.4, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set camera
        glLoadIdentity()
        glRotatef(camera_rot[0], 1, 0, 0)
        glRotatef(camera_rot[1], 0, 1, 0)
        glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
        
        # Draw all tracks
        for i, track in enumerate(tracks):
            # Calculate distance for performance culling
            distance = ((track.pos_x - camera_pos[0])**2 + (track.pos_y - camera_pos[2])**2)**0.5
            if distance < 150:  # Only render nearby tracks
                track.draw(is_day=True, camera_x=camera_pos[0], camera_z=camera_pos[2])
        
        pygame.display.flip()
        clock.tick(60)
    
    # Cleanup
    for track in tracks:
        for building in track.buildings:
            building.cleanup()
    
    pygame.quit()

if __name__ == "__main__":
    main()