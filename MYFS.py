from _io import BufferedRandom
import config
from utils import generateID, getMAC, sha256, bytesToInt, aesDecrypt, aesEncrypt, hkdf, strSize, overwrite
class MYFS:
    def __init__(self,myfsFile: BufferedRandom = None,sysFile: BufferedRandom =None):
        self.label = None
        self.id = None
        self.machine_id = None
        
        self.access_password = None
        self.sys_password = None
        
        self.myfsFile = myfsFile #this is myfsFile and always open from main
        self.sysFile = sysFile  #this is sysFile and always open from main
        
        self.sys_size=None
        self.sys_index = None
        self.max_file_size = None
        self.max_file = None
        
        self.cluster_size = None
        self.entry_size=None

        self.bitmap_size = None
        self.bitmap_index = None

        self.backup_size = None
        self.backup_index = None

        self.sdet_size = None
        self.sdet_index = None
        
        self.cluster_start = None
        
        self.read_result = None
        if sysFile!=None and myfsFile !=None:
            self.read_result = self.getInfo()

    def createMYFS(self,label = None, password=None):
        self.label = label
        self.max_file_size = config.MAX_FILE_SIZE
        self.max_file=config.MAX_FILE
        self.cluster_size = config.CLUSTER_SIZE
        self.entry_size = config.ENTRY_SIZE
        self.sys_size,self.sys_index = config.SYS_SIZE,config.SYS_INDEX
        self.bitmap_size,self.bitmap_index = config.BITMAP_SIZE,config.BITMAP_INDEX
        self.backup_size,self.backup_index = config.BACKUP_SIZE,config.BACKUP_INDEX
        self.sdet_size,self.sdet_index = config.SDET_SIZE,config.SDET_INDEX
        self.cluster_start = config.CLUSTER_START

        systemRegion = self.createSystemRegion(label,password)  # system region has 1024bit
        bitmapRegion =b'\x00' * self.bitmap_size
        sdetRegion = b'\x00'*self.sdet_size
        backupRegion = b'\x00'*self.backup_size
        #dataregion is too large, so can not create dataregion.
        label_sys = systemRegion
        label_myfs = bitmapRegion+sdetRegion+backupRegion
        self.sysFile=open('./MYFS/' + label +'_SYS.dat','w+b')
        self.sysFile.write(label_sys)
        self.myfsFile=open('./MYFS/' + label +'_MYFS.dat','w+b')
        self.myfsFile.write(label_myfs)

    def createSystemRegion(self, label: str, password: str):
        volumeLabel = label.encode(encoding="ascii") # 1 byte
        self.id = generateID(size=8)
        self.machine_id = getMAC()
        volumeID = self.id.encode(encoding="ascii") # 8 random bytes 
        machineID = int(self.machine_id, 16).to_bytes(6, "big", signed=False) # 6 bytes
        
        accessControlEnable = b'\x00' if password == None else b'\x01' # 1 bytes
        accessPwdHash = b'\x00' * 32 if password == None else sha256(password.encode(encoding="utf-8")) # 32 bytes
        systemData = volumeLabel + volumeID + machineID + accessControlEnable + accessPwdHash
        # print(len(systemData)) #48
        self.access_password = None if password == None else accessPwdHash
        
        clusterSize = self.cluster_size.to_bytes(4, "big", signed=False) # 4 bytes
        entrySize = self.entry_size.to_bytes(4, "big", signed=False) # 4 bytes
        bitMapSize = self.bitmap_size.to_bytes(4, "big", signed=False) # 4 bytes
        sdetSize = self.sdet_size.to_bytes(4, "big", signed=False) # 4 bytes
        backupSize = self.backup_size.to_bytes(4, "big", signed=False) # 4 bytes
        bitMapOffset = self.bitmap_index.to_bytes(4, "big", signed=False) # 4 bytes
        sdetOffset = self.sdet_index.to_bytes(4, "big", signed=False) # 4 bytes
        backupOffset = self.backup_index.to_bytes(4, "big", signed=False) # 4 bytes
        dataOffset = self.cluster_start.to_bytes(4, "big", signed=False) # 4 bytes
        systemData += clusterSize + entrySize + bitMapSize + sdetSize + backupSize + bitMapOffset + sdetOffset + backupOffset + dataOffset
        # print(len(systemData)) # 48 + 36 = 84
        endingMarker = "MYFS".encode(encoding="ascii") # 4 bytes
        reserved = b'\x00' * (self.sys_size - len(systemData) - len(endingMarker))
        systemData += reserved + endingMarker
        # print(len(systemData)) # 1024
        
        # Add sys manager (not encrypted by default)
        isEncrypted = b'\x00' # 1 byte
        sysEncryptedNonce = b'\x00' * 8 # 8 bytes
        sysPwdHash = b'\x00' * 32 # 32 bytes
        sysDataHash = sha256(systemData) # 32 bytes  
        systemManager = isEncrypted + sysEncryptedNonce + sysPwdHash + sysDataHash + endingMarker # +4 bytes
        # print(len(systemManager)) # 77
        self.sys_password = None
        
        systemData = systemManager + systemData # 77+1024= 1097 bytes
        return systemData
    
    def getSYSData(self, file: BufferedRandom) -> bool:
        file.seek(0)
        systemData = file.read()
        if len(systemData) != 77+1024:
            print(len(systemData), "Invalid sys file")
            return False
        
        systemManager = systemData[:77]
        systemData = systemData[77:]
        
        isSysEncrypted = True if systemManager[:1] == b'\x01' else False
        sysEncryptedNonce = systemManager[1:9]
        sysPwdHash = systemManager[9: 41]
        sysDataHash = systemManager[41: 73]
        endingMarker = (systemManager[73: 77]).decode("ascii")
        if (endingMarker != "MYFS"):
            print(endingMarker, "Invalid sys file")
            return False
        
        # Check system's data integrity
        if (sysDataHash != sha256(systemData)):
            print("Sys Data is corrupted")
            return False
        
        self.sys_password = sysPwdHash if isSysEncrypted == True else None 
        print()
        # Decrypt system's data
        while (isSysEncrypted):
            try:
                sysPwd = input('SYS is encrypted! Enter password or e/E to exit: ')
                if (sysPwd.lower() == 'e'):
                    return False
                if sha256(sysPwd.encode(encoding="utf-8")) == sysPwdHash:
                    systemData = aesDecrypt(hkdf(sysPwd), sysEncryptedNonce, systemData)
                    break
                else:
                    print("Wrong password!")
            except Exception as e: print(e)
            
        # print(":)")
        try:
            print(systemData[-4:])
            sysEndingMarker = (systemData[-4:]).decode("ascii")   
            if (sysEndingMarker != "MYFS"):
                print(sysEndingMarker, "Invalid sys file")
                return False
        except Exception as e: 
            print(e)
        
        volumeLabel = (systemData[:1]).decode("ascii")
        volumeID = (systemData[1:9]).decode("ascii")
        machineID = hex(int.from_bytes(systemData[9:15], "big", signed=False))[2:]
        accessControlEnable = True if (systemData[15:16] == b'\x01') else False
        accessPwdHash = systemData[16:48]
        # print(":)")
        if (machineID != getMAC()):
            print("Can not read volume from this machine")
            return False
        
        self.access_password = accessPwdHash if accessControlEnable == True else None
        print()
        while (accessControlEnable):
            accessPwd = input('Volume is protected! Enter password or e/E to exit: ')
            if (accessPwd.lower() == 'e'):
                return False
            if sha256(accessPwd.encode(encoding="utf-8")) == accessPwdHash:
                print()
                break
            else:
                print("Wrong password!")
        
        clusterSize = int.from_bytes(systemData[48:52], "big", signed=False)
        entrySize = int.from_bytes(systemData[52:56], "big", signed=False)
        bitMapSize = int.from_bytes(systemData[56:60], "big", signed=False)
        sdetSize = int.from_bytes(systemData[60:64], "big", signed=False)
        backupSize = int.from_bytes(systemData[64:68], "big", signed=False)
        bitMapOffset = int.from_bytes(systemData[68:72], "big", signed=False)
        sdetOffset = int.from_bytes(systemData[72:76], "big", signed=False)
        backupOffset = int.from_bytes(systemData[76:80], "big", signed=False)
        dataOffset = int.from_bytes(systemData[80:84], "big", signed=False)
        # reserved = systemData[84:-4]

        self.label = volumeLabel
        self.id = volumeID
        self.machine_id = machineID
        
        self.max_file_size = None
        self.max_file = None
        self.sys_size= 1024
        self.sys_index = 0
        
        self.cluster_size = clusterSize
        self.entry_size= entrySize
        self.bitmap_size = bitMapSize
        self.bitmap_index = bitMapOffset
        self.backup_size = backupSize
        self.backup_index = backupOffset
        self.sdet_size = sdetSize
        self.sdet_index = sdetOffset
        self.cluster_start = dataOffset
        return True
    
    def info(self):
            print('------------VOLUME------------')
            print("Label: ", self.label)
            print("ID: ", self.id)
            print("Machine ID: ", self.machine_id)
            
            print("Cluster size: ", strSize(self.cluster_size, "KB"))
            print("Entry size: ", strSize(self.entry_size, "KB"))
            print("Bitmap size: ", strSize(self.bitmap_size, "KB"))
            print("Sdet Size: ", strSize(self.sdet_size, "KB"))
            print("First cluster's offset: ", strSize(self.cluster_start, "KB"))
            print()

    def getInfo(self) -> bool:
        return self.getSYSData(self.sysFile) and self.getFSData(self.myfsFile)
        
    def getFSData(self, file: BufferedRandom) -> bool:
        return True
    
    def updateAccessPassword(self):
        print("-------Update volume password-------")
        if (self.access_password != None):
            while True:
                password = input("Enter current password (>=6) or b/B to back: ")
                if (password.lower() == 'b'):
                    return None
                if (sha256(password.encode(encoding="utf-8")) == self.access_password):
                    break
                else:
                    print("Wrong password!")
                
                
        password = ""
        while (len(password) < 6):
            password = input("Enter new password (>=6) or b/B to back: ")
            if (password.lower() == 'b'):
                return None
            
        confirm = ""
        while (confirm != password):
            confirm = input("Enter again to confirm: ")
            if (confirm.lower() == 'b'):
                return None
        
        self.access_password = sha256(password.encode(encoding="utf-8"))
        overwrite(self.sysFile, 77+15, b'\x01')
        overwrite(self.sysFile, 77+16, self.access_password)
        self.sysFile.seek(0)
        systemData = self.sysFile.read()[77: 77 + 1024]
        dataHash = sha256(systemData)
        overwrite(self.sysFile, 41, dataHash)
        self.sysFile.flush()
        # self.sysFile=open('./MYFS/' + self.label +'_SYS.dat','w+b')
        print("Successfully updated!")        
        pass
    
    def updateSysPassword(self):
        print("-------Update password for sys file-------")
        if (self.sys_password != None):
            while True:
                password = input("Enter current password or b/B to back: ")
                if (password.lower() == 'b'):
                    return None
                if (sha256(password.encode(encoding="utf-8")) == self.sys_password):
                    break
                else:
                    print("Wrong password!")
        
        password = ""
        while (len(password) < 6):
            password = input("Enter new password or b/B to back: ")
            if (password.lower() == 'b'):
                return None
            
        confirm = ""
        while (confirm != password):
            confirm = input("Enter again to confirm: ")
            if (confirm.lower() == 'b'):
                return None
            
        self.sys_password = sha256(password.encode(encoding="utf-8"))

        self.sysFile.seek(0)
        systemData = self.sysFile.read()[77: 77 + 1024]
        cipher_text, nonce = aesEncrypt(hkdf(password), systemData)
        dataHash = sha256(cipher_text)
        overwrite(self.sysFile, 0, b'\x01')
        overwrite(self.sysFile, 1, nonce)
        overwrite(self.sysFile, 9, self.sys_password)
        overwrite(self.sysFile, 41, dataHash)
        overwrite(self.sysFile, 77, cipher_text)
        self.sysFile.flush()
        # self.sysFile=open('./MYFS/' + self.label +'_SYS.dat','w+b')
        print("Successfully updated!")    
        pass
