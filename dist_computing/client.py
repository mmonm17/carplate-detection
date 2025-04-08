import Pyro4
import pandas as pd

def print_commands():
    print("Commands:")
    print("[1] Set Num of Workers")
    print("[2] Get Workers")
    print("[3] Set Image Directory")
    print("[4] Send Image Files to Workers")
    print("[5] Run Plate Recognition")
    print("[6] Get Inference Results")
    print("[7] Compute Computation Statistics")
    print("[8] Delete Images in Workers")
    print("[9] Exit")
    print("Please enter a command: ", end="")

def main():
    ns = Pyro4.locateNS("10.2.12.33", 9090)
    uri = ns.lookup("server")
    server = Pyro4.Proxy(uri)

    while True:
        print_commands()
        try:
            command = int(input())
            if command < 1 or command > 9:
                print("Invalid command. Please try again.")
                continue
            if command == 9:
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
                res = server.set_images(directory)
                print(res)
            elif command == 4: # Send Image Files to Workers
                transfer_type = input("Enter the transfer type [0] JPEG or [1] PNG): ")
                if transfer_type not in ["0", "1"]:
                    print("Invalid transfer type. Must be 0 or 1.")
                    continue
                transfer_type = "JPEG" if transfer_type == "0" else "PNG"
                print("Sending images to workers. Please wait, this may take a while...")
                res = server.send_image_files_to_workers(transfer_type)
                print(res)
            elif command == 5: # Run Plate Recognition
                try:
                    batch_size = int(input("Enter the batch size: "))
                    print("Running plate recognition. Please wait, this may take a while...")
                    res = server.call_workers(batch_size)
                    print(res)
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    continue
            elif command == 6:
                try:
                    res = server.get_inference_results()
                    for each in res:
                        worker_id, results = each
                        pd.DataFrame(results).to_csv(f"results_from_worker{worker_id}.csv", index=False)
                        print(f"Results saved to results_from_worker{worker_id}.csv")
                except Exception as e:
                    print(f"Error getting inference results: {e}")
                    continue
            elif command == 7:
                try:
                    file_transfer_time, inference_time = server.send_time()
                    res1 = pd.read_csv("results_from_worker1.csv")
                    res2 = pd.read_csv("results_from_worker2.csv")

                    res1 = res1.iloc[:,:2]
                    res2 = res2.iloc[:,:2]

                    res = pd.concat([res1, res2], axis=0, ignore_index=True).reset_index(drop=True)
                    recog_count = len(res) - len(res[(res["1"] == "N/A") | (res["1"].isnull())])

                    stats = f"Total Number of Images: {len(res)}\n"
                    stats += f"Recognized Plates: {recog_count}\n"
                    stats += f"File Transfer Time: {file_transfer_time:.2f} seconds\n"
                    stats += f"Inference Time: {inference_time:.2f} seconds\n"
                    stats += f"Total Time: {file_transfer_time + inference_time:.2f} seconds\n"

                    print(stats)
                    with open("statistics.txt", "w") as f:
                        f.write(stats)
                    print("Statistics saved to statistics.txt")
                except Exception as e:
                    print(f"Error computing statistics: {e}")
                    continue
            elif command == 8:
                try:
                    res = server.delete_image_files()
                    print(res)
                except Exception as e:
                    print(f"Error deleting images: {e}")
                    continue
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()