import Pyro4
import sys
import easyocr as ocr

@Pyro4.expose
class Worker(object):
    def __init__(self):
        self.model = None
        self.reader = ocr.Reader(['en'])
        return
    
    def set_model(self, model):
        try:
            self.model = model
            return f"Model set to {model}"
        except Exception as e:
            return f"Error setting model: {e}"
    
    def run(self):


def main():
    try:
        id = sys.argv[1]
    except:
        print("Error: Please provide a worker ID as a command line argument.")
        return
    daemon=Pyro4.Daemon(host="10.2.12.34")
    ns=Pyro4.locateNS("10.2.12.33", 9090)
    uri=daemon.register(Worker)
    ns.register(f"worker{id}", uri)
    print(f"Worker-{id} Ready")
    daemon.requestLoop()

if __name__ == "__main__":
    main()