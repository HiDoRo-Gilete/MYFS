import MYFS,OTP

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
def test():
    testUnprotectedMYFS()
    
test()