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
def caclNum(x,i=0):
    if x == 0: return i
    return caclNum(x//256,i+1)
def createDatarun(bit_string,l):
    index = 0
    n = len(bit_string)
    ar,total = [],0
    while index< n :
        if bit_string[index] == '0':
            start = index
            length = 0
            while index<n and bit_string[index] == '0' and total != l:
                length += 1
                index+= 1
                total += 1
            ar.append([start+1,length])
            bit_string= bit_string[0:start]+'1'*length+bit_string[start+length:]
            if total == l:
                d = b''
                for item in ar:
                    a = caclNum(item[0])
                    b = caclNum(item[1])
                    d+= (a*16+b).to_bytes(1,'big')
                    d+= item[0].to_bytes(a,'big')
                    d+=item[1].to_bytes(b,'big')
                    #print(d)
                return d,bit_string,ar
        index+=1

def getDatarun(b_dr):
    arr=[]
    i=0
    while i!= len(b_dr):
        a,b = b_dr[i]//16,b_dr[i]%16
        arr.append([int.from_bytes(b_dr[i+1:i+a+1],'big'),int.from_bytes(b_dr[i+a+1:i+a+b+1],'big')])
        i = i+a+b+1
    return arr
