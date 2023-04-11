This is my step by step, how to use my simpleperf tool.

When you are in the terminal window you have to navigate to the right folder. Write "portfolio1" then "cd simpleperf", then we are ready to run. 

Between h1 and h4:
First we would like to run the server side (h4). Write in "python3 simpleperf.py -s -b 10.0.5.2 -p 8080". -s is to indicat we want to run in server mode, -b is to bind it the the right ip address and -p is for the right port number: it should receive data and track the total number of bytes. Now you will se the server side pop up with a text "A simpleperf server is listening on port 8080". 

Now the for the client side(h1). Again navigate to the right folder in a new terminal window, type "portfolio1" then "cd simpleperf". Then type in "python3 simpleperf.py -c -I 10.0.5.2 -p 8080", -c is to indicate we want to run in client mode, -I is for binding to the right ip address. It will now calculate and display the bandwidth, now we see "A simpleperf client connecting to server 10.0.5.2, port 8080".

Now the server and client are communicating and we are waiting 25 seconds on the results (default time). We can see on the server side that "A simpleperf client with IP ('10.0.0.2', 469906) is connected with server IP: 10.0.5.2, 8080" and on the client "Client connected with server_IP port 10.0.5.2 8080". After 25 seconds we see the tables have been printed out with our raw data.

On the client side:

"ID                   Interval    Transfer       Bandwidth
10.0.5.2:8080      0.0 - 25.0 s     91 MB        28.38 Mbps

Server side: 
"ID               Interval      Received    Rate
10.0.0.2:46906     25 s         91MB        4 Mbps

If we want to see the intervals with x seconds in between each interval we have to specify with the -i flag for how many seconds each interval is going to be, and with -t, time flag if we want a different time from 25 seconds. What I instructed now is the basic version of the simpleperf tool. If you want to choose the amount of data being transfered, have parallell connections etc. you can use the different flags I have implemented. If you for example want to see intervals with 5 seconds in between each interval in the time space 35 seconds you write the code like this "python3 simpleperf.py -c -I 10.0.5.2 -p 8080 -t 35 -i 5 ". Here we have also specified the ip address and port number to match the client to the server (-I and -p). The server code is still just "simpleperf.py -s". 

The client side will now print out: 
"----------------------------------------------------------------
ID                Interval           Transfer   Bandwidth
10.0.5.2:8080     0.0 - 5.0 s       19.4 MB     4.06 Mbps
10.0.5.2:8080     5.0 - 10.0 s      12.4 MB     4.06 Mbps
10.0.5.2:8080     10.0 - 15.0 s     17.5 MB     4.07 Mbps
10.0.5.2:8080     15.0 - 20.0 s     18.9 MB     4.07 Mbps
10.0.5.2:8080     20.0 - 25.0 s     17.3 MB     4.08 Mbps
10.0.5.2:8080     25.0 - 30.0 s     17.3 MB     4.06 Mbps
10.0.5.2:8080     30.0 - 35.0 s     18.6 MB     4.08 Mbps
FINISHED
----------------------------------------------------------
ID                   Interval      Transfer      Bandwidth
10.0.5.2:8080       0.0 - 35.0 s    128 MB       28.44 Mbps

Here we can see each interval being printed out with 5 sec in between in total 35 seconds. The server side will also display the last line with summary of the raw data. 

Server side: 
"ID              Interval    Received          Rate
10.0.5.2:8080    35 s         128 MB          4 Mbps

As we can see, there are a lot of flags that we can play around with and get results from. 

Other flags are 
-P = Parallell connections
-n = Amount of data to transfer in the format <X>KB, <X>MB, <X>GB
-f = Choose the format of the summary of results


