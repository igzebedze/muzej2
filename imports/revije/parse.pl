#!/usr/bin/perl -w

use strict;
use JSON;

my @outputA;
my @outputB;

my $i = 0;
my $pk = 364;	# first available ID for Eksponat
my $ppk = 10000;	# first available ID for Primerek
my $catid = 10; # id of the category for Eksponat (production: 20)
my $userid = 5;	# user who created entries

my %revije;
my %deeplinks;
my %eksponati;
# my @eksponati;

# Moj mikro,junij 1984,2015,,http://pc.sux.org/indexMMSlo.html,https://plus.si.cobiss.net/opac7/bib/86807,,http://retrospec.sgn.net/users/tomcat/yu/magshow.php?all=MMS_84_06,http://pc.sux.org/phpgraphy/index.php?previewpic=MMS/1984/06/MMS_84_06_001.jpg

# first load list of eksponati and remember metadata

my $count = -1;	#skip header row
foreach my $line (readpipe("cat eksponati.csv")) {
	chop $line;
	my @line = split/,/,$line;
	
	$count++;
	next if not $count;
	
	$deeplinks{$line[0]} = $line[7];
		
	my %eksponat = (
		"model", "inventura.eksponat",
		"fields", {
			"ime", $line[0],
			"uradnastran", $line[3],
			"oldcomputers", $line[4],
			"vir", $line[5],	
			"visina_cm", 1,
			"sirina_cm", 20,
			"dolzina_cm", 30,
			"kategorija_id", $catid,
			"created_at", "2019-12-01 01:27:18.059691",
			"updated_at", "2019-12-01 01:27:18.059691",
		}
	);

	#push(@output, \%eksponat);
	$eksponati{$line[0]} = \%eksponat;
} 

#my $json_text = JSON->new->utf8->encode(\@eksponati);
#print $json_text."\n";

# then go through primerki and generate output, adding eksponat when needed

$count = -1;
foreach my $line (readpipe("cat primerki.csv")) {
	$count++;
	next if not $count;	# skip header row

	chop $line;
	my @line = split/,/,$line;	
	next if not $line[0];	# skip empty rows
	
	my $name = shift @line;
	my $year = int shift @line;
	$year = undef if not $year;
	
	my $deeplink = "";
	if ($deeplinks{$name} =~ /tomcat/) {
		my $d = $deeplinks{$name};
		my $y = substr $year, -2, 2;
		$deeplink = $d;
		$deeplink =~ s/\d\d_\d\d/$y/;
	}
	
	for (my $mon = 1; $mon <= 12; $mon++) {
		if ($line[$mon]) {
			my $d = $deeplink;
			my $m = sprintf '%02d', $mon;
			$d .= "_".$m if $d;
			
			my %primerek = (
				"id", $ppk,
				"model", "inventura.primerek",
				"fields", {
					"eksponat_id", &get_or_create_eksponat($name),
					"inventarna_st", $ppk,
					"leto_proizvodnje", $year,
					"inventariziral_id", $userid,
					"polica", "F3",
					"serijska_st", "$year-$mon",
					"datum_inventarizacije", "2019-12-01 01:27:18.059691",
					"created_at", "2019-12-01 01:27:18.059691",
					"updated_at", "2019-12-01 01:27:18.059691",
				}
			);
			
			$primerek{"fields"}{"zgodovina"} = "<a href='$d'>$d</a>" if $d;
			
			push (@outputB, \%primerek);
			$ppk++;
			$i++;
		}	
	}
}


my $json_text = JSON->new->utf8->pretty->encode(\@outputA);
open (A, "> eksponati.json");
print A $json_text;
close A;

$json_text = JSON->new->utf8->pretty->encode(\@outputB);
open (B, "> primerki.json");
print B $json_text;
close B;

#print $json_text."\n";
warn "\n".$i." objects created";

sub get_or_create_eksponat {
	my ($name) = @_;
	if ($revije{$name}) {
		return $revije{$name};
	} elsif ($name) {
		$pk++;
		$revije{$name} = $pk;
		$eksponati{$name}{"id"} = $pk;
		#warn "'$name' : $pk";
		push (@outputA, $eksponati{$name});
		$i++;
		return $pk;
	} else {
		warn "something's wrong"	
	}
}
