import Pyro4
import os
from PIL import Image
import io
import threading
import time
@Pyro4.expose
class Server(object):
    def __init__(self):
        self.workers = 0
        self.directory = ""
        self.worker_proxies = []
        self.image_directories = []
        self.file_transfer_time = 0
        self.inference_time = 0
        return
    
    def set_workers(self, workers):
        try:
            if workers < 1 or workers > 2:
                return f"Invalid number of workers. Must be either 1 or 2."
            else:
                self.workers = workers
                return f"Number of workers set to {workers}"
        except Exception as e:
            return f"Error setting workers: {e}"

    def set_images(self, directory):
        try:
            if not os.path.exists(directory):
                return "Directory does not exist. Please set a valid directory."
            else:
                self.directory = directory
                img_files = os.listdir(self.directory)
                img_dir = [os.path.join(self.directory, x) for x in img_files]
                if len(img_dir) == 0:
                    return "No images found in the directory."
                else:
                    self.image_directories = []
                    for each in img_dir:
                        if os.path.isfile(each):
                            self.image_directories.append(each)
                    return f"Image files Set from {self.directory}."
        except Exception as e:
            return f"Error getting images from {self.directory}: {e}"
        
    def sending_function(self, start, end, i, transfer_type):
        for each_img_dir in self.image_directories[start:end]:
            try:
                print(f"Reading {each_img_dir}")
                img = Image.open(each_img_dir)
                buffer = io.BytesIO()
                img.save(buffer, format=transfer_type)
                img_buffer = buffer.getvalue()
                filename = each_img_dir.split("/")[-1]
                res = self.worker_proxies[i].receive_image(img_buffer, filename)
                print(f"Worker {i+1}: {res}")
            except Exception as e:
                print(f"Error reading image {each_img_dir}: {e}")
                continue
        
    def send_image_files_to_workers(self, transfer_type):
        if self.workers == 0:
            return "No workers set."
        if self.workers < 1 or self.workers > 2:
            return "Invalid number of workers. Must be between 1 and 2."
        if len(self.worker_proxies) == 0:
            return "No workers available."
        if len(self.image_directories) == 0:
            return "No image files set. Please set image files."
        len_dir = len(self.image_directories)
        print(f"Total Number of Images: {len_dir}")
        print(f"Number of Workers: {self.workers}")

        start_time = time.time()
        images_per_worker = len_dir // self.workers
        processes = []
        for i in range(self.workers):
            start = i * (images_per_worker)
            end = (i + 1) * (images_per_worker) if i != self.workers - 1 else len_dir
            p = threading.Thread(target=self.sending_function, args=(start, end, i, transfer_type))
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()

        end_time = time.time()
        self.file_transfer_time = end_time - start_time
        print(f"File transfer time: {self.file_transfer_time} seconds")
            
        return f"{images_per_worker} image files sent to each worker."
        
    def get_workers(self):
        try:
            if self.workers == 0:
                return "No workers set."
            ns = Pyro4.locateNS("10.2.12.33", 9090)
            self.worker_proxies = []

            for i in range(self.workers):
                try:
                    uri = ns.lookup(f"worker{i+1}")
                    worker = Pyro4.Proxy(uri)
                    self.worker_proxies.append(worker)
                except Exception as e:
                    print(f"Error locating worker {i+1}: {e}")
                    continue

            return f"{len(self.worker_proxies)} workers found."
        except Exception as e:
            return f"Error getting workers: {e}"

    def call_workers(self, batch_size):
        if len(self.worker_proxies) == 0:
            return "No workers available."
        if batch_size <= 0:
            return "Invalid batch size. Must be greater than 0."
        
        start_time = time.time()
        processes = []
        for i in range(self.workers):
            p = threading.Thread(target=self.worker_proxies[i].predict, args=(batch_size,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
        end_time = time.time()
        self.inference_time = end_time - start_time
        return f"Inference time: {self.inference_time} seconds"

    def get_inference_results(self):
        if len(self.worker_proxies) == 0:
            return "No workers available."
        
        results = []
        for i in range(self.workers):
            try:
                res = self.worker_proxies[i].send_results()
                results.append((i+1, res))
            except Exception as e:
                print(f"Error getting results from worker {i+1}: {e}")
                continue
        return results
    
    def send_time(self):
        return self.file_transfer_time, self.inference_time
    
    def delete_image_files(self):
        if len(self.worker_proxies) == 0:
            return "No workers available."
        for i in range(self.workers):
            try:
                self.worker_proxies[i].delete_image_files()
            except Exception as e:
                print(f"Error deleting image files from worker {i+1}: {e}")
                continue
        return "Image files deleted."
    
def main():
    daemon=Pyro4.Daemon(host="10.2.12.33")
    ns=Pyro4.locateNS("10.2.12.33", 9090)
    uri=daemon.register(Server)
    ns.register("server", uri)
    print("Server Ready")
    daemon.requestLoop()

if __name__ == "__main__":
    main()