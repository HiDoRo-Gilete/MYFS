import config
from getmac import get_mac_address as gma

class MYFS:
    def __init__(self,myfsFile = None,sysFile=None):

        self.myfsFile = None #this is myfsFile and always open from main
        self.sysFile = None  #this is sysFile and always open from main
        self.clustor_size = None

        self.max_file_size = None
        self.max_file = None

        self.entry_size=None
        self.sys_size=None
        self.sys_index = None

        self.bitmap_size = None
        self.bitmap_index = None

        self.backup_size = None
        self.backup_index = None

        self.sdet_size = None
        self.sdet_index = None
        
        self.clustor_start = None

        if sysFile!=None and myfsFile !=None:
            self.getInfo()

    def createMYFS(self,label,password):
        self.clustor_size = config.CLUSTOR_SIZE
        self.max_file_size = config.MAX_FILE_SIZE
        self.max_file=config.MAX_FILE
        self.entry_size = config.ENTRY_SIZE
        self.sys_size,self.sys_index = config.SYS_SIZE,config.SYS_INDEX
        self.bitmap_size,self.bitmap_index = config.BITMAP_SIZE,config.BITMAP_INDEX
        self.backup_size,self.backup_index = config.BACKUP_SIZE,config.BACKUP_INDEX
        self.sdet_size,self.sdet_index = config.SDET_SIZE,config.SDET_INDEX
        self.clustor_start = config.CLUSTOR_START

        systemRegion = self.createSystemRegion(label,password)  # system region has 1024bit
        bitmapRegion =b'\x00' * self.bitmap_size
        sdetRegion = b'\x00'*self.sdet_size
        backupRegion = b'\x00'*self.backup_size
        #dataregion is too large, so can not create dataregion.
        label_sys = systemRegion
        label_myfs = bitmapRegion+sdetRegion+backupRegion
        self.sysFile=open(label+'_sys.dat','w+b')
        self.sysFile.write(label_sys)
        self.myfsFile=open(label+'_MYFS.dat','w+b')
        self.myfsFile.write(label_myfs)

    def createSystemRegion(self,label,password):
        systemData = label.encode()


    def getInfo(self):
        pass
