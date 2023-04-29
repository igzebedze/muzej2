#!/usr/bin/perl -w

use strict;
use Cwd;
my @dir = split("/",&cwd);

print join("\t", 'pdf', 'cover', 'pages', 'dir')."\n";
foreach my $pdf (readpipe("ls *.pdf")) {
    chop $pdf;	
    my ($name, $ending) = split/\./,$pdf;
    my @files = readpipe("ls $name/*.jpg");
    my $cover = shift @files;
    chop $cover;
    print join("\t", $pdf, $cover, $#files+2, $dir[-1])."\n"
}