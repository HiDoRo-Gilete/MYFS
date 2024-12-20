OTP_ACTIVE = False # True 

MAX_FILE_SIZE = int(4*1024*1024*1024) #4gb
MAX_FILE = 99  

SYS_SIZE = 1024 # 1kb
SYS_INDEX = 0
CLUSTER_SIZE = 1024*32 #32kb
ENTRY_SIZE = 2048 #2kb

BITMAP_SIZE = int(MAX_FILE_SIZE *MAX_FILE/CLUSTER_SIZE/8) 
BITMAP_INDEX = SYS_INDEX + SYS_SIZE 

SDET_SIZE = MAX_FILE*ENTRY_SIZE*2  
SDET_INDEX =  BITMAP_INDEX+BITMAP_SIZE

BACKUP_SIZE = BITMAP_SIZE + SDET_SIZE 
BACKUP_INDEX = SDET_INDEX+SDET_SIZE

CLUSTER_START = BACKUP_INDEX+BACKUP_SIZE
