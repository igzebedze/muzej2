# originalna verzija by @avian. natisne nalepke od-do iz ukazne vrstice

# coding=utf8
import os.path
import subprocess
import sys
from tempfile import NamedTemporaryFile

def write_label(outf, invst):

	url = "http://racunalniski-muzej.si/i/%d" % invst
	ps = """9 8 moveto (%(url)s) (eclevel=L width=0.6 height=0.6) /qrcode /uk.co.terryburton.bwipp findresource exec
newpath
ISOArial 8 scalefont setfont
60.000000 44.000000 moveto
(ra) show
/ccaron glyphshow
(unalni) show
/scaron glyphshow
(ki) show
ISOArial 10 scalefont setfont
60.000000 34.000000 moveto
(muzej) show
ISOArial 8 scalefont setfont
60.000000 9.000000 moveto
(inv. ) show
/scaron glyphshow
(t. %(invst)04d) show
stroke
BREAK
""" % {'invst': invst, 'url': url}

	outf.write(bytes(ps,'utf8'))

def main():
	if len(sys.argv) < 2:
		print ("UPORABA: python nalepke.py [od]-[do] [labelnation parametri]")
		return

	od, do = map(int, sys.argv[1].split("-"))
	lnargs = sys.argv[2:]
	codefile = NamedTemporaryFile()

	for invst in range(od, do):
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
	outf.write(bytes(open(barcodepath).read(),'utf8'))
	outf.write(lnout.read())

main()
