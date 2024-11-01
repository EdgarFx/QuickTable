from PIL import Image
from os import path
import json
import os
import sys
import django

sys.path.append(r'C:\Users\dell\Desktop\Junior\CIE6004\CIE_Pro\mysite')
sys.path.append(r'C:\Users\dell\Desktop\Junior\CIE6004\CIE_Pro\mysite\mysite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

dirpath = 'C:\\Users\\dell\\Desktop\\Junior\\CIE6004\\CIE_Pro\\mysite\\conversion\\QuickTable\\'

directories = os.listdir(dirpath + "Detection\\det_output\\")


j = 0
for di in directories:
    img = Image.open((dirpath + "Detection\\det_output\\%s\\%s.png")%(di,di)).convert('RGBA')
    try:
        f = open((dirpath + "Detection\\det_output\\%s\\%s.json")%(di,di),"r")
    except:
        continue
    lst = json.load(f)

    i = 0
    for dic in lst:
        cropped = img.crop((dic['bbox'][0],dic['bbox'][1],dic['bbox'][0]+dic['bbox'][2],dic['bbox'][1]+dic['bbox'][3]))  # (left, upper, right, lower)
        if not os.path.exists(dirpath + "det_tables\\"):
            os.makedirs(dirpath + "det_tables\\")
        cropped.save(dirpath + "det_tables\\table_%d_%d.png"%(j,i))
        i+=1
    j+=1