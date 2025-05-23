from PIL import Image

# Image dimensions
width, height = 1024, 1024
image = Image.new("RGB", (width, height), "black")
pixels = image.load()

# Define triangle vertices
A = (300, 100)
B = (100, 500)
C = (500, 500)

def line_equation(v1, v2, x, y):
    """ Determines which side of the line a point (x, y) is on """
    return (v2[0] - v1[0]) * (y - v1[1]) - (v2[1] - v1[1]) * (x - v1[0])

# Loop through all pixels in the image
for y in range(height):
    for x in range(width):
        w1 = line_equation(A, B, x, y)
        w2 = line_equation(B, C, x, y)
        w3 = line_equation(C, A, x, y)

        # Check if the point is inside the triangle 
        if (w1 >= 0 and w2 >= 0 and w3 >= 0) or (w1 <= 0 and w2 <= 0 and w3 <= 0):
            pixels[x, y] = (255, 0, 0)  # Fill with red

# Save and show the image
image.save("filled_triangle.png")
image.show()