EPL607 Rasterizer Project - Final README

Team Member
Panayiotis Marquez Charalambous

Programming Language
Python

Image Processing and Rendering Libraries
Pillow (PIL)

Used to create, manipulate, and save rendered PNG images.
PyWavefront

Used to load 3D models from Wavefront .obj files including mesh and face data.
NumPy

Used to perform matrix and vector operations for transformations.
imageio[ffmpeg]
Used to compile a series of PNG frames into a single MP4 video file.


Final Project Overview

This project implements a complete 3D software rasterizer from scratch using Python. The system supports model loading, camera projection, lighting, rasterization, and frame-by-frame animation rendering.


1. 3D Model Rendering

This component handles the conversion of 3D object geometry into a 2D raster image.

The .obj file is parsed using PyWavefront to extract a list of vertices and triangular faces.

The model is normalized to fit a unit cube, centered at the origin, and scaled appropriately to ensure visibility.

A custom perspective projection routine converts each 3D vertex into screen-space coordinates using x/z and y/z, simulating a pinhole camera.

A triangle rasterizer fills each triangle by evaluating pixel positions using edge functions and barycentric coordinates.

To ensure depth correctness, a Z-buffer (2D array) is used. It stores the closest Z value rendered at each pixel to discard hidden surfaces.

This part of the code demonstrates a foundational understanding of how 3D



2. Phong Shading

Lighting is handled with a realistic Phong lighting model.

Each vertex is assigned a normal vector, computed as the average of its adjacent face normals.

During rasterization, normals are interpolated across the surface of each triangle using barycentric weights.

The Phong shading model includes:

Ambient lighting, which simulates constant background light.

Diffuse lighting, computed as the dot product between the surface normal and the light direction, simulating matte surfaces.

Specular lighting, computed from the reflection vector and the viewer direction, adding shiny highlights.

A custom Material class encapsulates material properties like diffuse color, specular color, and shininess, allowing reusable material definitions.

A Light class allows placement and intensity control of a directional or point light.

Per-pixel lighting is calculated during rasterization, providing smooth shading across triangle surfaces.



3. Animation (Transformation Matrices)

The animation module showcases dynamic transformation of the 3D model over time:

Transformation matrices (4×4) are constructed and applied to every vertex before projection.

Each matrix encodes:

Scaling of the object uniformly.

Rotation around the Y-axis using a standard rotation matrix.

Translation in 3D space to ensure proper framing of the model in the camera view.

These transformations are combined into a single transformation matrix using matrix multiplication (T * R * S).

For animation, the model is rendered in a loop over 60 frames, incrementing the Y-axis rotation angle per frame to simulate a smooth rotation.

For each frame:

A fresh image and Z-buffer are created.

Transformed vertices are projected and rasterized.

The image is saved as frame_000.png, frame_001.png, ..., frame_059.png.

All images are compiled into animation.mp4 using imageio.get_writer, creating a real-time rendering sequence.



How to Run the Project

Install Dependencies: pip install pillow numpy pywavefront imageio[ffmpeg]

 Step 1: Generate Animation Frames (in Animation folder EPL607_Project/Lab3/Animation)

 python Version2_360rotation_60frames.py (in video folder EPL607_Project/Lab3/Animation/video)

 Step 2: Create the MP4 Animation

 python make_video.py



Output Files

frame_000.png to frame_059.png – 60 rendered frames of the rotating model.

animation.mp4 – final 3-second smooth animation.



Summary

This project showcases a complete graphics pipeline implemented in Python:

Geometry loading

Triangle rasterization

Lighting and shading

Depth buffering

Transformation matrices

Animation and video export

It demonstrates how to go from a raw 3D model file to a fully lit and animated render using fundamental rendering techniques.