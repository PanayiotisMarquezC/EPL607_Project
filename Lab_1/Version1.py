from PIL import Image, ImageDraw

# Image dimensions
width, height = 1024, 720
image = Image.new("RGB", (width, height), "black")
draw = ImageDraw.Draw(image)

# Define triangle vertices
v1 = (300, 100)
v2 = (100, 500)
v3 = (500, 500)

# Draw triangle using PIL
draw.line([v1, v2], fill="red", width=1)
draw.line([v2, v3], fill="red", width=1)
draw.line([v3, v1], fill="red", width=1)

# Save the image
image.save("triangle.png")
image.show()
