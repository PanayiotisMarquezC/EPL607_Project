import pywavefront
from PIL import Image
import math
from collections import defaultdict

# === CONFIG ===
WIDTH, HEIGHT = 1024, 1024
image = Image.new("RGB", (WIDTH, HEIGHT), "black")
pixels = image.load()
z_buffer = [[float('inf')] * WIDTH for _ in range(HEIGHT)]

# === LIGHTING ===
class Light:
    def __init__(self, position, intensity=(1, 1, 1)):
        self.position = position
        self.intensity = intensity

class Material:
    def __init__(self, diffuse, specular, shininess):
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess

light = Light(position=(0, 0, 2), intensity=(1, 1, 1))
material = Material(diffuse=(0.8, 0.1, 0.1), specular=(1.0, 1.0, 1.0), shininess=32)

# === LOAD MODEL ===
pywavefront.logger.setLevel('ERROR')
scene = pywavefront.Wavefront('man.obj', collect_faces=True, create_materials=True, parse=True, strict=False)

# === NORMALIZE VERTICES ===
all_vertices = [tuple(v[:3]) for v in scene.vertices]
min_x = min(v[0] for v in all_vertices)
max_x = max(v[0] for v in all_vertices)
min_y = min(v[1] for v in all_vertices)
max_y = max(v[1] for v in all_vertices)
min_z = min(v[2] for v in all_vertices)
max_z = max(v[2] for v in all_vertices)

center = ((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2)
scale = 2.5 / max(max_x - min_x, max_y - min_y, max_z - min_z)

def normalize_vertex(v):
    x, y, z = v[:3]
    x = (x - center[0]) * scale
    y = (y - center[1]) * scale
    z = (z - center[2]) * scale + 2.5
    return (x, y, z)

# === VECTOR MATH ===
def subtract(a, b): return tuple(a[i] - b[i] for i in range(3))
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def normalize_vector(v):
    length = math.sqrt(dot(v, v))
    return tuple(c / length for c in v) if length != 0 else (0, 0, 0)
def reflect(L, N):
    dotLN = dot(L, N)
    return tuple(2 * dotLN * N[i] - L[i] for i in range(3))

# === COMPUTE VERTEX NORMALS ===
vertex_normals = defaultdict(lambda: [0, 0, 0])
for mesh in scene.mesh_list:
    for face in mesh.faces:
        if len(face) == 3:
            v0 = normalize_vertex(scene.vertices[face[0]])
            v1 = normalize_vertex(scene.vertices[face[1]])
            v2 = normalize_vertex(scene.vertices[face[2]])
            edge1 = subtract(v1, v0)
            edge2 = subtract(v2, v0)
            face_normal = (
                edge1[1]*edge2[2] - edge1[2]*edge2[1],
                edge1[2]*edge2[0] - edge1[0]*edge2[2],
                edge1[0]*edge2[1] - edge1[1]*edge2[0]
            )
            for idx in face:
                for i in range(3):
                    vertex_normals[idx][i] += face_normal[i]

for idx in vertex_normals:
    vertex_normals[idx] = normalize_vector(vertex_normals[idx])

# === PHONG SHADING ===
def compute_phong_color(pos, normal, material, light):
    N = normalize_vector(normal)
    L = normalize_vector(subtract(light.position, pos))
    V = normalize_vector(tuple(-c for c in pos))

    if dot(N, L) < 0:
        N = tuple(-n for n in N)

    R = reflect(L, N)

    ambient = (0.1, 0.1, 0.1)
    dot_nl = max(dot(N, L), 0)
    diffuse = tuple(material.diffuse[i] * light.intensity[i] * dot_nl for i in range(3))
    dot_rv = max(dot(R, V), 0)
    specular = tuple(material.specular[i] * light.intensity[i] * (dot_rv ** material.shininess) for i in range(3))

    color = tuple(min(1, ambient[i] + diffuse[i] + specular[i]) for i in range(3))
    return tuple(int(c * 255) for c in color)

# === PROJECTION ===
def project_vertex(v):
    x, y, z = v
    if z == 0: z = 1e-5
    x_proj = x / z
    y_proj = y / z
    x_screen = int((x_proj + 1) * WIDTH / 2)
    y_screen = int((1 - y_proj) * HEIGHT / 2)
    return (x_screen, y_screen)

# === EDGE FUNCTION ===
def edge_func(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

# === DRAW TRIANGLES WITH PHONG SHADING & Z-BUFFER ===
def draw_phong(p1, p2, p3, v1, v2, v3, n1, n2, n3):
    min_x = max(min(p1[0], p2[0], p3[0]), 0)
    max_x = min(max(p1[0], p2[0], p3[0]), WIDTH - 1)
    min_y = max(min(p1[1], p2[1], p3[1]), 0)
    max_y = min(max(p1[1], p2[1], p3[1]), HEIGHT - 1)

    area = edge_func(p1, p2, p3)
    if area == 0: return

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            p = (x, y)
            w0 = edge_func(p2, p3, p)
            w1 = edge_func(p3, p1, p)
            w2 = edge_func(p1, p2, p)
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                alpha = w0 / area
                beta = w1 / area
                gamma = w2 / area

                pos = tuple(alpha * v1[i] + beta * v2[i] + gamma * v3[i] for i in range(3))
                z = pos[2]

                if z < z_buffer[y][x]:
                    z_buffer[y][x] = z
                    norm = tuple(alpha * n1[i] + beta * n2[i] + gamma * n3[i] for i in range(3))
                    color = compute_phong_color(pos, norm, material, light)
                    pixels[x, y] = color

# === MAIN LOOP ===
for mesh in scene.mesh_list:
    for face in mesh.faces:
        if len(face) == 3:
            idx0, idx1, idx2 = face
            v0 = normalize_vertex(scene.vertices[idx0])
            v1 = normalize_vertex(scene.vertices[idx1])
            v2 = normalize_vertex(scene.vertices[idx2])

            n0 = vertex_normals[idx0]
            n1 = vertex_normals[idx1]
            n2 = vertex_normals[idx2]

            p0 = project_vertex(v0)
            p1 = project_vertex(v1)
            p2 = project_vertex(v2)

            draw_phong(p0, p1, p2, v0, v1, v2, n0, n1, n2)

# === OUTPUT ===
image.save("rendered_phong_zbuffer.png")
image.show()
