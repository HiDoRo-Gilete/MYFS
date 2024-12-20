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
    os.mkdir('./ex1/Picture')
except:
    pass

def progress(file):
    count = 0
    pos = 0
    signal = None
    endsignal = None
    block = 512
    extend = ''
    data = file.read(block)
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
    print(f"Find and recovery {count} files")




def main():
    ispathfile = False
    path,imageFile = None,None
    count = 0
    while not ispathfile:
        path = input("Enter the path Image volume (e to exit): ")
        if path.lower() =='e':
            return
        try:
            imageFile = open(path,'rb')
            ispathfile = True
        except:
            count+=1
            print("Invalid path file")
            if count==3:
                print('Failed more than 3 times. Program is exiting!')
                return
    count = 0
    thr = Thread(target=progress,args=(imageFile,))
    thr.start()
    print('Read Volumn')
    while thr.is_alive():
        print('.')
        time.sleep(0.5)

    imageFile.close()

main()