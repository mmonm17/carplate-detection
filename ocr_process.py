import multiprocessing
import torch
import cv2
import easyocr as ocr

class OCRProcess(multiprocessing.Process):
    def __init__(self, process_dir, process_files, results, process_id, log_queue, model,  batch_size):
        multiprocessing.Process.__init__(self)
        self.process_dir = process_dir
        self.process_files = process_files
        self.results = results
        self.process_id = process_id
        self.log_queue = log_queue
        self.model = model
        self.batch_size = batch_size
        self.log_queue.put(f"Process {self.process_id} initialized")

    def get_plate(self, boxes, image,reader):
        x_min, y_min, x_max, y_max = map(round, boxes)
        cropped = image[y_min:y_max,x_min:x_max]
        ocr_result = reader.readtext(cropped)

        areas = []
        for i, (bbox, _, _) in enumerate(ocr_result):
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
        reader = ocr.Reader(['en'])
        self.log_queue.put(f"Process {self.process_id} started")
        
        for i in range(0, len(self.process_dir), self.batch_size):
            batch_dir = self.process_dir[i:i + self.batch_size]
            batch_files = self.process_files[i:i + self.batch_size]
            pred = self.model(batch_dir, stream=True)
        
            for result, file_name, img in zip(pred, batch_files, batch_dir):
                image = cv2.imread(img)
                ocr_results = []
                
                if image is None:
                    self.log_queue.put(f"Error reading image: {img}")
                    continue
                try:
                    boxes = result.boxes.xyxy.cpu()[0].numpy().tolist()
                    ocr_results = self.get_plate(boxes, image, reader)
                except:
                    self.log_queue.put(f"Error getting ocr from image: {img}")
                    ocr_results = ["N/A"]
                
                row = [file_name] + ocr_results
                self.results.append(row)
                
                del image
                torch.cuda.empty_cache()

            del pred
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        self.log_queue.put(f"Process {self.process_id} completed")