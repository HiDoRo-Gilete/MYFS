import MYFS,OTP,Converter

#0. testcase smatotp
# def testSmartOTP():
#     x=OTP.getX()
#     y= OTP.make_smartOTP(x)
#     print(x,y,len(x) == 4,len(y) == 8)
    
# #1. testcase createMYFS 
# def testCreateMYFS():
#     myfs = MYFS.MYFS()
#     myfs.createMYFS('H','helloworld') #result: 2 file H_SYS.dat and H_MYFS.dat is create

# #2. testcase declare MYFS
def testDeclareMYFS():
    myfs= MYFS.MYFS()
    myfs.createMYFS('H','helloworld')
    filesys = open('./MYFS/H_SYS.dat','r+b')
    filemyfs = open('./MYFS/H_MYFS.dat','r+b')
    myfs = None
    myfs = MYFS.MYFS(filemyfs,filesys)

def testUnprotectedMYFS():
    myfs= MYFS.MYFS()
    myfs.createMYFS('G')
    filesys = open('./MYFS/G_SYS.dat','r+b')
    filemyfs = open('./MYFS/G_MYFS.dat','r+b')
    myfs = None
    myfs = MYFS.MYFS(filemyfs,filesys)
    filesys.seek(0)
    data = filesys.read(1024)
    print(data)
def testImport():
    filesys = open('./MYFS/N_SYS.dat','r+b')
    filemyfs = open('./MYFS/N_MYFS.dat','r+b')
    myfs = MYFS.MYFS(filemyfs,filesys)
    try:
        # filemyfs.seek(myfs.bitmap_index)
        # print(int.from_bytes(filemyfs.read(1)))
        # filemyfs.seek(myfs.sdet_index)
        # print(filemyfs.read(4096))
        myfs.ImportFile('D:/document/An ninh may tinh/lab 1/guid.docx')
    except Exception as e:
        print(e)
    filemyfs.seek(myfs.sdet_index)
def testExport():
    filesys = open('./MYFS/T_SYS.dat','r+b')
    filemyfs = open('./MYFS/T_MYFS.dat','r+b')
    myfs = MYFS.MYFS(filemyfs,filesys)
    try:
        myfs.ExportFile('21120253.docx')
    except Exception as e:
        print(e)
def testDelete():
    filesys = open('./MYFS/G_SYS.dat','r+b')
    filemyfs = open('./MYFS/G_MYFS.dat','r+b')
    myfs = MYFS.MYFS(filemyfs,filesys)
    try:
        myfs.deleteFile('Converter.py')
    except Exception as e:
        print(e)
def testRecovery():
    filesys = open('./MYFS/T_SYS.dat','r+b')
    filemyfs = open('./MYFS/T_MYFS.dat','r+b')
    myfs = MYFS.MYFS(filemyfs,filesys)
    try:
        myfs.RecoveryMode()
    except Exception as e:
        print(e)
def testPWFile():
    filesys = open('./MYFS/N_SYS.dat','r+b')
    filemyfs = open('./MYFS/N_MYFS.dat','r+b')
    myfs = MYFS.MYFS(filemyfs,filesys)
    try:
        myfs.setFilePassword('slide.pptx')
    except Exception as e:
        print(e)
def test():
    #testUnprotectedMYFS()
    #testImport()
    #testDelete()
    #testRecovery()
    testPWFile()
    #testExport()
test()
