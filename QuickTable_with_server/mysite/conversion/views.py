# Create your views here.
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import re
import os
import fitz
from django.http import FileResponse
from os import path
import jieba as jb
import datetime

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

        pix.writePNG(imagePath + '\\' + 'images_%s.png' % pg)

    endTime_pdf2img = datetime.datetime.now() # end time
    print('pdf conversion time=', (endTime_pdf2img - startTime_pdf2img).seconds, 's')

    
def gci(file,imagePath):
    pyMuPDF_fitz(file,imagePath)


@api_view(["POST"])
def convert(request):
    # #get absolute path
    dir_path = path.dirname(path.abspath(__file__))
    
    # os.system("py " + dir_path + "\\test\\test.py")
    file = request.FILES['pdf'].name
    gci(dir_path + "\\QuickTable\\" + file,dir_path + '\\QuickTable\\images')
    # gci(file,dir_path + '\\QuickTable\\images')

    # 接下来就是对images里生成的图片先进行表格检测，这一步不需要区分中英文（用的都可以的模型）
    image_files = os.listdir(dir_path + '\\QuickTable\\images')
    temp = dir_path + "\\QuickTable\\" 
    for fi in image_files:
        os.system(('py ' + temp + 'Detection\\deploy\\infer.py --model_dir=' + temp + 'Detection\\output_inference\\picodet_lcnet_x1_0_fgd_layout_table_infer\\ \
        --image_file=' + temp + 'images\\%s --device=CPU --output_dir=' + temp + 'Detection\\det_output\\ --save_results')%fi)

    # 然后，切割得到表格图像
    os.system('py ' + temp + 'Detection\\deploy\\cut.py')

    # 接下来，即为表格结构识别和文本识别，并将得到excel文件，此时要判断中英文，由用户指定
    language = request.data.get("language")             # Chinese or English
    if language != "Chinese" and language != "English":
        return Response("Wrong input",status=status.HTTP_403_FORBIDDEN)


    tables = os.listdir(temp + "det_tables")
    for table in tables:
        if language == "Chinese":
            os.system(('py '+ temp + 'TableStructure\\ppstructure\\table\\predict_table.py ' + \
                '--det_model_dir=' + temp + 'TableStructure\\ppstructure\\inference\\ch_PP-OCRv3_det_infer ' + \
                '--rec_model_dir=' + temp + 'TableStructure\\ppstructure\\inference\\ch_PP-OCRv3_rec_infer ' + \
                '--table_model_dir=' + temp + 'TableStructure\\ppstructure\\inference\\ch_ppstructure_mobile_v2.0_SLANet_infer ' + \
                '--rec_char_dict_path=' + temp + 'TableStructure\\ppocr\\utils\\ppocr_keys_v1.txt ' + \
                '--table_char_dict_path=' + temp + 'TableStructure\\ppocr\\utils\\dict\\table_structure_dict_ch.txt ' \
                '--image_dir=' + temp + 'det_tables\\%s --output=' + temp + 'output\\%s')%(table,table[:-4]))
        elif language == "English":
            os.system(('py ' + temp + 'TableStructure\\ppstructure\\table\\predict_table.py ' +  \
                '--det_model_dir=' + temp + 'TableStructure\\ppstructure\\inference\\en_PP-OCRv3_det_infer ' + \
                '--rec_model_dir=' + temp + 'TableStructure\\ppstructure\\inference\\en_PP-OCRv3_rec_infer ' +  \
                '--table_model_dir=' + temp + 'TableStructure\\ppstructure\\inference\\en_ppstructure_mobile_v2.0_SLANet_infer ' + \
                '--rec_char_dict_path=' + temp + 'TableStructure\\ppocr\\utils\\ppocr_keys_v1.txt ' + \
                '--table_char_dict_path=' + temp + 'TableStructure\\ppocr\\utils\\dict\\table_structure_dict_ch.txt ' + \
                '--image_dir=' + temp + 'det_tables\\%s --output=' + temp + 'output\\%s')%(table,table[:-4]))

    excel_dir_path = temp + "output\\"
    num = len(os.listdir(excel_dir_path))
    print(num)
    cos_sim = []
    for i in range(num):
        df = pd.read_excel(excel_dir_path + "table_" + str(i) + "_0\\table_" + str(i) + "_0.xlsx")       
        col_name = list(df)
        key_word = request.data.get("keywords").split(" ")
        words = []
        for i in col_name:
            for j in df[i]:
                searchobj = re.compile(u"[\u4e00-\u9fa5]+").search(str(j))
                if searchobj != None:
                    words.append(searchobj.string)

        for i in col_name:
            searchobj = re.compile(u"[\u4e00-\u9fa5]+").search(str(i))
            if searchobj != None:
                words.append(searchobj.string)

        cos_similarity = 0
        for i in key_word:
            sep = list(jb.cut(i))
            length = len(sep)
            for w in words:
                vec = np.zeros(length)
                #calculate similarity vector
                for j in range(length):
                    n = len(sep[j])
                    if (w == sep[j]):
                        vec[j] = 1
                        break
                    elif (len(w) <= n):
                        vec[j] = 0
                        break
                    else:
                        for k in range(len(w) - n + 1):
                            if w[k:k + n] == sep[j]:
                                vec[j] += 1
                #calculate cosine similarity
                a = np.ones(length)
                if (vec.dot(a) != 0):
                    cos_similarity += vec.dot(a)
        
        cos_sim.append(cos_similarity)
    
    cos_sim = np.argsort(np.array(cos_sim))[::-1]

    f = open(excel_dir_path + "table_" + str(cos_sim[0]) + "_0\\table_" + str(cos_sim[0]) + "_0.xlsx", "rb")
    res = FileResponse(f)
    res["Content-Type"] = "application/octet-stream"
    res["Content-Disposition"] = 'filename="response.xlsx"'
    return res

