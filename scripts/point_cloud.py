#!/usr/bin/python3

from mt import np, geo3d

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *
import sys

global COORDS, COLORS, CAMERA_POSE, MPOSE, VERTEX_VBO, COLOR_VBO, MB, MX, MY, INVALID, SPEED


def display_gpu(*args):
    global CAMERA_POSE, MPOSE, VERTEX_VBO, COLOR_VBO, COORDS, INVALID

    glutTimerFunc(50, display_gpu, 0)

    if not INVALID:
        return

    glGetError()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Performing translation and rotation
    glLoadMatrixf((MPOSE * CAMERA_POSE).matrix.T)

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

    INVALID = False


def generate_cube_vertices_gpu(point_vals):
    global CAMERA_POSE, MPOSE, MB, COORDS, COLORS, INVALID, SPEED
    X, Y, Z = 0.0, 0.0, 0.0
    coords_arr = []
    colors_arr = []
    # Add 8 vertices in cube, colors for each vertex
    for x, y, z, r, g, b in point_vals:
        X += x
        Y += y
        Z += z
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

    # Calculate centroid for all vertices across cubes in each axis
    X /= len(COORDS)
    Y /= len(COORDS)
    Z /= len(COORDS)
    Z -= 20.0
    CAMERA_POSE = geo3d.Aff3d(offset=(X, Y, Z))
    MB = None
    MPOSE = geo3d.Aff3d()
    SPEED = 1
    INVALID = True


def onKeyDown(*args):
    global CAMERA_POSE, INVALID

    # Retrieving key events and storing translation/rotation values
    key = args[0].decode("utf-8")
    if key == "q":
        sys.exit()
    elif key == "w":
        pose = geo3d.Aff3d(offset=(0, -0.1, 0))
    elif key == "s":
        pose = geo3d.Aff3d(offset=(0, 0.1, 0))
    elif key == "a":
        pose = geo3d.Aff3d(offset=(0.1, 0, 0))
    elif key == "d":
        pose = geo3d.Aff3d(offset=(-0.1, 0, 0))
    elif key == "z":
        pose = geo3d.Aff3d(offset=(0, 0, -0.1))
    elif key == "x":
        pose = geo3d.Aff3d(offset=(0, 0, +0.1))
    elif key == "i":
        pose = geo3d.rot3d_z(-0.01)
    elif key == "k":
        pose = geo3d.rot3d_z(+0.01)
    elif key == "j":
        pose = geo3d.rot3d_y(+0.01)
    elif key == "l":
        pose = geo3d.rot3d_y(-0.01)
    elif key == "n":
        pose = geo3d.rot3d_z(+0.01)
    elif key == "m":
        pose = geo3d.rot3d_z(-0.01)
    else:
        pose = None

    if pose:
        CAMERA_POSE = pose * CAMERA_POSE
        INVALID = True


def onMouseButton(button: int, state: int, x: int, y: int):
    global MB, MX, MY, CAMERA_POSE, MPOSE, INVALID, SPEED

    print(f"{button} {state} {x} {y}")

    if state == GLUT_DOWN:
        MX = x
        MY = y
        MB = button
        INVALID = True
    elif state == GLUT_UP:
        MPOSE = geo3d.Aff3d()
        if MB == GLUT_LEFT_BUTTON:
            pose = geo3d.Aff3d(
                offset=((x - MX) * 0.05 * SPEED, (y - MY) * -0.05 * SPEED, 0)
            )
            CAMERA_POSE = pose * CAMERA_POSE
            INVALID = True
        elif MB == GLUT_MIDDLE_BUTTON:
            pose = geo3d.Aff3d(
                offset=((x - MX) * 0.05 * SPEED, 0, (y - MY) * -0.05 * SPEED)
            )
            CAMERA_POSE = pose * CAMERA_POSE
            INVALID = True
        elif MB == GLUT_RIGHT_BUTTON:
            rotX = geo3d.rot3d_y((x - MX) * -0.002)
            rotY = geo3d.rot3d_x((y - MY) * -0.002)
            CAMERA_POSE = rotY * rotX * CAMERA_POSE
            INVALID = True
        elif MB == 3:  # wheel scrolling up
            SPEED *= 2
            if SPEED > 10:
                SPEED = 10
            print(f"Speed: {SPEED}")
        elif MB == 4:  # wheel scrolling down
            SPEED /= 2
            if SPEED < 0.1:
                SPEED = 0.1
            print(f"Speed: {SPEED}")


def onMouseDrag(x: int, y: int):
    global MPOSE, MB, INVALID, SPEED

    print(f"{x} {y}")

    if MB == GLUT_LEFT_BUTTON:
        MPOSE = geo3d.Aff3d(
            offset=((x - MX) * 0.05 * SPEED, (y - MY) * -0.05 * SPEED, 0)
        )
        INVALID = True
    elif MB == GLUT_MIDDLE_BUTTON:
        MPOSE = geo3d.Aff3d(
            offset=((x - MX) * 0.05 * SPEED, 0, (y - MY) * -0.05 * SPEED)
        )
        INVALID = True
    elif MB == GLUT_RIGHT_BUTTON:
        rotX = geo3d.rot3d_y((x - MX) * -0.002)
        rotY = geo3d.rot3d_x((y - MY) * -0.002)
        MPOSE = rotY * rotX
        INVALID = True


def main():
    global COORDS, COLORS, VERTEX_VBO, COLOR_VBO
    file = sys.argv[1]

    # IO Skipping header row in csv
    point_vals = np.loadtxt(file, delimiter=",", skiprows=1)
    # OpenGL Boilerplate setup
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 800)
    glutInitWindowPosition(100, 100)
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
