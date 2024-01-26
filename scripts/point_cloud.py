from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *
import numpy as np
import sys

global COORDS, COLORS, X_AXIS, Y_AXIS, Z_AXIS, \
	PITCH, ROLL, YAW, MODE, VERTEX_VBO, COLOR_VBO


def display_cpu():
	global X_AXIS, Y_AXIS, Z_AXIS, \
		PITCH, ROLL, YAW, COORDS, COLORS

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()

	# Performing 'camera' translation and rotation
	glTranslatef(X_AXIS, Y_AXIS, Z_AXIS)
	glRotatef(PITCH, 1.0, 0.0, 0.0)
	glRotatef(ROLL, 0.0, 1.0, 0.0)
	glRotatef(YAW, 0.0, 0.0, 1.0)

	# Draw each face of each cube
	i = 0
	glBegin(GL_QUADS)
	for p1, p2, p3, p4, p5, p6, p7, p8 in COORDS:
		glColor3f(COLORS[i][0], COLORS[i][1], COLORS[i][2])

		glVertex3f(p1[0], p1[1], p1[2])
		glVertex3f(p2[0], p2[1], p2[2])
		glVertex3f(p3[0], p3[1], p3[2])
		glVertex3f(p4[0], p4[1], p4[2])

		glVertex3f(p5[0], p5[1], p5[2])
		glVertex3f(p6[0], p6[1], p6[2])
		glVertex3f(p7[0], p7[1], p7[2])
		glVertex3f(p8[0], p8[1], p8[2])

		glVertex3f(p1[0], p1[1], p1[2])
		glVertex3f(p4[0], p4[1], p4[2])
		glVertex3f(p8[0], p8[1], p8[2])
		glVertex3f(p5[0], p5[1], p5[2])

		glVertex3f(p1[0], p1[1], p1[2])
		glVertex3f(p3[0], p3[1], p3[2])
		glVertex3f(p7[0], p7[1], p7[2])
		glVertex3f(p6[0], p6[1], p6[2])

		glVertex3f(p1[0], p1[1], p1[2])
		glVertex3f(p2[0], p2[1], p2[2])
		glVertex3f(p6[0], p6[1], p6[2])
		glVertex3f(p5[0], p5[1], p5[2])

		glVertex3f(p4[0], p4[1], p4[2])
		glVertex3f(p3[0], p3[1], p3[2])
		glVertex3f(p7[0], p7[1], p7[2])
		glVertex3f(p8[0], p8[1], p8[2])

		i += 1

	glEnd()
	glutSwapBuffers()


def display_gpu():
	global X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW, \
		VERTEX_VBO, COLOR_VBO, COORDS
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
	glDrawArrays(GL_QUADS, 0, 4*6*len(COORDS))
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


def generate_cube_vertices_cpu(point_vals):
	global X_AXIS, Y_AXIS, Z_AXIS, COORDS, COLORS, PITCH, ROLL, YAW
	X_AXIS, Y_AXIS, Z_AXIS, PITCH, ROLL, YAW = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
	coords_arr = []
	colors_arr = []
	# Add 8 vertices in cube array and add colors for each vertex
	for x, y, z, r, g, b in point_vals:
		# Coord sum for centroid calculation
		X_AXIS += x
		Y_AXIS += y
		Z_AXIS += z
		cube = []
		cube.append([x, y, z])
		cube.append([x+0.25, y, z])
		cube.append([x+0.25, y+0.25, z])
		cube.append([x, y+0.25, z])
		cube.append([x, y, z+0.25])
		cube.append([x+0.25, y, z+0.25])
		cube.append([x+0.25, y+0.25, z+0.25])
		cube.append([x, y+0.25, z+0.25])
		coords_arr.append(cube)
		colors_arr.append([r, g, b])
	COORDS = np.array(coords_arr, dtype=np.float32)
	COLORS = np.array(colors_arr, dtype=np.float32)
	calculate_centroid()

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
		vertex_2 = [x+0.25, y, z]
		vertex_3 = [x+0.25, y+0.25, z]
		vertex_4 = [x, y+0.25, z]
		vertex_5 = [x, y, z+0.25]
		vertex_6 = [x+0.25, y, z+0.25]
		vertex_7 = [x+0.25, y+0.25, z+0.25]
		vertex_8 = [x, y+0.25, z+0.25]

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
	if key == 'q':
		sys.exit()
	elif key == 'w':
		Y_AXIS -= 0.1
	elif key == 's':
		Y_AXIS += 0.1
	elif key == 'a':
		X_AXIS += 0.1
	elif key == 'd':
		X_AXIS -= 0.1
	elif key == 'z':
		Z_AXIS -= 0.1
	elif key == 'x':
		Z_AXIS += 0.1
	elif key == 'i':
		YAW -= 1.0
	elif key == 'k':
		YAW += 1.0
	elif key == 'j':
		PITCH += 1.0
	elif key == 'l':
		PITCH -= 1.0
	elif key == 'n':
		ROLL += 1.0
	elif key == 'm':
		ROLL -= 1.0
	# Clamping rotation
	np.clip(ROLL, -360.0, 360.0)
	np.clip(PITCH, -360.0, 360.0)
	np.clip(YAW, -360.0, 360.0)
	# Re-render
	if MODE == "cpu":
		display_cpu()
	elif MODE == "gpu":
		display_gpu()


def main():
	global COORDS, COLORS, VERTEX_VBO, COLOR_VBO, MODE
	# IO using numpy
	try:
		file = sys.argv[1]
		MODE = sys.argv[2]
	except IndexError:
		print("Command line execution needs 2 arguments: \
			path to txt file and \"gpu\" or \"cpu\"")
		return

	# IO Skipping header row in csv
	point_vals = np.loadtxt(file, delimiter=',', skiprows=1)
	# OpenGL Boilerplate setup
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowSize(500, 500)
	glutInitWindowPosition(200, 200)
	window = glutCreateWindow("Point Cloud Viewer")
	# Assign mode specific display function
	if MODE == "cpu":
		generate_cube_vertices_cpu(point_vals)
		glutDisplayFunc(display_cpu)
	elif MODE == "gpu":
		generate_cube_vertices_gpu(point_vals)
		glutDisplayFunc(display_gpu)
	else:
		print("Please use either \
			\"gpu\" or \"cpu\" as the mode argument")
		return
	glutKeyboardFunc(onKeyDown)
	glClearColor(0.0, 0.0, 0.0, 0.0)
	glClearDepth(1.0)
	glDepthFunc(GL_LESS)
	glEnable(GL_DEPTH_TEST)
	glShadeModel(GL_SMOOTH)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(70., 640.0 / 360.0, 0.1, 100.0)
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
