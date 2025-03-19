# EPL607_Project
For your course project you will be implementing a software rasterizer. A rasterizer renders 3D geometry made of triangles by projecting it on a 2D plane and coloring each pixel based on the visibility of each triangle.


Team Members:
Panayiotis Marquez Charalambous

Programming Language:
Python

Image Processing Library:
Pillow (PIL)


Process for Rendering the Test Triangle:

1. Created a 1024x1024 pixel image with a black background.

2. Defining the Triangle:
Defined three vertices:
A (300, 100) (Top vertex)
B (100, 400) (Bottom-left vertex)
C (400, 500) (Bottom-right vertex)

3. Implementing Triangle Rasterization:
Used a line equation method to determine whether a pixel is inside the triangle.
Found the bounding box for efficiency.
The algorithm loops through all pixels within the bounding box.
If a pixel satisfies the inside-triangle condition, it is colored red (255, 0, 0).

4. Saving and Displaying the Image
Once the triangle was rendered, the PIL library was used to:
Save the final image as filled_triangle.png
Display the image on the screen