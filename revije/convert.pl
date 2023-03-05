#!/usr/bin/perl -w

use strict;
my $homedir = "pc.sux.org.nosync";

# convert -density 300 file.pdf[0] -resize 80x80 -background white -alpha remove -strip -quality 70 thumb.jpg

foreach my $file (sort readpipe("find $homedir -name '*.gif'")) {
	chop $file;
	#warn $file;
	my $target = $file;
	$target =~ s/\.gif//;
	system("convert '$file' -background white -alpha remove '$target.jpg'") if not -f "$target.jpg"; 
}

foreach my $file (sort readpipe("find $homedir -name '*.JPG'")) {
	chop $file;
	#warn $file;
	my $target = $file;
	$target =~ s/\.JPG//;
	system("mv '$file' '$target.jpg'") if not -f "$target.jpg"; 
}

foreach my $file (sort readpipe("find $homedir -name '*.jpg.jpg'")) {
	chop $file;
	#warn $file;
	my $target = $file;
	$target =~ s/\.jpg//g;
	system("mv '$file' '$target.jpg'") if not -f "$target.jpg"; 
}
