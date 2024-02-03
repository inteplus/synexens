#!/usr/bin/python3


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *

import synexens as s
from mt import np, geo3d, glfw, pd


class ShipSpeed:
    """Speed parameters for the camera ship.

    Parameters
    ----------
    move : float
        speed to move along the z-axis of the camera ship. Range: [-10, +10] mm/s. Step: 0.01 mm/s
    roll : float
        speed to rotate about the z-axis of the camera ship. Range: [-0.05, +0.05] rad/s. Step: 0.01 mm/s.
    pitch : float
        speed to rotate about the y-axis of the camera ship. Range: [-0.05, +0.05] rad/s. Step: 0.01 mm/s.
    yaw : float
        speed to rotate about the x-axis of the camera ship. Range: [-0.05, +0.05] rad/s. Step: 0.01 mm/s.

    """

    def __init__(self, move: float, roll: float, pitch: float, yaw: float):
        self.move = move
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw


ship_speed = ShipSpeed(0, 0, 0, 0)
global COORDS, COLORS, VERTEX_VBO, COLOR_VBO, CAMERA_POSE, LAST_TS, device, window


def update_point_cloud():
    global COORDS, COLORS, VERTEX_VBO, COLOR_VBO, device

    frame = device.get_last_frame_data()
    if frame is None:
        return

    depth_image = frame[s.SYFRAMETYPE_DEPTH]
    point_image = device.get_depth_point_cloud(depth_image, True)
    # depth_image = (depth_image // 32).astype(np.uint8)

    h, w = depth_image.shape[:2]
    n_points = h * w

    depth_arr = depth_image.reshape((n_points,))  # range from 0 to 7000
    # print(f"depth: min {depth_arr.min(axis=0)} max {depth_arr.max(axis=0)}")

    infra_image = frame[s.SYFRAMETYPE_IR]  # range from 0 to 2047
    # infra_image = (infra_image // 8).astype(np.uint8)

    point_arr = point_image.reshape((n_points, 3)) / 50.0
    invalid_arr = (depth_arr < 100) | (depth_arr > 5000) | (point_arr[:, 2] < 1e-4)

    indices = []
    for i in range(n_points - w - 1):
        if i % w == w - 1:
            continue
        if (
            invalid_arr[i]
            or invalid_arr[i + 1]
            or invalid_arr[i + w]
            or invalid_arr[i + w + 1]
        ):
            continue
        max_depth = max(
            depth_arr[i], depth_arr[i + 1], depth_arr[i + w], depth_arr[i + w + 1]
        )
        min_depth = min(
            depth_arr[i], depth_arr[i + 1], depth_arr[i + w], depth_arr[i + w + 1]
        )
        if max_depth > min_depth + 20:
            continue

        indices.append((i, i + 1, i + w + 1, i + w))

    if False:
        color_image = device.get_depth_color(depth_image)
        color_arr = color_image.reshape((n_points, 3)) / 10.0
    else:
        color_arr = infra_image.reshape((n_points, 1)).astype(np.float32) / 2048.0
        color_arr = np.repeat(color_arr, 3, axis=1)

    # print(f"indices: {len(indices)}")
    # print(f"point: min {point_arr.min(axis=0)} max {point_arr.max(axis=0)}")
    # print(f"color: min {color_arr.min(axis=0)} max {color_arr.max(axis=0)}")

    COORDS = point_arr[indices]
    COLORS = color_arr[indices]

    # copy the data to the buffer
    glBindBuffer(GL_ARRAY_BUFFER, VERTEX_VBO)
    glBufferData(GL_ARRAY_BUFFER, COORDS, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, COLOR_VBO)
    glBufferData(GL_ARRAY_BUFFER, COLORS, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # print(f"frame found {COORDS.shape} {COLORS.shape} {COORDS.dtype} {COLORS.dtype}")


def display_gpu():
    global CAMERA_POSE, LAST_TS, ship_speed, VERTEX_VBO, COLOR_VBO, COORDS

    # measure time
    ts = pd.Timestamp.utcnow()
    sec = (ts - LAST_TS).total_seconds()
    LAST_TS = ts

    CAMERA_POSE = geo3d.rot3d_z(ship_speed.roll * sec) * CAMERA_POSE
    CAMERA_POSE = geo3d.rot3d_x(ship_speed.pitch * sec) * CAMERA_POSE
    CAMERA_POSE = geo3d.rot3d_y(ship_speed.yaw * sec) * CAMERA_POSE
    CAMERA_POSE = geo3d.Aff3d(offset=(0, 0, ship_speed.move * sec)) * CAMERA_POSE

    glGetError()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Performing translation and rotation
    glLoadMatrixf(CAMERA_POSE.matrix.T)

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


def generate_cube_vertices_gpu(point_vals):
    global CAMERA_POSE, LAST_TS, COORDS, COLORS
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
    Z -= 50.0
    CAMERA_POSE = geo3d.Aff3d(offset=(X, Y, Z))
    LAST_TS = pd.Timestamp.utcnow()


def on_key(window, key: int, scancode: int, action: int, mods: int):
    # print(f"on_key: key {key} scancode {scancode} action {action} mods {mods}")

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, glfw.TRUE)
        return

    if action == glfw.RELEASE:
        if key in (glfw.KEY_E, glfw.KEY_Q):
            ship_speed.roll = 0
        elif key in (glfw.KEY_S, glfw.KEY_W):
            ship_speed.pitch = 0
        elif key in (glfw.KEY_A, glfw.KEY_D):
            ship_speed.yaw = 0
    else:
        if key == glfw.KEY_Z:
            ship_speed.move = max(ship_speed.move - 0.01, -10.0)
        elif key == glfw.KEY_C:
            ship_speed.move = min(ship_speed.move + 0.01, 10.0)
        elif key == glfw.KEY_W:
            ship_speed.pitch = min(ship_speed.pitch + 0.04, 0.50)
        elif key == glfw.KEY_S:
            ship_speed.pitch = max(ship_speed.pitch - 0.04, -0.50)
        elif key == glfw.KEY_D:
            ship_speed.yaw = min(ship_speed.yaw + 0.04, 0.50)
        elif key == glfw.KEY_A:
            ship_speed.yaw = max(ship_speed.yaw - 0.04, -0.50)
        elif key == glfw.KEY_Q:
            ship_speed.roll = max(ship_speed.roll - 0.04, -1.0)
        elif key == glfw.KEY_E:
            ship_speed.roll = min(ship_speed.roll + 0.04, 1.0)
        elif key == glfw.KEY_X:
            ship_speed.move = 0


def on_mouse_button(window, button: int, action: int, mod: int):
    print(f"on_mouse_button: button {button} action {action} mod {mod}")


def on_mouse_move(window, xpos: float, ypos: float):
    print(f"on_mouse_move: xpos {xpos} ypos {ypos}")


def on_scroll(window, xoffset: float, yoffset: float):
    print(f"on_scroll: xoffset {xoffset} yoffset {yoffset}")


def main():
    global COORDS, COLORS, VERTEX_VBO, COLOR_VBO, device, window

    with s.Device() as the_device:
        device = the_device
        print(device.info)
        device.resolution = s.SYRESOLUTION_640_480
        device.stream_on(s.SYSTREAMTYPE_DEPTHIR)

        # IO Skipping header row in csv
        point_vals = np.loadtxt("generated_points_100.txt", delimiter=",", skiprows=1)

        # OpenGL Boilerplate setup
        with glfw.scoped_create_window(
            1200, 800, "Synexens Viewer", None, None
        ) as the_window:
            window = the_window

            glfw.set_window_pos(window, 100, 100)
            glfw.make_context_current(window)

            # Assign mode specific display function
            generate_cube_vertices_gpu(point_vals)
            glfw.set_key_callback(window, on_key)
            glfw.set_cursor_pos_callback(window, on_mouse_move)
            glfw.set_mouse_button_callback(window, on_mouse_button)
            glfw.set_scroll_callback(window, on_scroll)
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
            while not glfw.window_should_close(window):
                update_point_cloud()
                display_gpu()

                glfw.swap_buffers(window)
                glfw.poll_events()


if __name__ == "__main__":
    main()
