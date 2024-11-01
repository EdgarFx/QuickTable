# This script implements the pipeline of quicktable
# 直接 python quicktable.py 应该就可以把这个脚本跑起来

import datetime
import os
import fitz  # fitz is pip install PyMuPDF
import cv2
import shutil
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# First, convert the input pdf file into images
def pyMuPDF_fitz(pdfPath, imagePath):
    startTime_pdf2img = datetime.datetime.now()  # start time

    print("imagePath=" + imagePath)
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0)
        zoom_x = 1.4
        zoom_y = 1.4
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)

        if not os.path.exists(imagePath): 
            os.makedirs(imagePath)  

        pix.writePNG(imagePath + '/' + 'images_%s.png' % pg)

    endTime_pdf2img = datetime.datetime.now() # end time
    print('pdf conversion time=', (endTime_pdf2img - startTime_pdf2img).seconds, 's')

# 文件是要用户给的
file = '600999.pdf'

imagePath = 'images'
def gci(file):
    pyMuPDF_fitz(file,imagePath)

gci(file)


# 接下来就是对images里生成的图片先进行表格检测，这一步不需要区分中英文（用的都可以的模型）
image_files = os.listdir('images')
for fi in image_files:
    os.system('python detection/deploy/infer.py --model_dir=detection/output_inference/picodet_lcnet_x1_0_fgd_layout_table_infer/ \
    --image_file=images/%s --device=CPU --output_dir=detection/det_output/ --save_results'%fi)


# 然后，切割得到表格图像
os.system('python detection/deploy/cut.py')


# 接下来，即为表格结构识别和文本识别，并将得到excel文件，此时要判断中英文，由用户指定
language = "Chinese" # or English


tables = os.listdir("det_tables")

for table in tables:
    if language == "Chinese":
        os.system('python table_structure/ppstructure/table/predict_table.py \
            --det_model_dir=table_structure/ppstructure/inference/ch_PP-OCRv3_det_infer \
            --rec_model_dir=table_structure/ppstructure/inference/ch_PP-OCRv3_rec_infer \
            --table_model_dir=table_structure/ppstructure/inference/ch_ppstructure_mobile_v2.0_SLANet_infer \
            --rec_char_dict_path=table_structure/ppocr/utils/ppocr_keys_v1.txt \
            --table_char_dict_path=table_structure/ppocr/utils/dict/table_structure_dict_ch.txt \
            --image_dir=det_tables/%s --output=output/%s'%(table,table[:-4]))
    elif language == "English":
        os.system('python table_structure/ppstructure/table/predict_table.py \
            --det_model_dir=table_structure/ppstructure/inference/en_PP-OCRv3_det_infer \
            --rec_model_dir=table_structure/ppstructure/inference/en_PP-OCRv3_rec_infer \
            --table_model_dir=table_structure/ppstructure/inference/en_ppstructure_mobile_v2.0_SLANet_infer \
            --rec_char_dict_path=table_structure/ppocr/utils/ppocr_keys_v1.txt \
            --table_char_dict_path=table_structure/ppocr/utils/dict/table_structure_dict_ch.txt \
            --image_dir=det_tables/%s --output=output/%s'%(table,table[:-4]))



