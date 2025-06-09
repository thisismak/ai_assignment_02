# 習作一：自動搜集圖像數據集與初步處理

## 學生資料
- 姓名：麥志榮
- 學號：23816955
- 主題編號：5
- 主題名稱：各種不同品種的狗

# 程式運行記錄
- 安裝流程及執行流程
1. 安裝python 3.10
https://www.python.org/downloads/release/python-3100/
2. VScode中安裝Python插件
Python + Python Debugger
3. 升級 pip 到最新版本
python -m pip install --upgrade pip
4. 安裝C++
https://aka.ms/vs/17/release/vc_redist.x64.exe
5. 安裝依賴
python -m pip install pillow tensorflow imagehash numpy requests playwright
playwright install
6. TensorFlow 2.16.1 是已知與 Windows 上的 Python 3.10 兼容的穩定版本。
pip uninstall tensorflow
pip install tensorflow==2.16.1
pip show tensorflow
7. 運行程式
python script.py


- 運作日誌
## script result
$ python clean_dataset.py
2025-06-09 14:27:20.389869: I tensorflow/core/util/port.cc:113] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.    
2025-06-09 14:27:24.775534: I tensorflow/core/util/port.cc:113] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.    
Downloading data from https://storage.googleapis.com/tensorflow/keras-applications/resnet/resnet50_weights_tf_dim_ordering_tf_kernels.h5
102967424/102967424 ━━━━━━━━━━━━━━━━━━━━ 29s 0us/step  
Downloading data from https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt
10484/10484 ━━━━━━━━━━━━━━━━━━━━ 0s 0us/step
清理統計: {'清理前總圖片數': 4000, '移除的重複圖片數': 99, '移除的不相關圖片數': 2311, '清理後總圖 
片數': 1590, '唯一網域數': 2, '品種分佈': {'Dachshund': 109, 'Maltese': 205, 'Pomeranian': 214, 'Chihuahua': 163, 'Poodle': 133, 'Shih Tzu': 150, 'Miniature Schnauzer': 172, 'Yorkshire Terrier': 201, 'Shiba Inu': 50, 'Labrador Retriever': 193}}
數據集清理成功完成。
最終統計: {'清理前總圖片數': 4000, '移除的重複圖片數': 99, '移除的不相關圖片數': 2311, '清理後總圖 
片數': 1590, '唯一網域數': 2, '品種分佈': {'Dachshund': 109, 'Maltese': 205, 'Pomeranian': 214, 'Chihuahua': 163, 'Poodle': 133, 'Shih Tzu': 150, 'Miniature Schnauzer': 172, 'Yorkshire Terrier': 201, 'Shiba Inu': 50, 'Labrador Retriever': 193}, '估計爬取頁數': 70}

## breed_distribution.csv
breed,image_count
Maltese,400
Yorkshire Terrier,400
Pomeranian,400
Chihuahua,400
Miniature Schnauzer,400
Shih Tzu,400
Poodle,400
Dachshund,400
Shiba Inu,400
Labrador Retriever,400


## cleaning_report.csv
指標,值
清理前總圖片數,4000
移除的重複圖片數,99
移除的不相關圖片數,2311
清理後總圖片數,1590
唯一網域數,2
品種分佈,"{'Dachshund': 109, 'Maltese': 205, 'Pomeranian': 214, 'Chihuahua': 163, 'Poodle': 133, 'Shih Tzu': 150, 'Miniature Schnauzer': 172, 'Yorkshire Terrier': 201, 'Shiba Inu': 50, 'Labrador Retriever': 193}"
估計爬取頁數,70


## image_cleaning_output.log
2025-06-09 14:28:10,916 - INFO - 圖像 dog_images\Dachshund\Dachshund_0_0.jpg 分類為狗 (類別: redbone, 置信度: 0.82)
2025-06-09 14:28:11,262 - WARNING - 圖像 dog_images\Dachshund\Dachshund_1_1.jpg 未分類為狗 (類別: Rhodesian ridgeback, 置信度: 0.33)
2025-06-09 14:28:11,262 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_1_1.jpg
2025-06-09 14:28:11,651 - INFO - 圖像 dog_images\Dachshund\Dachshund_2_2.jpg 分類為狗 (類別: black-and-tan coonhound, 置信度: 0.81)
2025-06-09 14:28:12,010 - WARNING - 圖像 dog_images\Dachshund\Dachshund_3_3.jpg 未分類為狗 (類別: Sussex spaniel, 置信度: 0.20)
2025-06-09 14:28:12,010 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_3_3.jpg
2025-06-09 14:28:12,415 - WARNING - 圖像 dog_images\Dachshund\Dachshund_4_4.jpg 未分類為狗 (類別: miniature pinscher, 置信度: 0.60)
2025-06-09 14:28:12,415 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_4_4.jpg
2025-06-09 14:28:12,775 - INFO - 圖像 dog_images\Dachshund\Dachshund_5_5.jpg 分類為狗 (類別: black-and-tan coonhound, 置信度: 0.79)
2025-06-09 14:28:13,103 - INFO - 圖像 dog_images\Dachshund\Dachshund_6_6.jpg 分類為狗 (類別: Irish setter, 置信度: 0.86)
2025-06-09 14:28:13,448 - WARNING - 圖像 dog_images\Dachshund\Dachshund_7_7.jpg 未分類為狗 (類別: redbone, 置信度: 0.43)
2025-06-09 14:28:13,448 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_7_7.jpg
2025-06-09 14:28:13,771 - WARNING - 圖像 dog_images\Dachshund\Dachshund_8_8.jpg 未分類為狗 (類別: whippet, 置信度: 0.25)
2025-06-09 14:28:13,771 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_8_8.jpg
2025-06-09 14:28:14,119 - WARNING - 圖像 dog_images\Dachshund\Dachshund_9_9.jpg 未分類為狗 (類別: Doberman, 置信度: 0.13)
2025-06-09 14:28:14,119 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_9_9.jpg
2025-06-09 14:28:14,448 - WARNING - 圖像 dog_images\Dachshund\Dachshund_10_10.jpg 未分類為狗 (類別: golden retriever, 置信度: 0.41)
2025-06-09 14:28:14,448 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_10_10.jpg
2025-06-09 14:28:14,792 - WARNING - 圖像 dog_images\Dachshund\Dachshund_11_11.jpg 未分類為狗 (類別: vizsla, 置信度: 0.65)
2025-06-09 14:28:14,792 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_11_11.jpg

## image_cleaning.log
2025-06-09 14:28:10,916 - INFO - 圖像 dog_images\Dachshund\Dachshund_0_0.jpg 分類為狗 (類別: redbone, 置信度: 0.82)
2025-06-09 14:28:11,262 - WARNING - 圖像 dog_images\Dachshund\Dachshund_1_1.jpg 未分類為狗 (類別: Rhodesian ridgeback, 置信度: 0.33)
2025-06-09 14:28:11,262 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_1_1.jpg
2025-06-09 14:28:11,651 - INFO - 圖像 dog_images\Dachshund\Dachshund_2_2.jpg 分類為狗 (類別: black-and-tan coonhound, 置信度: 0.81)
2025-06-09 14:28:12,010 - WARNING - 圖像 dog_images\Dachshund\Dachshund_3_3.jpg 未分類為狗 (類別: Sussex spaniel, 置信度: 0.20)
2025-06-09 14:28:12,010 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_3_3.jpg
2025-06-09 14:28:12,415 - WARNING - 圖像 dog_images\Dachshund\Dachshund_4_4.jpg 未分類為狗 (類別: miniature pinscher, 置信度: 0.60)
2025-06-09 14:28:12,415 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_4_4.jpg
2025-06-09 14:28:12,775 - INFO - 圖像 dog_images\Dachshund\Dachshund_5_5.jpg 分類為狗 (類別: black-and-tan coonhound, 置信度: 0.79)
2025-06-09 14:28:13,103 - INFO - 圖像 dog_images\Dachshund\Dachshund_6_6.jpg 分類為狗 (類別: Irish setter, 置信度: 0.86)
2025-06-09 14:28:13,448 - WARNING - 圖像 dog_images\Dachshund\Dachshund_7_7.jpg 未分類為狗 (類別: redbone, 置信度: 0.43)
2025-06-09 14:28:13,448 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_7_7.jpg
2025-06-09 14:28:13,771 - WARNING - 圖像 dog_images\Dachshund\Dachshund_8_8.jpg 未分類為狗 (類別: whippet, 置信度: 0.25)
2025-06-09 14:28:13,771 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_8_8.jpg
2025-06-09 14:28:14,119 - WARNING - 圖像 dog_images\Dachshund\Dachshund_9_9.jpg 未分類為狗 (類別: Doberman, 置信度: 0.13)
2025-06-09 14:28:14,119 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_9_9.jpg
2025-06-09 14:28:14,448 - WARNING - 圖像 dog_images\Dachshund\Dachshund_10_10.jpg 未分類為狗 (類別: golden retriever, 置信度: 0.41)
2025-06-09 14:28:14,448 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_10_10.jpg
2025-06-09 14:28:14,792 - WARNING - 圖像 dog_images\Dachshund\Dachshund_11_11.jpg 未分類為狗 (類別: vizsla, 置信度: 0.65)
2025-06-09 14:28:14,792 - INFO - 移除不相關圖像: dog_images\Dachshund\Dachshund_11_11.jpg

## image_failure_report.csv
keyword,url,alt_text,failure_stage,failure_reason
Dachshund,https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg,Google,processing,Compression or processing error
Maltese,https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg,Google,processing,Compression or processing error
Maltese,https://r.bing.com/rp/UYtUYDcn1oZlFG-YfBPz59zejYI.svg,在此处拖放图像,processing,Compression or processing error
Maltese,https://r.bing.com/rp/KC_nX2_tPPyFvVw1RK20Yu1FyDk.svg,粘贴图像或 URL,processing,Compression or processing error
Maltese,https://r.bing.com/rp/5yVAKe18OXFf_XvuMPJO61GQVsc.svg,筛选器,processing,Compression or processing error
Maltese,https://r.bing.com/rp/bSmUb4SdiINJy0O6_CJPQxImT6o.svg,筛选器,processing,Compression or processing error
Maltese,https://r.bing.com/rp/-A5v-hTPFRzEXEMXLO7124F8nt0.svg,GIF 自动播放设置,processing,Compression or processing error
Maltese,https://r.bing.com/rp/Q5BJPjebyYN5QiqznkcMQmLrF9U.svg,关闭对话框,processing,Compression or processing error
Pomeranian,https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg,Google,processing,Compression or processing error
Chihuahua,https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg,Google,processing,Compression or processing error
Poodle,https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg,Google,processing,Compression or processing error
Poodle,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTY_G64jeJMDFue_woAcx4H0EifwWTZTVcRew&s,Maltese vs Poodle: A Comprehensive Guide to Choosing Pet,database,Duplicate URL
Shih Tzu,https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg,Google,processing,Compression or processing error
Shih Tzu,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTVQ0KmkUQUcdtot6WlijmjyudZJVqihRAoCg&s,Maltese Shih Tzu Mix Breed Guide: Characteristics & Facts | Bored Panda,database,Duplicate URL
Shih Tzu,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFVrXURc7Y0ZGYbkMhWIZOTzDQWBEAbhaz-w&s,"Maltese Shih Tzu breed insights: care, personality & expert tips | Lyka Blog",database,Duplicate URL
Shih Tzu,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_ILr0WWqkqd0usWjlUqKqtxLBO7FVG_3Z2Q&s,Maltese Shih Tzu Dog Breed Information | Temperament & Health,database,Duplicate URL
Shih Tzu,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdEJPkyczCMqpxeivRAtJFvqzw7bx316hj6Q&s,Maltese Shih Tzu Feeding Guide | Dog Feeding Guide | ProDog Raw,database,Duplicate URL
Shih Tzu,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSHYTIi1jTmNStAig66jdwIUQTluIRUfAN9A&s,The Maltese Shih Tzu (Malshi): Best Dog Ever! - PetHelpful,database,Duplicate URL
Shih Tzu,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRc1h-A9Xj4dhXlh0jDLt52HpeyEOSPtJC0pQ&s,"Shih Poo | Discover the Shihpoo, a Shih Tzu Poodle Mix Full of Personality",database,Duplicate URL

## 功能完成度自評

（依照評分標準勾選完成的項目）

### 清理和處理（40 分）

- 清理下載的圖像（30 分）

  - [X] 清除不相關的圖像
  - [X] 清除重複的圖像
  - [X] 使用圖片分類模型輔助清理

- 數據集縮減或擴充（10 分）
  - [X] 清除後的圖像數量在 500 至 2000 之間
  - [X] 必要時完成額外圖像收集

### 數據報告（25 分）

- 統計數據（15 分）

  - [X] 列出收集的原始圖像數量
  - [X] 列出清除後的圖像數量

- 來源分析（10 分）
  - [X] 統計爬取的頁面數量
  - [X] 統計不同來源網站（唯一網域）數量

### 自動化和代碼質量（35 分）

- 自動化程度（20 分）

  - [X] 實現圖像分類模型的自動化應用
  - [X] 實現重複圖像的自動檢測
  - [X] 實現數據統計的自動化生成

- 程式碼結構和註釋（15 分）
  - [X] 使用函數和類來組織代碼
  - [X] 代碼結構清晰易讀
  - [X] 註釋完整且有意義