import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('static', exist_ok=True)

w, h = 400, 240
bg = (238, 238, 238)
color = (136, 136, 136)
font_size = 36

try:
    font = ImageFont.truetype('arial.ttf', font_size)
except:
    font = ImageFont.load_default()

for i in range(1, 11):
    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)
    text = f'help{i}.png'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w-tw)//2, (h-th)//2), text, fill=color, font=font)
    img.save(f'static/help{i}.png')

print('10张占位图片已生成 static/help1.png ~ static/help10.png') 