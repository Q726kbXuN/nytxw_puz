#!/usr/bin/env python3

# Fairly straight port of
# https://github.com/pieroxy/lz-string/
# to Python.  Only decompress was ported

import re


def decompress(compressed):
    if (compressed is None) or (compressed == ''):
        return ''

    dictionary = {}
    enlargeIn = 4
    dictSize = 4
    numBits = 3
    (entry, result, w, c) = ('', '', '', '')
    (i, nnext, bits, resb, maxpower, power) = (0, 0, 0, 0, 0, 0)

    data_string = compressed
    data_val = ord(compressed[0])
    data_position = 32768
    data_index = 1

    for i in range(3):
        dictionary[i] = ''

    bits = 0
    maxpower = pow(2, 2)
    power = 1

    while power != maxpower:
        resb = data_val & data_position
        data_position >>= 1

        if data_position == 0:
            data_position = 32768
            data_val = ord(data_string[data_index])
            data_index += 1

        bits |= (1 if resb > 0 else 0) * power
        power <<= 1

    nnext = bits
    if nnext == 0:
        bits = 0
        maxpower = pow(2, 8)
        power = 1

        while power != maxpower:
            resb = data_val & data_position
            data_position >>= 1

            if data_position == 0:
                data_position = 32768
                data_val = ord(data_string[data_index])
                data_index += 1

            bits |= (1 if resb > 0 else 0) * power
            power <<= 1

        c = chr(bits)
    elif nnext == 1:
        bits = 0
        maxpower = pow(2, 16)
        power = 1

        while power != maxpower:
            resb = data_val & data_position
            data_position >>= 1

            if data_position == 0:
                data_position = 32768
                data_val = ord(data_string[data_index])
                data_index += 1

            bits |= (1 if resb > 0 else 0) * power
            power <<= 1

        c = chr(bits)
    elif nnext == 2:
        return ''

    dictionary[3] = c
    result = c
    w = result

    while True:
        if data_index > len(data_string):
            return ''

        bits = 0
        maxpower = pow(2, numBits)
        power = 1

        while power != maxpower:
            resb = data_val & data_position
            data_position >>= 1

            if data_position == 0:
                data_position = 32768
                data_val = ord(data_string[data_index])
                data_index += 1

            bits |= (1 if resb > 0 else 0) * power
            power <<= 1

        c = bits

        if c == 0:
            bits = 0
            maxpower = pow(2, 8)
            power = 1

            while power != maxpower:
                resb = data_val & data_position
                data_position >>= 1

                if data_position == 0:
                    data_position = 32768
                    data_val = ord(data_string[data_index])
                    data_index += 1

                bits |= (1 if resb > 0 else 0) * power
                power <<= 1

            dictionary[dictSize] = chr(bits)
            dictSize += 1
            c = dictSize - 1
            enlargeIn -= 1
        elif c == 1:
            bits = 0
            maxpower = pow(2, 16)
            power = 1

            while power != maxpower:
                resb = data_val & data_position
                data_position >>= 1

                if data_position == 0:
                    data_position = 32768
                    data_val = ord(data_string[data_index])
                    data_index += 1

                bits |= (1 if resb > 0 else 0) * power
                power <<= 1

            dictionary[dictSize] = chr(bits)
            dictSize += 1
            c = dictSize - 1
            enlargeIn -= 1
        elif c == 2:
            return result

        if enlargeIn == 0:
            enlargeIn = pow(2, numBits)
            numBits += 1

        if c in dictionary:
            entry = dictionary[c]
        else:
            if c == dictSize:
                entry = w + w[0]
            else:
                return None

        result += entry

        dictionary[dictSize] = w + entry[0]
        dictSize += 1
        enlargeIn -= 1

        w = entry

        if enlargeIn == 0:
            enlargeIn = pow(2, numBits)
            numBits += 1


def decode(value):
    value = re.sub("%u([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), value)
    value = re.sub("%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), value)
    return value


if __name__ == "__main__":
    print("This module is not meant to be run directly")
