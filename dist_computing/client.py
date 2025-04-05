import Pyro4

def main():
    ns = Pyro4.locateNS("10.2.12.33", 9090)
    uri = ns.lookup("server")
    server = Pyro4.Proxy(uri)
    
    server.set_workers(1)
    server.get_workers()
    server.call_workers()

if __name__ == "__main__":
    main()