screen_size = (1920,1080)

from OpenGL.GL import *
from OpenGL.GLU import *

from math import radians
import random
from matrix44 import *
from Vector3 import Vector3

import pygame
from pygame.locals import *
pygame.init()

screen = pygame.display.set_mode(screen_size, FULLSCREEN|HWSURFACE|OPENGL|DOUBLEBUF)

def resize(width, height):

    glViewport(0,0,width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., float(width)/height, 1., 10000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():

# Enable the GL features we will be using
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_TEXTURE_2D)

    glShadeModel(GL_FLAT)
    glClearColor(0.5, 0.5, 0.5, 0.0) # white

    # Set the material
    glMaterial(GL_FRONT, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glMaterial(GL_FRONT, GL_DIFFUSE, (0.2, 0.2, 0.2, 1.0))
    glMaterial(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterial(GL_FRONT, GL_SHININESS, 10.0)

    # Set light parameters
    glLight(GL_LIGHT0, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glLight(GL_LIGHT0, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
    glLight(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

def str_to_list(string):
    return list(map(int, string.split(" ")))

def draw_results(max_cubes):
    i = 0
    with open("results.txt") as f:
        vol = str_to_list(f.readline())
        glColor(0.0, 0.0, 0.0, 1.0)
        draw_cube(Vector3(*vol[:3]), Vector3(*vol[3:]), i)
        next_line = f.readline()
        glLineWidth(2.5)
        while next_line != "" and i < max_cubes:
            i += 1
            if next_line[0] == "v":
                glLineWidth(5.0)
                glColor(i / max_cubes, 0.0, 0.0, 1.0)
            elif next_line[0] == "o":
                glLineWidth(10.0)
                glColor(0.0, i / max_cubes, 0.0, 1.0)
            if i == max_cubes:
                glLineWidth(15.0)
            next_obj = str_to_list(next_line[1:])
            draw_cube(Vector3(*next_obj[:3]), Vector3(*next_obj[3:]), i)
            next_line = f.readline()

def draw_cube(dim, pos, seed=None):
    glBegin(GL_LINE_STRIP)

    # Bottom face
    glVertex(*pos)
    glVertex(*(pos + Vector3(dim.x, 0.0, 0.0)))
    glVertex(*(pos + Vector3(dim.x, dim.y, 0.0)))
    glVertex(*(pos + Vector3(0.0, dim.y, 0.0)))

    # Bottom face
    glVertex(*pos)
    glVertex(*(pos + Vector3(dim.x, 0.0, 0.0)))
    glVertex(*(pos + Vector3(dim.x, 0.0, dim.z)))
    glVertex(*(pos + Vector3(0.0, 0.0, dim.z)))

    # Bottom face
    glVertex(*pos)
    glVertex(*(pos + Vector3(0.0, 0.0, dim.z)))
    glVertex(*(pos + Vector3(0.0, dim.y, dim.z)))
    glVertex(*(pos + Vector3(0.0, dim.y, 0.0)))

    # Bottom face
    glVertex(*(pos + Vector3(0.0, dim.y, 0.0)))
    glVertex(*(pos + Vector3(dim.x, dim.y, 0.0)))
    glVertex(*(pos + Vector3(dim.x, dim.y, dim.z)))
    glVertex(*(pos + Vector3(0.0, dim.y, 0.0)))

    # Bottom face
    glVertex(*(pos + Vector3(dim.x, dim.y, dim.z)))
    glVertex(*(pos + Vector3(dim.x, 0.0, dim.z)))
    glVertex(*(pos + Vector3(dim.x, 0.0, dim.z)))
    glVertex(*(pos + Vector3(dim.x, dim.y, 0.0)))

    # Bottom face
    glVertex(*(pos + Vector3(0.0, 0.0, dim.z)))
    glVertex(*(pos + Vector3(dim.x, 0.0, dim.z)))
    glVertex(*(pos + Vector3(dim.x, dim.y, dim.z)))
    glVertex(*(pos + Vector3(0.0, dim.y, dim.z)))
    glEnd()

def run():

    resize(*screen_size)
    init()
    clock = pygame.time.Clock()

    camera_matrix = Matrix44()
    camera_matrix.translate = (20.0, 0.0, 50.0)

    # Initialize speeds and directions
    rotation_direction = Vector3()
    rotation_speed = radians(90.0)
    movement_direction = Vector3()
    movement_speed = 5.0

    mouse_x = 0.0
    mouse_y = 0.0

    pygame.mouse.set_visible(False)
    max_cubes = 1

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()

            if event.type == KEYDOWN and event.key == K_SPACE:
                max_cubes += 1

        movement_direction = Vector3()
        rotation_direction = Vector3()

        time_passed = clock.tick()
        time_passed_seconds = time_passed / 1000.

        pressed = pygame.key.get_pressed()

        # Reset rotation and movement directions

        if pressed[K_F2]:
            pygame.image.save(screen, "Screenshot.png")

        if pressed[K_ESCAPE]:
            return

        pressed_buttons = pygame.mouse.get_pressed()
        if pressed_buttons[0] == 1:
            movement_direction.z = -5.0

        elif pressed_buttons[2]== 1:
            movement_direction.z = +5.0

        if pressed_buttons[1] == 1:
            movement_direction.z *= 3.0

        mouse_rel_x, mouse_rel_y = pygame.mouse.get_rel()

        rotation_direction.y = float(mouse_rel_x) / -5.0
        rotation_direction.x = float(mouse_rel_y) / 5.0

        # Calculate rotation matrix and multiply by camera matrix
        rotation = rotation_direction * rotation_speed * time_passed_seconds
        rotation_matrix = Matrix44.xyz_rotation(*rotation)
        camera_matrix *= rotation_matrix

        # Calcluate movment and add it to camera matrix translate
        heading = Vector3(camera_matrix.forward)
        movement = heading * movement_direction.z * movement_speed
        camera_matrix.translate += movement * time_passed_seconds

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        glRotatef(mouse_y, 1, 0, 0)
        glRotatef(mouse_x, 0, 1, 0)

        glLoadMatrixd(camera_matrix.get_inverse().to_opengl())

        draw_results(max_cubes)

        pygame.display.flip()

run()
