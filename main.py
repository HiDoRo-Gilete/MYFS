import MYFS
import os

def createMyFS():
    x = input('Create a new MYFS (y/N): ')
    while x.lower() !='y' and x.lower() !='n':
        x = input('Input error, create MYFS (y/N):')
    if x == 'y':
        label = ""
        while (len(label) != 1 or label < 'A' or label > 'Z' ):
            label = input("Enter volume's label (A-Z): ").upper()
            
        password = ""
        while (len(password) < 6):
            password = input("Enter volume's protection password (>=6): ")
        myfs = MYFS.MYFS()
        myfs.createMYFS(label, password)
        return myfs
    return None

def selectMYFS():
    allfile = os.listdir('./MYFS')
    labels = []
    for file in allfile:
        if '_MYFS.dat' in file:
            label = file[0:1].upper()
            if labels.count(label) == 0:
                if (label + '_SYS.dat') in allfile:
                    labels.append(label)
    
    if len(labels) == 0:
        myfs = createMyFS()
    else:
        print('List of volumes detected:')
        for i, label in enumerate(labels):
            print(str(i) + ".", label)
        print(str(len(labels)) + ".", "Create new volume")
        print(str(len(labels) + 1) + ".", "Exit")  
        label = None
        while (label == None):
            option = input(">> ")
            
            try:
                option = int(option)
                if (option == len(labels)):
                    myfs = createMyFS()
                    return myfs
                elif (option == len(labels) + 1):
                    return None
                elif (option >=0 and option < len(labels)):
                    label = labels[option]
                else:
                    print('No such volume!')
                    label = None
            except:
                pass                
        try:
            label = label.upper()
            myfsFile = open('./MYFS/' + label + '_MYFS.dat', 'r+b')
            sysFile = open('./MYFS/' + label + '_SYS.dat', 'r+b')
            myfs = MYFS.MYFS(myfsFile, sysFile)
            if not myfs.read_result == True:
                myfs = None
        except:
            print('Failed to read volume')
            myfs = None
    return myfs
        
def menu(myfs: MYFS.MYFS):
    myfs.info()

    action = -1
    while True:
        print('------------------MENU---------------------')
        print("0. List")
        print("1. Import")
        print("2. Export")
        print("3. Delete file")
        print("4. Recover")
        print("5. Encrypt file")
        print("6. Update volume's password")
        print("7. Encrypt volume's sys file")
        print("8. Exit")
        action = input(">> ")
        try:
            action = int(action)
            if (action < 0 and action > 8):
                continue
            if action == 0:
                print('Developing...')
                pass
            elif action == 1:
                print('Developing...')
                pass
            elif action == 2:
                print('Developing...')
                pass
            elif action == 3:
                print('Developing...')
                pass
            elif action == 4:
                print('Developing...')
                pass
            elif action == 5:
                print('Developing...')
                pass
            elif action == 6:
                myfs.updateAccessPassword()
                pass
            elif action == 7:
                myfs.updateSysPassword()
                pass
            elif action == 8:
                return None
        except:
            pass
        
def main():
    myfs = None
    myfs = selectMYFS()
    if myfs == None:
        return
    menu(myfs)
    
main()
