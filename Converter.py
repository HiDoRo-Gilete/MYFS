def xorMes(mes,xorValue):
    n = len(xorValue)
    result = b''
    for i in range(len(mes)):
        result+= (mes[i]^(xorValue[i%8])).to_bytes(1)
    return result

def decimalToBit(decimal,numbyte):
    numbit = numbyte*8
    
    return ('{0:0'+str(numbit)+'b}').format(decimal)

def bitstring_to_bytes(s,numbyte):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    result= bytes(b[::-1])
    if len(result) != numbyte:
        result = b'\x00' *(numbyte - len(result))+result
    return result

def intToByte(num,numbyte):
    return num.to_bytes(numbyte, byteorder ='big')
def createDatarun(arr):
    d = b''
    for item in arr:
        a = item[0]//256 +1
        b = item[1]//256 +1
        d+= (a*16+b).to_bytes(1,'big')
        d+= item[0].to_bytes(a,'big')
        d+=item[1].to_bytes(b,'big')
    return d
def getDatarun(b_dr):
    arr=[]
    i=0
    while i!= len(b_dr):
        a,b = b_dr[i]//16,b_dr[i]%16
        arr.append([int.from_bytes(b_dr[i+1:i+a+1]),int.from_bytes(b_dr[i+a+1:i+a+b+1])])
        i = i+a+b+1
    return arr
