Part 2 Overview: Perspective Projection and Rasterization


1. Scene Setup

A scene was constructed using a list of 3D triangles. Each triangle is defined by:

[(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (R, G, B)]

Multiple triangles were added at different depths and positions to visualize the effect of perspective.



2. Perspective Projection

Each 3D vertex was projected onto a 2D image plane using:

x_proj = x / z
y_proj = y / z

Then normalized 2D coordinates were mapped to screen coordinates:

x_screen = int((x_proj + 1) * WIDTH / 2)
y_screen = int((1 - y_proj) * HEIGHT / 2)

Also computed 1/z per vertex to approximate depth for sorting purposes.



3. Rasterization

Each triangle was filled using a line equation test. This determines whether a pixel lies inside the triangle:

w1 = line_equation(A, B, x, y)
w2 = line_equation(B, C, x, y)
w3 = line_equation(C, A, x, y)

If all values are of the same sign, the pixel is inside the triangle.



4. Depth Sorting

Before rasterization, triangles were sorted by their average 1/z value:

projected_triangles.sort(key=lambda t: t[0])

This ensured that farther triangles were drawn first, and closer triangles overwrote them correctly.