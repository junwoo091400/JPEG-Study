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
8. 

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

#'''
class JPEG:
    def __init__(self, image_file):
        with open(image_file, 'rb') as f:
            self.img_data = f.read()
    
    def decodeHuffman(self, data):
        offset = 0
        header, = unpack("B",data[offset:offset+1])
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
            elements += (unpack("B"*i, data[offset:offset+i]))
            # Each 'element' is assumed to be a Byte
            offset += i 
        # Adding 'tuples' https://www.programiz.com/python-programming/list-vs-tuples
        
        print("Header: ",header)
        print("lengths: ", lengths)
        print("Elements: ", len(elements))

        hf = HuffmanTable()
        hf.GetHuffmanBits(lengths, elements)
        data = data[offset:] # Why?
    
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
                chunk = data[4:lenchunk + 2] # Data chunk excluding length data & header.
                if marker == 0xffdb: # Quantization Table
                    print('QT Sneek :', chunk)
                    # Length and Destination info is taking 3 bytes (Hence length of 67 bytes.)
                elif marker == 0xffc4: # Huffman Table
                    self.decodeHuffman(chunk)
                    #print('HT Sneek :', data[4:2+lenchunk]) # From 'Class' to End.
                    # Class (0: DC, 1: AC) / Destination (Number of HT : 0 ~ 3) -> ex. Luminance and Chrominance would be 0 and 1.
                    # 16 Bytes of 'total number of symbol / data with H-code length of x' (x = 1 ~ 16)
                    # Table of Symbols. From short to Increasing code length.
                data = data[2+lenchunk:] # Skip to the next data.
                print('lenchunk :', lenchunk)        
            if len(data)==0:
                break        

if __name__ == "__main__":
    img = JPEG('yasoob_example.jpg')
    img.decode()
# '''

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