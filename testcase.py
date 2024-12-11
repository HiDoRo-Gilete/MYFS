import MYFS,OTP
#0. testcase smatotp
x=OTP.getX()
y= OTP.make_smartOTP(x)
print(x,y,len(x) == 4,len(y) == 8)

#1. testcase createMYFS 
myfs = MYFS.MYFS()
myfs.createMYFS('H','helloword') #result: 2 file H_SYS.dat and H_MYFS.dat is create

#2. testcase declare MYFS

myfs= MYFS.MYFS()
myfs.createMYFS('H','helloword')
filesys = open('H_SYS.dat','r+b')
filemyfs = open('H_MYFS.dat','r+b')
myfs = None
myfs = MYFS.MYFS(filemyfs,filesys)