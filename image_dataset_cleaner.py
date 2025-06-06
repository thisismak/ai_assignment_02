import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'  # Enable detailed TensorFlow logging
import sqlite3
import logging
import csv
from urllib.parse import urlparse
from PIL import Image
import imagehash
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from collections import defaultdict
import subprocess
import sys
import re
from uuid import uuid4

# Configure logging for tracking progress and errors
logging.basicConfig(
    filename='dataset_cleaning.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Configuration constants
OUTPUT_DIR = "dog_images"
DB_NAME = "dog_images.db"
TARGET_IMAGE_COUNT_MIN = 1000
TARGET_IMAGE_COUNT_MAX = 2000
CLEANED_DIR = "cleaned_dog_images"
TEMP_DIR = "temp_images"
MODEL_CONFIDENCE_THRESHOLD = 0.6  # Relaxed threshold for dog classification
HASH_SIZE = 8  # Size for perceptual hash
PAGE_COUNT_LOG = "image_collection.log"  # Log file from Exercise 1

# Initialize ResNet50 model for dog classification
try:
    model = ResNet50(weights='imagenet')
    logging.info("ResNet50 model loaded successfully")
except Exception as e:
    logging.error(f"Failed to load ResNet50 model: {str(e)}")
    raise

class DatasetCleaner:
    """Class to handle image dataset cleaning and analysis."""
    
    def __init__(self):
        """Initialize database connection, create images table, and output directories."""
        try:
            self.conn = sqlite3.connect(DB_NAME)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    alt_text TEXT,
                    filename TEXT,
                    breed TEXT
                )
            ''')
            self.conn.commit()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise
        if not os.path.exists(CLEANED_DIR):
            os.makedirs(CLEANED_DIR)
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        self.image_hashes = {}
        self.failure_log = []
        self.breed_counts = defaultdict(int)
        self.unique_domains = set()
        self.page_count = 0

    def is_dog_image(self, image_path):
        """Classify if an image contains a dog using ResNet50."""
        try:
            if image_path.lower().endswith('.svg'):
                logging.warning(f"Skipping SVG file: {image_path}")
                self.failure_log.append(["N/A", "N/A", "N/A", "classification", f"SVG file: {image_path}"])
                return False
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224), Image.Resampling.LANCZOS)
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            predictions = model.predict(img_array, batch_size=1, verbose=0)
            decoded = tf.keras.applications.imagenet_utils.decode_predictions(predictions, top=1)
            if not decoded or not decoded[0]:
                logging.error(f"No predictions returned for {image_path}")
                self.failure_log.append(["N/A", "N/A", "N/A", "classification", f"No predictions for {image_path}"])
                return False
            predicted_class = decoded[0][0]
            class_id, class_name, confidence = predicted_class
            is_dog = 151 <= int(class_id.split('_')[1]) <= 268 if class_id.startswith('n') else False
            logging.info(f"Image {image_path}: Classified as {class_name} (ID: {class_id}) with confidence {confidence}, is_dog: {is_dog}")
            if not is_dog or confidence < MODEL_CONFIDENCE_THRESHOLD:
                self.failure_log.append(["N/A", "N/A", "N/A", "classification", f"Classified as {class_name} with confidence {confidence}, is_dog: {is_dog}"])
            return is_dog and confidence >= MODEL_CONFIDENCE_THRESHOLD
        except Exception as e:
            logging.error(f"Error classifying {image_path}: {str(e)}")
            self.failure_log.append(["N/A", "N/A", "N/A", "classification", f"Error classifying {image_path}: {str(e)}"])
            return False

    def compute_image_hash(self, image_path):
        """Compute perceptual hash of an image."""
        try:
            if image_path.lower().endswith('.svg'):
                logging.warning(f"Skipping hash computation for SVG file: {image_path}")
                self.failure_log.append(["N/A", "N/A", "N/A", "hashing", f"SVG file: {image_path}"])
                return None
            with Image.open(image_path) as img:
                return str(imagehash.average_hash(img, hash_size=HASH_SIZE))
        except Exception as e:
            logging.error(f"Error computing hash for {image_path}: {str(e)}")
            self.failure_log.append(["N/A", "N/A", "N/A", "hashing", f"Error computing hash for {image_path}: {str(e)}"])
            return None

    def check_database(self):
        """Check if the images table contains data."""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
            if not self.cursor.fetchone():
                logging.error("Images table does not exist in the database.")
                return False
            self.cursor.execute("SELECT COUNT(*) FROM images")
            count = self.cursor.fetchone()[0]
            logging.info(f"Database contains {count} records in images table.")
            if count == 0:
                logging.error("No data found in images table. Please run script.py first.")
                return False
            return True
        except sqlite3.OperationalError as e:
            logging.error(f"Database error in check_database: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in check_database: {str(e)}")
            return False

    def clean_dataset(self):
        """Clean the dataset by removing irrelevant and duplicate images."""
        if not self.check_database():
            logging.error("Cannot proceed with cleaning due to empty database or table issue.")
            return 0, 0, 0

        try:
            self.cursor.execute("SELECT id, url, alt_text, filename, breed FROM images")
            images = self.cursor.fetchall()
            logging.info(f"Retrieved {len(images)} images from database for cleaning.")
        except sqlite3.OperationalError as e:
            logging.error(f"Database error in clean_dataset: {str(e)}. Ensure images table exists.")
            return 0, 0, 0

        cleaned_count = 0
        irrelevant_count = 0
        duplicate_count = 0
        images_to_remove = []

        for img_id, url, alt_text, filename, breed in images:
            # Verify file exists
            if not os.path.exists(filename):
                logging.warning(f"Image file {filename} not found for breed {breed}, URL: {url}")
                self.failure_log.append([breed, url, alt_text, "file_missing", "File not found"])
                images_to_remove.append(img_id)
                continue

            # Check if image is a dog
            if not self.is_dog_image(filename):
                irrelevant_count += 1
                self.failure_log.append([breed, url, alt_text, "classification", "Not classified as a dog image"])
                logging.info(f"Marked {filename} for removal: not a dog image")
                images_to_remove.append(img_id)
                continue

            # Check for duplicates using perceptual hash
            img_hash = self.compute_image_hash(filename)
            if img_hash is None:
                irrelevant_count += 1
                self.failure_log.append([breed, url, alt_text, "hashing", "Failed to compute hash"])
                logging.warning(f"Failed to compute hash for {filename}")
                images_to_remove.append(img_id)
                continue
            if img_hash in self.image_hashes:
                duplicate_count += 1
                self.failure_log.append([breed, url, alt_text, "duplicate", f"Duplicate of {self.image_hashes[img_hash]}"])
                logging.info(f"Marked {filename} for removal: duplicate of {self.image_hashes[img_hash]}")
                images_to_remove.append(img_id)
                continue
            self.image_hashes[img_hash] = filename

            # Move to cleaned directory
            cleaned_filename = os.path.join(CLEANED_DIR, os.path.basename(filename))
            try:
                os.rename(filename, cleaned_filename)
                self.cursor.execute("UPDATE images SET filename = ? WHERE id = ?", (cleaned_filename, img_id))
                logging.info(f"Moved {filename} to {cleaned_filename}")
            except OSError as e:
                logging.error(f"Error moving file {filename} to {cleaned_filename}: {str(e)}")
                self.failure_log.append([breed, url, alt_text, "file_move", str(e)])
                images_to_remove.append(img_id)
                continue

            self.breed_counts[breed] += 1
            cleaned_count += 1

            # Extract domain for source analysis
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            self.unique_domains.add(domain)

        # Remove invalid images
        for img_id in images_to_remove:
            self.cursor.execute("DELETE FROM images WHERE id = ?", (img_id,))
            filename = next((img[3] for img in images if img[0] == img_id), None)
            if filename and os.path.exists(filename):
                os.remove(filename)

        self.conn.commit()
        logging.info(f"Cleaned dataset: {cleaned_count} images kept, {irrelevant_count} irrelevant, {duplicate_count} duplicates")
        return cleaned_count, irrelevant_count, duplicate_count

    def supplement_images(self, target_min, target_max):
        """Supplement dataset if cleaned count is below target minimum."""
        cleaned_count, _, _ = self.clean_dataset()
        if cleaned_count >= target_min:
            return cleaned_count

        logging.info(f"Supplementing dataset: {target_min - cleaned_count} images needed")
        try:
            result = subprocess.run([sys.executable, "script.py"], capture_output=True, text=True, check=True)
            logging.info(f"Successfully ran script.py to supplement images: {result.stdout}")
            self.conn.commit()
            return self.clean_dataset()[0]  # Re-clean after supplementing
        except subprocess.CalledError as e:
            logging.error(f"Failed to run script.py for supplementing: {e.stderr}")
            self.failure_log.append(["N/A", "N/A", "N/A", "supplement", f"Subprocess error: {e.stderr}"])
            return cleaned_count
        except Exception as e:
            logging.error(f"Error supplementing images: {e}")
            self.failure_log.append(["N/A", "N/A", "N/A", "supplement", str(e)])
            return cleaned_count

    def count_pages(self):
        """Count the number of pages crawled from the log file."""
        try:
            if os.path.exists(PAGE_COUNT_LOG):
                with open(PAGE_COUNT_LOG, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                    self.page_count = len(re.findall(r'Searching (Google|Bing) for keyword', log_content))
                logging.info(f"Total pages crawled: {self.page_count}")
            else:
                logging.warning(f"Log file {PAGE_COUNT_LOG} not found")
                self.page_count = 0
        except Exception as e:
            logging.error(f"Error counting pages: {str(e)}")
            self.page_count = 0

    def generate_report(self, cleaned_count, irrelevant_count, duplicate_count):
        """Generate CSV report with statistics and source analysis."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM images")
            original_count = self.cursor.fetchone()[0]
        except sqlite3.OperationalError as e:
            logging.error(f"Error querying database for report: {str(e)}")
            original_count = 0

        report_data = [
            ["Metric", "Value"],
            ["Original Image Count", original_count],
            ["Cleaned Image Count", cleaned_count],
            ["Irrelevant Images Removed", irrelevant_count],
            ["Duplicate Images Removed", duplicate_count],
            ["Unique Domains", len(self.unique_domains)],
            ["Pages Crawled", self.page_count]
        ]
        with open("dataset_report.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(report_data)
        logging.info("Generated dataset report")

        # Export breed distribution
        with open("cleaned_breed_distribution.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Breed", "Image Count"])
            for breed, count in self.breed_counts.items():
                writer.writerow([breed, count])
        logging.info("Generated breed distribution report")

        # Export failure log
        with open("cleaning_failure_report.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Breed", "URL", "Alt Text", "Failure Stage", "Failure Reason"])
            writer.writerows(self.failure_log)
        logging.info("Generated failure report")

    def close(self):
        """Close database connection."""
        try:
            self.conn.commit()
            self.conn.close()
            logging.info("Database connection closed successfully")
        except Exception as e:
            logging.error(f"Error closing database connection: {str(e)}")

def main():
    """Main function to clean dataset and generate reports."""
    cleaner = DatasetCleaner()
    cleaned_count = 0
    irrelevant_count = 0
    duplicate_count = 0
    try:
        cleaner.count_pages()
        cleaned_count, irrelevant_count, duplicate_count = cleaner.clean_dataset()
        if cleaned_count < TARGET_IMAGE_COUNT_MIN:
            cleaned_count = cleaner.supplement_images(TARGET_IMAGE_COUNT_MIN, TARGET_IMAGE_COUNT_MAX)
        cleaner.generate_report(cleaned_count, irrelevant_count, duplicate_count)
        if cleaned_count == 0:
            print("清理失敗：數據庫為空或無有效圖像數據。請先運行 script.py 收集圖像。")
            logging.error("Cleaning aborted due to empty dataset or database error.")
            return
        logging.info("Dataset cleaning and reporting completed")
        print(f"數據集清理完成：")
        print(f"原始圖像數量：{cleaner.cursor.execute('SELECT COUNT(*) FROM images').fetchone()[0]}")
        print(f"清理後圖像數量：{cleaned_count}")
        print(f"移除的不相關圖像：{irrelevant_count}")
        print(f"移除的重複圖像：{duplicate_count}")
        print(f"唯一網域數量：{len(cleaner.unique_domains)}")
        print(f"爬取的頁數：{cleaner.page_count}")
        print(f"品種分佈：{dict(cleaner.breed_counts)}")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"程式執行失敗：{str(e)}")
        cleaner.generate_report(cleaned_count, irrelevant_count, duplicate_count)
    finally:
        cleaner.close()

if __name__ == "__main__":
    main()