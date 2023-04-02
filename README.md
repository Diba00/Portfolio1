This is my step by step, how to use my simpleperf tool.

How to run it in vscode:

First you open up my simpleperf code, then you press the play button on the top right corner. After doing so the terminal window will pop up with the text "Portfolio1 *users computer name*$". Then you have to navigate to the right folder. Write "cd simpleperf", then we are ready to run. 

First we would like to run the server side. Write in "python3 simpleperf.py -s". -s is to indicat we want to run in server mode: it should receive data and track the total number of bytes. Now you will se the server side pop up with a text "A simpleperf server is listening on port 8080". 

Now the for the client side. Press the button beside the trash icon in the terminal window, that has a screen split in two. Now we get another terminal window to pop up but we're in the correct folder. Now type in "python3 simpleperf.py -c", -c is to indicate we want to run in client mode and calculate and display bandwidth, now we see "A simpleperf client connecting to server 127.0.0.1, port 8080".

Now the server and client are communicating and we are waiting 25 seconds on the results (default time). We can see on the server side that "A simpleperf client with IP ('127.0.0.1', 51532) is connected with server IP: 127.0.0.1, 8080" and on the client "Client connected with server_IP port 127.0.0.1 8080". After 25 seconds we see the tables have been printed out with our raw data.

On the client side:

"ID                   Interval        Transfer       Bandwidth
127.0.0.1:8080      0.0 - 25.0 s     12847 MB       4110.14 Mbps"

Server side: 
"ID               Interval       Received          Rate
127.0.0.1:51532     25 s         12847 MB        514 Mbps"

If we want to see the intervals with x seconds in between each interval we have to specify with the -i flag for how many seconds each interval is going to be, and with -t, time flag if we want a different time from 25 seconds. What I instructed now is the basic version of the simpleperf tool. If you want to choose the amount of data being transfered, have parallell connections etc. you can use the different flags I have implemented. If you for example want to see intervals with 5 seconds in between each interval in the time space 35 seconds you write the code like this "python3 simpleperf.py -c -I 127.0.0.1 -p 8080 -t 35 -i 5 ". Here we have also specified the ip address and port number to match the client to the server (-I and -p). The server code is still just "simpleperf.py -s". 

The client side will now print out: 
"----------------------------------------------------------------
ID                      Interval      Transfer       Bandwidth
127.0.0.1:8080      0.0 - 5.0 s       2562.7 MB       0.51 Mbps
127.0.0.1:8080      5.0 - 10.0 s      2612.8 MB       0.52 Mbps
127.0.0.1:8080      10.0 - 15.0 s     2622.3 MB       0.52 Mbps
127.0.0.1:8080      15.0 - 20.0 s     2620.8 MB       0.52 Mbps
127.0.0.1:8080      20.0 - 25.0 s     2646.4 MB       0.53 Mbps
127.0.0.1:8080      25.0 - 30.0 s     2607.2 MB       0.52 Mbps
127.0.0.1:8080      30.0 - 35.0 s     2590.6 MB       0.52 Mbps
FINISHED
----------------------------------------------------------
ID                      Interval                Transfer       Bandwidth
127.0.0.1:8080      0.0 - 35.0 s               18287 MB         4178.91 Mbps"

Here we can see each interval being printed out with 5 sec in between in total 35 seconds. The server side will also display the last line with summary of the raw data. 

Server side: 
"ID              Interval        Received                Rate
127.0.0.1:51546     35 s         18287 MB        522 Mbps"

As we can see, there are a lot of flags that we can play around with and get results from. 

Other flags are 
-P = Parallell connections
-n = Amount of data to transfer in the format <X>KB, <X>MB, <X>GB
-f = Choose the format of the summary of results
-b = Bind to the default address

How to run the tests 2 on ubuntu:

As we have gone through how to use the code in vscode, we will now use it in ubuntu and run the tests with the help of mininet. You now know how to run the code, it is the exact same in ubuntu. I will not go through how to download your vscode into your ubuntu machines files (github).

Open up ubuntu and run this in the terminal "sudo fuser -k 6653/tcp", then run "sudo python portfolio-topology.py", then your password for the ubuntu machine. Now we can use mininet for test 2 since we are using the topology. For test 2 we need to use r1 and r2. Write in "xterm r1 r2". Now you have two terminal windows up and running. r1 is the client and r2 is the server. 

Server r2: You have to be in the right folder, type in "cd portfolio1" the "cd simpleperf". Now you can type in "python3 simpleperf.py -s -b 10.0.1.2 -p 8088", then the message "A simpleperf server is listening on port 8088" will show.

Client r1: you have to first be in the correct folder again. Write in "cd portfolio1" then "cd simpleperf". Now you are in the correct folder and can start to write in your client code. "python3 simpleperf.py -c -I 10.0.1.2 -p 8088 -t 25", then this message will pop up"

Host: 10.0.1.2
Port: 8088
----------------------------------------------------------------
A simpleperf client connecting to server 10.0.1.2, port 8088
----------------------------------------------------------------
Client connected with server_IP port 10.0.1.2 8088
----------------------------------------------------------------
"

After 25 seconds the raw data table will show up with the results, on the client:

"
----------------------------------------------------------
ID			         Interval		Transfer		Bandwidth
10.0.1.2:8088      0.0 - 25.0 s     121 MB           38.14 Mbps

"

And just like this test 2 is complete. 


PING: We don't use my simpleperf tool to ping between r1 and r2 but how you do it is by writing "xterm r1" in the terminal on ubuntu then you write "ping 10.0.1.2 -c 25" in the new black terminal r1 window. Now you will ping out 25 packets.  10.0.1.2 is r2 ip address, see topology.
