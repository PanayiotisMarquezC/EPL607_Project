import pywavefront
from PIL import Image
import os

# === SETUP CANVAS ===
WIDTH, HEIGHT = 1024, 1024
image = Image.new("RGB", (WIDTH, HEIGHT), "black")
pixels = image.load()

# === LOAD MODEL (ignore missing .mtl file) ===
pywavefront.logger.setLevel('ERROR')  # Suppress material warnings
scene = pywavefront.Wavefront(
    'man.obj',  # Make sure this is the correct filename
    collect_faces=True,
    create_materials=True,
    parse=True,
    strict=False
)

# === NORMALIZE & CENTER MODEL ===
all_vertices = [tuple(v[:3]) for v in scene.vertices]
min_x = min(v[0] for v in all_vertices)
max_x = max(v[0] for v in all_vertices)
min_y = min(v[1] for v in all_vertices)
max_y = max(v[1] for v in all_vertices)
min_z = min(v[2] for v in all_vertices)
max_z = max(v[2] for v in all_vertices)

center = (
    (min_x + max_x) / 2,
    (min_y + max_y) / 2,
    (min_z + max_z) / 2
)
scale = 2.0 / max(max_x - min_x, max_y - min_y, max_z - min_z)

def normalize(vertex):
    x, y, z = vertex[:3]
    x = (x - center[0]) * scale
    y = (y - center[1]) * scale
    z = (z - center[2]) * scale + 2.5  # push forward into view
    return (x, y, z)

# === PROJECTION ===
def project_vertex(vertex):
    x, y, z = vertex
    if z == 0:
        z = 1e-5
    x_proj = x / z
    y_proj = y / z
    x_screen = int((x_proj + 1) * WIDTH / 2)
    y_screen = int((1 - y_proj) * HEIGHT / 2)
    return (x_screen, y_screen)

# === RASTERIZATION ===
def line_equation(v1, v2, x, y):
    return (v2[0] - v1[0]) * (y - v1[1]) - (v2[1] - v1[1]) * (x - v1[0])

def draw_triangle(p1, p2, p3, color):
    min_x = max(min(p1[0], p2[0], p3[0]), 0)
    max_x = min(max(p1[0], p2[0], p3[0]), WIDTH - 1)
    min_y = max(min(p1[1], p2[1], p3[1]), 0)
    max_y = min(max(p1[1], p2[1], p3[1]), HEIGHT - 1)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            w1 = line_equation(p1, p2, x, y)
            w2 = line_equation(p2, p3, x, y)
            w3 = line_equation(p3, p1, x, y)
            if (w1 >= 0 and w2 >= 0 and w3 >= 0) or (w1 <= 0 and w2 <= 0 and w3 <= 0):
                pixels[x, y] = color

# === DRAW MODEL ===
for mesh in scene.mesh_list:
    for face in mesh.faces:
        if len(face) == 3:
            v1 = normalize(scene.vertices[face[0]])
            v2 = normalize(scene.vertices[face[1]])
            v3 = normalize(scene.vertices[face[2]])
            p1 = project_vertex(v1)
            p2 = project_vertex(v2)
            p3 = project_vertex(v3)
            draw_triangle(p1, p2, p3, (255, 255, 255))  # white

# === SAVE IMAGE ===
image.save("rendered_model.png")
image.show()
