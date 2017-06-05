#!/usr/bin/python3

import argparse

def main():
    parser = argparse.ArgumentParser('Implementaiton of LZ78 compression')
    parser.add_argument('-c', help='compress', action='store_true')
    parser.add_argument('ifiles', metavar='files', type=str, nargs='+',
                        help='input files')

    args = parser.parse_args()
    
    for file in args.ifiles:
        if args.c is True: compress(file)
        else: decompress(file)

def compress(inputFile):
    text = ''
    with open(inputFile, 'r') as f:
        text = f.read()

    ngrams, symbol_dict = tokenize(text)
    print(text)

    binaryString = encode(ngrams, symbol_dict)
    print(binaryString)
    print(len(binaryString))

    zeros_needed = 0
    if len(binaryString) % 8 != 0:
        zeros_needed = 8 - (len(binaryString) % 8)
        format_str = '{0:0' + str(zeros_needed) +'b}'
        binaryString = binaryString + format_str.format(0)

    print(binaryString)

    header = makeHeader(symbol_dict, zeros_needed)
    print(header)

    payload = header + binaryString
    payload_size = len(payload) // 8

    compressedData = int(payload, 2)
    dataAsBytes = compressedData.to_bytes(payload_size, byteorder='big')
    print(dataAsBytes)

    baseOFilePath = '.' + ''.join(inputFile.split('.')[:-1])
    outputFile = baseOFilePath + '.mz'

    with open(outputFile, 'wb') as f:
        f.write(dataAsBytes)

def tokenize(text):
    tokens = []
    symbols = []
    accumulated = ''

    for c in text:
        accumulated = accumulated + c

        if accumulated not in tokens:
            tokens.append(accumulated)
            accumulated = ''

        if c not in symbols:
            symbols.append(c)

    if not (accumulated == ''):
        tokens.append(accumulated)

    return (tokens, symbols)

def encode(tokens, symbols):
    bin_str = ''
    bits_to_use = 0
    bit_counter = 0 
    last_token = tokens[-1]
    last_index = len(tokens) - 1
    last_is_cpy = not (last_index == tokens.index(last_token))
    
    for idx, token in enumerate(tokens):
        if bin_str == '': # if the first symbol, deal with it specially
            bin_str = symbolCode(token, symbols)
            bits_to_use = bits_to_use + 1
            bit_counter = 1
        else: # if not the first item, deal with it normally
            format_str = '{0:0' + str(bits_to_use) +'b}'
            dict_idx = 0
            if len(token) > 1 and not(last_is_cpy and idx == last_index):
                dict_idx = 1 + tokens.index(token[:-1])
            elif len(token) > 1: # it is the last token and we have a duplicate
                dict_idx = 1 + tokens.index(token)

            dict_idx_str = (format_str.format(dict_idx))

            if not(last_is_cpy and token is last_token):
                new_phrase = dict_idx_str + symbolCode(token[-1:], symbols)
            else: # it is the last token and we have a duplicate
                new_phrase = dict_idx_str 


            bin_str = bin_str + new_phrase

            bit_counter = bit_counter - 1
            if bit_counter == 0:
                bits_to_use = bits_to_use + 1
                bit_counter = 2 ** (bits_to_use - 1)

    #TODO append number of codewords and binary for codewords
    return bin_str


def symbolCode(symbol, symbols):
    return str(bin(symbols.index(symbol))[2:])

def makeHeader(symbols, num_zeros):
    format_str = '{0:08b}'

    header = format_str.format(len(symbols))

    for symbol in symbols:
        header = header + format_str.format(ord(symbol))

    header = header + format_str.format(num_zeros)

    return header


def decompress(inputFile):
        print(inputFile)

if __name__ == '__main__':
    main()

#EOF
