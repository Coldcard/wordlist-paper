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

def get_words(h):
    # Apply BIP39 to convert into seed words
    v = int.from_bytes(h, 'big') << 8
    w = []
    for i in range(24):
        v, m = divmod(v, 2048)
        w.insert(0, m)
    assert not v

    # final 8 bits are a checksum
    w[-1] |= sha256(h).digest()[0]

    return w

def calc_check(words):
    assert len(words) == 24
    x = 0
    for i in range(24):
        x <<= 11
        x |= words[i]
    x >>= 8
    raw = x.to_bytes(32, 'big')

    cb = sha256(raw).digest()[0]

    x <<= 8
    x |= cb

    return raw, (x % 0x800)

def print_phrase(raw, indent=' '*4):

    tw = TextWrapper(width=WIDTH, initial_indent=indent, subsequent_indent=indent)

    if len(raw) == 32:
        words = get_words(raw)
        assert len(words) == 24
    else:
        words = list(raw)
        assert len(words) in {23, 24}

    x = ['%d=%s_[%03X]'%(n+1, wordlist[i],i) for n,i in enumerate(words)]
    msg = ', '.join(x)
    eng = [ln.replace('_', ' ') for ln in tw.wrap(msg)]

    hx = ' '.join('%03X'%i for i in words)
    
    return eng, hx, words

def worked_example(count=3):

    rng = Random(123 * count)

    print(f'# XOR Seed Example Using {count} Parts\n')

    indent = ' '*6
    digits = []
    for n in range(count):
        raw = bytearray(rng.randint(0, 255) for i in range(32))

        eng, hx, words = print_phrase(raw, indent)

        print(f'## Seed {n+10:X}  ({n+1} of {count})\n')
        print('\n'.join(eng))
        print(f'\n{indent}{n+10:X} = {hx}\n\n')

        digits.append(hx)

    print('## Calculation (XOR each hex digit)\n')
    for n in range(count):
        print(f'{indent}{n+10:X} = {digits[n]}')

    xor = ''
    for pos in range(len(digits[0]) - 2):
        if digits[0][pos] == ' ':
            xor += ' '
            continue

        here = 0
        for n in range(count):
            here ^= int(digits[n][pos], 16)
        assert 0 <= here < 16, here
        xor += '%X' % here

    xor += 'xx'

    lst = list(range(0, 100, 16)) + [23*4]
    align = ''.join(('|' if n in lst else ' ') for n in range(len(xor)))
    print(f'{indent}    {align}')

    print(f'{indent[2:]}XOR = {xor}')


    print('\n\n## Resulting Seed Phrase\n')
    rw = [int(i, 16) for i in xor.split(' ')[:-1]]

    eng, hx, _ = print_phrase(rw, indent)
    print('\n'.join(eng))
    chk = int(xor.split(' ')[-1][0], 16) * 0x100
    print(f'\n{indent}final word between: %s [%03X] - %s [%03X]' % (
            wordlist[chk], chk, wordlist[chk+0xff], chk+0xff))

    secret, final = calc_check(rw + [chk])
    print(f'{indent}correct final word: %s [%03X]' % (wordlist[final], final))

    # check our checksum math
    _, chk_hx, _ = print_phrase(secret, indent)
    assert chk_hx.split(' ')[-1] == '%03X'%final 

    print('''\
- It's not possible to calculate the checksum of the final seed phrase on paper (needs SHA256).
- But it must start with the indicated digit, and there will be only one
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
    worked_example()


