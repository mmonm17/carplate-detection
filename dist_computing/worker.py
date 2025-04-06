import Pyro4
import sys
import easyocr as ocr
from ultralytics import YOLO
import cv2
import os

@Pyro4.expose
class Worker(object):
    def __init__(self):
        self.model = YOLO("best.pt")
        self.reader = ocr.Reader(['en'])
        return
    
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
    
    def run(self):
        path = "/home/monm/mp/test/"
        img_files = os.listdir(path)
        img_dir = [path + x for x in img_files]
        pred = self.model(img_dir, stream=True)
        results_seq = []
        print(img_files, img_dir)

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
            results_seq.append(row)
            del image
        print(results_seq)

def main():
    try:
        id = sys.argv[1]
        ip = sys.argv[2]
    except:
        print("Error: Please provide a worker ID and Host IP as a command line argument.")
        return
    daemon=Pyro4.Daemon(host=ip)
    ns=Pyro4.locateNS("10.2.12.33", 9090)
    uri=daemon.register(Worker)
    ns.register(f"worker{id}", uri)
    print(f"Worker-{id} Ready")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
