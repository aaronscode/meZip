from bitarray import bitarray
import mezip
import unittest

#---------------------------------------------------------------------------
#
# compression tests
#
#---------------------------------------------------------------------------

abba = 'AABABBBABAABABBBABBABB'
abba_newline = 'AABABBBABAABABBBABBABB\n'
abba_compressed = '01110100101001011100101100111'
abba_newline_compressed = '001011001000101000101011000101100011110'
abba_full_payload = '0000001001000001010000100000001101110100101001011100101100111000'
abba_newline_full_payload = '00000011010000010100001000001010000000010010110010001010001010110001011000111100'

class TestCompression(unittest.TestCase):

    def test_tokenize(self):

        ngrams, symbol_dict = mezip.tokenize(abba)
        self.assertEqual(ngrams, ['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB'])
        self.assertEqual(symbol_dict, ['A', 'B'])

        
        ngrams, symbol_dict = mezip.tokenize(abba_newline)
        self.assertEqual(ngrams, ['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB\n'])
        self.assertEqual(symbol_dict, ['A', 'B', '\n'])

    def test_encode(self):

        ngrams, symbol_dict = mezip.tokenize(abba)
        bit_string = mezip.encode(ngrams, symbol_dict)
        self.assertEqual(bit_string, bitarray(abba_compressed))

        bit_string = mezip.encode(['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB'], ['A', 'B'])
        self.assertEqual(bit_string, bitarray(abba_compressed))
        
        ngrams, symbol_dict = mezip.tokenize(abba_newline)
        bit_string = mezip.encode(ngrams, symbol_dict)
        self.assertEqual(bit_string,
                bitarray(abba_newline_compressed))

        bit_string = mezip.encode(['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB\n'], ['A', 'B', '\n'])
        self.assertEqual(bit_string,
                bitarray(abba_newline_compressed))


    def test_byte_align(self):
        
        bit_string, num_zeros = mezip.byte_align(bitarray('01110100101001011100101100111'))
        self.assertEqual(bit_string, bitarray('01110100101001011100101100111000'))
        self.assertEqual(num_zeros, 3)

        bit_string, num_zeros = mezip.byte_align(bitarray('001011001000101000101011000101100011110'))
        self.assertEqual(bit_string,
                bitarray('0010110010001010001010110001011000111100'))
        self.assertEqual(num_zeros, 1)

    def test_makeHeader(self):
        ngrams, symbol_dict = mezip.tokenize(abba)
        header = mezip.makeHeader(symbol_dict, 3)
        self.assertEqual(header, bitarray('00000010010000010100001000000011'))

        ngrams, symbol_dict = mezip.tokenize(abba_newline)
        header = mezip.makeHeader(symbol_dict, 1)
        self.assertEqual(header, bitarray('0000001101000001010000100000101000000001'))

    def test_compress(self):
        payload = mezip.compress(abba)
        self.assertEqual(payload, bitarray(abba_full_payload))
        
        payload = mezip.compress(abba_newline)
        self.assertEqual(payload, bitarray(abba_newline_full_payload))
#---------------------------------------------------------------------------
#
# decompression tests
#
#---------------------------------------------------------------------------

'''
class TestDecompression(unittest.TestCase):

    def test_ConsumeHeader(self):
        pass

    def test_getByteString(self):
        pass

    def test_tokenizeCompressed(self):
        pass
'''

if __name__ == '__main__':
    unittest.main()
