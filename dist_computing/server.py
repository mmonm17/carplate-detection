import Pyro4
import os

@Pyro4.expose
class Server(object):
    def __init__(self):
        self.workers = 0
        self.directory = ""
        self.worker_proxies = []
        return
    
    def set_workers(self, workers):
        try:
            if workers < 1 or workers > 3:
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
        
    def get_workers(self):
        if self.workers == 0:
            return "No workers set."
        ns = Pyro4.locateNS("10.2.12.33", 9090)

        uri = ns.lookup("worker1")
        worker = Pyro4.Proxy(uri)
        self.worker_proxies.append(worker)

    def call_workers(self):
        if len(self.worker_proxies) == 0:
            return "No workers available."
        for worker in self.worker_proxies:
            worker.test()
    
def main():
    daemon=Pyro4.Daemon(host="10.2.12.33")
    ns=Pyro4.locateNS("10.2.12.33", 9090)
    uri=daemon.register(Server)
    ns.register("server", uri)
    print("Server Ready")
    daemon.requestLoop()

if __name__ == "__main__":
    main()