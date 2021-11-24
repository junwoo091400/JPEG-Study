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

compressed_string_bitlen = 0

print(' Char | Huffman code ')
print('----------------------')
for (char, frequency) in freq:
    print(' %-4r |%12s' % (char, huffmanCode[char]))
    compressed_string_bitlen += frequency * len(huffmanCode[char])

print('Original String length (bits) :', 8 * len(string))
print('HE string bit length :', compressed_string_bitlen)
print('Compressibility :', 100 * (compressed_string_bitlen / (8 * len(string))), '[%]')