import os
import sqlite3
import logging
import csv
from urllib.parse import urlparse
from collections import Counter
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
import shutil
from pathlib import Path
import imagehash

# 設置日誌記錄，使用 UTF-8 編碼
logging.basicConfig(
    filename='image_cleaning.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 配置常量
DB_NAME = "dog_images.db"
OUTPUT_DIR = "dog_images"
CLEANED_DIR = "cleaned_dog_images"
TARGET_IMAGE_COUNT_MIN = 1000
TARGET_IMAGE_COUNT_MAX = 5000
IMAGE_SIZE = (224, 224)
DOG_BREEDS = [
    "Maltese", "Yorkshire Terrier", "Pomeranian", "Chihuahua", "Miniature Schnauzer",
    "Shih Tzu", "Poodle", "Dachshund", "Shiba Inu", "Labrador Retriever"
]
CONFIDENCE_THRESHOLD = 0.7

# 初始化 ResNet50 模型
model = ResNet50(weights='imagenet')

def init_database():
    """初始化 SQLite 數據庫連接。"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

def load_imagenet_labels():
    """加載 ImageNet 標籤。"""
    labels_path = tf.keras.utils.get_file(
        'ImageNetLabels.txt',
        'https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt'
    )
    with open(labels_path, 'r') as f:
        labels = f.read().splitlines()[1:]
    return labels

def is_dog_image(image_path, labels):
    """使用 ResNet50 分類圖像，檢查是否為狗。"""
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        predictions = model.predict(img_array, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]
        
        if 151 <= predicted_class <= 268 and confidence >= CONFIDENCE_THRESHOLD:
            logging.info(f"圖像 {image_path} 分類為狗 (類別: {labels[predicted_class]}, 置信度: {confidence:.2f})")
            return True
        else:
            logging.warning(f"圖像 {image_path} 未分類為狗 (類別: {labels[predicted_class]}, 置信度: {confidence:.2f})")
            return False
    except Exception as e:
        logging.error(f"分類圖像 {image_path} 時出錯: {str(e)}")
        return False

def get_unique_domains(cursor):
    """從數據庫提取唯一網域。"""
    cursor.execute("SELECT url FROM images")
    urls = [row[0] for row in cursor.fetchall()]
    domains = set()
    for url in urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain:
                domains.add(domain)
        except Exception as e:
            logging.warning(f"解析 URL {url} 時出錯: {str(e)}")
    return domains

def export_cleaning_report(stats, filename="cleaning_report.csv"):
    """導出清理報告到 CSV。"""
    headers = ["指標", "值"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for key, value in stats.items():
            writer.writerow([key, value])
    logging.info(f"已導出清理報告到 {filename}")

def clean_dataset():
    """清理數據集，移除不相關和重複圖像。"""
    conn, cursor = init_database()
    labels = load_imagenet_labels()
    
    # 創建清理後目錄
    if not os.path.exists(CLEANED_DIR):
        os.makedirs(CLEANED_DIR)
    for breed in DOG_BREEDS:
        breed_dir = os.path.join(CLEANED_DIR, breed.replace(' ', '_'))
        if not os.path.exists(breed_dir):
            os.makedirs(breed_dir)
    
    # 獲取數據庫中的圖像
    cursor.execute("SELECT id, url, alt_text, filename, breed FROM images")
    images = cursor.fetchall()
    
    total_images = len(images)
    duplicates_removed = 0
    irrelevant_removed = 0
    cleaned_images = 0
    breed_counts = Counter()
    seen_hashes = set()
    
    for img_id, url, alt_text, filename, breed in images:
        if not os.path.exists(filename):
            logging.warning(f"圖像文件 {filename} 不存在，跳過")
            continue
        
        # 檢查圖像有效性並計算哈希
        try:
            with Image.open(filename) as img:
                img.verify()  # 驗證圖像完整性
            with Image.open(filename) as img:  # 重新打開以進行哈希
                img_hash = str(imagehash.average_hash(img))
                if img_hash in seen_hashes:
                    logging.info(f"檢測到重複圖像: {filename}")
                    duplicates_removed += 1
                    cursor.execute("DELETE FROM images WHERE id = ?", (img_id,))
                    if os.path.exists(filename):
                        os.remove(filename)
                    continue
                seen_hashes.add(img_hash)
        except Exception as e:
            logging.error(f"圖像 {filename} 處理時出錯: {str(e)}")
            irrelevant_removed += 1
            cursor.execute("DELETE FROM images WHERE id = ?", (img_id,))
            if os.path.exists(filename):
                os.remove(filename)
            continue
        
        # 分類圖像
        if not is_dog_image(filename, labels):
            logging.info(f"移除不相關圖像: {filename}")
            irrelevant_removed += 1
            cursor.execute("DELETE FROM images WHERE id = ?", (img_id,))
            if os.path.exists(filename):
                os.remove(filename)
            continue
        
        # 複製到清理後目錄
        cleaned_filename = os.path.join(CLEANED_DIR, breed.replace(' ', '_'), os.path.basename(filename))
        shutil.copy(filename, cleaned_filename)
        cursor.execute("UPDATE images SET filename = ? WHERE id = ?", (cleaned_filename, img_id))
        cleaned_images += 1
        breed_counts[breed] += 1
    
    conn.commit()
    
    # 檢查數據集大小
    if cleaned_images < TARGET_IMAGE_COUNT_MIN:
        logging.warning(f"清理後數據集有 {cleaned_images} 張圖片，低於最小值 {TARGET_IMAGE_COUNT_MIN}。需要額外採集。")
    elif cleaned_images > TARGET_IMAGE_COUNT_MAX:
        logging.warning(f"清理後數據集有 {cleaned_images} 張圖片，超過最大值 {TARGET_IMAGE_COUNT_MAX}。隨機移除多餘圖片。")
        cursor.execute("SELECT id, filename, breed FROM images")
        remaining_images = cursor.fetchall()
        np.random.shuffle(remaining_images)
        excess = cleaned_images - TARGET_IMAGE_COUNT_MAX
        for img_id, filename, breed in remaining_images[:excess]:
            cursor.execute("DELETE FROM images WHERE id = ?", (img_id,))
            if os.path.exists(filename):
                os.remove(filename)
            cleaned_images -= 1
            breed_counts[breed] -= 1
        conn.commit()
    
    # 分析唯一網域
    unique_domains = get_unique_domains(cursor)
    
    # 生成統計數據
    stats = {
        "清理前總圖片數": total_images,
        "移除的重複圖片數": duplicates_removed,
        "移除的不相關圖片數": irrelevant_removed,
        "清理後總圖片數": cleaned_images,
        "唯一網域數": len(unique_domains),
        "品種分佈": dict(breed_counts)
    }
    
    logging.info(f"清理統計: {stats}")
    print(f"清理統計: {stats}")
    
    export_cleaning_report(stats)
    
    conn.close()
    return stats

def main():
    """主函數，執行清理和報告生成。"""
    try:
        stats = clean_dataset()
        logging.info("數據集清理成功完成。")
        print("數據集清理成功完成。")
        
        shutil.copy('image_cleaning.log', 'image_cleaning_output.log')
        
        pages_crawled = len(DOG_BREEDS) * 7
        stats["估計爬取頁數"] = pages_crawled
        logging.info(f"最終統計: {stats}")
        print(f"最終統計: {stats}")
        export_cleaning_report(stats)
        
    except Exception as e:
        logging.error(f"主程序錯誤: {str(e)}")
        print(f"主程序錯誤: {str(e)}")
        raise

if __name__ == "__main__":
    main()