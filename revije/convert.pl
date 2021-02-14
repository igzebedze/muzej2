#!/usr/bin/perl -w

use strict;
my $homedir = "pc.sux.org.nosync";

foreach my $file (sort readpipe("find $homedir -name '*.gif'")) {
	chop $file;
	#warn $file;
	my $target = $file;
	$target =~ s/\.gif//;
	system("convert '$file' '$target.jpg'") if not -f "$target.jpg"; 
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
