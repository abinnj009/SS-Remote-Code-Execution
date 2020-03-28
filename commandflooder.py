import paramiko
import threading
import os.path
import subprocess
import time
import sys
import re


def ip_is_valid():
    checkFlag = False
    global ip_list
    
    while True:
        ip_file = raw_input("# Enter IP file name and extension: ")
       
        
        #Changing exception message
        try:
            
            selected_ip_file = open(ip_file, 'r')
            
           
            selected_ip_file.seek(0)
            
            
            ip_list = selected_ip_file.readlines()
            
           
            selected_ip_file.close()
            
        except IOError:
            print "\n* File %s does not exist! Please check and try again!\n" % ip_file
            
                 
        for ip in ip_list:
            a = ip.split('.')
            
            if (len(a) == 4) and (1 <= int(a[0]) <= 223) and (int(a[0]) != 127) and (int(a[0]) != 169 or int(a[1]) != 254) and (0 <= int(a[1]) <= 255 and 0 <= int(a[2]) <= 255 and 0 <= int(a[3]) <= 255):
                checkFlag = True
                break
                 
            else:
                print '\n* There was an INVALID IP address! Please check and try again!\n'
                checkFlag = False
                continue
               
        if checkFlag == False:
            continue
        
        elif checkFlag == True:
            break

  
    print "\n* Checking IP reachability. Please wait...\n"
    
    checkFlag2 = False
    
    while True:
        for ip in ip_list:
            ping_reply = subprocess.call(['ping', '-c', '2', '-w', '2', '-q', '-n', ip])
            
            if ping_reply == 0:
                checkFlag2 = True
                continue
            
            elif ping_reply == 2:
                print "\n* No response from device %s." % ip
                checkFlag2 = False
                break
            
            else:
                print "\n* Ping to the following device has FAILED:", ip
                checkFlag2 = False
                break
            
       
        if checkFlag2 == False:
            print "* Please re-check IP address list or device.\n"
            ip_is_valid()
        
        elif checkFlag2 == True:
            print '\n* All devices are reachable. Waiting for username/password file...\n'
            break


def user_is_valid():
    global user_file
    
    while True:
      
        user_file = raw_input("# Enter user/pass file name and extension: ")
       
        
        
        if os.path.isfile(user_file) == True:
            print "\n* Username/password file has been validated. Waiting for command file...\n"
            break
        
        else:
            print "\n* File %s does not exist! \n" % user_file
            continue


def cmd_is_valid():
    global cmd_file
    
    while True:
       
        cmd_file = raw_input("# Enter command file name and extension: ")
        
        
      
        if os.path.isfile(cmd_file) == True:
            print "\n* Sending command(s) to device(s)...\n"
            break
        
        else:
            print "\n* File %s does not exist!\n" % cmd_file
            continue

try:  
    ip_is_valid()
    
except KeyboardInterrupt:
    print "\n\n* Program aborted by user.\n"
    sys.exit()

try:  
    user_is_valid()
    
except KeyboardInterrupt:
    print "\n\n* Program aborted by user. \n"
    sys.exit()

try:
   
    cmd_is_valid()
    
except KeyboardInterrupt:
    print "\n\n* Program aborted by user. \n"
    sys.exit()

def open_ssh_conn(ip):
    
    try:
       
        selected_user_file = open(user_file, 'r')
     
        selected_user_file.seek(0)
        
      
        username = selected_user_file.readlines()[0].split(',')[0]
        
        
        selected_user_file.seek(0)
        
        
        password = selected_user_file.readlines()[0].split(',')[1].rstrip("\n")
        
       
        session = paramiko.SSHClient()
        
       
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
              
        session.connect(ip, username = username, password = password)
        
       
        connection = session.invoke_shell()	
        
       
        connection.send("terminal length 0\n")
        time.sleep(1)
        
        
        connection.send("\n")
        connection.send("configure terminal\n")
        time.sleep(1)
        
       
        selected_cmd_file = open(cmd_file, 'r')
            
       
        selected_cmd_file.seek(0)
        

        for each_line in selected_cmd_file.readlines():
            connection.send(each_line + '\n')
            time.sleep(2)
        
        selected_user_file.close()
        
       
        selected_cmd_file.close()
        
        
        router_output = connection.recv(65535)
        
        if re.search(r"% Invalid input detected at", router_output):
            print "* There was at least one IOS syntax error on device %s" % ip
            
        else:
            print "\nDONE for device %s" % ip
       
        session.close()
     
    except paramiko.AuthenticationException:
        print "* Invalid username or password. \n* Check the username/password file or the device configuration!"
        print "* Closing program...\n"

   
def create_threads():
    threads = []
    for ip in ip_list:
        th = threading.Thread(target = open_ssh_conn, args = (ip,))  
        th.start()
        threads.append(th)
        
    for th in threads:
        th.join()

create_threads()
