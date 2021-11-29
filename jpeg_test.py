'''
https://yasoob.me/posts/understanding-and-writing-jpeg-decoder-in-python/
20.11.2021 - 8:44pm readin.
JPEG is an algorithm

unpack('>H', ...) : "Big-Endian" & "Unsigned Short"
https://www.techtarget.com/searchnetworking/definition/big-endian-and-little-endian
Big Endian : 'Big End' is stored first. (MSB first in memory!)
ex. FF D8 => "0xFFD8"

DCT : https://www.youtube.com/watch?v=Q2aEzeMDHMA
*64 Cosine functions that can combine and make ANY 8x8 image.
1. Shifted Block (to Center around 0, since Cosines always sum up to 0)
2. Calculate coefficients (8x8, float)
3. Low Frequency Coefficients are generally big.
4. *QUantization Table. It will be the 'dividor' for the coeffs.
*Ohhh that's why it's not EXACLY the same image! Sometimes JPGs are block-y
5. EVERY 8x8 block will be quantized into this, and serial-ized. Then Huffman!
*Sooo it's a TERRIBLE Way to send the EXACT Data I guess. Only for humans!
*Butt QUantization Tables can greatly improve the quality!!!

Delta Encoding for 'DC' values for each block
*Wow you can screw up the whole image by just altering this first block's absolute value!

Run length encoding (<Number> <How many times?>)

Huffman encoding
-Binary Tree
-Custom mapping.
With the Delta Encoding for ex. The 'Variety' of the data decreases, better for Huffman Encoding!
https://www.youtube.com/watch?v=JsTptu56GM8
*Text can't be LOSS-ed! So HE is important.
Ohhhh so until you reach the *end of the Binary tree, you keep going down
Hence, no risk of mis-thinking that certain data (ex. a) is another (ex. b)

DC and AC on differetn Huffman Table.
Luminance and Chrominance each having DC / AC values.
Total of 4 HT.

YUV
Y : Luminance (Brightness)
U : Amount of Blue Color
V : Amount of Red Color.

*Oh soo Chrominance of Blue / Red are stored together! (No separation)

Wow Python's "__sizeof__" function. Showing real size of object.
Oh, 'tuples' are un-mutable. So they are good for key values in dictionary.
*Oh only 'certain' types are allowed as keys I guess?


<Q>
1. Can JPEG be LOSS-LESS? (EXact same image)
2. HE for non-ASCII? (ex. Ganji)
3. Are HE good for encoding bunch of 0s? Or just Run Length Encoding is?
4. How does python get the type of the object?
5. How does dir() function fo robjects work? (Getting all fnctions)
6. How can Tuple store integers bigger than 4 bytes into just 4 extra bytes?

>>> (1,2,3).__sizeof__()
24
>>> (1,2).__sizeof__()   
20
>>> (1,2,0xfffffffff).__sizeof__() 
24
>>> (1,2,0xffffffffffffffffffffffff).__sizeof__() 
24

7. In which cases do HE trees have the BOTH left & right children at the root?
8. Exact difference between 'bytes' and 'list' with bytes in it?
9. Can there be a more efficient way of defining "RemoveFF00" function?
*like not getting the 2 values at a time? Since it's wasting read exec time?
10. De-DCT'ed values are what the JPEG encoder 'encodes'?
*Does it make sense for em to get L, Cr, Cb from NEGATIVE R, G or B values?

<IDEA>
1. Show diff Quantization Table examples (show how you can wrong-ly decode the image.)
2. Do the Huffman Coding example coding.
3. 

'''
from struct import unpack

marker_mapping = {
    0xffd8: "Start of Image",
    0xffe0: "Application Default Header",
    0xffdb: "Quantization Table",
    0xffc0: "Start of Frame",
    0xffc4: "Define Huffman Table",
    0xffda: "Start of Scan",
    0xffd9: "End of Image"
}

# Converting string into bits
class Stream:
    def __init__(self, data):
        self.data= data
        self.pos = 0

    def GetBit(self):
        b = self.data[self.pos >> 3] # Byte data.
        s = 7-(self.pos & 0x7) # as pos increases, we scan from MSb to LSb.
        self.pos += 1
        return (b >> s) & 1

    def GetBitN(self, l): # Get the N bits of the data in the stream.
        val = 0
        for i in range(l):
            val = val<<1 + self.GetBit()
        return val

class HuffmanTable:
    def __init__(self):
        self.root=[]
        self.elements = [] # List of all the elements (data)
    
    # element : element we are going to insert into the Huffman Tree
    # pos : Length - 1 of the Huffman Code. (i.e. Depth in the Tree.)
    def BitsFromLengths(self, root, element, pos):
        if isinstance(root,list):
            if pos==0: # Element with HE code's bit count of 1 (ex. 0)
                if len(root)<2:
                    root.append(element)
                    return True                
                return False
            for i in [0,1]:
                if len(root) == i:
                    root.append([])
                if self.BitsFromLengths(root[i], element, pos-1) == True:
                    return True
        return False
    
    # Builds root, a Binary Tree, from 'lengths' and 'elements' data.
    def GetHuffmanBits(self, lengths, elements):
        self.elements = elements
        ii = 0
        for i in range(len(lengths)):
            for _ in range(lengths[i]): # elements with (i+1) number of bits as HE code.
                self.BitsFromLengths(self.root, elements[ii], i)
                ii+=1

    # Input : Stream of a Huffman Code
    # Returns : Decoded Data instance (ex. The Character)
    # IF no feasible data is found, could return invalid value. (Error)
    def Find(self,st):
        r = self.root
        while isinstance(r, list):
            r=r[st.GetBit()]
        return  r 

    def GetCode(self, st):
        while(True):
            res = self.Find(st)
            if res == 0:
                return 0
            elif ( res != -1):
                return res

import math

class IDCT:
    """
    An inverse Discrete Cosine Transformation Class
    """

    def __init__(self):
        self.base = [0] * 64
        self.zigzag = [
            [0, 1, 5, 6, 14, 15, 27, 28],
            [2, 4, 7, 13, 16, 26, 29, 42],
            [3, 8, 12, 17, 25, 30, 41, 43],
            [9, 11, 18, 24, 31, 40, 44, 53],
            [10, 19, 23, 32, 39, 45, 52, 54],
            [20, 22, 33, 38, 46, 51, 55, 60],
            [21, 34, 37, 47, 50, 56, 59, 61],
            [35, 36, 48, 49, 57, 58, 62, 63],
        ]
        self.idct_precision = 8
        self.idct_table = [
            [
                (self.NormCoeff(u) * math.cos(((2.0 * x + 1.0) * u * math.pi) / 16.0))
                for x in range(self.idct_precision)
            ]
            for u in range(self.idct_precision)
        ]

    def NormCoeff(self, n):
        if n == 0:
            return 1.0 / math.sqrt(2.0)
        else:
            return 1.0

    def rearrange_using_zigzag(self):
        for x in range(8):
            for y in range(8):
                self.zigzag[x][y] = self.base[self.zigzag[x][y]]
        return self.zigzag

    def perform_IDCT(self):
        out = [list(range(8)) for i in range(8)]

        for x in range(8):
            for y in range(8):
                local_sum = 0
                for u in range(self.idct_precision):
                    for v in range(self.idct_precision):
                        local_sum += (
                            self.zigzag[v][u]
                            * self.idct_table[u][x]
                            * self.idct_table[v][y]
                        )
                out[y][x] = local_sum // 4
        self.base = out

# Get the list of data out of a 'byte array'
# handy method for decoding a variable number of bytes from binary data
def GetArray(type, l, length):
    s = type * length # Ex. "B"*16
    return list(unpack(s,l[:length]))

# Since image data can contain 0xff as data, it appends 0x00 after that,
# to avoid confusion of it being recognized as one of JPEG 'headers'.
# Espeically since the Image Data's length is not specified!
def RemoveFF00(data):
    datapro = []
    i = 0
    while(True):
        b,bnext = unpack("BB",data[i:i+2])        
        if (b == 0xff):
            if (bnext != 0):
                break # Probably a 'End of Image' flag, 0xffd9
            datapro.append(data[i])
            i+=2
        else:
            datapro.append(data[i])
            i+=1
    return datapro,i # return the length of the 

# Decode 'code' length number of bits as a 'signed' number.
def DecodeNumber(code, bits):
    l = 2**(code-1) # code is the 'length' of the bits data.
    if bits>=l:
        return bits
    else:
        return bits-(2*l-1) # The Negative number case.

# Clamp to 0 ~ 255 range.
def Clamp(col):
    col = 255 if col>255 else col
    col = 0 if col<0 else col
    return  int(col)

def ColorConversion(Y, Cr, Cb):
    R = Cr*(2-2*.299) + Y
    B = Cb*(2-2*.114) + Y
    G = (Y - .114*B - .299*R)/.587
    # Restore the original RGB by adding 128 offset to the de-DCT'ed values
    return (Clamp(R+128),Clamp(G+128),Clamp(B+128) )
  
  # Draw the matrix on the Tkinter canvas.
def DrawMatrix(x, y, matL, matCb, matCr):
    for yy in range(8):
        for xx in range(8):
            c = "#%02x%02x%02x" % ColorConversion(
                matL[yy][xx], matCb[yy][xx], matCr[yy][xx]
            )
            x1, y1 = (x * 8 + xx) * 2, (y * 8 + yy) * 2
            x2, y2 = (x * 8 + (xx + 1)) * 2, (y * 8 + (yy + 1)) * 2
            w.create_rectangle(x1, y1, x2, y2, fill=c, outline=c)
            #print(x1,y1,x2,y2,': Color of :', c)

#'''
class JPEG:
    def __init__(self, image_file):
        self.huffman_tables = {}
        self.quant = {}
        self.quantMapping = []
        with open(image_file, 'rb') as f:
            self.img_data = f.read()

    # Builds the Matrix using IDCT.
    '''
    The BuildMatrix method will return the inverse DCT matrix and the value of the DC coefficient.
    Remember, this inverse DCT matrix is only for one tiny 8x8 MCU (Minimum Coded Unit) matrix.
    We will be doing this for all the individual MCUs in the whole image file.
    '''
    def BuildMatrix(self, st, idx, quant, olddccoeff):
        i = IDCT()

        code = self.huffman_tables[0 + idx].GetCode(st) # DC huffman table.
        bits = st.GetBitN(code)
        
        # Delta encoded, so add the old dc coeff to get NEW dc coeff.
        dccoeff = DecodeNumber(code, bits) + olddccoeff

        i.base[0] = (dccoeff) * quant[0]
        l = 1
        while l < 64:
            code = self.huffman_tables[16 + idx].GetCode(st) # AC tables w/ header (index) of "0x1?"
            if code == 0: # End of Block.
                break

            # The first part of the AC quantization table
            # is the number of leading zeros
            if code > 15:
                l += code >> 4
                code = code & 0x0F

            bits = st.GetBitN(code)

            if l < 64:
                coeff = DecodeNumber(code, bits)
                i.base[l] = coeff * quant[l]
                l += 1

        i.rearrange_using_zigzag()
        i.perform_IDCT()

        return i, dccoeff
    
    def decodeHuffman(self, data):
        offset = 0
        header, = unpack("B",data[offset:offset+1]) # Huffman Header, indicating AC/DC + Destination.
        offset += 1

        # Extract the 16 bytes containing length data as a 'tuple'
        lengths = unpack("BBBBBBBBBBBBBBBB", data[offset:offset+16]) 
        offset += 16
        '''
        >>> a = unpack("BBBB",bytearray([0,5,2,3])) 
        >>> a
        (0, 5, 2, 3)
        >>> type(a)
        <class 'tuple'>
        '''

        # Extract the elements after the initial 16 bytes
        elements = []
        for i in lengths:
            elements += GetArray("B", data[offset:offset+i], i)
            # You can ADD tuple to the list object.
            # Each 'element' is assumed to be a Byte
            offset += i 
        # Adding 'tuples' https://www.programiz.com/python-programming/list-vs-tuples
        
        print("Header: ",header)
        print("lengths: ", lengths)
        print("Elements: ", len(elements))

        print(elements)

        hf = HuffmanTable()
        hf.GetHuffmanBits(lengths, elements)

        self.huffman_tables[header] = hf # Add to the HT dictionary!
        data = data[offset:] # Why?
    
    def DefineQuantizationTables(self, data):
        hdr, = unpack("B",data[0:1])
        self.quant[hdr] =  GetArray("B", data[1:1+64],64)
        print('QT with idx :', hdr, self.quant[hdr])
        #data = data[65:]

    def BaselineDCT(self, data):
        hdr, self.height, self.width, components = unpack(">BHHB",data[0:6])
        # header contains the 'precision' info.
        # B for unsigned char, H for unsigned short.
        # https://docs.python.org/3/library/struct.html
        print("size %ix%i" % (self.width,  self.height))
        for i in range(components):
            id, samp, QtbId = unpack("BBB",data[6+i*3:9+i*3])
            # ID, Factor, Table ID
            self.quantMapping.append(QtbId)
        # quantization table numbers of each component in the quantMapping list
        print('Quant Mapping :', self.quantMapping)

    def StartOfScan(self, data, hdrlen):
        for ht in self.huffman_tables.values():
            print(ht.root) 
        print(self.quant)
        print(self.quantMapping)
        data,lenchunk = RemoveFF00(data[hdrlen:]) # Only get the Image Data.
        # Image data as a list of bytes, length of the image data is returned!
        st = Stream(data)
        oldlumdccoeff, oldCbdccoeff, oldCrdccoeff = 0, 0, 0
        print('Height :', self.height, ', Width :', self.width)
        for y in range(self.height//8):
            for x in range(self.width//8):
                #print('Processing image height idx', y, ', width idx', x)
                matL, oldlumdccoeff = self.BuildMatrix(st,0, self.quant[self.quantMapping[0]], oldlumdccoeff)
                matCr, oldCrdccoeff = self.BuildMatrix(st,1, self.quant[self.quantMapping[1]], oldCrdccoeff)
                matCb, oldCbdccoeff = self.BuildMatrix(st,1, self.quant[self.quantMapping[2]], oldCbdccoeff)
                DrawMatrix(x, y, matL.base, matCb.base, matCr.base) # Conversion to RGB
        return lenchunk+hdrlen

    def decode(self):
        data = self.img_data # 'bytes' data type.
        while(True):
            marker, = unpack(">H", data[0:2]) # HEX, Big Endian. MSB first.
            print(marker_mapping.get(marker))
            if marker == 0xffd8: # Start of Image
                data = data[2:]
            elif marker == 0xffd9: # End of Image
                print(data)
                return
            else:
                lenchunk, = unpack(">H", data[2:4]) # Assume we just 'read' the marker.
                lenchunk += 2 # Includer the header. Total chunk size.
                print('lenchunk :', lenchunk)
                chunk = data[4:lenchunk] # Data chunk excluding length data & header.
                if marker == 0xffdb: # Quantization Table
                    print('QT Sneek :', chunk)
                    # Length and Destination info is taking 3 bytes (Hence length of 67 bytes.)
                    self.DefineQuantizationTables(chunk)
                elif marker == 0xffc0: # START of FRAME
                    self.BaselineDCT(chunk)
                elif marker == 0xffc4: # Huffman Table
                    self.decodeHuffman(chunk)
                    #print('HT Sneek :', data[4:2+lenchunk]) # From 'Class' to End.
                    # Class (0: DC, 1: AC) / Destination (Number of HT : 0 ~ 3) -> ex. Luminance and Chrominance would be 0 and 1.
                    # 16 Bytes of 'total number of symbol / data with H-code length of x' (x = 1 ~ 16)
                    # Table of Symbols. From short to Increasing code length.
                elif marker == 0xffda: # Start of Scan
                    lenchunk = self.StartOfScan(data, lenchunk)
                data = data[lenchunk:] # Skip to the next data.
            if len(data)==0: # Exhausted all the data in our buffer.
                break        

if __name__ == "__main__":
    from tkinter import *
    master = Tk()
    w = Canvas(master, width = 1600, height = 600)
    w.pack()
    img = JPEG('yasoob_example.jpg')
    img.decode()
    mainloop() # For TK-inter.
# '''

'''
for ht in self.huffman_tables.values():
            print(ht.root) 
print(self.quant)
print(self.quantMapping)
[[5, 6], [[3, 4], [[2, 7], [8, [1, [0, [9]]]]]]]
[[1, 2], [[3, [0, 4]], [[17, [5, 33]], [[[6, 18], [49, 65]], [[[7, 19], [34, 81]], [[97, [20, 113]], [[[8, 50], [129, 145]], [[[21, 35], [66, 161]], [[[82, 177], [193, [51, 98]]], [[[209, 225], [[9, 22], [23, 36]]], [[[114, 146], [240, 241]], [[[37, 52], [67, 130]], [[178, [24, 39]], [[68, 83], [162, [115]]]]]]]]]]]]]]]]
[[1, 2], [[0, 3], [4, [5, [6, [7]]]]]]
[[0, 1], [[2, 17], [[3, 33], [[18, 49], [[4, 65], [[81, [19, 34]], [[97, [5, 50]], [[113, [145, [20, 35]]], [[[66, 129], [161, 177]], [[209, [6, 21]], [[193, 240], [[36, 241], [[51, 82], [162]]]]]]]]]]]]]]
{0: [3, 2, 2, 3, 2, 2, 3, 3, 3, 3, 4, 3, 3, 4, 5, 8, 5, 5, 4, 4, 5, 10, 7, 7, 6, 8, 12, 10, 12, 12, 11, 10, 11, 11, 13, 14, 18, 16, 13, 14, 17, 14, 11, 11, 16, 22, 16, 17, 19, 20, 21, 21, 21, 12, 15, 23, 24, 22, 20, 24, 18, 20, 21, 20], 1: [3, 4, 4, 5, 4, 5, 9, 5, 5, 9, 20, 13, 11, 13, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]}
[0, 1, 1]
Height : 400 , Width : 400
'''

'''
class JPEG:
    def __init__(self, image_file):
        with open(image_file, 'rb') as f:
            self.img_data = f.read()
    
    def decode(self):
        data = self.img_data
        while(True):
            marker, = unpack(">H", data[0:2])
            print(marker_mapping.get(marker))
            if marker == 0xffd8: # Start of Image
                data = data[2:]
            elif marker == 0xffd9: # End of Image
                print(data)
                return
            elif marker == 0xffda: # Start of SCAN!
                data = data[-2:] # Skip to the end marker.
            else:
                lenchunk, = unpack(">H", data[2:4]) # Assume we just 'read' the marker.
                if marker == 0xffdb: # Quantization Table
                    print('QT Sneek :', data[4:4+65]) # Include 'destination and table'
                elif marker == 0xffc4: # Huffman Table
                    print('HT Sneek :', data[4:2+lenchunk]) # From 'Class' to End.
                    # Class (0: DC, 1: AC) / Destination (0 / 1), each 4 bits.
                data = data[2+lenchunk:] # Length doesn't include marker!
                print('lenchunk :', lenchunk)        
            if len(data)==0:
                break        

if __name__ == "__main__":
    img = JPEG('yasoob_example.jpg')
    img.decode()

Output

Start of Image
Application Default Header
lenchunk : 16
Quantization Table
QT Sneek : b'\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14'
lenchunk : 67
Quantization Table
QT Sneek : b'\x01\x03\x04\x04\x05\x04\x05\t\x05\x05\t\x14\r\x0b\r\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
lenchunk : 67
Start of Frame
lenchunk : 17
Define Huffman Table
HT Sneek : b'\x00\x00\x02\x02\x03\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x06\x03\x04\x02\x07\x08\x01\x00\t'
lenchunk : 29
Define Huffman Table
HT Sneek : b'\x10\x00\x02\x01\x03\x02\x04\x05\x02\x04\x04\x03\x04\x08\x05\x05\x01\x01\x02\x03\x00\x04\x11\x05!\x06\x121A\x07\x13"Qa\x14q\x082\x81\x91\x15#B\xa1R\xb1\xc13b\xd1\xe1\t\x16\x17$r\x92\xf0\xf1%4C\x82\xb2\x18\'DS\xa2s'
lenchunk : 72
Define Huffman Table
HT Sneek : b'\x01\x00\x02\x03\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x03\x04\x05\x06\x07'
lenchunk : 27
Define Huffman Table
HT Sneek : b'\x11\x00\x02\x02\x02\x02\x02\x01\x03\x03\x01\x07\x04\x02\x03\x00\x00\x00\x01\x02\x11\x03!\x121\x04AQ\x13"a\x052q\x91\x14#B\x81\xa1\xb1\xd1\x06\x15\xc1\xf0$\xf13R\xa2'
lenchunk : 53
Start of Scan
End of Image
b'\xff\xd9'
'''


'''
Output

Start of Image
Application Default Header
lenchunk : 16
Quantization Table
lenchunk : 67
Quantization Table
lenchunk : 67
Start of Frame
lenchunk : 17
Define Huffman Table
lenchunk : 29
Define Huffman Table
lenchunk : 72
Define Huffman Table
lenchunk : 27
Define Huffman Table
lenchunk : 53
Start of Scan
End of Image
b'\xff\xd9'
'''

'''
Height : 400 , Width : 400
0 2 2 2 : Color of : #2a4407
2 4 4 2 : Color of : #344b0f
4 6 6 2 : Color of : #3e531a
6 8 8 2 : Color of : #455920
8 10 10 2 : Color of : #4a5d27
10 12 12 2 : Color of : #4f622e
12 14 14 2 : Color of : #526634
14 16 16 2 : Color of : #536735
0 2 2 4 : Color of : #304a0d
2 4 4 4 : Color of : #384f13
4 6 6 4 : Color of : #3f541b
6 8 8 4 : Color of : #455920
8 10 10 4 : Color of : #495c26
10 12 12 4 : Color of : #4e612d
12 14 14 4 : Color of : #506432
14 16 16 4 : Color of : #506432
0 2 2 6 : Color of : #385215
2 4 4 6 : Color of : #3d5418
4 6 6 6 : Color of : #42571e
6 8 8 6 : Color of : #465a21
8 10 10 6 : Color of : #495c26
10 12 12 6 : Color of : #4d602c
12 14 14 6 : Color of : #4d612f
14 16 16 6 : Color of : #4d612f
0 2 2 8 : Color of : #3e581b
2 4 4 8 : Color of : #41581c
4 6 6 8 : Color of : #43581f
6 8 8 8 : Color of : #465a21
8 10 10 8 : Color of : #495c26
10 12 12 8 : Color of : #4c5f2b
12 14 14 8 : Color of : #4c602e
14 16 16 8 : Color of : #4c602e
0 2 2 10 : Color of : #405a1d
2 4 4 10 : Color of : #42591d
4 6 6 10 : Color of : #43581f
6 8 8 10 : Color of : #475b22
8 10 10 10 : Color of : #4a5d27
10 12 12 10 : Color of : #4c5f2b
12 14 14 10 : Color of : #4d612f
14 16 16 10 : Color of : #4e6230
0 2 2 12 : Color of : #3e581b
2 4 4 12 : Color of : #40571b
4 6 6 12 : Color of : #43581f
6 8 8 12 : Color of : #475b22
8 10 10 12 : Color of : #4b5e28
10 12 12 12 : Color of : #4d602c
12 14 14 12 : Color of : #506432
14 16 16 12 : Color of : #536735
0 2 2 14 : Color of : #3b5518
2 4 4 14 : Color of : #3e5519
4 6 6 14 : Color of : #42571e
6 8 8 14 : Color of : #485c23
8 10 10 14 : Color of : #4b5e28
10 12 12 14 : Color of : #4e612d
12 14 14 14 : Color of : #526634
14 16 16 14 : Color of : #576b39
0 2 2 16 : Color of : #395316
2 4 4 16 : Color of : #3c5317
4 6 6 16 : Color of : #42571e
6 8 8 16 : Color of : #485c23
8 10 10 16 : Color of : #4b5e28
10 12 12 16 : Color of : #4e612d
12 14 14 16 : Color of : #536735
14 16 16 16 : Color of : #5a6e3c
16 18 18 2 : Color of : #001c00
18 20 20 2 : Color of : #052400
20 22 22 2 : Color of : #122f00
22 24 24 2 : Color of : #203900
24 26 26 2 : Color of : #2b4301
26 28 28 2 : Color of : #334b0d
28 30 30 2 : Color of : #344e11
30 32 32 2 : Color of : #344e13
16 18 18 4 : Color of : #052400
18 20 20 4 : Color of : #0d2c00
20 22 22 4 : Color of : #1a3700
22 24 24 4 : Color of : #274000
24 26 26 4 : Color of : #314909
26 28 28 4 : Color of : #395113
28 30 30 4 : Color of : #3a5417
30 32 32 4 : Color of : #395316
16 18 18 6 : Color of : #102f00
18 20 20 6 : Color of : #173500
20 22 22 6 : Color of : #233f00
22 24 24 6 : Color of : #304806
24 26 26 6 : Color of : #395111
26 28 28 6 : Color of : #3f5719
28 30 30 6 : Color of : #41581c
30 32 32 6 : Color of : #3f591c
16 18 18 8 : Color of : #183600
18 20 20 8 : Color of : #1f3b00
20 22 22 8 : Color of : #2b4400
22 24 24 8 : Color of : #354d0b
24 26 26 8 : Color of : #3e5417
26 28 28 8 : Color of : #42591d
28 30 30 8 : Color of : #445b1f
30 32 32 8 : Color of : #425c1f
16 18 18 10 : Color of : #1b3900
18 20 20 10 : Color of : #213d00
20 22 22 10 : Color of : #2d4600
22 24 24 10 : Color of : #384f0d
24 26 26 10 : Color of : #405619
26 28 28 10 : Color of : #43591d
28 30 30 10 : Color of : #445b1f
30 32 32 10 : Color of : #445b1f
16 18 18 12 : Color of : #1b3800
18 20 20 12 : Color of : #203d00
20 22 22 12 : Color of : #2b4500
22 24 24 12 : Color of : #364d0b
24 26 26 12 : Color of : #3e5415
26 28 28 12 : Color of : #41571a
28 30 30 12 : Color of : #42591d
30 32 32 12 : Color of : #435a1e
16 18 18 14 : Color of : #173500
18 20 20 14 : Color of : #1b3800
20 22 22 14 : Color of : #264000
22 24 24 14 : Color of : #324905
24 26 26 14 : Color of : #3a5011
26 28 28 14 : Color of : #3d5316
28 30 30 14 : Color of : #3f5519
30 32 32 14 : Color of : #40571b
16 18 18 16 : Color of : #123000
18 20 20 16 : Color of : #183300
20 22 22 16 : Color of : #213b00
22 24 24 16 : Color of : #2e4500
24 26 26 16 : Color of : #364d0b
26 28 28 16 : Color of : #3a5013
28 30 30 16 : Color of : #3c5216
30 32 32 16 : Color of : #3d541a
32 34 34 2 : Color of : #001a00
34 36 36 2 : Color of : #022000
36 38 38 2 : Color of : #0d2a00
38 40 40 2 : Color of : #173400
40 42 42 2 : Color of : #203900
42 44 44 2 : Color of : #213a00
44 46 46 2 : Color of : #1f3900
46 48 48 2 : Color of : #1d3700
32 34 34 4 : Color of : #072500
34 36 36 4 : Color of : #0d2b00
36 38 38 4 : Color of : #173400
38 40 40 4 : Color of : #203c00
40 42 42 4 : Color of : #274000
42 44 44 4 : Color of : #294200
44 46 46 4 : Color of : #284100
46 48 48 4 : Color of : #263f00
32 34 34 6 : Color of : #153200
34 36 36 6 : Color of : #193600
36 38 38 6 : Color of : #213d00
38 40 40 6 : Color of : #284300
40 42 42 6 : Color of : #2f4707
42 44 44 6 : Color of : #304808
44 46 46 6 : Color of : #2f4705
46 48 48 6 : Color of : #2e4604
32 34 34 8 : Color of : #1c3800
34 36 36 8 : Color of : #213d00
36 38 38 8 : Color of : #274200
38 40 40 8 : Color of : #2e4908
40 42 42 8 : Color of : #334b0d
42 44 44 8 : Color of : #344c0e
44 46 46 8 : Color of : #334b0d
46 48 48 8 : Color of : #31490b
32 34 34 10 : Color of : #213d00
34 36 36 10 : Color of : #254100
36 38 38 10 : Color of : #2c4704
38 40 40 10 : Color of : #324d0c
40 42 42 10 : Color of : #374f11
42 44 44 10 : Color of : #374f11
44 46 46 10 : Color of : #354d0f
46 48 48 10 : Color of : #334b0d
32 34 34 12 : Color of : #244000
34 36 36 12 : Color of : #284400
36 38 38 12 : Color of : #2e4a04
38 40 40 12 : Color of : #34500a
40 42 42 12 : Color of : #39510f
42 44 44 12 : Color of : #39510f
44 46 46 12 : Color of : #385010
46 48 48 12 : Color of : #364e0e
32 34 34 14 : Color of : #223e00
34 36 36 14 : Color of : #254100
36 38 38 14 : Color of : #2b4700
38 40 40 14 : Color of : #304c03
40 42 42 14 : Color of : #354e08
42 44 44 14 : Color of : #364f09
44 46 46 14 : Color of : #364f0a
46 48 48 14 : Color of : #354e09
32 34 34 16 : Color of : #1d3a00
34 36 36 16 : Color of : #203d00
36 38 38 16 : Color of : #244100
38 40 40 16 : Color of : #294600
40 42 42 16 : Color of : #2f4900
42 44 44 16 : Color of : #314b02
44 46 46 16 : Color of : #324c03
46 48 48 16 : Color of : #324b05
48 50 50 2 : Color of : #062700
50 52 52 2 : Color of : #123200
52 54 54 2 : Color of : #214000
54 56 56 2 : Color of : #2a4700
56 58 58 2 : Color of : #2e4a03
58 60 60 2 : Color of : #314d06
60 62 62 2 : Color of : #355108
62 64 64 2 : Color of : #37530a
48 50 50 4 : Color of : #0f2f00
50 52 52 4 : Color of : #173700
52 54 54 4 : Color of : #214000
54 56 56 4 : Color of : #294500
56 58 58 4 : Color of : #2d4903
58 60 60 4 : Color of : #304c06
60 62 62 4 : Color of : #314d04
62 64 64 4 : Color of : #314d04
48 50 50 6 : Color of : #183800
50 52 52 6 : Color of : #1d3c00
52 54 54 6 : Color of : #244000
54 56 56 6 : Color of : #284400
56 58 58 6 : Color of : #2c4704
58 60 60 6 : Color of : #2e4a04
60 62 62 6 : Color of : #2f4802
62 64 64 6 : Color of : #2c4600
48 50 50 8 : Color of : #1c3900
50 52 52 8 : Color of : #213e00
52 54 54 8 : Color of : #264200
54 56 56 8 : Color of : #294401
56 58 58 8 : Color of : #2c4706
58 60 60 8 : Color of : #2f4705
60 62 62 8 : Color of : #2c4500
62 64 64 8 : Color of : #294300
48 50 50 10 : Color of : #193600
50 52 52 10 : Color of : #203c00
52 54 54 10 : Color of : #274200
54 56 56 10 : Color of : #2b4605
56 58 58 10 : Color of : #2e4608
58 60 60 10 : Color of : #2e4604
60 62 62 10 : Color of : #2c4500
62 64 64 10 : Color of : #2a4400
48 50 50 12 : Color of : #163300
50 52 52 12 : Color of : #1e3a00
52 54 54 12 : Color of : #274200
54 56 56 12 : Color of : #2d4507
56 58 58 12 : Color of : #2e4608
58 60 60 12 : Color of : #2e4606
60 62 62 12 : Color of : #2e4702
62 64 64 12 : Color of : #2e4701
48 50 50 14 : Color of : #163300
50 52 52 14 : Color of : #1d3900
52 54 54 14 : Color of : #284100
54 56 56 14 : Color of : #2c4404
56 58 58 14 : Color of : #2e4608
58 60 60 14 : Color of : #2f4707
60 62 62 14 : Color of : #314806
62 64 64 14 : Color of : #314803
48 50 50 16 : Color of : #173400
50 52 52 16 : Color of : #1e3b00
52 54 54 16 : Color of : #274000
54 56 56 16 : Color of : #2b4303
56 58 58 16 : Color of : #2d4507
58 60 60 16 : Color of : #2f4707
60 62 62 16 : Color of : #324907
62 64 64 16 : Color of : #314804
64 66 66 2 : Color of : #000300
66 68 68 2 : Color of : #000a00
68 70 70 2 : Color of : #001100
70 72 72 2 : Color of : #001600
72 74 74 2 : Color of : #001800
74 76 76 2 : Color of : #001700
76 78 78 2 : Color of : #001300
78 80 80 2 : Color of : #001000
64 66 66 4 : Color of : #000b00
66 68 68 4 : Color of : #001000
68 70 70 4 : Color of : #001700
70 72 72 4 : Color of : #001a00
72 74 74 4 : Color of : #001a00
74 76 76 4 : Color of : #001900
76 78 78 4 : Color of : #001700
78 80 80 4 : Color of : #001400
64 66 66 6 : Color of : #001500
66 68 68 6 : Color of : #001900
68 70 70 6 : Color of : #001d00
70 72 72 6 : Color of : #001e00
72 74 74 6 : Color of : #001d00
74 76 76 6 : Color of : #001d00
76 78 78 6 : Color of : #001a00
78 80 80 6 : Color of : #001800
64 66 66 8 : Color of : #001c00
66 68 68 8 : Color of : #001f00
68 70 70 8 : Color of : #002000
70 72 72 8 : Color of : #002000
72 74 74 8 : Color of : #001f00
74 76 76 8 : Color of : #001e00
76 78 78 8 : Color of : #001c00
78 80 80 8 : Color of : #001900
64 66 66 10 : Color of : #001d00
66 68 68 10 : Color of : #001e00
68 70 70 10 : Color of : #002000
70 72 72 10 : Color of : #001f00
72 74 74 10 : Color of : #001f00
74 76 76 10 : Color of : #001e00
76 78 78 10 : Color of : #001c00
78 80 80 10 : Color of : #001900
64 66 66 12 : Color of : #001900
66 68 68 12 : Color of : #001c00
68 70 70 12 : Color of : #001d00
70 72 72 12 : Color of : #001d00
72 74 74 12 : Color of : #001d00
74 76 76 12 : Color of : #001d00
76 78 78 12 : Color of : #001900
78 80 80 12 : Color of : #001600
64 66 66 14 : Color of : #001300
66 68 68 14 : Color of : #001600
68 70 70 14 : Color of : #001800
70 72 72 14 : Color of : #001900
72 74 74 14 : Color of : #001a00
74 76 76 14 : Color of : #001800
76 78 78 14 : Color of : #001400
78 80 80 14 : Color of : #000e00
64 66 66 16 : Color of : #000d00
66 68 68 16 : Color of : #001000
68 70 70 16 : Color of : #001300
70 72 72 16 : Color of : #001600
72 74 74 16 : Color of : #001500
74 76 76 16 : Color of : #001300
76 78 78 16 : Color of : #000e00
78 80 80 16 : Color of : #000800
80 82 82 2 : Color of : #000000
82 84 84 2 : Color of : #000000
84 86 86 2 : Color of : #000000
86 88 88 2 : Color of : #000200
88 90 90 2 : Color of : #000200
90 92 92 2 : Color of : #000200
92 94 94 2 : Color of : #000000
94 96 96 2 : Color of : #000000
80 82 82 4 : Color of : #000000
82 84 84 4 : Color of : #000000
84 86 86 4 : Color of : #000200
86 88 88 4 : Color of : #000400
88 90 90 4 : Color of : #000400
90 92 92 4 : Color of : #000200
92 94 94 4 : Color of : #000000
94 96 96 4 : Color of : #000000
80 82 82 6 : Color of : #000000
82 84 84 6 : Color of : #000100
84 86 86 6 : Color of : #000500
86 88 88 6 : Color of : #000600
88 90 90 6 : Color of : #000400
90 92 92 6 : Color of : #000400
92 94 94 6 : Color of : #000200
94 96 96 6 : Color of : #000100
80 82 82 8 : Color of : #000000
82 84 84 8 : Color of : #000200
84 86 86 8 : Color of : #000500
'''