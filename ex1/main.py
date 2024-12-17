from threading import Thread
import time,os

block = 512
id = 0

signalJPG = b'\xFF\xD8\xFF\xE0'
signalPNG = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
endPNG = b'\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'
endJPG = b'\xFF\xD9'
#signal = b'\x85\x4E\x47\x0D\x0A\x1A\x0A'
#ending
try:
    os.mkdir('Picture')
except:
    pass

def progress(file):
    data = file.read(block)
    count = 0
    pos = 0
    signal = None
    endsignal = None
    extend = ''
    while data !=b'':
        if data[:8] == signalPNG:
            signal,endsignal = signalPNG,endPNG
            extend = '.png'
        elif data[:4] == signalJPG:
            signal,endsignal = signalJPG,endJPG
            extend = '.jpg'
        if signal != None:
            count+=1
            newfile = str(count)+extend
            desFile = open('./ex1/Picture/'+newfile,'w+b')
            size = 0
            while endsignal not in data:
                if data.count(b'\x00') != block and data.count(b'\xFF') != block:
                    desFile.write(data)
                data = file.read(block)
                size+=512
                if endsignal in data:
                    data = data[:data.index(endsignal)+len(endsignal)]
                    size+=len(data)
                    desFile.write(data)
            desFile.close() 
        data = file.read(block)
        signal = None
    print('find',count,'file')

file = open("./ex1/VHD1.Vol",'rb')
block = 512

thr = Thread(target=progress,args=(file,))
thr.start()
print('Read Volumn')
while thr.is_alive():
    print('.')
    time.sleep(0.5)

file.close()

