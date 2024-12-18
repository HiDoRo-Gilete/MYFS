import MYFS
import os
from OTP import run
def createMyFS():
    x = None
    x = input("Create a new MYFS! 'enter' to proceed: ")
    if (x != ''):
        return None
    
    label = ""
    while (len(label) != 1 or label < 'A' or label > 'Z' ):
        label = input("Enter volume's label (A-Z): ").upper()
        
    password = ""
    while (password != None and len(password) < 6):
        password = input("Enter volume's protection password (length >=6) or 'enter' to skip: ")
        if (password == ""):
            password = None
    myfs = MYFS.MYFS()
    myfs.createMYFS(label, password)
    return myfs

def selectMYFS():
    myfs = None
    while myfs == None:
        allfile = os.listdir('./MYFS')
        labels = []
        for file in allfile:
            if '_MYFS.dat' in file:
                label = file[0:1].upper()
                if labels.count(label) == 0:
                    if (label + '_SYS.dat') in allfile:
                        labels.append(label)
                    

        print("-----------MAIN-----------")
        print('List of volumes:')
        for i, label in enumerate(labels):
            print(str(i) + ".", label)
        print(str(len(labels)) + ".", "Create new volume")
        print("e.", "Exit")  
        
        label = None
        while (label == None):
            option = input(">> ")
            if (option.lower() == 'e'):
                myfs = None
                return None
            try:
                option = int(option)
                if (option == len(labels)):
                    myfs = createMyFS()
                    break
                elif (option == len(labels) + 1):
                    myfs = None
                    break
                elif (option >=0 and option < len(labels)):
                    label = labels[option]
                else:
                    print('No such volume!')
            except:
                if option.upper() in labels:
                    label = option.upper()
                                   
        if label != None:
            try:
                label = label.upper()
                myfsFile = open('./MYFS/' + label + '_MYFS.dat', 'r+b')
                sysFile = open('./MYFS/' + label + '_SYS.dat', 'r+b')
                myfs = MYFS.MYFS(myfsFile, sysFile)
                if not myfs.read_result == True:
                    myfs = None
            except Exception as e:
                print(e)
                print('Failed to read volume')
                myfs = None
                
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
    if not run():
        return
    myfs = None
    while True:
        myfs = selectMYFS()
        if myfs == None or menu(myfs) == -1:
            return
    
main()
