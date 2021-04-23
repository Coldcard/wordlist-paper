# Failed attempt at using HTML to show a table.
#
# - do not use
# - particularly bad because ultimately we need this printed on paper
# - don't be distracted by how close I got
#

def worksheet(count=5):
    with open('worksheet.html', 'wt') as fd:
        P = lambda *a: print(*a, file=fd)

        P('''
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/purecss@2.0.5/build/pure-min.css">
<style>
td { text-align: center; }
td.R { text-align: right; }
td.L { text-align: left; }
#bb {
    transform: rotate(90deg) translate(33%, 0%);
}
</style>
<body>
<div id="bb" class="pure-g">
<div class="pure-u-1">
''')


        P('<h2>XOR Seed Worksheet</h2>\n')
        
        P('<table class="pure-table pure-table-bordered"><tbody>')
        for c in range(count):
            dig = chr(65+c)
            P(f'<tr class="pure-table-odd"><td rowspan=3>{dig}<td class=R>Word #' + ''.join(f'<td colspan=3>{n+1}' for n in range(24)))
            P('<tr><td class=R>Word' + ''.join(f'<td colspan=3>' for n in range(24)))
            P('<tr><td class=R>Hex&nbsp;Digit' + ''.join(f'<td> ' for n in range(24*3)))
            if c:
                if c == 1:
                    here = 'A'
                elif c > 2:
                    here = '...'
                else:
                    here = '(' + '&oplus;'.join('%X' % (z+10-1) for z in range(1, c+1)) + ')'
                P(f'<tr><td colspan=2 class=R>{here}&oplus;{dig}' 
                        + ''.join(f'<td> ' for n in range((24*3)-2)) + '<td>X<td>X')
            if c in {2, 5}:
                if c == 2:
                    m = 'sane people stop here'
                else:
                    m = 'please stop, this hurts'
                P(f'<tr class="pure-table-odd"><td colspan=2><td colspan=99 class=L><em>{m}</em>')

        P('</table>')

worksheet()

