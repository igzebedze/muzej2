#!/usr/bin/perl -w

use strict;
my $homedir = "pc.sux.org.nosync";

# 3) for each magazine generate pdf
# /usr/local/bin/hocr-pdf test > test/test.pdf

# 4) prepare metadata for library
# - year-month
# - page 1 text (cover)
# - page 3 text (editorial)
 
foreach my $magazine (readpipe("ls -1 $homedir")) {
	chop $magazine;
	
	next if $magazine =~ /joker/i;
		
	foreach my $year (readpipe("ls -1 $homedir/$magazine")) {
		chop $year;

		if ($year =~ /\d\d\d\d/ ) {
			foreach my $month (readpipe("ls -1 $homedir/$magazine/$year")) {
				chop $month;
				my $path = "$magazine/$year/$month";
				my $name = "$magazine-$year-$month";
				&process($path, $name);
			}
		} else {
			my $path = "$magazine/$year";
			my $name = "$magazine-$year";
			&process($path, $name);
		}
	}
}

sub process {
	my ($path, $name) = @_;
	
# count if we have hocr for every jpeg
	my @hocrs = readpipe("ls -1 ./$homedir/$path/*.hocr");
	my @jpegs = readpipe("ls -1 ./$homedir/$path/*.jpg");
	if ($#hocrs != $#jpegs) {
		warn "\terror: checksum failed on ./$homedir/$path/";
		next;
	}
			
# process hocr-pdf --savefile out.pdf <imgdir>
	if (!-f "results/$name.pdf" or !-s "results/name.pdf") {
		#system("mogrify './$homedir/$magazine/$year/$month/*.jpg' -sampling-factor 4:2:0 -strip -quality 75 -interlace Plane -define jpeg:dct-method=float -colorspace RGB"); # - didn't yield much size savings
		system("python3 hocr-pdf.py --savefile 'results/$name.pdf' './$homedir/$path'");
	} else { 
		#warn "\tpdf exists, skipping";  
	}
}