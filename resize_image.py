from PIL import Image
import os

# This file is used to resize the images to the same size, for overleaf paper.

def resize_images(input_folder, output_folder, target_size=(640, 480)):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            with Image.open(os.path.join(input_folder, filename)) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # save images
                output_path = os.path.join(output_folder, filename)
                resized_img.save(output_path, quality=95)
                print(f"处理完成: {filename}")

input_folder = "D:\桌面\image"
output_folder = "D:\桌面\imagess"
resize_images(input_folder, output_folder)