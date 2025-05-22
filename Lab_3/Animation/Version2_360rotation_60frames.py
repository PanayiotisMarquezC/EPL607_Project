import pywavefront
from PIL import Image
import math
import numpy as np
from collections import defaultdict

# === CONFIG ===
WIDTH, HEIGHT = 1024, 1024
TOTAL_FRAMES = 60  # for a full 360° rotation

# === LIGHTING & MATERIAL ===
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

# === NORMALIZATION ===
all_vertices = [np.array(v[:3]) for v in scene.vertices]
min_bound = np.min(all_vertices, axis=0)
max_bound = np.max(all_vertices, axis=0)
center = (min_bound + max_bound) / 2
scale = 2.5 / np.max(max_bound - min_bound)
translation = np.array([0.0, 0.0, 2.5])

# === TRANSFORMATIONS ===
def build_transformation_matrix(angle_deg, scale_factor, translation_vec):
    angle_rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    S = np.diag([scale_factor, scale_factor, scale_factor, 1.0])
    R = np.array([
        [cos_a, 0, sin_a, 0],
        [0,     1, 0,     0],
        [-sin_a,0, cos_a, 0],
        [0,     0, 0,     1]
    ])
    T = np.identity(4)
    T[:3, 3] = translation_vec
    return T @ R @ S

def transform_vertex(v, matrix):
    vec = np.array([v[0], v[1], v[2], 1.0])
    result = matrix @ vec
    return tuple(result[:3])

# === VECTOR UTILS ===
def subtract(a, b): return tuple(a[i] - b[i] for i in range(3))
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def normalize_vector(v):
    length = math.sqrt(dot(v, v))
    return tuple(c / length for c in v) if length != 0 else (0, 0, 0)
def reflect(L, N):
    dotLN = dot(L, N)
    return tuple(2 * dotLN * N[i] - L[i] for i in range(3))

# === VERTEX NORMALS (same across all frames) ===
vertex_normals = defaultdict(lambda: [0, 0, 0])
for mesh in scene.mesh_list:
    for face in mesh.faces:
        if len(face) == 3:
            v0 = (scene.vertices[face[0]][0:3] - center) * scale
            v1 = (scene.vertices[face[1]][0:3] - center) * scale
            v2 = (scene.vertices[face[2]][0:3] - center) * scale
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

# === SHADING ===
def compute_phong_color(pos, normal, material, light):
    N = normalize_vector(normal)
    L = normalize_vector(subtract(light.position, pos))
    V = normalize_vector(tuple(-c for c in pos))
    if dot(N, L) < 0:
        N = tuple(-n for n in N)
    R = reflect(L, N)
    ambient = (0.1, 0.1, 0.1)
    diffuse = tuple(material.diffuse[i] * light.intensity[i] * max(dot(N, L), 0) for i in range(3))
    specular = tuple(material.specular[i] * light.intensity[i] * (max(dot(R, V), 0) ** material.shininess) for i in range(3))
    color = tuple(min(1, ambient[i] + diffuse[i] + specular[i]) for i in range(3))
    return tuple(int(c * 255) for c in color)

def project_vertex(v):
    x, y, z = v
    if z == 0: z = 1e-5
    x_proj = x / z
    y_proj = y / z
    x_screen = int((x_proj + 1) * WIDTH / 2)
    y_screen = int((1 - y_proj) * HEIGHT / 2)
    return (x_screen, y_screen)

def edge_func(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

def draw_phong(p1, p2, p3, v1, v2, v3, n1, n2, n3, pixels, z_buffer):
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
                    pixels[x, y] = compute_phong_color(pos, norm, material, light)

# === ANIMATION FRAME LOOP ===
for frame in range(TOTAL_FRAMES):
    angle_deg = (frame / TOTAL_FRAMES) * 360
    print(f"Rendering frame {frame:03d}...")

    transform = build_transformation_matrix(angle_deg, scale, translation)
    image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    pixels = image.load()
    z_buffer = [[float('inf')] * WIDTH for _ in range(HEIGHT)]

    for mesh in scene.mesh_list:
        for face in mesh.faces:
            if len(face) == 3:
                idx0, idx1, idx2 = face
                v0 = transform_vertex(scene.vertices[idx0][:3] - center, transform)
                v1 = transform_vertex(scene.vertices[idx1][:3] - center, transform)
                v2 = transform_vertex(scene.vertices[idx2][:3] - center, transform)

                n0 = vertex_normals[idx0]
                n1 = vertex_normals[idx1]
                n2 = vertex_normals[idx2]

                p0 = project_vertex(v0)
                p1 = project_vertex(v1)
                p2 = project_vertex(v2)

                draw_phong(p0, p1, p2, v0, v1, v2, n0, n1, n2, pixels, z_buffer)

    image.save(f"frame_{frame:03d}.png")
