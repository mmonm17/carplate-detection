import Pyro4
import os
from PIL import Image
import io

@Pyro4.expose
class Server(object):
    def __init__(self):
        self.workers = 0
        self.directory = ""
        self.worker_proxies = []
        self.image_directories = []
        return
    
    def set_workers(self, workers):
        try:
            if workers < 1 or workers > 2:
                return f"Invalid number of workers. Must be between 1 and 3."
            else:
                self.workers = workers
                return f"Number of workers set to {workers}"
        except Exception as e:
            return f"Error setting workers: {e}"
        
    def set_directory(self, directory):
        try:
            if not os.path.exists(directory):
                return "Directory does not exist."
            else:
                self.directory = directory
                return f"Directory set to {directory}"
        except Exception as e:
            return f"Error setting directory: {e}"

    def set_images(self):
        try:
            if not os.path.exists(self.directory):
                return "Directory does not exist. Please set a valid directory."
            else:
                img_files = os.listdir(self.directory)
                img_dir = [os.path.join(self.directory, x) for x in img_files]
                if len(img_dir) == 0:
                    return "No images found in the directory."
                else:
                    for each in img_dir:
                        if os.path.isfile(each):
                            self.image_directories.append(each)
                    return f"Image files Set from {self.directory}."
        except Exception as e:
            return f"Error getting images from {self.directory}: {e}"
        
    def send_image_files_to_workers(self):
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

        for i in range(self.workers):
            start = i * (len_dir // self.workers)
            end = (i + 1) * (len_dir // self.workers) if i != self.workers - 1 else len_dir

            for each_img_dir in self.image_directories[start:end]:
                try:
                    print(f"Reading {each_img_dir}")
                    img = Image.open(each_img_dir)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    img_buffer = buffer.getvalue()
                    filename = each_img_dir.split("/")[-1]
                    res = self.worker_proxies[i].receive_image(img_buffer, filename)
                    print(f"Worker {i+1}: {res}")
                except Exception as e:
                    print(f"Error reading image {each_img_dir}: {e}")
                    continue
            
        return f"Image files sent to workers."
        
    def get_workers(self):
        try:
            if self.workers == 0:
                return "No workers set."
            ns = Pyro4.locateNS("10.2.12.33", 9090)

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

    def call_workers(self):
        if len(self.worker_proxies) == 0:
            return "No workers available."
        for worker in self.worker_proxies:
            worker.run()
    
def main():
    daemon=Pyro4.Daemon(host="10.2.12.33")
    ns=Pyro4.locateNS("10.2.12.33", 9090)
    uri=daemon.register(Server)
    ns.register("server", uri)
    print("Server Ready")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
