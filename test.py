import mezip
import unittest

#---------------------------------------------------------------------------
#
# compression tests
#
#---------------------------------------------------------------------------

class TestCompression(unittest.TestCase):

    def test_tokenize(self):

        ngrams, symbol_dict = mezip.tokenize('AABABBBABAABABBBABBABB')
        self.assertEqual(ngrams, ['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB'])
        self.assertEqual(symbol_dict, ['A', 'B'])

        
        ngrams, symbol_dict = mezip.tokenize('AABABBBABAABABBBABBABB\n')
        self.assertEqual(ngrams, ['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB\n'])
        self.assertEqual(symbol_dict, ['A', 'B', '\n'])

    def test_encode(self):

        ngrams, symbol_dict = mezip.tokenize('AABABBBABAABABBBABBABB')
        bit_string = mezip.encode(ngrams, symbol_dict)
        self.assertEqual(bit_string, '01110100101001011100101100111')

        bit_string = mezip.encode(['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB'], ['A', 'B'])
        self.assertEqual(bit_string, '01110100101001011100101100111')
        
        ngrams, symbol_dict = mezip.tokenize('AABABBBABAABABBBABBABB\n')
        bit_string = mezip.encode(ngrams, symbol_dict)
        self.assertEqual(bit_string, '001011001000101000101011000101100011110')

        bit_string = mezip.encode(['A', 'AB', 'ABB', 'B', 'ABA', 'ABAB', 'BB',
            'ABBA', 'BB\n'], ['A', 'B', '\n'])
        self.assertEqual(bit_string, '001011001000101000101011000101100011110')

    def test_makeHeader(self):
        ngrams, symbol_dict = mezip.tokenize('AABABBBABAABABBBABBABB')
        header = mezip.makeHeader(symbol_dict, 3)
        self.assertEqual(header, '00000010010000010100001000000011')

        ngrams, symbol_dict = mezip.tokenize('AABABBBABAABABBBABBABB\n')
        header = mezip.makeHeader(symbol_dict, 1)
        self.assertEqual(header, '0000001101000001010000100000101000000001')
        
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
