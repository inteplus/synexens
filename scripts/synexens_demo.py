#!/usr/bin/python3

import glm

import synexens as s
from mt import np, geo3d, gl, glfw, pd, ctx


class ShipSpeed:
    """Speed parameters for the camera ship.

    Parameters
    ----------
    move : float
        speed to move along the z-axis of the camera ship. Range: [-1, +1] m/s. Step: 1cm/s
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
height = 480
width = 640


class Camera:
    def __init__(self, pose, last_ts):
        self.pose = pose
        self.last_ts = last_ts


camera = Camera(geo3d.Aff3d(offset=(0, 0, -3.0)), pd.Timestamp.utcnow())


def initial_point_cloud():
    posits = np.random.rand(height * width, 3).astype(np.float32)
    colors = np.random.randint(256, size=height * width * 3, dtype=np.uint8).reshape(
        height * width, 3
    )
    return posits, colors


def framebuffer_size(window, width: int, height: int):
    gl.glViewport(0, 0, width, height)


def update_point_cloud(device):
    frame = device.get_last_frame_data()
    if frame is None:
        return

    depth_image = frame[s.SYFRAMETYPE_DEPTH]  # range from 0 to 7000
    point_image = device.get_depth_point_cloud(
        depth_image, True
    )  # range from -1 to 8, in metres
    # depth_image = (depth_image // 32).astype(np.uint8)

    posits = (
        point_image.reshape(height * width, 3).astype(np.float32) / 10000
    )  # to have range [0,1]

    # depth_arr = depth_image.reshape((n_points,))  # range from 0 to 7000
    # print(f"depth: min {depth_arr.min(axis=0)} max {depth_arr.max(axis=0)}")

    infra_image = frame[s.SYFRAMETYPE_IR]  # range from 0 to 2047
    # infra_image = (infra_image // 8).astype(np.uint8)

    color_image = device.get_depth_color(depth_image)  # range from 0 to 255
    # now mix up with infra to get range [0,1]
    colors = (
        (infra_image.astype(np.float32) / 2048)
        + (color_image.astype(np.float32) / 256) * 0.3
    ) / 1.3
    colors = (colors * 256.0).astype(np.uint8).reshape(height * width, 3)

    return posits, colors


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
            ship_speed.move = max(ship_speed.move - 0.01, -1.0)
        elif key == glfw.KEY_C:
            ship_speed.move = min(ship_speed.move + 0.01, 1.0)
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


def load_shaders_old():
    shader_srcs = {
        gl.GL_VERTEX_SHADER: """
#version 330

layout(location = 0) in vec4 imgcoord;

uniform ivec2 imgres;
uniform sampler2D position; // point cloud (in 10m per unit)
uniform sampler2D color;  // color in RGB ([0,1] each)
uniform mat4 view;
uniform mat4 projection;

void main()
{
gl_Position = vec4(imgcoord.xy, 0, 1);
}
        """,
        gl.GL_GEOMETRY_SHADER: """
#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform ivec2 imgres;
uniform sampler2D position; // point cloud (in 10m per unit)
uniform sampler2D color;  // color in RGB ([0,1] each)
uniform mat4 view;
uniform mat4 projection;

out vec3 v_color;

void main()
{
    ivec2 tl = ivec2(gl_in[0].gl_Position.xy * vec2(imgres));
    if(tl.x < 0 || tl.x+1 >= imgres.x || tl.y < 0 || tl.y+1 >= imgres.y)
        return;

    gl_Position = projection * view * vec4(tl.x, tl.y, 0.0, 1.0);
    v_color = texelFetch(color, tl, 0).xyz;
    EmitVertex();

    gl_Position = projection * view * vec4(tl.x+1, tl.y, 0.0, 1.0);
    v_color = texelFetch(color, ivec2(tl.x+1, tl.y), 0).xyz;
    EmitVertex();

    gl_Position = projection * view * vec4(tl.x, tl.y+1, 0.0, 1.0);
    v_color = texelFetch(color, ivec2(tl.x, tl.y+1), 0).xyz;
    EmitVertex();

    gl_Position = projection * view * vec4(tl.x+1, tl.y+1, 0.0, 1.0);
    v_color = texelFetch(color, ivec2(tl.x+1, tl.y+1), 0).xyz;
    EmitVertex();

    EndPrimitive();
}
        """,
        gl.GL_FRAGMENT_SHADER: """
#version 330

in vec3 v_color;
layout(location = 0) out vec4 color;

void main()
{
    color = vec4(v_color, 1.0);
}
        """,
    }

    compiled_shaders = [gl.compileShader(v, k) for k, v in shader_srcs.items()]
    return gl.compileProgram(*compiled_shaders)


def load_shaders():
    shader_srcs = {
        gl.GL_VERTEX_SHADER: """
#version 330

layout(location = 0) in vec4 imgcoord;

uniform ivec2 imgres;
uniform sampler2D position; // point cloud (in 10m per unit)
uniform sampler2D color;  // color in RGB ([0,1] each)
uniform mat4 view;
uniform mat4 projection;

void main()
{
gl_Position = vec4(imgcoord.xy, 0, 1);
}
        """,
        gl.GL_GEOMETRY_SHADER: """
#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform ivec2 imgres;
uniform sampler2D position; // point cloud (in 10m per unit)
uniform sampler2D color;  // color in RGB ([0,1] each)
uniform mat4 view;
uniform mat4 projection;

out vec3 v_color;

void main()
{
    ivec2 tl = ivec2(round(gl_in[0].gl_Position.xy * vec2(imgres)));
    if(tl.x < 0 || tl.x+1 >= imgres.x || tl.y < 0 || tl.y+1 >= imgres.y)
        return;

    ivec2 tr = ivec2(tl.x+1, tl.y);
    ivec2 bl = ivec2(tl.x, tl.y+1);
    ivec2 br = ivec2(tr.x, tr.y+1);
    vec3 p_tl = texelFetch(position, tl, 0).xyz * 10;  // 1m per unit now
    vec3 p_tr = texelFetch(position, tr, 0).xyz * 10;
    vec3 p_bl = texelFetch(position, bl, 0).xyz * 10;
    vec3 p_br = texelFetch(position, br, 0).xyz * 10;
    vec3 p_max = max(max(p_tl, p_tr), max(p_bl, p_br));
    vec3 p_min = min(min(p_tl, p_tr), min(p_bl, p_br));
    vec3 d_max = p_max - p_min;
    float v_max = max(max(d_max.x, d_max.y), d_max.z);
    if(v_max > 0.05f) // larger than 5cm
        return;

    gl_Position = projection * view * vec4(p_tl, 1.0);
    v_color = texelFetch(color, tl, 0).xyz;
    EmitVertex();

    gl_Position = projection * view * vec4(p_tr, 1.0);
    v_color = texelFetch(color, tr, 0).xyz;
    EmitVertex();

    gl_Position = projection * view * vec4(p_bl, 1.0);
    v_color = texelFetch(color, bl, 0).xyz;
    EmitVertex();

    gl_Position = projection * view * vec4(p_br, 1.0);
    v_color = texelFetch(color, br, 0).xyz;
    EmitVertex();

    EndPrimitive();
}
        """,
        gl.GL_FRAGMENT_SHADER: """
#version 330

in vec3 v_color;
layout(location = 0) out vec4 color;

void main()
{
    color = vec4(v_color, 1.0);
}
        """,
    }

    compiled_shaders = [gl.compileShader(v, k) for k, v in shader_srcs.items()]
    return gl.compileProgram(*compiled_shaders)


@ctx.contextmanager
def create_textures():
    posit_tex, color_tex = gl.glGenTextures(2)

    try:
        yield posit_tex, color_tex
    finally:
        gl.glDeleteTextures(2, [posit_tex, color_tex])


def update_textures(posits, colors, posit_tex, color_tex):
    # posit_tex
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, posit_tex)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGB32F,
        width,
        height,
        0,
        gl.GL_RGB,
        gl.GL_FLOAT,
        glm.array.as_reference(posits).ptr,
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    # color_tex
    gl.glActiveTexture(gl.GL_TEXTURE0 + 1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, color_tex)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGB8,
        width,
        height,
        0,
        gl.GL_RGB,
        gl.GL_UNSIGNED_BYTE,
        glm.array.as_reference(colors).ptr,
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    # gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


def main():
    # OpenGL Boilerplate setup
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    with glfw.scoped_create_window(1200, 800, "Synexens Viewer", None, None) as window:
        glfw.set_window_pos(window, 100, 100)
        glfw.make_context_current(window)

        # Assign mode specific display function
        glfw.set_key_callback(window, on_key)
        glfw.set_cursor_pos_callback(window, on_mouse_move)
        glfw.set_mouse_button_callback(window, on_mouse_button)
        glfw.set_scroll_callback(window, on_scroll)
        glfw.set_framebuffer_size_callback(window, framebuffer_size)

        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)

        program = load_shaders()

        vao = gl.VAO()
        vbo = gl.VBO()
        with vao:
            vertices = np.empty((height, width, 2), dtype=np.float32)
            vertices[:, :, 0] = np.arange(width)[np.newaxis, :] / width
            vertices[:, :, 1] = np.arange(height)[:, np.newaxis] / height
            vertices = vertices.reshape((width * height, 2))
            vertices = glm.array(vertices)
            vbo.set_data(0, vertices, gl.GL_STATIC_DRAW)

        with create_textures() as texes:
            posit_tex, color_tex = texes
            posits, colors = initial_point_cloud()
            update_textures(posits, colors, posit_tex, color_tex)

            with program:
                program.set_uniform("imgres", glm.ivec2(640, 480))
                projection = glm.perspective(
                    glm.radians(50), width / height, 0.1, 100.0
                )
                program.set_uniform("projection", projection)

                with s.Device() as device:
                    print(device.info)
                    device.resolution = s.SYRESOLUTION_640_480
                    device.stream_on(s.SYSTREAMTYPE_DEPTHIR)

                    # Render Loop
                    while not glfw.window_should_close(window):
                        ret = update_point_cloud(device)
                        if ret:
                            posits, colors = ret
                            update_textures(posits, colors, posit_tex, color_tex)

                        # measure time
                        ts = pd.Timestamp.utcnow()
                        sec = (ts - camera.last_ts).total_seconds()
                        camera.last_ts = ts

                        camera.pose = geo3d.rot3d_z(ship_speed.roll * sec) * camera.pose
                        camera.pose = (
                            geo3d.rot3d_x(ship_speed.pitch * sec) * camera.pose
                        )
                        camera.pose = geo3d.rot3d_y(ship_speed.yaw * sec) * camera.pose
                        camera.pose = (
                            geo3d.Aff3d(offset=(0, 0, ship_speed.move * sec))
                            * camera.pose
                        )

                        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
                        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

                        program.set_uniform_texture_unit("position", 0)
                        program.set_uniform_texture_unit("color", 1)
                        program.set_uniform("view", camera.pose.affine)
                        with vao:
                            gl.glDrawArrays(gl.GL_POINTS, 0, width * height)

                        glfw.swap_buffers(window)
                        glfw.poll_events()


if __name__ == "__main__":
    main()
