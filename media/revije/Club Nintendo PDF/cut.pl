#!/usr/bin/perl -w

use strict;

# BIT-1984-09.pdf
foreach my $pdf (readpipe("ls *.pdf")) {
    chop $pdf;
    my ($name, $ending) = split/\./,$pdf;
    system ("mkdir $name") if !-d $name; 
    system ("convert -density 150 $pdf -quality 90 $name/0%07d.jpg");
}

#print join("\t", 'pdf', 'cover', 'pages')."\n";
#foreach my $pdf (readpipe("ls *.pdf")) {
#    chop $pdf;	
#    my ($name, $ending) = split/\./,$pdf;
#    my @files = readpipe("ls $name/*.jpg");
#    my $cover = shift @files;
#    chop $cover;
#    print join("\t", $pdf, $cover, $#files+2)."\n"
#}