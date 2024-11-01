from PIL import Image
import json
import os


directories = os.listdir("Detection/det_output/")

j = 0
for di in directories:
    img = Image.open("Detection/det_output/%s/%s.png"%(di,di)).convert('RGBA')
    try:
        f = open("Detection/det_output/%s/%s.json"%(di,di),"r")
    except:
        continue
    lst = json.load(f)

    i = 0
    for dic in lst:
        cropped = img.crop((dic['bbox'][0],dic['bbox'][1],dic['bbox'][0]+dic['bbox'][2],dic['bbox'][1]+dic['bbox'][3]))  # (left, upper, right, lower)
        if not os.path.exists("det_tables/"):
            os.makedirs("det_tables/")
        cropped.save("det_tables/table_%d_%d.png"%(j,i))
        i+=1
    j+=1