import os
import re
import subprocess
import time
import json
import sys, getopt
import requests


def getLANInfo():

    regexLan = ' dev (\w+).*src (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    output = subprocess.check_output(['ip', 'r']).decode()
    lan = re.search(regexLan, output, re.MULTILINE).group(1)
    ip = re.search(regexLan, output, re.MULTILINE).group(2)
    lanName = ""
    if (lan.startswith("wlan")):
        output = subprocess.check_output(['sudo', 'iwgetid']).decode()
        lanName = output.split('"')[1]
    elif(lan.startswith("eth")):
        lanName = "{lan}-{ip}".format(lan=lan,ip=ip)

    return lanName

def getConfig(configFile):
    if (not os.path.isfile(configFile)):
        f = open(configFile,"w")
        f.write('{"active":true,"speedResultFile":"~/speedtest/speedtest.csv","usbFile":"/media/usbstick/speedtest-all.csv"}')

    f = open(configFile)
    config = json.load(f)
    txtLan = "".format
    config["lan"]= getLANInfo()
    return config

def postRequestAPI(config,data):
    if (config["apiCmd"]):
        url = config["apiCmd"].format(lan=config["lan"],down=data["download"],up=data["upload"])
        x = requests.get(url)


def writeJson(config,data):

    with open(config["jsonFile"],'r+') as fr:
        try:
            file_data = json.load(fr)
        except:
            file_data = {"wifi":[]}

    with open(config["jsonFile"],'w') as fw:
        if config["lan"] not in file_data:
            file_data[config["lan"]] = []
        file_data[config["lan"]].append(data)
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
        "time": time.strftime('%H:%M'),
        "ts":int(time.time()*1000)
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

    print("writing results")
    postRequestAPI(config,data)
    writeTransferFile(config, data)
    writeJson(config,data)

if __name__ == "__main__":
   main(sys.argv[1:])