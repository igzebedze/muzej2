#!/usr/bin/perl -w

use strict;

foreach my $pdf (readpipe("ls *.pdf")) {
    chop $pdf;
    my ($name, $end) = split/\./,$pdf;
    foreach my $file (readpipe("ls $name/*.jpg")) {
        chop $file;
        my ($f, $e) = split/\./, $file;
        warn "tesseract $file $f -l slv";
#        next;
        system("tesseract $file $f -l slv");
    }
}