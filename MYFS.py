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
        
        # Add sys manager (not encrypted by default)
        isSysEncrypted = b'\x00' # 1 byte
        sysEncryptedNonce = b'\x00' * 8 # 8 bytes
        sysPwdHash = b'\x00' * 32 # 32 bytes
        sysDataHash = sha256(systemData) # 32 bytes  
        sysEndingMarker = "MYFS".encode(encoding="ascii") # 4 bytes
        manager = isSysEncrypted + sysEncryptedNonce + sysPwdHash + sysDataHash + sysEndingMarker
        # print(len(systemManager)) # 77
        self.sys_password = None
        systemData += manager
        
        endingMarker = "MYFS".encode(encoding="ascii") # 4 bytes
        reserved = b'\x00' * (self.sys_size - len(systemData) - len(endingMarker))
        systemData += reserved + endingMarker
        # print(len(systemData)) # 1024
        return systemData
    
    def getSYSData(self, file: BufferedRandom) -> bool:
        file.seek(0)
        systemData = file.read()
        if len(systemData) != 1024:
            print(len(systemData), "Invalid sys file")
            return False
        
        metadata = systemData[:84]
        manager = systemData[84:84+77]
        endingMarker = (systemData[-4:]).decode("ascii")
        
        isSysEncrypted = True if manager[:1] == b'\x01' else False
        sysEncryptedNonce = manager[1:9]
        sysPwdHash = manager[9: 41]
        sysDataHash = manager[41: 73]
        sysEndingMarker = (manager[73: 77]).decode("ascii")
        # Check manager's ending marker
        if (sysEndingMarker != "MYFS"):
            print(sysEndingMarker, "Invalid sys file")
            return False
        self.sys_password = sysPwdHash if isSysEncrypted == True else None 

        try:
            print(endingMarker)
            if (endingMarker != "MYFS"):
                print(endingMarker, "Invalid sys file")
                return False
        except Exception as e: 
            print(e)
            
        print()
        # Check system's data integrity
        if (sysDataHash != sha256(metadata)):
            print("SYS data is corrupted")
            return False
        
        # Decrypt system's data
        while (isSysEncrypted):
            try:
                sysPwd = input('SYS is encrypted! Enter password or e/E to exit: ')
                if (sysPwd.lower() == 'e'):
                    return False
                if sha256(sysPwd.encode(encoding="utf-8")) == sysPwdHash:
                    metadata = aesDecrypt(hkdf(sysPwd), sysEncryptedNonce, metadata)
                    break
                else:
                    print("Wrong password!")
            except Exception as e: print(e)
            
        
        volumeLabel = (metadata[:1]).decode("ascii")
        volumeID = (metadata[1:9]).decode("ascii")
        machineID = hex(int.from_bytes(metadata[9:15], "big", signed=False))[2:]
        accessControlEnable = True if (metadata[15:16] == b'\x01') else False
        accessPwdHash = metadata[16:48]
        self.access_password = accessPwdHash if accessControlEnable == True else None
        # Check machine's origin
        if (machineID != getMAC()):
            print("Can not read volume from this machine")
            return False
        
        while (accessControlEnable):
            accessPwd = input('Volume is protected! Enter password or e/E to exit: ')
            if (accessPwd.lower() == 'e'):
                return False
            if sha256(accessPwd.encode(encoding="utf-8")) == accessPwdHash:
                break
            else:
                print("Wrong password!")
        
        clusterSize = int.from_bytes(metadata[48:52], "big", signed=False)
        entrySize = int.from_bytes(metadata[52:56], "big", signed=False)
        bitMapSize = int.from_bytes(metadata[56:60], "big", signed=False)
        sdetSize = int.from_bytes(metadata[60:64], "big", signed=False)
        backupSize = int.from_bytes(metadata[64:68], "big", signed=False)
        bitMapOffset = int.from_bytes(metadata[68:72], "big", signed=False)
        sdetOffset = int.from_bytes(metadata[72:76], "big", signed=False)
        backupOffset = int.from_bytes(metadata[76:80], "big", signed=False)
        dataOffset = int.from_bytes(metadata[80:84], "big", signed=False)

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
            print("Label:", self.label)
            print("ID:", self.id)
            print("Machine ID:", self.machine_id)
            print("Protection:", "None" if self.access_password == None else "Password")
            print("SYS encryption:", "False" if self.sys_password == None else "Yes")
            print()
            
            print("Cluster size:", strSize(self.cluster_size, "KB"))
            print("Entry size:", strSize(self.entry_size, "KB"))
            print("Bitmap size:", strSize(self.bitmap_size, "KB"))
            print("Sdet Size:", strSize(self.sdet_size, "KB"))
            print("First cluster's offset:", strSize(self.cluster_start, "KB"))
            print()

    def getInfo(self) -> bool:
        return self.getSYSData(self.sysFile) and self.getFSData(self.myfsFile)
        
    def getFSData(self, file: BufferedRandom) -> bool:
        return True
    
    def updateFSPassword(self):
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
        overwrite(self.sysFile, 15, b'\x01')
        overwrite(self.sysFile, 16, self.access_password)
        
        self.sysFile.seek(0)
        systemData = self.sysFile.read()
        metadata = systemData[:84]
        
        # update manager # sysDataHash
        overwrite(self.sysFile, 84+41, sha256(metadata))
        self.sysFile.flush()
        print("Successfully updated!")   
        input()     
        pass
    
    def updateSysPassword(self):
        print("-------Update password for sys file-------")
        old_password = ""
        if (self.sys_password != None):
            while True:
                old_password = input("Enter current password or b/B to back: ")
                if (old_password.lower() == 'b'):
                    return None
                if (sha256(old_password.encode(encoding="utf-8")) == self.sys_password):
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
            
        try:
            self.sys_password = sha256(password.encode(encoding="utf-8"))
            self.sysFile.seek(0)
            systemData = self.sysFile.read()
            # decrypt to get plain metadata
            metadata = self.decryptSysData(systemData, old_password)
            
            # create new manager
            isSysEncrypted = b'\x01' # 1 byte
            # re-encrypt metadata
            sysEncryptedData, sysEncryptedNonce = aesEncrypt(hkdf(password), metadata)
            sysPwdHash = self.sys_password # 32 bytes
            sysDataHash = sha256(sysEncryptedData)
            sysEndingMarker = "MYFS".encode(encoding="ascii") # 4 bytes
            manager = isSysEncrypted + sysEncryptedNonce + sysPwdHash + sysDataHash + sysEndingMarker # +4 bytes
            overwrite(self.sysFile, 84+0, manager)
            overwrite(self.sysFile, 0, sysEncryptedData)
            self.sysFile.flush()
            print("Successfully updated!")   
            input() 
        except Exception as e: print(e)
        pass
    
    def decryptSysData(self, systemData: bytes, sysPwd: str):
        metadata = systemData[:84]
        manager = systemData[84: 84+77]
        isSysEncrypted = True if manager[:1] == b'\x01' else False
        if isSysEncrypted == False:
            return metadata
        
        sysEncryptedNonce = manager[1:9]
        sysPwdHash = manager[9: 41]
        sysDataHash = manager[41: 73]
        if sha256(metadata) != sysDataHash:
            print("SYS data is corrupted")
            return None
        if (sha256(sysPwd.encode()) != sysPwdHash):
            print("Wrong password!")
            return None
        return aesDecrypt(hkdf(sysPwd), sysEncryptedNonce, metadata)
