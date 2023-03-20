# print a large worksheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.enums import *
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from mnemonic import Mnemonic
wordlist = Mnemonic('english').wordlist

styleSheet = getSampleStyleSheet()

labelStyle = ParagraphStyle('llab', fontFace='courier', alignment=TA_RIGHT)
labelStyleCenter = ParagraphStyle('tlab', fontFace='courier', alignment=TA_CENTER)

commentStyle = ParagraphStyle('com', alignment=TA_CENTER)

hex_style = ParagraphStyle('tlab', fontName='Courier-Bold', alignment=TA_LEFT, fontSize=6, spaceAfter=2, spaceBefore=0, leading=4)
word_style = ParagraphStyle('cell', alignment=TA_CENTER, fontSize=8, spaceBefore=0, spaceAfter=0, leading=8)

def cell(w):
    assert 0 <= w < 0x800
    word = wordlist[w]
    hex = ('%03x' % w).upper()

    #rv = Paragraph(f'{word}\n<br/><font face="courier">{hex}</font>', cellStyle)
    rv = []
    rv.append(Paragraph(hex, hex_style))
    rv.append(Paragraph(word, word_style))

    return rv

def left_label(x):
    return Paragraph(x, labelStyle)
def top_label(x):
    return Paragraph(x, labelStyleCenter)

def doit(fname='worksheet.pdf', word_length=24):
    doc = SimpleDocTemplate(fname, pagesize=landscape(letter))

    doc.leftMargin = doc.rightMargin =  \
    doc.topMargin = doc.bottomMargin = 0.1 * inch

    # container for the 'Flowable' objects
    data = []
    blanks = ['' for _ in range(word_length*3)]
    for part in 'ABCD':
        row = [part, 'Word #']
        for i in range(word_length):
            row.append(str(i+1))
            row.append('')
            row.append('')

        data.append(row)
        data.append(['', 'Word'] + blanks)
        data.append(['', 'Hex Digit'] + blanks)

        if part != 'A':
            if part == 'B':
                xor = 'A⊕B'
            elif part == 'C':
                xor = '(A⊕B)⊕C'
            else:
                xor = '...⊕' + part
            if word_length == 24:
                data.append([xor, ''] + blanks[:-2] + ['X', 'X'])
            elif word_length == 12:
                data.append([xor, ''] + blanks[:-1] + ['X'])
            else:
                data.append([xor, ''] + blanks)

    conf = [
        #('BACKGROUND',(1,1),(-2,-2),colors.green),
        #('TEXTCOLOR',(0,0),(0,-1),colors.red),
        ('VALIGN', (0,0),(0,-1), 'MIDDLE'),
        #('ALIGN', (0,0),(0,-1), 'RIGHT'),
        ('ALIGN', (0,0),(0,1), 'CENTER'),
        ('ALIGN', (1,0),(2,-1), 'RIGHT'),
        ('ALIGN', (2,0),(-1,-1), 'CENTER'),
        ('VALIGN', (0,0),(0,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0),(-1,-1), 2),
        ('RIGHTPADDING', (0,0),(-1,-1), 2),
        #('TOPPADDING', (0,0),(-1,-1), 0),
        #('BOTTOMPADDING', (0,0),(-1,-1), 4.25),
        ('GRID', (0,0),(-1,-1), 0.5, colors.grey),
        ('LINEBEFORE', (2,0), (2, -1), 1.0, colors.grey),
    ]
    for y in [0, 3, 3+4, 3+4+4]:
        conf.extend([
            ('SPAN', (0,y), (0, y+2)),
            ('BACKGROUND', (0,y), (0, y+2), colors.lightgrey),
            ('LINEABOVE', (0,y), (-1, y), 1.0, colors.grey),
        ])
        if y:
            conf.extend([
                ('SPAN', (0,y+3), (1, y+3)),
                ('ALIGN', (0,y+3),(1,y+3), 'RIGHT'),
                ('LINEABOVE', (0,y+3), (-1, y+3), 1.0, colors.grey),
            ])

        for x in range(word_length):
            pos = 2 + (x*3)
            conf.extend([
                ('SPAN', (pos,y), (pos+2, y)),
                ('SPAN', (pos,y+1), (pos+2, y+1)),
            ])

    for x in range(3, word_length*3, 6):
        conf.extend([
            ('BACKGROUND', (2+x,0), (2+x+2, -1), colors.lightgrey),
        ])



    W1 = 10
    W2 = W1 + 2
    t = Table(data, repeatRows=0, colWidths=[W2, None]+[W1 for _ in range(word_length*3)])
    t.setStyle(TableStyle(conf))

    seed_samples = [[cell(w) for w in 
            sorted(list(range(0, 0x800, 0x100)) + [0, 1, 2, 3, 0x7fd, 0x7fe, 0x7ff])]]

    t2 = Table(seed_samples, colWidths=50)
    t2.setStyle(TableStyle([
        ('LEFTPADDING', (0,0),(-1,-1), 2),
        ('RIGHTPADDING', (0,0),(-1,-1), 2),
        ('TOPPADDING', (0,0),(-1,-1), 0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 4.25),
        ('GRID', (0,0),(-1,-1), 0.5, colors.grey),
        ]),
    )

    hex_table = [['⊕'] + ['%X'%i for i in range(16)]]
    for y in range(16):
        hex_table.append( ['%X'%y] + ['%X'%(x^y) for x in range(16)] )

    t3 = Table(hex_table, colWidths=None)
    t3s = TableStyle([
            ('ALIGN', (1,1),(-1,-1), 'CENTER'),
            ('ALIGN', (1,1),(-1,-1), 'RIGHT'),
            ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
            ('GRID', (0,0),(-1,-1), 0.5, colors.grey),
            ('FONT', (0,0), (-1, -1), 'Courier-Bold', 6),
            ('FONT', (1,1), (-1, -1), 'Courier', 6),
        ])
    for x in range(0, 16, 2):
        t3s.add('BACKGROUND', (2+x,0), (2+x, -1), colors.lightgrey)
    t3.setStyle(t3s)

    # page top-to-bottom
    elements = []
    elements.append(Paragraph(f'Seed XOR Worksheet — {word_length} Words',
        ParagraphStyle('tlab2', alignment=TA_LEFT, fontSize=16, spaceAfter=20, spaceBefore=20)))
    elements.append(t)

    elements.append(Spacer(0, 20))
    elements.append(t3)

    if 1:
        elements.append(Paragraph('IMPORTANT: After use, burn with fire!', 
            ParagraphStyle('tlab', alignment=TA_LEFT, fontSize=8, spaceAfter=2, spaceBefore=4)))


    if 0:
        elements.append(Spacer(0, 10))
        elements.append(t2)

    doc.build(elements)

doit("worksheet12.pdf", 12)
doit("worksheet.pdf", 24)
