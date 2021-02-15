#!/usr/bin/perl -w

use strict;

# generate csv for importing into inventory system

# go through directory of pdfs
# separate books
# separate those with years
# identify existing magazines and dont import duplicates, connect with hardcopy
# get or create eksponat

# generate: 
#	eksponat = folder name
#	serijska = year-month
#	leto = year
#	stanje = text
#	zgodovina = 'pc.sux.net bulk import'
#	fotografije = webhome/image.pdf

# todo: cover image upload

my $homedir = "http://revije.muzej.si";
my $donedir = "results.nosync";

print join("\t", 'eksponat', 'vrsta', 'serijska', 'leto', 'fotografije')."\n";
foreach my $pdf (readpipe("find $donedir -iname '*.pdf'")) {
	chop $pdf;
	
	my ($root, $what, $which) = split/\//,$pdf;
	$which =~ s/\.pdf//;
	my @which = split/-/,$which;
	# todo: how to add text of first page?

	my $file = join('/', $homedir, $what, $which).".pdf";	
	my $type = 'Revija';
	my $serial = '';
	my $year = '';
	
	next if $which eq 'Joker';	# these were imported previously
	
	if ($what eq 'Knjige') {
		$serial = $which;
		$type= 'Knjiga';
	}
	
	if ($which[1] =~ /(\d{4})/) {
		$year = $which[1];
		my $month = $which[2];
		$serial = join('-',$year, $month);
		
	} else {
		$serial = $which[1];
		
	}
	
	print join("\t", $what, $type, $serial, $year, $file)."\n";
}
