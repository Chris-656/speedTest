import os
import re
import subprocess
import time
import json
import sys, getopt

def getConfig(configFile):
    if (not os.path.isfile(configFile)):
        f = open(configFile,"w")
        f.write('{"active":true,"speedResultFile":"~/speedtest/speedtest.csv","usbFile":"/media/usbstick/speedtest-all.csv"}')

    f = open(configFile)
    config = json.load(f)
    return config

def writeJson(config,data):
    with open(config["jsonFile"],'r+') as fr:
        try:
            file_data = json.load(fr)
        except:
            file_data = {"speedData":[]}

    with open(config["jsonFile"],'w') as fw:
        file_data["speedData"].append(data)
        #file.seek(0)
        json.dump(file_data, fw)

def writeTransferFile(config, data):
    with open(config["transferFile"],'w') as file:
        json.dump(data, file)

# def writeUsbFile(config, data):
#     f = open(config["usbFile"], 'a+')
#     f.write('{},{},{},{},{},{}\r\n'.format(time.strftime('%d.%m.%y'), time.strftime('%H:%M'), data["ping"], data["jitter"], data["download"], data["upload"]))
#     f.close()

def extractSpeedData(response):

    wifi =str(subprocess.check_output(['iwgetid -r'], shell=True)).split('\'')[1][:-2]

    speedData = {
        "ssid":wifi,
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


    config = getConfig(configFile)

    print('get Config \r\n active:{}\r\n file:{}\r\n'.format(config["active"],config["transferFile"]))
    if (not config["active"]):
        print("active is set to false Do nothing")
        sys.exit(0)

    print("getting speed data")
    response = subprocess.Popen(config["cmd"], shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    data = extractSpeedData(response)

    writeJson(config,data)
    writeTransferFile(config, data)

if __name__ == "__main__":
   main(sys.argv[1:])