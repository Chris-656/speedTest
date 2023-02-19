import os
import re
import subprocess
import time
import json
import sys, getopt
import requests

def getWifiName():
    output = subprocess.check_output(['sudo', 'iwgetid']).decode()
    global wifi
    wifi=output.split('"')[1]
    if (wifi == ""):
        wifi="LAN"

def getConfig(configFile):
    if (not os.path.isfile(configFile)):
        f = open(configFile,"w")
        f.write('{"active":true,"speedResultFile":"~/speedtest/speedtest.csv","usbFile":"/media/usbstick/speedtest-all.csv"}')

    f = open(configFile)
    config = json.load(f)
    return config

def postRequestAPI(config,data):
    if (config["apiCmd"]):
        url = config["apiCmd"].format(wifi=wifi,down=data["download"],up=data["upload"])
        x = requests.get(url)


def writeJson(config,data):

    with open(config["jsonFile"],'r+') as fr:
        try:
            file_data = json.load(fr)
        except:
            file_data = {wifi:[]}

    with open(config["jsonFile"],'w') as fw:
        if wifi not in file_data:
            file_data[wifi] = []
        file_data[wifi].append(data)
        #file.seek(0)
        json.dump(file_data, fw)

def writeTransferFile(config, data):
    with open(config["transferFile"],'w') as file:
        json.dump(data, file)

def extractSpeedData(response):
    speedData = {
        "ping":re.search('Latency:\s+(.*?)\s', response, re.MULTILINE).group(1),
        "download":re.search('Download:\s+(.*?)\s', response, re.MULTILINE).group(1),
        "upload":re.search('Upload:\s+(.*?)\s', response, re.MULTILINE).group(1),
        "jitter":re.search('Latency:.*?jitter:\s+(.*?)ms', response, re.MULTILINE).group(1),
        "date":time.strftime('%d.%m.%y'),
        "time": time.strftime('%H:%M')
        }
    return speedData


def main(argv):
    configFile = ''
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    if (len(opts) >0):
        for opt, arg in opts:
            if opt == '-h':
                print ('speedtest.py -c <configfile>')
                sys.exit()
            elif opt in ("-c", "--configFile"):
                configFile = arg
    else:
        configFile = os.path.dirname(__file__)+"/config.json"

    getWifiName()

    config = getConfig(configFile)

    print('get Config \r\n active:{}\r\n file:{}\r\n'.format(config["active"],config["transferFile"]))
    if (not config["active"]):
        print("active is set to false Do nothing")
        sys.exit(0)

    print("getting speed data")
    response = subprocess.Popen(config["cmd"], shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    data = extractSpeedData(response)

    print("writing results")
    postRequestAPI(config,data)
    writeTransferFile(config, data)
    writeJson(config,data)

if __name__ == "__main__":
   main(sys.argv[1:])