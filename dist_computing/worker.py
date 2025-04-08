import Pyro4
import sys
import easyocr as ocr
from ultralytics import YOLO
import cv2
import os, shutil
import io
from PIL import Image
import serpent
import pandas as pd

@Pyro4.expose
class Worker(object):
    def __init__(self, id):
        self.model = YOLO("best.pt")
        self.reader = ocr.Reader(['en'])
        self.path_to_images = "/home/monm/mp/images/"
        self.id = id
        self.images = []
        self.filenames = []
        return
    
    def receive_image(self, img_b64, filename):
        try:
            img_bytes = serpent.tobytes(img_b64)
            img = Image.open(io.BytesIO(img_bytes))
            self.filenames.append(filename)
            img.save(self.path_to_images + filename)
            print(f"Image {filename} received and saved.")
            return f"Image received."
        except Exception as e:
            return f"Error receiving image: {e}"
    
    def set_model(self, model):
        try:
            self.model = model
            return f"Model set to {model}"
        except Exception as e:
            return f"Error setting model: {e}"

    def get_plate(self, boxes, image):
        x_min, y_min, x_max, y_max = map(round, boxes)
        cropped = image[y_min:y_max,x_min:x_max]
        ocr_result = self.reader.readtext(cropped)

        # get the box with the largest area
        areas = []
        for i, (bbox, text, conf) in enumerate(ocr_result):
            [x1,y1], [x2,y2], [x3,y3], [x4,y4] = bbox
            
            x_values = [x1,x2,x3,x4]
            y_values = [y1,y2,y3,y4]
            width = max(x_values) - min(x_values)
            height = max(y_values) - min(y_values)
            area = width * height
            areas.append(area)

        results = []
        for each in sorted(areas, reverse=True):
            index = areas.index(each)
            results.append(ocr_result[index][1])
        return results
    
    def predict(self, batch_size):
        img_files = os.listdir(self.path_to_images)
        if len(img_files) == 0:
            print("No images found in the directory.")
            return
        
        img_dir = [self.path_to_images + x for x in img_files]
        print(f"Predicting {len(img_dir)} images...")
        
        if len(img_dir) / batch_size != len(img_dir) // batch_size:
            iters = 1 + len(img_dir) // batch_size
        else:
            iters = len(img_dir) // batch_size
        results_seq = []
        for i in range(iters):
            start = i * batch_size
            end = (i + 1) * batch_size if i != iters - 1 else len(img_dir)
            img_dir_batch = img_dir[start:end]
            pred = self.model(img_dir_batch, stream=True)
            results = []
            print(f"Image Index Start: {start}")
            print(f"Image Index End: {end}")

            for result, file_name, img in zip(pred, img_files, img_dir):
                image = cv2.imread(img)

                if image is None:
                    print(f"Error reading image: {img}")
                    continue
                try:
                    boxes = result.boxes.xyxy.cpu()[0].numpy().tolist()
                    ocr_results = self.get_plate(boxes, image)
                except:
                    print(f"Error getting ocr from image: {img}")
                    ocr_results = ["N/A"]
                    
                row = [file_name] + ocr_results
                results.append(row)
                del image
            results_seq += results
            print(results)
        pd.DataFrame(results_seq).to_csv(f"results_from_worker{self.id}.csv", index=False)
        print(f"Prediction completed for {len(img_dir)} images.")

    def send_results(self):
        try:
            df = pd.read_csv(f"results_from_worker{self.id}.csv")
            return df.to_numpy().tolist()
        except Exception as e:
            return f"Error sending results: {e}"
        
    def delete_image_files(self):
        try:
            for each in os.listdir(self.path_to_images):
                os.remove(os.path.join(self.path_to_images, each))
            return f"Image files deleted."
        except Exception as e:
            return f"Error deleting image files: {e}"

def main():
    try:
        id = sys.argv[1]
        ip = sys.argv[2]
    except:
        print("Error: Please provide a worker ID and Host IP as a command line argument.")
        return
    
    try:
        worker = Worker(id)
        daemon=Pyro4.Daemon(host=ip)
        ns=Pyro4.locateNS("10.2.12.33", 9090)
        uri=daemon.register(worker)
        ns.register(f"worker{id}", uri)
        print(f"Worker-{id} Ready")
        daemon.requestLoop()
    except Exception as e:
        print(f"Error starting worker: {e}")
        return
if __name__ == "__main__":
    main()
