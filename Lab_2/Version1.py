from PIL import Image

# === CONFIG ===
WIDTH, HEIGHT = 1024, 1024
BACKGROUND_COLOR = (0, 0, 0)

# === SETUP IMAGE ===
image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
pixels = image.load()

# === TRIANGLES IN 3D ===
# Each triangle = [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (R, G, B)]
triangles = [
    # Green triangle, farther and to the right
    [(1.3, -0.5, 5), (1.5, 1.2, 5), (1.0, 0.5, 5), (0, 255, 0)],

    # Red triangle, closer and centered
    [(-0.5, -0.5, 2), (0.5, 0, 2), (0.0, 0.5, 2), (255, 0, 0)],

    # Blue triangle, also close and shifted downward
    [(-0.5, -1.5, 2), (0.5, -1.5, 2), (0.5, 0.5, 2), (0, 0, 255)],

    # Random triangle, also close and shifted downward
    [(1.5, -1.5, 3), (0.5, -1.5, 4), (0.5, 0.5, 3), (50, 10, 100)]
]

# === PERSPECTIVE PROJECTION ===
def perspective_project(vertex):
    x, y, z = vertex
    if z == 0:
        z = 1e-5  # Avoid divide-by-zero
    x_proj = x / z
    y_proj = y / z
    return (x_proj, y_proj, 1 / z)

def to_screen(x_proj, y_proj):
    """Convert normalized coordinates (-1 to 1) to image space"""
    x_screen = int((x_proj + 1) * WIDTH / 2)
    y_screen = int((1 - y_proj) * HEIGHT / 2)
    return x_screen, y_screen

# === RASTERIZATION ===
def line_equation(v1, v2, x, y):
    return (v2[0] - v1[0]) * (y - v1[1]) - (v2[1] - v1[1]) * (x - v1[0])

def draw_triangle(screen_coords, color):
    A, B, C = screen_coords

    # Clip to screen bounds
    min_x = max(min(A[0], B[0], C[0]), 0)
    max_x = min(max(A[0], B[0], C[0]), WIDTH - 1)
    min_y = max(min(A[1], B[1], C[1]), 0)
    max_y = min(max(A[1], B[1], C[1]), HEIGHT - 1)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            w1 = line_equation(A, B, x, y)
            w2 = line_equation(B, C, x, y)
            w3 = line_equation(C, A, x, y)

            if (w1 >= 0 and w2 >= 0 and w3 >= 0) or (w1 <= 0 and w2 <= 0 and w3 <= 0):
                pixels[x, y] = color

# === MAIN PIPELINE ===
projected_triangles = []

for tri in triangles:
    verts = tri[:3]
    color = tri[3]
    projected = [perspective_project(v) for v in verts]
    screen_coords = [to_screen(x, y) for (x, y, inv_z) in projected]
    avg_inv_z = sum(inv_z for (_, _, inv_z) in projected) / 3
    projected_triangles.append((avg_inv_z, screen_coords, color))

# Sort by depth: draw farthest (lowest 1/z) first
projected_triangles.sort(key=lambda t: t[0])

# Rasterize all triangles
for _, tri_2d, color in projected_triangles:
    draw_triangle(tri_2d, color)

# === SAVE & SHOW ===
image.save("project_p2_result_3.png")
image.show()
