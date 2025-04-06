import Pyro4

def print_commands():
    print("Commands:")
    print("[1] Set Num of Workers")
    print("[2] Get Workers")
    print("[3] Set Image Directory")
    print("[4] Set Image Files")
    print("[5] Send Image Files to Nodes")
    print("[6] Run Plate Recognition")
    print("[7] Exit")
    print("Please enter a command: ", end="")

def main():
    ns = Pyro4.locateNS("10.2.12.33", 9090)
    uri = ns.lookup("server")
    server = Pyro4.Proxy(uri)

    while True:
        print_commands()
        try:
            command = int(input())
            if command < 1 or command > 7:
                print("Invalid command. Please try again.")
                continue
            if command == 7:
                print("Exiting...")
                break
            if command == 1: # Set Num of Workers
                try:
                    num_workers = int(input("Enter the number of workers (1 or 2): "))
                    if num_workers < 1 or num_workers > 2:
                        print("Invalid number of workers. Must be 1 or 2.")
                        continue
                    res = server.set_workers(num_workers)
                    print(res)
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    continue
            elif command == 2: # Get Workers
                res = server.get_workers()
                print(res)
            elif command == 3: # Set Image Directory
                directory = input("Enter the image directory: ")
                res = server.set_directory(directory)
                print(res)
            elif command == 4: # Set Image Files
                res = server.set_images()
                print(res)
            elif command == 5: # Send Image Files to Workers
                print("Please wait, this may take a while...")
                res = server.send_image_files_to_workers()
                print(res)
            elif command == 6: # Run Plate Recognition
                res = server.call_workers()
                print(res)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()