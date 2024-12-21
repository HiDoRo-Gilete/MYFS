import MYFS
import os
import config
from OTP import otp

def createMyFS():
    print("-------------Create Volume-------------")
    x = None
    x = input("Create a new MYFS! 'Enter' to proceed: ")
    if (x != ''):
        return None
    
    label = ""
    while (len(label) != 1 or label < 'A' or label > 'Z' ):
        label = input("Enter volume's label (A-Z): ").upper()
        
    password = ""
    while (password != None and len(password) < 6):
        password = input("Enter volume's protection password (length >=6) or 'Enter' to skip: ")
        if (password == ""):
            password = None
    myfs = MYFS.MYFS()
    myfs.createMYFS(label, password)
    return myfs

def readMyFSFromPath(myfsPath, sysPath):
    myfs = None
    try:
        myfsFile = open(myfsPath,'r+b')
        sysFile = open(sysPath, 'r+b')
        myfs = MYFS.MYFS(myfsFile, sysFile)
        if not myfs.read_result == True:
            myfs = None
    except Exception as e:
        print(e)
        print('Failed to read volume')
        pass
    return myfs

def readMyFS():
    print("-------------Read Volume-------------")
    myfsPath = ""
    while myfsPath == "":
        myfsPath = input("Enter the MYFS file's path or b/B to back: ") 
        if (myfsPath.lower() == "b"):
            myfsPath = ""
            break
        if ("_MYFS.dat" not in myfsPath):
            print("Not a MYFS file")
            myfsPath = ""
        elif not os.path.isfile(myfsPath):
            print("File does not exist :(\n")
            myfsPath = ""
    
    sysPath = ""
    while myfsPath != "" and sysPath == "":
        sysPath = input("Enter the SYS file's path or b/B to back: ") 
        if (sysPath.lower() == "b"):
            sysPath = ""
            break
        if ("_SYS.dat" not in sysPath):
            print("Not a SYS file")
            sysPath = ""
        elif not os.path.isfile(sysPath):
            print("File does not exist :(\n")
            sysPath = ""

    myfs = None
    if (myfsPath != "" and sysPath != ""):
        myfs = readMyFSFromPath(myfsPath, sysPath)
    return myfs

def selectMYFS():
    myfs = None
    while myfs == None:
        sysFiles = os.listdir('./SYS')
        myfsFiles = os.listdir('./MYFS')
        allFiles = []
        for e in sysFiles: allFiles.append(e)
        for e in myfsFiles: allFiles.append(e)
        labels = []
        for file in allFiles:
            if '_MYFS.dat' in file:
                label = file[0:1].upper()
                if labels.count(label) == 0:
                    if (label + '_SYS.dat') in allFiles:
                        labels.append(label)
                            
        label = None
        print("-----------MAIN-----------")
        print('Detected volumes:')
        for i, lb in enumerate(labels):
            print(str(i) + ".", lb)
        print(str(len(labels)) + ".", "Create new volume")
        print(str(len(labels) + 1) + ".", "Read volume")
        print("e.", "Exit")  
        option = input(">> ")
        
        if (option.lower() == 'e'):
            return None
        try:
            option = int(option)
            if (option == len(labels)):
                myfs = createMyFS()
            elif (option == len(labels) + 1):
                myfs = readMyFS()
            elif (option == len(labels) + 2):
                myfs = None
            elif (option >=0 and option < len(labels)):
                label = labels[option]
            else:
                print('No such volume!')
        except:
            if option.upper() in labels:
                label = option.upper()
                    
                
        if myfs == None and label != None:
            label = label.upper()
            myfsPath = './MYFS/' + label + '_MYFS.dat'
            sysPath = './SYS/' + label + '_SYS.dat'
            myfs = readMyFSFromPath(myfsPath, sysPath)
                
    return myfs
        
def menu(myfs: MYFS.MYFS):
    action = -1
    while True:
        myfs.info()
        print('------------------MENU------------------')
        print("0. List")
        print("1. Import")
        print("2. Export")
        print("3. Delete file")
        print("4. Recover")
        print("5. Encrypt file")
        print("6. Update volume's password")
        print("7. Encrypt volume's SYS file")
        print("b. Back")
        print("e. Exit")
        action = input(">> ")
        if (action.lower() == 'b'):
            return 0
        elif (action.lower() == 'e'):
            return -1
        try:
            action = int(action)
            if (action < 0 and action > 8):
                continue
            if action == 0:
                print("----------------List files----------------")
                myfs.printFiles()
                input()
                pass
            elif action == 1:
                print("----------------Import file----------------")
                while True:
                    path = input("Enter the file's path or b/B to back: ") 
                    if (path.lower() == "b"):
                        break
                    if not os.path.isfile(path):
                        print("File does not exist :(\n")
                    else:
                        myfs.ImportFile(path)
                        input()
                        break
                
            elif action == 2:
                print("----------------Export file----------------")
                myfs.printFiles()
                filename = input("Enter the file's name or b/B to back: ") 
                if (filename.lower() != "b"):
                    myfs.ExportFile(filename)
                    input()
                
            elif action == 3:
                print("----------------Delete file----------------")
                myfs.printFiles()
                filename = input("Enter the file's name or b/B to back: ") 
                if (filename.lower() != "b"):
                    myfs.deleteFile(filename)
                    input()
                    
            elif action == 4:
                print("----------------Recovery----------------")
                myfs.RecoveryMode()
                input()
                
            elif action == 5:
                print("----------------Encrypt file----------------")
                myfs.printFiles()
                filename = input("Enter the file's name or b/B to back: ") 
                if (filename.lower() != "b"):
                    myfs.setFilePassword(filename)
                    input()
                
            elif action == 6:
                myfs.updateFSPassword()
                
            elif action == 7:
                myfs.updateSysPassword()
                
            elif action == 8:
                return 0
            
            elif action == 9:
                return -1
            
        except:
            pass
        
def main():
    if config.OTP_ACTIVE and not otp():
       return
    myfs = None
    while True:
        myfs = selectMYFS()
        if myfs == None or menu(myfs) == -1:
            return
    
main()
