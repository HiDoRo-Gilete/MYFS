import MYFS
import os

def createMyFS():
    x = input('Can not find MYFS in system! To continue, create MYFS (y/N): ')
    while x.lower() !='y' and x.lower() !='n':
        x = input('Input error, create MYFS (y/N):')
    if x == 'y':
        return None
    return None

def selectMYFS():
    allfile = os.listdir('./MYFS')
    datExist = False
    myfs = None
    for file in allfile:
        if '.dat' in file:
            datExist = True
            break
    if not datExist:
        myfs = createMyFS()
    else:
        for file in allfile:
            if '.dat' in file:
                print(file,end=' ')
        try:
            myfs = input("\nSelect MYFS file to use:")
            if myfs not in allfile:
                print('No such file!')
                myfs = None
        except:
            myfs =  None
    return myfs
        
def menu(myfsFile):
    print('---------------------------------------')
    print("1. Set/reset password for "+myfsFile)
    print("2. Check password for "+myfsFile)
    print("3. List all file in "+myfsFile)
    print("4. Set/reset password for a file in  "+myfsFile)
    print("5. Import a file to "+myfsFile)
    print("6. Export a file from "+myfsFile)
    print("7. Delete a file from "+myfsFile)
    print("8. Recovery mode "+myfsFile)
    print('---------------------------------------')
def main():
    action = -1
    myfsFile = None
    myfsFile = selectMYFS()
    if myfsFile != None:
        action = menu(myfsFile)
    else:
        return

#main()
