# QuickTable
In this work, we proposes a new pipeline to extract tables of interest in PDF files, and develops an ultra lightweight application named QuickTable accordingly.

Most of the previous research only focused on one or two tasks of table recognition and there is little research on finding tables of interest. The developed QuickTable uses the proposed pipeline based on PP-Picodet, SLANet, PPOCRv3, Text Segmentation and Cosine Similarity Analysis, which allows users to upload PDF files **from mobile devices** and **enter keywords to get tables of interest**. In addition, we have trained models in both Chinese and English so that users can upload files in **different languages**. Experiments show that the proposed pipeline is lightweight and outperforms previous approaches, demonstrating the effectiveness of our method.

## Usage
The directory QuickTable_with_server is the application that combined with the django back-end codes. 
If you don't want to deploy the software environment, you can just run the script quicktable.py in the directory QuickTable, which is a quickstart demo of our algorithm.
