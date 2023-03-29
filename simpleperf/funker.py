
import re
import socket
import sys
import time
import argparse
import multiprocessing
from multiprocessing import Process
                
# Server function
def server(host, port):
    # Create a socket and bind to host and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
       
        # Print server listening information
        print(f"----------------------------------------------------------")
        print(f"A simpleperf server is listening on port {port}")
        print(f"----------------------------------------------------------")
        while True:
            conn, addr = s.accept()
            with conn:
                total_data = 0
                
                #Print client connection information
                print(f"----------------------------------------------------------------------------------------------")
                print(f"A simpleperf client with IP {addr} is connected with server IP: {host}, {port}")
                print(f"----------------------------------------------------------------------------------------------")
                
                # Initialize start time
                start_time = time.monotonic()
                
                while True:
                    # Receive and send back data
                    data = conn.recv(1000)
                    if data.decode() == "BYE":
                        break
                    total_data += len(data)
                    conn.sendall(data)
                    
                # Update current time
                current_time = time.monotonic()
                
                # Calculate and print throughput for each iteration
                duration = current_time - start_time

                total_bytes=total_data
                
                total_data_mb = total_bytes / (1000000) # Received
                
                throughput = total_bytes * 8 / duration /1000000 # Deler på 8 antall tall i bytes og deler med 1 mill Mbps #Rate
                
                interval_str = f"{duration:.0f} s" #Interval
                
                print(f"ID\t\tInterval\tReceived\t\tRate")
                print(f"{addr[0]}:{addr[1]:<10}{interval_str:>2} {total_data_mb:>13.0f} MB  {throughput:>9.0f} Mbps")
                
                # Send ACK message and close connection
                conn.sendall(b"ACK: BYE")
                conn.close()

def client(host, port, duration, interval=None, transfer_amount=None, format="MB"):
    # Create a socket and connect to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # Print client connection information
        print("----------------------------------------------------------------")
        print(f"A simpleperf client connecting to server {host}, port {port}")
        print("----------------------------------------------------------------")
        print("Client connected with server_IP port", host, port)
        print("----------------------------------------------------------------")

        # Initialize start time and total data transferred
        start_time = time.monotonic()
        total_data = 0

        # Initialize interval data and start time
        interval_data = 0
        interval_start_time = time.monotonic()

        headers_printed = False #addeddddddd

        # Loop until duration or transfer_amount is reached
        while (time.monotonic() - start_time) < duration and (transfer_amount is None or total_data < transfer_amount):
            # Send and receive data
            message = b"x" * 1000
            s.sendall(message)
            data = s.recv(1000)
            total_data += len(data)

            # Calculate and print interval statistics if the interval flag is set
            if interval and (time.monotonic() - interval_start_time) >= interval:
                interval_str = f"{interval_start_time:.1f} - {time.monotonic():.1f} s" #interval
                if format == "B":
                    interval_data_transfer = interval_data
                elif format == "KB":
                    interval_data_transfer = interval_data / 1000
                else:
                    interval_data_transfer = interval_data / 1000000
                interval_duration = time.monotonic() - interval_start_time 
                if format == "B":
                    throughput = interval_data_transfer * 8 / interval_duration
                else:
                    throughput = interval_data_transfer * 8 / interval_duration / 1000
                
                if not headers_printed:
                    print(f"ID\t\t\tInterval\t\tTransfer\t\tBandwidth")
                    headers_printed = True
                
                if format == "B":
                    interval_data_mb = interval_data
                elif format == "KB":
                    interval_data_mb = interval_data / 1000
                else:
                    interval_data_mb = interval_data / 1000000
                
                print(f"{host}:{port:<10}{interval_str:>10} {interval_data_mb:>5.1f} {format} {throughput:>10.2f} Mbps")
                
                interval_data = 0
                interval_duration = interval if interval else duration
                interval_start_time = time.monotonic() - (time.monotonic() % interval_duration)

            # Add to interval data count
            interval_data += len(data)

        # Send termination message
        s.send("BYE".encode())

        # Receive acknowledgement message
        ack = s.recv(1024)

        # Calculate and print final statistics
        end_time = time.monotonic()
        if format == "B":
            total_data_transfer = total_data
        elif format == "KB":
            total_data_transfer = total_data / 1000
        else:
            total_data_transfer = total_data / 1000000
        
        throughput = total_data_transfer * 8 / (end_time - start_time) / 1000 #bandwith
        print("----------------------------------------------------------")
        print(f"ID\t\t\tInterval\t\tTransfer\t\tBandwidth")
        
        if format == "B":
            total_data_mb = total_data_transfer
        elif format == "KB":
            total_data_mb = total_data_transfer / 1000
        else:
            total_data_mb = total_data_transfer
            
        print(f"{host}:{port:<10}{'0.0 - ' + str(duration) + '.0 s':>10} {total_data_mb:>.0f} {format} {throughput:>15.2f} Mbps")


# Main function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Simple server/client example")
        parser.add_argument("-c", "--client", action="store_true", help="Run as client")
        parser.add_argument("-I", "--serverip", default="127.0.0.1", help="Bind the client to the default address")
        parser.add_argument("-b", "--bind", default="127.0.0.1", help="Bind to the default address")
        parser.add_argument("-s", "--server", action="store_true", help="Run as server")
        parser.add_argument("-i", "--interval", type=int, help="Display interval statistics every t seconds (client mode only)")
        parser.add_argument("-p", "--port", type=int, default=8080, help="Server port number")
        parser.add_argument("-t", "--time", type=int, default=25, help="Client run duration in seconds")
        parser.add_argument("-n", "--num", type=str, help="Amount of data to transfer in the format <X>KB, <X>MB, <X>GB")
        parser.add_argument("-P", "--parallels", type=int, default=1, help="Number of parallel connections")
        parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="Choose the format of the summary of results")
        
        args = parser.parse_args()

        transfer_amount = None
        if args.num:
            units = {"B": 1, "KB": 1000, "MB": 1000000}
            match = re.match(r"(\d+)\s*([a-zA-Z]+)", args.num)
            if match:
                num_str, unit = match.groups()
                if unit not in units:
                    raise ValueError(f"Invalid unit: {unit}. Supported units are: {', '.join(units.keys())}")
                num = int(num_str)
                transfer_amount = num * units[unit]
            else:
                raise ValueError("Invalid format for -n flag. Please use the format <X>B, <X>KB, or <X>MB.")
            #num, unit = int(args.num[:-2]), args.num[-2:]
            #transfer_amount = num * units[unit]

        if args.client:
            clients = []
            for i in range(args.parallels):
                client_proc = Process(target=client, args=(args.bind, args.port, args.time, args.interval, transfer_amount, args.format))
                clients.append(client_proc)
                client_proc.start()
            for client_proc in clients:
                client_proc.join()
        elif args.server:
            server(args.bind, args.port)
        else:
            print("Error: you must run either in server or client mode")
            sys.exit(1)
    else:
        print("Please provide arguments for the script. Run 'python3 simpleperf.py -h' for help.")


        
       