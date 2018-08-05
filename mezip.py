#!/usr/bin/python3
"""
# meZip.py: a custom implementation of the LZ78 compression algorithm.
# Takes a file or list of text files as imput and compresses them with the -c
# flag into files with a .mz extention, or decompresses them otherwise.
#
"""

import argparse
from bitarray import bitarray
import math
import os

BYTE_ORDER = 'big' # use bigendian byte order

#---------------------------------------------------------------------------
#
# main method
#
#---------------------------------------------------------------------------

def main():
    # create a command line parser with the argparse module
    parser = argparse.ArgumentParser('Implementaiton of LZ78 compression')
    parser.add_argument('-c', help='compress', action='store_true')
    parser.add_argument('-i',  metavar='input_files', type=str, nargs='+',
                        help='input files')
    parser.add_argument('-o', metavar='output_dir', type=str, nargs='?',
            default=None, help='output dir')

    args = parser.parse_args()

    if args.o is not None:
        if not os.path.isdir(args.o):
            print("arg output_dir is not directory")
            exit(-1)
    else:
        args.o = '.'

    # compress or decompress every file in the input list
    for file in args.i:
        if args.c is True: read_compress_write(file, args.o)
        else: decompress(file, args.o)

#---------------------------------------------------------------------------
#
# compression methods
#
#---------------------------------------------------------------------------

def read_compress_write(input_file, output_dir):
        # TODO refactor into bytearray, not text
        # read the input text from the file
        text = ''
        with open(input_file, 'r') as f:
            text = f.read()

        payload = compress(text)

        # get the output file path + name
        output_file = os.path.splitext(os.path.basename(input_file))[0] + '.mz'

        # write the compressed data to file
        with open(os.path.join(output_dir, output_file), 'wb') as f:
            payload.tofile(f)


def compress(text):
    # TODO combine tokenize and encode into single method
    # should be able to do both in a single pass

    # tokenize the input text to ngrams, also form a dictonary of the base
    # symbol set
    ngrams, symbol_dict = tokenize(text)

    # use the tokenized file and symbol dictonary to
    # form an encoded (compressed) string of bits
    bin_string = encode(ngrams, symbol_dict)

    # make sure our encoded data is byte aligned
    # by padding with extra zeros on the end if necessary
    bin_string, zero_pad = byte_align(bin_string)

    # made the header using the symbol dictionary
    # and number of zeros to pad with
    header = makeHeader(symbol_dict, zero_pad)

    # concatinate the header and the encoded data
    header.extend(bin_string)
    return header # header now contains header and compressed data


# tokenize input text and create a dictionary of symbols
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


# TODO add comments explaining encoding process
def encode(tokens, symbols):
    bin_encod = bitarray()
    bits_to_use = 0
    bit_counter = 0
    last_token = tokens[-1]
    last_index = len(tokens) - 1
    last_is_cpy = not (last_index == tokens.index(last_token))
    symbol_fmt_str = '{0:0' + str(digits_in_sym_code(symbols)) + 'b}'

    for idx, token in enumerate(tokens):
        if bin_encod.length() == 0: # if the first symbol, deal with it specially
            bin_encod = bitarray(symbolCode(token, symbols, symbol_fmt_str))
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

            if not(last_is_cpy and token is last_token and idx == last_index):
                new_symbol_code = symbolCode(token[-1:], symbols, symbol_fmt_str)
                if int(new_symbol_code,2) > len(symbols):
                    print("We have a problem here")

                new_phrase = dict_idx_str + new_symbol_code
            else: # it is the last token and we have a duplicate
                new_phrase = dict_idx_str 

            bin_encod.extend(new_phrase)

            bit_counter = bit_counter - 1
            if bit_counter == 0:
                bits_to_use = bits_to_use + 1
                bit_counter = 2 ** (bits_to_use - 1)

    return bin_encod


def symbolCode(symbol, symbols, format_str):
    return format_str.format(symbols.index(symbol))

def makeHeader(symbols, num_zeros):
    format_str = '{0:08b}'

    header = bitarray(format_str.format(len(symbols)))

    for symbol in symbols:
        header.extend(format_str.format(ord(symbol)))

    # use one byte to encode the number of zeros we
    # had to pad our payload with to make it byte-aligned
    header.extend(format_str.format(num_zeros))

    return header

def digits_in_sym_code(symbols):
    return math.ceil(math.log(len(symbols), 2))

def byte_align(bin_encod):
    # after creating our binary encoding, we need to byte align it
    zeros_needed = 0
    if len(bin_encod) % 8 != 0:
        zeros_needed = 8 - (len(bin_encod) % 8)
        format_str = '{0:0' + str(zeros_needed) +'b}'
        bin_encod.extend(format_str.format(0))

    return bin_encod, zeros_needed


#---------------------------------------------------------------------------
#
# decompression methods
#
#---------------------------------------------------------------------------

def decompress(inputFile, outputDir):

    decoded_string = ''

    with open(inputFile, 'rb') as f:

        symbols = consumeHeader(f)

        # num zeros the last byte is padded with
        num_pad_zeros = int.from_bytes(f.read(1), byteorder=BYTE_ORDER)

        # get the number of bits we're using to encode the symbol
        bits_per_sym = digits_in_sym_code(symbols)

        byte_string = getByteString(f, num_pad_zeros)

        tokens = tokenizeCompressed(byte_string, bits_per_sym)

        last_token = tokens[-1]
        second_to_last_token = tokens[-2]
        last_is_repeat = (len(last_token) + bits_per_sym) < len(second_to_last_token)

        print('------------------')
        decoded_tokens = []
        decoded_tokens.append('')
        for token in tokens:
            if token is last_token and last_is_repeat:
                text = decoded_tokens[int(tokens,2)]
                decoded_tokens.append(text)
            else:
                if len(decoded_tokens) < 2:
                    decoded_tokens.append(symbols[int(token,2)])
                else:
                    """
                    print(token)
                    print(token[:-bits_per_sym])
                    print(token[-bits_per_sym:])
                    print(int(token[-bits_per_sym:],2))
                    print(len(symbols))
                    print(decoded_tokens)
                    """
                    prefix = decoded_tokens[int(token[:-bits_per_sym],2)]
                    #print(prefix)
                    suffix = symbols[int(token[-bits_per_sym:],2)]
                    #print(suffix)
                    decoded_tokens.append(prefix + suffix)


        decoded_string = ''.join(decoded_tokens)
        print(decoded_string)

    outputFile = os.path.splitext(os.path.basename(inputFile))[0] + '.txt_dec'

    with open(os.path.join(outputDir, outputFile), 'w') as f:
        f.write(decoded_string)


def consumeHeader(fHandle):
    symbols = []

    # the first byte tells us the number of symbols, but we need to convert it
    # from a byte to int
    num_symbols_b = fHandle.read(1)
    num_symbols_i = int.from_bytes(num_symbols_b, byteorder=BYTE_ORDER)

    # read in num_symbols bytes, iterating over each one and adding it to our
    # symbols list
    for byte in fHandle.read(num_symbols_i):
        symbols.append(chr(byte))

    return symbols

def getByteString(fHandle, num_zeros):
    byte_strings = []

    bin_data = fHandle.read()

    for byte in bin_data:
        byte_s = '{0:08b}'.format(byte)
        byte_strings.append(byte_s)

    byte_string = ''.join(byte_strings)
    if num_zeros != 0:
        return byte_string[:-num_zeros]
    else:
        return byte_string

def tokenizeCompressed(byte_string, bits_per_sym):
    tokens = []
    token_count = 0
    token_index = 0
    token = ''
    bits_to_use = 0
    bit_counter = 0

    while token_index + 1 < len(byte_string):
        if token_count < 1:
            token = byte_string[0:bits_per_sym]
            token_count = token_count + 1
            token_index = bits_per_sym
            bits_to_use = bits_to_use + 1
            bit_counter = 1
        else:
            len_token = bits_to_use + bits_per_sym
            if len_token + token_index + 1 < len(byte_string):
                token = byte_string[token_index:token_index+len_token]
            else:
                token = byte_string[token_index:]

            token_count = token_count + 1
            token_index = token_index + len_token

            bit_counter = bit_counter - 1
            if bit_counter == 0:
                bits_to_use = bits_to_use + 1
                bit_counter = 2 ** (bits_to_use - 1)

        tokens.append(token)

    return tokens


#--------------------------------------------------------------

if __name__ == '__main__':
    main()

#EOF
