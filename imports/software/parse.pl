#!/usr/bin/perl -w

use strict;
use JSON;
use UTF8;

my %eksponati = (		# IDji ustreznih objektov v bazi, treba narest vnaprej
	'igra', 508,
	'operacijski sistem', 509,
	'programska oprema', 510,
	'izobraževalno', 511,
);

my $ppk = 20000;	# sw id's start from 20000
my $userid = 5;	# user who created entries

my @output;

# vrsta   proizvajalec    program verzija leto    stanje  OS      medij   avtor
my @headers;
foreach my $line (readpipe("cat boxes.tsv")) {
	chop $line;
	#$line =~ s/([\w']+)/\u\L$_/g;
	my @row = split/\t/,$line;
	
	if (not @headers) {
		@headers = @row;
		next;	
	}
	
	my $eksponat = $eksponati{$row[0]};
		warn "manjka eksponat" if not $eksponat;
	my $proizvajalec = $row[1];
	my $leto = int $row[4];
	
	# proizvajalec, program, verzija, OS
	my $primerek = ucfirst($row[1])." ".ucfirst($row[2]); 
	if ($row[3]) { $primerek .= " ".ucfirst($row[3]); }
	if ($row[6]) { $primerek .= " for ".uc($row[6]); } 
	
	my $stanje = $row[5]."\n".$row[7]; # stanje, medij
	my $avtor = $row[8];
	
	my %primerek = (
				"id", $ppk,
				"model", "inventura.primerek",
				"fields", {
					"eksponat_id", $eksponat,
					"inventarna_st", $ppk,
					"leto_proizvodnje", $leto,
					"inventariziral_id", $userid,
					"polica", "F3",
					"serijska_st", $primerek,
					"stanje", $stanje,
					"zgodovina", $avtor,
					"datum_inventarizacije", "2019-12-04 01:27:18.059691",
					"created_at", "2019-12-04 01:27:18.059691",
					"updated_at", "2019-12-04 01:27:18.059691",
				}
			);
			
	push (@output, \%primerek);
	$ppk++;
}


my $json_text = JSON->new->utf8->pretty->encode(\@output);
open (A, "> primerki.json");
print A $json_text;
close A;

