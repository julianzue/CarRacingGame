import pygame
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt

def main():
    # Initialize pygame and create an OpenGL context
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("OpenGL Test")

    # Set up the perspective projection
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

    # Test glLightfv
    light_position = [1.0, 1.0, 1.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Function to draw a simple cube
    def draw_cube():
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

    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw a cube in the center of the scene
        glPushMatrix()
        glTranslatef(0.0, 0.0, -5.0)  # Move the cube back so it's visible
        glColor3f(1.0, 0.0, 0.0)  # Set cube color to red
        draw_cube()
        glPopMatrix()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()