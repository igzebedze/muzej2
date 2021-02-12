#!/usr/bin/perl -w

use strict;
my $homedir = "pc.sux.org.nosync";

foreach my $file (sort readpipe("find $homedir -iname '*.gif'")) {
	chop $file;
	warn $file;
	my $target = $file;
	$target =~ s/\.gif//;
	system("convert '$file' '$target.jpg'") if not -f "$target.jpg"; 
}