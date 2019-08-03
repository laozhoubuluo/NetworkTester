#!/usr/bin/python3
import os
import time
import urllib
from urllib import parse
import sys
import configparser
import requests

runPath = sys.path[0] + "/"
logFile = runPath + "network.log"
playWarningAudioCommand = runPath + "playWarningAudio.sh"
playOnlineAudioCommand = runPath + "playOnlineAudio.sh"
#playWarningAudioCommand = "cat /proc/cpuinfo"

configPath = runPath + "config.ini"
config = configparser.ConfigParser()
config.read(configPath)

def readConfig(table,key):
    print(config[table][key])
    if config[table][key] == "yes":
        return True
    elif config[table][key] == "no":
        return False
    else:
        return config[table][key]

debugSwitch = readConfig("run","debug")
print("debugSwitch: " + str(debugSwitch))
sleepTime = int(readConfig("run","sleepTime"))
playAudio = readConfig("report","playAudio")
print("playAudio: " + str(playAudio))
reportToTelegram = readConfig("report","reportToTelegram")
print("reportToTelegram: " + str(reportToTelegram))
telegramBotKey = readConfig("report","telegramBotKey")
telegramBotChat = readConfig("report","telegramBotChat")
locationName = readConfig("report","locationName")
reportToTelegram_WithOutboundIPv4 = readConfig("report","reportToTelegram_WithOutboundIPv4")
reportToTelegram_WithOutboundIPv6 = readConfig("report","reportToTelegram_WithOutboundIPv6")

def getNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def logToStd(content):
    timeNow = getNowTime()
    print('[' + timeNow + '] ' + content)
def logToFile(content):
    timeNow = getNowTime()
    logToStd(content)
    content = '[' + timeNow + '] ' + content
    os.system("echo " + "'" + content + "' >> " + logFile)

def isNetworkAvailable():
    output = os.popen(runPath + "pingTest.sh")
    pingResult = str(output.read())
    # print(pingResult)
    pingSuccess = pingResult.count('from')
    if pingSuccess > 1:
        return True
    else:
        return False

def playAudio(command):
    if playAudio:
        logToFile("Play audio (" + command + ")")
        playAudioReturn = os.system(command + " > /dev/null 2>&1")
        if playAudioReturn != 0:
            logToFile("Play audio (" + command + ") failed!")
        else:
            logToFile("Play audio (" + command + ") complete")

def errorMessageReport(body):
    if reportToTelegram:
        logToStd("Report error information to Telegram")
        default_encoding = 'utf-8'
        if sys.getdefaultencoding() != default_encoding:
            reload(sys)
            sys.setdefaultencoding(default_encoding)
        botKey = telegramBotKey
        toChat   = telegramBotChat
        subject  = locationName + " 检测到网络连接中断"
        message_ip = "\n"
        if reportToTelegram_WithOutboundIPv4:
            try:
                v4ip = requests.get(url="https://api-ipv4.ip.sb/ip")
                if v4ip.status_code == 200:
                    message_ip = message_ip + "\n公网IPv4地址:" + v4ip.text
            except:
               message_ip = message_ip + "\n公网IPv4地址:获取失败\n"
        if reportToTelegram_WithOutboundIPv6:
            try:
                v6ip = requests.get(url="https://api-ipv6.ip.sb/ip")
                if v6ip.status_code == 200:
                    message_ip = message_ip + "\n公网IPv6地址:" + v6ip.text
            except:
                    message_ip = message_ip + "\n公网IPv6地址:获取失败\n"
        message = subject + "\n\n" + body + message_ip + "\nZZNetworkTester @ " + locationName
        link = "https://telegramapi.asec01.net/bot" + botKey + "/sendmessage?text=" + urllib.parse.quote(message) + "&chat_id=" + toChat
        command = "curl \"" + link+"\""
        reportErrMsgReturn = os.system(command + " > /dev/null 2>&1")
        if reportErrMsgReturn != 0:
            logToFile("Report error information to Telegram failed!")
        else:
            logToFile("Report error information to Telegram complete")



#def check():
while True:
    if isNetworkAvailable():
        if debugSwitch:
            logToStd("Network status ok")
        time.sleep(sleepTime)
    else:
        offlineTimeMark = getNowTime()
        logToFile("Network error dected")
        playAudio(playWarningAudioCommand)
        while not isNetworkAvailable():
            playAudio(playWarningAudioCommand)
        onlineTimeMark = getNowTime()
        logToFile("Network back online")
        playAudio(playOnlineAudioCommand)
        errorMessageReport("中断时间:" + offlineTimeMark + "\n恢复时间:" + onlineTimeMark)

# check()
