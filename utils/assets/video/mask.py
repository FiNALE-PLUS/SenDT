from math import ceil

from PIL import Image, ImageDraw

PV_SIZE = (600, 600)
MAX_REFLECTION_BRIGHTNESS = 2/3

def generate_finale_pv_mask(source_width: int, source_height: int, output_size: tuple[int, int] = PV_SIZE) -> Image:
    mask_img = Image.new(mode='RGBA', size=output_size)
    
    aspect_ratio = source_width / source_height
    
    resized_height = output_size[0] * (output_size[1] / source_height)
    source_switch_y = ceil((output_size[1] / 2) + (resized_height / 2))
    
    mask_draw = ImageDraw.Draw(mask_img)
    mask_draw.fill = True
    mask_draw.rectangle([(0, 0), (source_width, source_switch_y)], (255, 255, 255, 255))
    
    gradient_height = output_size[1] - source_switch_y
    for gradient_y in range(gradient_height):
        line_y = source_switch_y + gradient_y
        brightness = (255, 255, 255, int(255 * (1 - (gradient_y / gradient_height)) * MAX_REFLECTION_BRIGHTNESS))
        mask_draw.line([(0, line_y), (output_size[0] - 1, line_y)], fill=brightness)
    mask_img.save(r'D:\FFmpeg testing\maska.png')
    return mask_img