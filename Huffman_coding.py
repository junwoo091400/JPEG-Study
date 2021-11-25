'''
https://www.programiz.com/dsa/huffman-coding
https://www.fulltextarchive.com/page/Pride-and-Prejudice1/
'''

# Join the whole text (which is read as a list of separate paragraphs) into a big string.
string = ''.join(open('huffman_test_text.txt','rt'))

# Creating tree nodes
class NodeTree(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return (self.left, self.right)

    def nodes(self):
        return (self.left, self.right)

    def __str__(self):
        return '%s_%s' % (self.left, self.right)


# Main function implementing huffman coding
def huffman_code_tree(node, left=True, binString=''):
    if type(node) is str: # reached the node-end with the datatype of 'string' (character)
        #print('Returning HT end node :', node, binString)
        return {node: binString}
    (l, r) = node.children() # Left & Right children of Node.
    d = dict()
    d.update(huffman_code_tree(l, True, binString + '0'))
    d.update(huffman_code_tree(r, False, binString + '1'))
    return d


# Calculating frequency
freq = {}
for c in string:
    if c in freq:
        freq[c] += 1
    else:
        freq[c] = 1

# Sort via decreasing order of frequency. Most frequent in the beginning.
freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
print(freq)

nodes = freq

while len(nodes) > 1:
    (key1, c1) = nodes[-1]
    (key2, c2) = nodes[-2] # Bigger freq sum value.
    nodes = nodes[:-2] # Delete last 2 nodes from the list.
    node = NodeTree(key1, key2)
    nodes.append((node, c1 + c2)) # Add the count.
    # Keep sorting to keep nodes list with descending count of freq sum.
    nodes = sorted(nodes, key=lambda x: x[1], reverse=True)
    #print(nodes)

# Get the NodeTree of the whole HT (nodes[0][1] is the 'total Count')
huffmanCode = huffman_code_tree(nodes[0][0])

# SECOND way
nodes_2 = freq
while len(nodes_2) > 1:
    (key1, c1) = nodes_2[-1]
    (key2, c2) = nodes_2[-2]
    nodes_2 = nodes_2[:-2]
    node = NodeTree(key1, key2)
    nodes_2 = [(node, c1 + c2)] + nodes_2 # Add to front.
    # Don't sort.

huffmanCode_2 = huffman_code_tree(nodes_2[0][0])

def print_huffmancode(hc, freq):
    compressed_string_bitlen = 0
    print(' Char | Huffman code ')
    print('----------------------')
    for (char, frequency) in freq:
        print(' %-4r |%12s' % (char, hc[char]))
        compressed_string_bitlen += frequency * len(hc[char])
    return compressed_string_bitlen

compressed_bitlen_1 = print_huffmancode(huffmanCode, freq)
print('\nMethod 2')
compressed_bitlen_2 = print_huffmancode(huffmanCode_2, freq)

print('Original String length (bits) :', 8 * len(string))
print('1) String bit length :', compressed_bitlen_1)
print('2) String bit length :', compressed_bitlen_2)
print("1's Compressibility :", 100 * (compressed_bitlen_1 / (8 * len(string))), '[%]')


'''
[(' ', 14105), ('e', 8686), ('t', 5717), ('a', 5190), ('o', 4994), ('n', 
4809), ('i', 4609), ('s', 4184), ('r', 4091), ('h', 4017), ('d', 2828), ('l', 2655), ('\n', 2027), ('u', 1957), ('y', 1753), ('m', 1610), ('c', 1593), ('w', 1473), ('f', 1434), ('g', 1322), (',', 1201), ('b', 995), ('p', 935), ('.', 906), ('"', 773), ('v', 700), ('k', 406), ('I', 398), ('M', 323), ('B', 240), (';', 205), ('-', 166), ('T', 140), ('E', 135), ('H', 
122), ('z', 118), ('x', 115), ('D', 113), ('L', 100), ('q', 95), ('Y', 86), ('A', 83), ('S', 82), ('W', 78), ("'", 77), ('!', 75), ('j', 70), ('C', 67), ('J', 63), ('?', 62), ('N', 60), ('O', 56), ('P', 48), ('R', 39), 
('F', 28), (':', 20), ('U', 20), ('G', 15), ('V', 8), ('K', 8), ('1', 5), ('8', 3), ('2', 3), ('(', 2), (')', 2), ('0', 2), ('Z', 2), ('â', 1), ('€', 1), ('”', 1), ('3', 1), ('4', 1), ('5', 1), ('6', 1), ('7', 1), ('9', 1), ('+', 1)]
 Char | Huffman code
----------------------
 ' '  |         110
 'e'  |         001
 't'  |        1010
 'a'  |        1000
 'o'  |        0110
 'n'  |        0101
 'i'  |        0100
 's'  |        0001
 'r'  |        0000
 'h'  |       11111
 'd'  |       10011
 'l'  |       01111
 '\n' |      111101
 'u'  |      111100
 'y'  |      111001
 'm'  |      111000
 'c'  |      101110
 'w'  |      101101
 'f'  |      100101
 'g'  |      100100
 ','  |      011100
 'b'  |     1110111
 'p'  |     1110101
 '.'  |     1110100
 '"'  |     1011110
 'v'  |     1011000
 'k'  |    10111110
 'I'  |    10110011
 'M'  |    01110110
 'B'  |   111011010
 ';'  |   101111110
 '-'  |   011101111
 'T'  |   011101001
 'E'  |   011101000
 'H'  |  1110110110
 'z'  |  1110110010
 'x'  |  1110110001
 'D'  |  1110110000
 'L'  |  1011111110
 'q'  |  1011001011
 'Y'  |  1011001001
 'A'  |  1011001000
 'S'  |  0111011101
 'W'  |  0111011100
 "'"  |  0111010111
 '!'  |  0111010110
 'j'  |  0111010100
 'C'  | 11101101111
 'J'  | 11101101110
 '?'  | 11101100111
 'N'  | 11101100110
 'O'  | 10111111111
 'P'  | 10110010101
 'R'  | 01110101011
 'F'  |101111111101
 ':'  |101100101001
 'U'  |101100101000
 'G'  |1011111111001
 'V'  |0111010101010
 'K'  |0111010101001
 '1'  |10111111110000
 '8'  |101111111100010
 '2'  |011101010101111
 '('  |011101010101110
 ')'  |1011111111000111
 '0'  |1011111111000110
 'Z'  |011101010100001
 'â'  |0111010101011001
 '€'  |0111010101011000
 '”'  |0111010101011011
 '3'  |0111010101011010
 '4'  |0111010101000101
 '5'  |0111010101000100
 '6'  |0111010101000111
 '7'  |0111010101000110
 '9'  |0111010101000001
 '+'  |0111010101000000

Method 2
 Char | Huffman code
----------------------
 ' '  |      110010
 'e'  |      110001
 't'  |      110000
 'a'  |      101111
 'o'  |      101110
 'n'  |      101101
 'i'  |      101100
 's'  |      101011
 'r'  |      101010
 'h'  |      101001
 'd'  |      101000
 'l'  |      100111
 '\n' |      100110
 'u'  |      100101
 'y'  |      100100
 'm'  |      100011
 'c'  |      100010
 'w'  |      100001
 'f'  |      100000
 'g'  |      011111
 ','  |      011110
 'b'  |      011101
 'p'  |      011100
 '.'  |      011011
 '"'  |      011010
 'v'  |      011001
 'k'  |      011000
 'I'  |      010111
 'M'  |      010110
 'B'  |      010101
 ';'  |      010100
 '-'  |      010011
 'T'  |      010010
 'E'  |      010001
 'H'  |      010000
 'z'  |      001111
 'x'  |      001110
 'D'  |      001101
 'L'  |      001100
 'q'  |      001011
 'Y'  |      001010
 'A'  |      001001
 'S'  |      001000
 'W'  |      000111
 "'"  |      000110
 '!'  |      000101
 'j'  |      000100
 'C'  |      000011
 'J'  |      000010
 '?'  |      000001
 'N'  |      000000
 'O'  |     1111111
 'P'  |     1111110
 'R'  |     1111101
 'F'  |     1111100
 ':'  |     1111011
 'U'  |     1111010
 'G'  |     1111001
 'V'  |     1111000
 'K'  |     1110111
 '1'  |     1110110
 '8'  |     1110101
 '2'  |     1110100
 '('  |     1110011
 ')'  |     1110010
 '0'  |     1110001
 'Z'  |     1110000
 'â'  |     1101111
 '€'  |     1101110
 '”'  |     1101101
 '3'  |     1101100
 '4'  |     1101011
 '5'  |     1101010
 '6'  |     1101001
 '7'  |     1101000
 '9'  |     1100111
 '+'  |     1100110
Original String length (bits) : 706512
1) String bit length : 401770
2) String bit length : 530155
1's Compressibility : 56.866691577779285 [%]
'''