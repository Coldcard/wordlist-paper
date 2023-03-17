# print some charts
from hashlib import sha256
from mnemonic import Mnemonic
from random import Random
from textwrap import TextWrapper

wordlist = Mnemonic('english').wordlist

WIDTH = 110

def xor_table(indent=' '*8):
    print(indent + '| XOR |' + '|'.join(' %X ' % x for x in range(16)))
    print(indent + '|----:' + '|---'*16)

    for y in range(16):
        print(indent + '|**%X**|' % y, end='')
        print('|'.join(' %X ' % (x^y) for x in range(16)))

    print('''\


- XOR = EOR = &oplus; = Exclusive OR [Wikipedia](https://en.wikipedia.org/wiki/Exclusive_or)
- values in table are: x &oplus; y in hex
- go sideways for first digit, then look down for second digit
- in fact, doesn't matter if you do row or column first
- example: 2 XOR 6 => 4  same as   6 XOR 2 => 4
- any values XOR itself is zero (diagonal on this table)
- alternative view: (x) XOR (y) = flip bits of (x) that are set in (y)
    - XOR with zero does nothing (flips no bits)
    - XOR with 0xF flips all four bits
    - XOR with self flips all set bits, so gives zero
- to XOR three values together, do (a&oplus;b)=X then (X&oplus;c)=answer
    - right to A, down to B ... take that number, and go to that column
    - down to C, that is answer: a &oplus; b &oplus; c
''')


def get_words(entropy):
    e_len = len(entropy)
    assert e_len in [16, 20, 24, 28, 32]
    csum_len = int(e_len / 4)
    num_words = int(((e_len * 8) + csum_len) / 11)
    v = int.from_bytes(entropy, 'big') << csum_len
    indexes = []
    for i in range(num_words):
        v, m = divmod(v, 2048)
        indexes.insert(0, m)
    # final csum_len bits are a checksum
    indexes[-1] += sha256(entropy).digest()[0] >> (8 - csum_len)
    return indexes


def calc_check(words):
    words_len = len(words)
    csum_len = int(words_len / 3)
    e_len = int(((words_len * 11) - csum_len) / 8)
    x = 0
    for i in range(words_len):
        x <<= 11
        x |= words[i]
    x >>= csum_len
    raw = x.to_bytes(e_len, 'big')

    cb = sha256(raw).digest()[0] >> (8 - csum_len)
    x <<= csum_len
    x |= cb

    return raw, (x % 0x800)


def entropy_length_to_word_length(entropy_len):
    entropy_bit_len = entropy_len * 8
    cs_bit_len = entropy_bit_len // 32
    return (entropy_bit_len + cs_bit_len) // 11


def print_phrase(raw, indent=' '*4, from_entropy=False):

    tw = TextWrapper(width=WIDTH, initial_indent=indent, subsequent_indent=indent)

    if from_entropy:
        words = get_words(raw)
    else:
        words = list(raw)

    x = ['%d=%s_[%03X]'%(n+1, wordlist[i],i) for n,i in enumerate(words)]
    msg = ', '.join(x)
    eng = [ln.replace('_', ' ') for ln in tw.wrap(msg)]

    hx = ' '.join('%03X'%i for i in words)
    
    return eng, hx, words

def worked_example(count=3, entropy_bytes=32):

    rng = Random(123 * count)
    num_words = entropy_length_to_word_length(entropy_bytes)
    print(f'# {num_words} Words XOR Seed Example Using {count} Parts\n')

    indent = ' '*6
    digits = []
    for n in range(count):
        raw = bytearray(rng.randint(0, 255) for _ in range(entropy_bytes))

        eng, hx, words = print_phrase(raw, indent, from_entropy=True)

        print(f'## Seed {n+10:X}  ({n+1} of {count})\n')
        print('\n'.join(eng))
        print(f'\n{indent}{n+10:X} = {hx}\n\n')

        digits.append(hx)

    print('## Calculation (XOR each hex digit)\n')
    for n in range(count):
        print(f'{indent}{n+10:X} = {digits[n]}')

    if entropy_bytes == 32:
        constant = 2
    elif entropy_bytes == 16:
        constant = 1
    else:
        constant = 0
    xor = ''
    for pos in range(len(digits[0]) - constant):
        if digits[0][pos] == ' ':
            xor += ' '
            continue

        here = 0
        for n in range(count):
            here ^= int(digits[n][pos], 16)
        assert 0 <= here < 16, here
        xor += '%X' % here

    xor += 'x' * constant

    lst = list(range(0, 100, 16)) + [23*4]
    align = ''.join(('|' if n in lst else ' ') for n in range(len(xor)))
    print(f'{indent}    {align}')

    print(f'{indent[2:]}XOR = {xor}')


    print('\n\n## Resulting Seed Phrase\n')
    rw = [int(i, 16) for i in xor.split(' ')[:-1]]

    eng, hx, _ = print_phrase(rw, indent)
    print('\n'.join(eng))
    if len(rw) == 11:
        _range = 0x10
        chk = int(xor.split(' ')[-1][0:2], 16) * _range
    elif len(rw) == 23:
        _range = 0x100
        chk = int(xor.split(' ')[-1][0], 16) * _range
    else:
        # for these cases - bitwise operations required
        # as their checksums have length in (5,6,7)
        lw = xor.split(' ')[-1]
        lw_int = int(lw, 16)
        chk_len = int((len(rw) + 1) / 3)
        _range = (2 ** chk_len) - 1
        chk = (lw_int >> chk_len) << chk_len

    print(f'\n{indent}final word between: %s [%03X] - %s [%03X]' % (
            wordlist[chk], chk, wordlist[chk+_range], chk+_range))

    secret, final = calc_check(rw + [chk])
    print(f'{indent}correct final word: %s [%03X]' % (wordlist[final], final))

    # check our checksum math
    _, chk_hx, _ = print_phrase(secret, indent, from_entropy=True)
    assert chk_hx.split(' ')[-1] == '%03X'%final 


def footer_text():
    print('''\
- It's not possible to calculate the checksum of the final seed phrase on paper (needs SHA256).
- It must start with the indicated digit(s). If using 24 words XOR, there will be only one
  suitable choice offered by the Coldcard in that range (x00 to xFF),
  once you have entered the other 23 words.
- The checksum of each of the XOR-parts protects the final result, assuming your XOR
  math is correct.
''')


if 1:
    print('## XOR Lookup Table\n\n')
    xor_table('')
    print('---\n')

if 1:
    worked_example(3, entropy_bytes=32)
    print("\n\n")
    worked_example(3, entropy_bytes=16)
    print("\n\n")
    footer_text()


