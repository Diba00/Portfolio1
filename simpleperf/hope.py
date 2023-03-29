import socket
import sys
import time
import argparse
import multiprocessing
from multiprocessing import Process


"""
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
                
                # Print client connection information
                print(f"A simpleperf client with IP {addr} is connected with server IP: {host}, {port}")
                print(f"----------------------------------------------------------------------------------------------")
                #total_data = 0
                start_time = None
                while True:
                    
                    # Receive and send back data
                    data = conn.recv(1000)
                    if data.decode() == "BYE":
                        break
                    if start_time is None:
                        start_time = time.monotonic()
                        current_time = start_time
                    else:
                        current_time = time.monotonic()
                    total_data += len(data)
                    conn.sendall(data)
                    
                # Calculate and print throughput for each iteration
                duration = current_time - start_time
                total_bytes=total_data
                total_data_mb = total_bytes / (1000000) # Recieved
                throughput = total_bytes * 8 / duration /1000000 #deler på 8 antall tall i bytes og deler med 1 mill Mbps #Rate
                interval_str = f"{start_time:.2f}-{current_time:.2f} s" #Interval
                print(f"ID\t\t\tInterval\t\t\tReceived\t\tRate")
                print(f"{addr[0]}:{addr[1]:<10}{interval_str:>15} {total_data_mb:>15.0f} MB  {throughput:>15.0f} Mbps")
                
                # Send ACK message and close connection
                conn.sendall(b"ACK: BYE")
                conn.close()
"""
                
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
                
                # Print client connection information
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
                
                print(f"ID\t\tInterval\tReceived\tRate")
                print(f"{addr[0]}:{addr[1]:<10}{interval_str:>2} {total_data_mb:>13.0f} MB  {throughput:>9.0f} Mbps")
                
                # Send ACK message and close connection
                conn.sendall(b"ACK: BYE")
                conn.close()


# Client function
def client(host, port, duration):
    # Create a socket and connect to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        # Print client connection information
        print(f"----------------------------------------------------------")
        print(f"A simpleperf client is connected with server IP:{port}")
        print(f"----------------------------------------------------------")
        start_time = 0 #time.time()
        total_data = 0 
        while (time.monotonic() - start_time) < duration:
            if start_time is None:
                start_time = time.monotonic()
                current_time = start_time
            else:
                current_time = time.monotonic()
           
            message = b"x" * 1000
            s.sendall(message)
            data = s.recv(1000)
            total_data += len(data)
        
        s.send("BYE".encode())
        ack = s.recv(1024)


        print(f"Client connected with server_IP port:{port}")
        print(f"----------------------------------------------------------")

        # Calculate and accumulate throughput for each iteration
        duration = current_time - start_time #time.time() - start_time
        interval_str = f"{start_time:.2f}-{current_time:.2f} s" #Interval
        total_data_mb = total_data / 1000000
        throughput = total_data_mb * 8 / duration /1000000 #divided with 1 mil to get Mbps
        
        # Wait for ACK message from server and print final results in table format
        ack = s.recv(1024)
        total_data_mb = total_data / 1000000  #Transfer
        throughput = total_data * 8 / duration / 1000000 #Bandwith
        print(f"ID\t\t\tInterval\t\tTransfer\t\tBandwidth")
        print(f"{host}:{port:<10}{interval_str:>15} s  {total_data_mb:>13.0f} MB   {throughput:>15.2f} Mbps")


# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple server/client example")
    parser.add_argument("-c", "--client", action="store_true", help="Run as client")
    parser.add_argument("-b", "--bind", default="127.0.0.1", help="Bind to the default address")
    parser.add_argument("-s", "--server", action="store_true", help="Run as server")
    parser.add_argument("-i", "--interval", type=int, help="Print intervals")
    parser.add_argument("-p", "--port", type=int, default=2000, help="Server port number")
    parser.add_argument("-t", "--time", type=int, default=5, help="Client run duration in seconds")
    parser.add_argument("-n", "--num", type=int, nargs='+', help="List of numbers")
    parser.add_argument("-f", "--format", choices=["B", "KB","MB"], default="MB", help="Format, default in MB")
    parser.add_argument("-P", "--parallels", type=int, default=1, help="Number of parallel connections")
    parser.add_argument("-I", "--ipaddress", help="IP address for an additional connection")
    args = parser.parse_args()

    if args.client:
        clients = []
        for i in range(args.parallels):
            client_proc = Process(target=client, args=(args.bind, args.port, args.time))
            clients.append(client_proc)
            client_proc.start()
        for client_proc in clients:
            client_proc.join()
    elif args.server:
        server(args.bind, args.port)
    else:
        print("Error: you must run either in server or client mode")
        sys.exit()

"""
# Client function
def client(host, port, duration, interval=None, transfer_amount=None, format = "MB"):
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
                interval_data_mb = interval_data / 1000000 #transfer
                interval_duration = time.monotonic() - interval_start_time 
                throughput = interval_data_mb * 8 / interval_duration / 1000 #bandwith
               
                #print(f"ID\t\t\tInterval\t\tTransfer\t\tBandwidth")
                if not headers_printed:
                    print(f"ID\t\t\tInterval\t\tTransfer\t\tBandwidth")
                    headers_printed = True
                
                print(f"{host}:{port:<10}{interval_str:>10} {interval_data_mb:>5.1f} MB {throughput:>10.2f} Mbps")
                #interval_data = 0
                #interval_start_time = time.monotonic()
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
        total_data_mb = total_data / 1000000 #transfer
        throughput = total_data_mb * 8 / (end_time - start_time) / 1000 #bandwith
        print("----------------------------------------------------------")
        print(f"ID\t\t\tInterval\t\tTransfer\t\tBandwidth")
        print(f"{host}:{port:<10}{'0.0 - ' + str(duration) + '.0 s':>10} {total_data_mb:>.0f} MB {throughput:>15.2f} Mbps")
       


# Helper function to print interval statistics
def print_interval_stats(host, port, interval_str, total_data, current_time, start_time):
    total_data_mb = total_data / 1000000 #transfer
    throughput = total_data_mb * 8 / (current_time - start_time) / 1000000 #bandwith
    
    print(f"{host}:{port:<10}{interval_str:>10} s  {total_data_mb:>13.0f} MB   {throughput:>15.2f} Mbps")

DENNE KODEN FUNKER MED SIMPLEPERF.PY ER BARE UTEN B, MB, KB GREIENE
"""

