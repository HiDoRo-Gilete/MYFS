from _io import BufferedRandom
import config,Converter,os,datetime
import hashlib
from Cryptodome.Cipher import AES 
from utils import generateID, getMAC, sha256, bytesToInt, aesDecrypt, aesEncrypt, hkdf, strSize, overwrite
class MYFS:
    def __init__(self,myfsFile: BufferedRandom = None,sysFile: BufferedRandom =None):
        self.label = None
        self.id = None
        self.machine_id = None
        self.allFiles =[]
        
        self.access_password = None
        self.sys_password = None
        
        self.myfsFile = myfsFile #this is myfsFile and always open from main
        self.sysFile = sysFile  #this is sysFile and always open from main
        
        self.sys_size=None
        self.sys_index = None
        self.max_file_size = config.MAX_FILE_SIZE
        self.max_file = config.MAX_FILE
        
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
            self.allFiles = self.List()

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
        self.myfsFile.write(1024*b'\x00')
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
        
        clusterSize = config.CLUSTER_SIZE.to_bytes(4, "big", signed=False) # 4 bytes
        entrySize = config.ENTRY_SIZE.to_bytes(4, "big", signed=False) # 4 bytes
        bitMapSize = config.BITMAP_SIZE.to_bytes(4, "big", signed=False) # 4 bytes
        sdetSize = config.SDET_SIZE.to_bytes(4, "big", signed=False) # 4 bytes
        backupSize = config.BACKUP_SIZE.to_bytes(4, "big", signed=False) # 4 bytes
        bitMapOffset = config.BITMAP_INDEX.to_bytes(4, "big", signed=False) # 4 bytes
        sdetOffset = config.SDET_INDEX.to_bytes(4, "big", signed=False) # 4 bytes
        backupOffset = config.BACKUP_INDEX.to_bytes(4, "big", signed=False) # 4 bytes
        dataOffset = config.CLUSTER_START.to_bytes(4, "big", signed=False) # 4 bytes
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
            # print(endingMarker)
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
        print("\nVolume: "+ volumeLabel +" - MYFS\n")
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
            print()
            print('------------INFO------------')
            print("Volume Label:", self.label)
            print("Volume ID:", self.id)
            print("Machine ID:", self.machine_id)
            print("Protection:", "None" if self.access_password == None else "Password")
            print("SYS encryption:", "False" if self.sys_password == None else "Yes")
            print()
            
            print("Cluster size:", strSize(self.cluster_size, "KB"))
            print("Entry size:", strSize(self.entry_size, "KB"))
            print("Bitmap size:", strSize(self.bitmap_size, "KB"))
            print("SDET Size:", strSize(self.sdet_size, "KB"))
            print("First cluster's offset:", strSize(self.cluster_start))
            print()

    def getInfo(self) -> bool:
        return self.getSYSData(self.sysFile) and self.getFSData(self.myfsFile)
        
    def getFSData(self, file: BufferedRandom) -> bool:
        return True
    
    def updateFSPassword(self):
        print("-----------Update Volume Password-----------")
        if (self.access_password != None):
            while True:
                password = input("Enter current password or b/B to back: ")
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
        print("-----------Encrypt Volume SYS-----------")
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
            password = input("Enter new password (>=6) or b/B to back: ")
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

    def printFiles(self):
        if len(self.allFiles) == 0:
            print("Empty")
        else:
            for i, file in enumerate(self.allFiles):
                print(str(i) + ".", file.get("filename"), "-", file.get("size"))
        print()
    #====================================================MYFS DATA==================================
                        
    def ImportFile(self,path):
        
        self.sys_index = config.SYS_INDEX
        self.cluster_size = config.CLUSTER_SIZE
        self.entry_size=config.ENTRY_SIZE

        self.bitmap_size = config.BITMAP_SIZE
        self.bitmap_index = config.BITMAP_INDEX

        self.backup_size = config.BACKUP_SIZE
        self.backup_index = config.BACKUP_INDEX

        self.sdet_size = config.SDET_SIZE
        self.sdet_index = config.SDET_INDEX
        
        self.cluster_start = config.CLUSTER_START
        self.cluster_size = config.CLUSTER_SIZE

        size=os.path.getsize(path)
        if size >self.max_file_size:
            raise ValueError('File is too large!')
        filename = path.split('/')[len(path.split('/'))-1]
        if filename in [fn['filename'] for fn in self.allFiles]:
            raise ValueError('File is existed on MYFS!')
        if len(self.allFiles) == self.max_file:
            raise ValueError('The system has reached the maximum file')
        #if os.path.getsize(path) < 100*1024*1024:
            #backup
        entry = b'\x01'
        #ngay tao
        current_time = datetime.datetime.now()
        y,m,d= current_time.year-1980, current_time.month, current_time.day
        byear = Converter.decimalToBit(y,0) 
        if len(byear) !=7: byear = '0'*(7-len(byear)) +byear
        bmonth= Converter.decimalToBit(m,0) 
        if len(bmonth) !=4: bmonth = '0'*(4-len(bmonth)) +bmonth
        bdate = Converter.decimalToBit(d,0) 
        if len(bdate) !=5: bdate = '0'*(5-len(bdate)) +bdate
        Date= Converter.bitstring_to_bytes(byear+bmonth+bdate,2)
        #gio tao
        h,m,s= current_time.hour, current_time.minute, current_time.second//2
        bhour = Converter.decimalToBit(h,0)
        if len(bhour) !=5: bhour = '0'*(5-len(bhour)) +bhour
        bminute= Converter.decimalToBit(m,0) 
        if len(bminute) !=6: bminute = '0'*(6-len(bminute)) +bminute
        bsecond = Converter.decimalToBit(s,0) 
        if len(bsecond) !=5: bsecond = '0'*(5-len(bsecond)) +bsecond
        Time= Converter.bitstring_to_bytes(bhour+bminute+bsecond,2)
        entry+=Date+Time+Date+Time
        entry+=Converter.intToByte(size,4)
        entry+=b'\x00'
        entry+=b'\x00'*8
        entry+=b'\x00'*32
        if size < 100*1024*1024:
            f=open(path,'rb')
            data = f.read()
            f.close()
            entry+=sha256(data)
        else: entry+= b'\x00' *32
        #print(len(entry))
        entry+=b'\x00'
        entry+= Converter.intToByte(len(filename),1)
        entry+= Converter.intToByte(len(path),1)
        entry+=filename.encode()
        entry+=path.encode()
        #data run
        pos = self.findAvailableEntry()
        #print(pos)
        self.myfsFile.seek(self.bitmap_index)
        bitstring = ''.join(format(byte, '08b') for byte in self.myfsFile.read(self.bitmap_size))
        numcluster = os.path.getsize(path) //self.cluster_size +1
        datarun,newbitstring,arr_Datarun = Converter.createDatarun(bitstring,numcluster)
        entry+=datarun
        fs = open(path,'rb')
        for item in arr_Datarun:
            self.myfsFile.seek(self.getOffset(item[0]))
            for i in range(item[1]):
                datasrc = fs.read(self.cluster_size)
                self.myfsFile.write(datasrc)
        newbyte = Converter.bitstring_to_bytes(newbitstring,self.bitmap_size)
        self.myfsFile.seek(self.bitmap_index)
        self.myfsFile.write(newbyte)
        #print(entry)
        self.myfsFile.seek(pos)
        self.myfsFile.write(entry)
        POS = [pos]
        #backup
        if size <100*1024*1024:
            c_entry = entry[:86]+b'\x01'+entry[87:]
            pos = self.findAvailableEntry()
            #print(pos)
            self.myfsFile.seek(self.bitmap_index)
            bitstring = ''.join(format(byte, '08b') for byte in self.myfsFile.read(self.bitmap_size))
            print(bitstring[:10])
            #numcluster = os.path.getsize(path) //self.cluster_size +1
            datarun,newbitstring,arr_Datarun = Converter.createDatarun(bitstring,numcluster)
            fs.seek(0)
            for item in arr_Datarun:
                self.myfsFile.seek(self.getOffset(item[0]))
                for i in range(item[1]):
                    datasrc = fs.read(self.cluster_size)
                    self.myfsFile.write(datasrc)
            newbyte = Converter.bitstring_to_bytes(newbitstring,self.bitmap_size)
            self.myfsFile.seek(self.bitmap_index)
            self.myfsFile.write(newbyte)
            #print(entry)
            self.myfsFile.seek(pos)
            index_datarun = 89 +c_entry[87]+c_entry[88]
            c_entry = c_entry[:index_datarun] + datarun+c_entry[index_datarun+len(datarun):]
            self.myfsFile.write(c_entry)
            POS.append(pos)
        # print(POS)
        # for p in POS:
        #     self.myfsFile.seek(p)
        #     entry = self.myfsFile.read(self.entry_size)
        #     filenamelen = entry[87]
        #     datarun = entry[89+filenamelen+entry[88]:]
        #     datarun=datarun[:datarun.index(b'\x00')]
        #     arr = Converter.getDatarun(datarun)
        #     for item in arr:
        #         self.myfsFile.seek(self.getOffset(item[0]))
        #         for i in range(item[1]):
        #             dataread = self.myfsFile.read(self.cluster_size)
        #             #print('1======\n',self.getOffset(item[0]),self.sdet_index)
        #             if oldkey !=b'':
        #                 dataread=aes2.decrypt(dataread)
        #             dataread = n_aes.encrypt(dataread)
        #             self.myfsFile.seek(self.getOffset(item[0]+i))
        #             self.myfsFile.write(dataread)
        #     entry = entry[:13]+b'\x01'+n_aes.nonce+sha256(newkey)+entry[54:]
        #     self.myfsFile.seek(p)
        #     self.myfsFile.write(entry)
        self.allFiles = self.List()

    def List(self):
        list=[]
        self.myfsFile.seek(self.sdet_index)
        pos = self.sdet_index
        entry = self.myfsFile.read(self.entry_size)
        while entry[0] != 0:
            if entry[0] == 1 and entry[86] == 0:
                filesize = int.from_bytes(entry[9:13])
                filenamelen = entry[87]
                pathlen = entry[88]
                bytedate_create = Converter.decimalToBit(entry[1],1)+Converter.decimalToBit(entry[2],1)
                y1 = Converter.bitstring_to_bytes(bytedate_create[0:7],1)[0]
                m1= Converter.bitstring_to_bytes(bytedate_create[7:11],1)[0]
                d1 = Converter.bitstring_to_bytes(bytedate_create[11:16],1)[0]
                bytetime_create = Converter.decimalToBit(entry[3],1)+Converter.decimalToBit(entry[4],1)
                h1 = Converter.bitstring_to_bytes(bytetime_create[0:5],1)[0]
                mi1= Converter.bitstring_to_bytes(bytetime_create[5:11],1)[0]
                s1 = Converter.bitstring_to_bytes(bytetime_create[11:16],1)[0]

                bytedate_modifier = Converter.decimalToBit(entry[5],1)+Converter.decimalToBit(entry[6],1)
                y2 = Converter.bitstring_to_bytes(bytedate_modifier[0:7],1)[0]
                m2= Converter.bitstring_to_bytes(bytedate_modifier[7:11],1)[0]
                d2 = Converter.bitstring_to_bytes(bytedate_modifier[11:16],1)[0]
                bytetime_modifier = Converter.decimalToBit(entry[7],1)+Converter.decimalToBit(entry[8],1)
                h2 = Converter.bitstring_to_bytes(bytetime_modifier[0:5],1)[0]
                mi2= Converter.bitstring_to_bytes(bytetime_modifier[5:11],1)[0]
                s2 = Converter.bitstring_to_bytes(bytetime_modifier[11:16],1)[0]

                isencrypt = 'yes' if entry[13] == 1 else 'no'
                filename = entry[89:89+filenamelen].decode()
                path=entry[89+filenamelen:89+filenamelen+pathlen].decode()
                list.append({'filename':filename,
                             'path':path,
                             'password': isencrypt,
                             'date create':str(d1)+'/'+str(m1)+'/'+str(y1)+' '+str(h1)+':'+str(mi1)+':'+str(s1),
                             'date modifier':str(d2)+'/'+str(m2)+'/'+str(y2)+' '+str(h2)+':'+str(mi2)+':'+str(s2),
                             'size':filesize
                               })
            pos+=self.entry_size
            self.myfsFile.seek(pos)
            entry=self.myfsFile.read(self.entry_size)
        return list

    def findAvailableEntry(self):
        self.myfsFile.seek(self.backup_index-self.entry_size)
        if self.myfsFile.read(1) != b'\x00':
            #find entry deleted with max size
            maxsize,index,pos = 0,self.sdet_index,-1
            self.myfsFile.seek(index)
            while index<self.backup_index:
                if self.myfsFile.read(1) ==b'\x0E':
                    self.myfsFile.seek(index+9)
                    l = int.from_bytes(self.myfsFile.read(4),"big")
                    if l >max:
                        maxsize,pos = l,index
                index+=self.entry_size
                self.myfsFile.seek(index)
            #turn off bitmap
            posdelete =[pos]
            self.myfsFile.seek(pos)
            entrydelete,index = self.myfsFile.read(self.entry_size),pos+self.entry_size
            fn = entrydelete[89:89+entrydelete[87]]
            #find the backup of this file if exist
            self.myfsFile.seek(index)
            while index<self.backup_index:
                if self.myfsFile.read(1) ==b'\x0E':
                    en = self.myfsFile.read(self.entry_size)
                    if en[89:89:en[87]] == fn:
                        posdelete.append(index)
                        break
                index+=self.entry_size
                self.myfsFile.seek(index)
            self.myfsFile.seek(self.bitmap_index)
            bitstring = ''.join(format(byte, '08b') for byte in self.myfsFile.read(self.bitmap_size))
            for p in posdelete:
                self.myfsFile.seek(p)
                en = self.myfsFile.read(self.entry_size)
                datarun = [89+en[87]+en[88]]
                datarun = datarun[:datarun.index(b'\x00')]
                arr = Converter.getDatarun(datarun)
                for ite in arr:
                    bitstring=bitstring[0:index[0]-1]+'0'*index[1]+bitstring[index[0]-1+index[1]:]
            return pos

        index = self.sdet_index
        self.myfsFile.seek(index)
        while index<self.backup_index:
            if self.myfsFile.read(1) ==b'\x00':
                return index
            index+=self.entry_size
            self.myfsFile.seek(index)
        return -1

    def getOffset(self,cluster):
        return self.cluster_start+(cluster-1)*self.cluster_size

    def ExportFile(self,filename):
        exportfile =filename.encode()
        pos,entry,filenamelen = -1,None,0
        index = self.sdet_index
        self.myfsFile.seek(index)
        while index<self.backup_index:
            entry=self.myfsFile.read(self.entry_size)
            filenamelen = entry[87]
            if entry[0] == 1 and exportfile == entry[89:89+filenamelen] and entry[86] == 0:
                pos = index
                break
            index+=self.entry_size
            self.myfsFile.seek(index)
        if pos <0:
            raise ValueError('Filename is not existed! Please check and try again!')
        path = entry[89+filenamelen:89+filenamelen+entry[88]].decode()
        filedes = None
        try:
            filedes = open(path,'w+b')
        except:
            newpath = 'C:/Users/'+path.split('/')[len(path.split('/'))-1]
            print(path+' Can not find! The new path file is '+newpath)
            filedes = open(newpath,'w+b')
        datarun = entry[89+filenamelen+entry[88]:]
        datarun=datarun[:datarun.index(b'\x00')]
        arr = Converter.getDatarun(datarun)
        size = int.from_bytes(entry[9:13])
        aes = None
        if entry[13] ==1:
            pw = input("Enter the password: ")
            count = 0
            key = hashlib.md5(pw.encode()).digest()
            hashpw = sha256(key)
            while  hashpw != entry[22:54]:
                count+=1
                if count ==3: 
                    print("Wrong more than 3 times!")
                    return
                pw = input("Wrong password! Try again(c to exit): ")
                if pw.lower == 'c': return
                key = hashlib.md5(pw.encode()).digest()
                hashpw = sha256(key)
            aes = AES.new(key,mode=AES.MODE_CTR,nonce=entry[14:22])
        for item in arr:
            self.myfsFile.seek(self.getOffset(item[0]))
            for i in range(item[1]):
                datawrite = self.myfsFile.read(self.cluster_size)
                if aes !=None:
                    datawrite = aes.decrypt(datawrite)
                if i ==item[1] - 1 and arr.index(item) == len(arr) -1:
                     datawrite = datawrite[:size%self.cluster_size]
                filedes.write(datawrite)
                #print(datawrite)
        filedes.close()
        print('File is exported at ',path)
        #idFile,index = pos//128,pos%128
    
    def setFilePassword(self,filename):
        filen =filename.encode()
        pos,entry= [],None
        index = self.sdet_index
        self.myfsFile.seek(index)
        while index<self.backup_index:
            entry=self.myfsFile.read(self.entry_size)
            filenamelen = entry[87]
            if entry[0] == 1 and filen == entry[89:89+filenamelen]:
                pos.append(index)
            index+=self.entry_size
            self.myfsFile.seek(index)
        if len(pos) == 0:
            raise ValueError('File is not existed in MYFS! Please check and try again!')
        oldkey, newkey =b'',b''
        self.myfsFile.seek(pos[0])
        entry = self.myfsFile.read(self.entry_size)
        if entry[13] == 1: 
            count = 0
            pw = input('Please enter the old password: ')
            oldkey = hashlib.md5(pw.encode()).digest()
            hashpw = sha256(oldkey)
            while hashpw != entry[22:54]:
                pw = input("Invalid password! Try again: ")
                oldkey = hashlib.md5(pw.encode()).digest()
                hashpw = sha256(oldkey)
                count+=1
                if count == 3:
                    print("Wrong more than 3 times! ")
                    return
        newpw = input("Enter the new password (must be >= 8 characters): ")
        while len(newpw) < 8:
            newpw = input("Password must be >= 8 characters! Try again (c to exit): ")
            if newpw.lower() == 'c': return
        renewpw = input("Password again (must be the same): ")
        while renewpw != newpw:
            renewpw = input("Try again(c to exit): ")
            if renewpw.lower() == 'c': return
        newkey = hashlib.md5(newpw.encode()).digest()
        n_aes = AES.new(newkey,mode=AES.MODE_CTR)
        aes2 = None
        if oldkey!=b'':
            aes2 = AES.new(oldkey,mode=AES.MODE_CTR,nonce=entry[14:22])
        size = int.from_bytes(entry[9:13])
        #hashcontent =
        for p in pos:
            self.myfsFile.seek(p)
            entry = self.myfsFile.read(self.entry_size)
            filenamelen = entry[87]
            datarun = entry[89+filenamelen+entry[88]:]
            datarun=datarun[:datarun.index(b'\x00')]
            arr = Converter.getDatarun(datarun)
            for item in arr:
                self.myfsFile.seek(self.getOffset(item[0]))
                for i in range(item[1]):
                    dataread = self.myfsFile.read(self.cluster_size)
                    #print(self.getOffset(item[0]),'\n',dataread)
                    if oldkey !=b'':
                        dataread=aes2.decrypt(dataread)
                    dataread = n_aes.encrypt(dataread)
                    self.myfsFile.seek(self.getOffset(item[0]+i))
                    self.myfsFile.write(dataread)
            entry = entry[:13]+b'\x01'+n_aes.nonce+sha256(newkey)+entry[54:]
            self.myfsFile.seek(p)
            self.myfsFile.write(entry)
                           
    def deleteFile(self,filename):
        deleteFile =filename.encode()
        pos,entry= [],None
        index = self.sdet_index
        self.myfsFile.seek(index)
        while index<self.backup_index:
            entry=self.myfsFile.read(self.entry_size)
            filenamelen = entry[87]
            if entry[0] == 1 and deleteFile == entry[89:89+filenamelen]:
                pos.append(index)
            index+=self.entry_size
            self.myfsFile.seek(index)
        if len(pos) == 0:
            raise ValueError('File is not existed in MYFS! Please check and try again!')
        #print(pos)
        for p in pos:
            self.myfsFile.seek(p)
            self.myfsFile.write(b'\x0E')
        self.allFiles = self.List()
    
    def RecoveryMode(self):
        pos,entry,count= [],None,0
        index = self.sdet_index
        self.myfsFile.seek(index)
        while index<self.backup_index:
            entry=self.myfsFile.read(self.entry_size)
            if entry[0] == 14:
                if entry[86] ==0:
                    count+=1
                pos.append(index)
            index+=self.entry_size
            self.myfsFile.seek(index)
        #print(pos)
        for p in pos:
            self.myfsFile.seek(p)
            self.myfsFile.write(b'\x01')
        self.allFiles = self.List()
        print('Find and recover ',count,' files')
    