# nova verzija by @igzebedze, natisne nalepke po stevilkah iz datoteke

# coding=utf8
import os.path
import subprocess
import sys
from tempfile import NamedTemporaryFile

def write_label(outf, invst):

	url = "http://racunalniski-muzej.si/i/%s" % invst

	ps = """9 8 moveto (%(url)s) (eclevel=L width=0.6 height=0.6) /qrcode /uk.co.terryburton.bwipp findresource exec
newpath
ISOArial 8 scalefont setfont
60.000000 44.000000 moveto
(ra) show
/ccaron glyphshow
(unalni) show
/scaron glyphshow
(ki) show
ISOArialBold 10 scalefont setfont
60.000000 34.000000 moveto
(muzej) show
ISOArial 8 scalefont setfont
60.000000 9.000000 moveto
(inv. ) show
/scaron glyphshow
(t. %(invst)s) show
stroke
BREAK
""" % {'invst': invst, 'url': url}

	outf.write(ps)

def main():
	if len(sys.argv) < 2:
		print "UPORABA: python nalepke.py seznam.txt [labelnation parametri]"
		return

	seznam = sys.argv[1]
	lnargs = sys.argv[2:]
	codefile = NamedTemporaryFile()

	file = open(seznam, 'r')
	data = file.readlines()
	for invst in data:
		invst = invst.rstrip("\n")
		write_label(codefile, invst)

	codefile.flush()

	lnpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "labelnation"))
	lnout = NamedTemporaryFile()

	subprocess.call([lnpath, 
		'-d', 'BREAK',
		'-c', '-i', codefile.name,
		'-o', lnout.name] + lnargs)

	outf = open("nalepke.ps", "wb")

	barcodepath = os.path.join(os.path.dirname(__file__), "barcode.ps")
	outf.write(open(barcodepath).read())
	outf.write(lnout.read())

main()
