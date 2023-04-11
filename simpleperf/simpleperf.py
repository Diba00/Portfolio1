import re
import socket
import sys
import time
import argparse
import threading
import ipaddress
                
# Server function
def server(host, port):
    # Create a socket and bind to host and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket object to the host and port
        s.bind((host, port))
        # Listen for incoming connections
        s.listen()
       
        # Print server listening information
        print(f"----------------------------------------------------------")
        print(f"A simpleperf server is listening on port {port}")
        print(f"----------------------------------------------------------")
       
       #Create a parallel function so that the server can handle multiple connecctions
        def parallel(conn,addr):
             # Manage client connection within a context manager
            with conn:
                total_data = 0
                
                #Print client connection information
                print(f"----------------------------------------------------------------------------------------------")
                print(f"A simpleperf client with IP {addr} is connected with server IP: {addr[0]}, {addr[1]}")
                print(f"----------------------------------------------------------------------------------------------")
                
                # Initialize start time for measuring throughput
                start_time = time.monotonic()
                
                # Loop for receiving and semding data back to the client
                while True:
                    # Receive and send back data
                    data = conn.recv(1000)
                    #print(data)

                     #Check if the client sends the "BYE" message and break the loop if it does
                    if "BYE" in data.decode():
                    #if data.decode() == "BYE": FEIL SAFIQUL SA DET IKKE FUNKER ALLTID
                        print("FINISHED")
                    
                        break
                     # Update the total amount of data received
                    total_data += len(data)
                  
                    
                 # Calculate duration for throughput measurement
                current_time = time.monotonic()
                duration = current_time - start_time

                # Calculate total received data in megabytes and throughput in Mbps
                total_bytes=total_data
                total_data_mb = total_bytes / (1000000) # Received
                throughput = total_bytes  / duration /1000000 #Rate
                
                # Format duration as a string
                interval_str = f"{duration:.0f} s" #Interval
                
                 # Print throughput information
                print(f"ID\t\tInterval\tReceived\t\tRate")
                print(f"{addr[0]}:{addr[1]:<10}{interval_str:>2} {total_data_mb:>13.0f} MB  {throughput:>9.0f} Mbps")
                
                # Send ACK message and clos connection with teh client
                conn.sendall(b"ACK: BYE")
                conn.close()
        
       # Main server looop to accept multiple clients
        while True:
            # Accept client connection
            conn, addr = s.accept()

            parallel_client = threading.Thread(target=parallel,args=(conn,addr))
            parallel_client.start()
            

#Client function
def client(client_id, host, port, duration, interval=None, transfer_amount=None, format="MB"):
    # Create a socket and connect to server
    print(f"Host: {host}")
    print(f"Port: {port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((str(host), int(port)))

        # Print client connection information
        print("----------------------------------------------------------------")
        print(f"A simpleperf client {client_id} connecting to server {host}, port {port}")
        print("----------------------------------------------------------------")
        print("Client connected with server_IP port", host, port)
        print("----------------------------------------------------------------")

        # Initialize start time and total data transferred, time.time() gave me high number and even though i subtracted with the end time it would not budge. Used monotonic instead
        start_time = time.monotonic()
        total_data = 0

        # Initialize interval data and start time
        interval_data = 0
        interval_start_time = time.monotonic()

        headers_printed = False #Added so the headers only pop up when the calculations start

       # Main loop for sending and receiving data until duration or transfer_amount is reached
        while (time.monotonic() - start_time) < duration and (transfer_amount is None or total_data < transfer_amount):
            # Create message and send 1000 bytes the server
            data = b"x" * 1000
            s.sendall(data)

            # Receive data from the server
            #data = s.recv(1000)
            total_data += len(data)

            # Calculate and print interval statistics if the interval flag is set
            if interval and (time.monotonic() - interval_start_time) >= interval:
                
                # Calculate interval string and interval data transfer
                interval_str = f"{interval_start_time:.1f} - {time.monotonic():.1f} s" #interval

                #formating during the client run

                #Calculate interval data transfer based on the chosen forman (B, KB, MB)
                if format == "B":
                    interval_data_transfer = interval_data
                elif format == "KB":
                    interval_data_transfer = interval_data / 1000
                else:
                    interval_data_transfer = interval_data * 8 / 1000000 #in MB, added 8 to get Mb, interval bandwidth

                #Calculate interval duration   
                interval_duration = time.monotonic() - interval_start_time 
                
                # Calculate interval throughput based on the chosen format (B, KB, MB)
                if format == "B":
                    throughput = interval_data_transfer / interval_duration
                else:
                    throughput = interval_data_transfer * 8 / interval_duration / 1000  #MB OR KB, added 8
                
                # Print headers only once, before printing interval statistics
                if not headers_printed:
                    print(f"ID\t\t\tInterval\tTransfer\tBandwidth")
                    headers_printed = True
                
                # Calculate interval data transfer in MB and print interval statistics based on the chosen format
                if format == "B":
                    interval_data_mb = interval_data
                elif format == "KB":
                    interval_data_mb = interval_data / 1000
                else:
                    interval_data_mb = interval_data / 1000000 #transfer
                
                # Print interval statistics
                print(f"{client_id:<5} {host}:{port:<15}{interval_str:>10} {interval_data_mb:>10.1f} {format:>3} {throughput:>10.2f} Mbps")
                
                # Reset interval data and update interval start time
                interval_data = 0
                interval_duration = interval if interval else duration
                interval_start_time = time.monotonic() - (time.monotonic() % interval_duration)

            # Add to interval data count
            interval_data += len(data)

        # Send termination message 
        print("FINISHED")
        s.send("BYE".encode())

        # Receive acknowledgement message
        ack = s.recv(1000)

         # Calculate total data transfer and throughput in Mbps. formating the final statistics
        end_time = time.monotonic()

        if format == "B":
            total_data_transfer = total_data
        elif format == "KB":
            total_data_transfer = total_data / 1000
        else:
            total_data_transfer = total_data / 1000000
        
        throughput = total_data_transfer  * 8 / (end_time - start_time) #bandwith, siste linje i intervallene, oppsummerende linje

        # Print final statistics
        print("----------------------------------------------------------")
        print(f"ID\t\t\tInterval\tTransfer\tBandwidth")
        
        if format == "B":
            total_data_mb = total_data_transfer
        elif format == "KB":
            total_data_mb = total_data_transfer / 1000
        else:
            total_data_mb = total_data_transfer #dont divide with 1mil bc i want it in MB
        
        # Print final statistics
        print(f"{client_id:<5} {host}:{port:<15}{'0.0 - ' + str(duration) + '.0 s':>10} {total_data_mb:>10.1f} {format:>3} {throughput:>10.2f} Mbps")


# Main function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Simple server/client example")
        parser.add_argument("-c", "--client", action="store_true", help="Run as client")
        parser.add_argument("-I", "--serverip", type=str, default="127.0.0.1", help="Bind the client to the default address")
        parser.add_argument("-b", "--bind", type=str, default="127.0.0.1", help="Bind to the default address")
        parser.add_argument("-s", "--server", action="store_true", help="Run as server")
        parser.add_argument("-i", "--interval", type=int, help="Display interval statistics every t seconds (client mode only)")
        parser.add_argument("-p", "--port", type=int, default=8080, help="Server port number")
        parser.add_argument("-t", "--time", type=int, default=25, help="Client run duration in seconds")
        parser.add_argument("-n", "--num", type=str, help="Amount of data to transfer in the format <X>KB, <X>MB, <X>GB")
        parser.add_argument("-P", "--parallels", type=int, default=1, help="Number of parallel connections")
        parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="Choose the format of the summary of results")


    
        
        # Parse the command line arguments and store them in the 'args' variable
        args = parser.parse_args()

        if args.port < 1044 or args.port > 65535:
            sys.exit("feil i portnummer")

        try:
            ipaddress.ip_address(args.bind)
        except ValueError:
            sys.exit("error i -b flagget")

        try:
            ipaddress.ip_address(args.serverip)
        except ValueError:
            sys.exit("error i -I flagget")

        if args.time < 1:
            sys.exit("tid må være positiv")

        if args.parallels < 1 or args.parallels > 5 :
            sys.exit("parallel må være mellom 1 og 5")

        # Convert the amount of data to transfer to bytes if the '-n' flag was passed
        transfer_amount = None
        if args.num:
            # Define the units of data that can be used (B = bytes, KB = kilobytes, MB = megabytes)
            units = {"B": 1, "KB": 1000, "MB": 1000000}
            # Use regex to match the format of the data amount passed in
            match = re.match(r"(\d+)\s*([a-zA-Z]+)", args.num)
            if match:
                 # Extract the amount and unit of data passed in
                num_str, unit = match.groups()
                 # Raise an error if an unsupported unit is used
                if unit not in units:
                    raise ValueError(f"Invalid unit: {unit}. Supported units are: {', '.join(units.keys())}")
                # Convert the amount of data to bytes
                num = int(num_str)
                transfer_amount = num * units[unit]
            else:
                 # Raise an error if the format of the data amount passed in is invalid
                raise ValueError("Invalid format for -n flag. Please use the format <X>B, <X>KB, or <X>MB.")
        
         # Check if runing as a client
        if args.client:
            # Create multilpe client processes to run in parallel
            clients = []
            for i in range(args.parallels):
                client_thread = threading.Thread(target=client, args=(i, args.serverip, args.port, args.time, args.interval, transfer_amount, args.format))
                clients.append(client_thread)
                client_thread.start()
            # Wait for all client threads to finish
            for client_thread in clients:
                client_thread.join()
                
        # Check if running as a server
        elif args.server:
            server(args.bind, args.port)
        else:
            # Display errorr message if not running as a server or client
            print("Error: you must run either in server or client mode")
            sys.exit(1)
    else:
        # Display help messge if no command line arguments were passed
        print("Please provide arguments for the script, either -s or -c.")

