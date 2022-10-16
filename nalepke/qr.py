# nova verzija by @igzebedze, natisne nalepke po stevilkah iz datoteke

# coding=utf8
import os.path
import subprocess
import sys
from tempfile import NamedTemporaryFile

def write_label(outf, invst):

	url = "https://qr.muzej.si/%s" % invst

	ps = b"9 8 moveto (%(url)s) (eclevel=L width=0.6 height=0.6) /qrcode /uk.co.terryburton.bwipp findresource exec BREAK" % {b'url': url.encode('utf-8')}

	outf.write(ps)

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
	outf.write(open(barcodepath).read())
	outf.write(lnout.read())

main()
