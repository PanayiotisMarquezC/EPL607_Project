import imageio.v2 as imageio

# Video writer setup
output_filename = "animation.mp4"
fps = 20
frame_count = 60  # total frames

with imageio.get_writer(output_filename, fps=fps) as writer:
    for frame in range(frame_count):
        filename = f"frame_{frame:03d}.png"
        print(f"Adding {filename} to video...")
        image = imageio.imread(filename)
        writer.append_data(image)

print(f"✅ Saved video as {output_filename}")
