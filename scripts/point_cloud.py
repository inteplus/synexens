#!/usr/bin/python3

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *
import numpy as np
import sys

global COORDS, COLORS, X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW, MODE, VERTEX_VBO, COLOR_VBO, MX, MY


def display_gpu():
    global X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW, VERTEX_VBO, COLOR_VBO, COORDS
    glGetError()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Performing translation and rotation
    glTranslatef(X_AXIS, Y_AXIS, Z_AXIS)
    glRotatef(PITCH, 1.0, 0.0, 0.0)
    glRotatef(ROLL, 0.0, 1.0, 0.0)
    glRotatef(YAW, 0.0, 0.0, 1.0)

    glBindBuffer(GL_ARRAY_BUFFER, VERTEX_VBO)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glEnableClientState(GL_VERTEX_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, COLOR_VBO)
    glColorPointer(3, GL_FLOAT, 0, None)
    glEnableClientState(GL_COLOR_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # Define buffer size as
    # no. of vertices * no. of faces * no. of cubes
    glDrawArrays(GL_QUADS, 0, 4 * 6 * len(COORDS))
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glFlush()
    glutSwapBuffers()


def calculate_centroid():
    global COORDS, X_AXIS, Y_AXIS, Z_AXIS
    # Calculate centroid for all vertices across cubes in each axis
    X_AXIS /= len(COORDS)
    Y_AXIS /= len(COORDS)
    Z_AXIS /= len(COORDS)
    Z_AXIS -= 20.0


def generate_cube_vertices_gpu(point_vals):
    global X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW, COORDS, COLORS
    X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    coords_arr = []
    colors_arr = []
    # Add 8 vertices in cube, colors for each vertex
    for x, y, z, r, g, b in point_vals:
        X_AXIS += x
        Y_AXIS += y
        Z_AXIS += z
        vertex_1 = [x, y, z]
        vertex_2 = [x + 0.25, y, z]
        vertex_3 = [x + 0.25, y + 0.25, z]
        vertex_4 = [x, y + 0.25, z]
        vertex_5 = [x, y, z + 0.25]
        vertex_6 = [x + 0.25, y, z + 0.25]
        vertex_7 = [x + 0.25, y + 0.25, z + 0.25]
        vertex_8 = [x, y + 0.25, z + 0.25]

        coords_arr.extend([vertex_1, vertex_2, vertex_3, vertex_4])
        coords_arr.extend([vertex_5, vertex_6, vertex_7, vertex_8])
        coords_arr.extend([vertex_1, vertex_4, vertex_8, vertex_5])
        coords_arr.extend([vertex_1, vertex_3, vertex_7, vertex_6])
        coords_arr.extend([vertex_1, vertex_2, vertex_6, vertex_5])
        coords_arr.extend([vertex_4, vertex_3, vertex_7, vertex_8])
        for x in range(24):
            colors_arr.append([r, g, b])
    COORDS = np.array(coords_arr, dtype=np.float32)
    COLORS = np.array(colors_arr, dtype=np.float32)
    calculate_centroid()


def onKeyDown(*args):
    global X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW
    # Retrieving key events and storing translation/rotation values
    key = args[0].decode("utf-8")
    if key == "q":
        sys.exit()
    elif key == "w":
        Y_AXIS -= 0.1
    elif key == "s":
        Y_AXIS += 0.1
    elif key == "a":
        X_AXIS += 0.1
    elif key == "d":
        X_AXIS -= 0.1
    elif key == "z":
        Z_AXIS -= 0.1
    elif key == "x":
        Z_AXIS += 0.1
    elif key == "i":
        YAW -= 1.0
    elif key == "k":
        YAW += 1.0
    elif key == "j":
        PITCH += 1.0
    elif key == "l":
        PITCH -= 1.0
    elif key == "n":
        ROLL += 1.0
    elif key == "m":
        ROLL -= 1.0
    # Clamping rotation
    np.clip(ROLL, -360.0, 360.0)
    np.clip(PITCH, -360.0, 360.0)
    np.clip(YAW, -360.0, 360.0)
    # Re-render
    display_gpu()


def onMouseButton(button: int, state: int, x: int, y: int):
    global MX, MY
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            MX = x
            MY = y
            print(f"lbutton down {x} {y}")
        else:
            print(f"lbutton up {x-MX} {y-MY}")


def onMouseDrag(x: int, y: int):
    print(f"dragging along {x} {y}")


def main():
    global COORDS, COLORS, VERTEX_VBO, COLOR_VBO, MODE
    # IO using numpy
    try:
        file = sys.argv[1]
        MODE = "gpu"
    except IndexError:
        print("Command line execution needs 1 arguments: path to txt file")
        return

    # IO Skipping header row in csv
    point_vals = np.loadtxt(file, delimiter=",", skiprows=1)
    # OpenGL Boilerplate setup
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutInitWindowPosition(200, 200)
    window = glutCreateWindow("Point Cloud Viewer")
    # Assign mode specific display function
    generate_cube_vertices_gpu(point_vals)
    glutDisplayFunc(display_gpu)
    glutKeyboardFunc(onKeyDown)
    glutMouseFunc(onMouseButton)
    glutMotionFunc(onMouseDrag)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70.0, 640.0 / 360.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    # Setup buffers for parallelization
    VERTEX_VBO, COLOR_VBO = glGenBuffers(2)
    glBindBuffer(GL_ARRAY_BUFFER, VERTEX_VBO)
    glBufferData(GL_ARRAY_BUFFER, COORDS, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, COLOR_VBO)
    glBufferData(GL_ARRAY_BUFFER, COLORS, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    # Render Loop
    glutMainLoop()


if __name__ == "__main__":
    main()
