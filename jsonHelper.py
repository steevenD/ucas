import os.path
import json

def writeInFile(filePath, data):
    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def readFromFile(filePath):
    with open(filePath, mode='r', encoding='utf-8') as f:
        return json.load(f)

def addToFile(fileName, data):
    filePath = './' + fileName + '.json'
    if os.path.isfile(filePath) != True:
        writeInFile(filePath, [])
    datas = readFromFile(filePath)
    datas.append(data)
    writeInFile(filePath, datas)