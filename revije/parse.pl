#!/usr/bin/perl -w

use strict;
use JSON;
use MIME::Base64;
use REST::Client;

my $homedir = "pc.sux.org.nosync";
my $apikey = 'AIzaSyCHMMfTampPU4Jp9QxOcTtj7Pl1gVhRUl8';
$ENV{'PERL_LWP_SSL_VERIFY_HOSTNAME'} = 0;

# 1) for each jpg fetch json files 
# bash gvocr.sh test/sk19841003.jpg "AIzaSyCHMMfTampPU4Jp9QxOcTtj7Pl1gVhRUl8"

# 2) for each json generate hocr
# /usr/local/bin/gcv2hocr test/sk19841003.jpg.json test/sk19841003.hocr

my $count = 0;
my $existing = 0;
my %texts;

my @todo = sort readpipe("find $homedir -iname '*.jpg'");
foreach my $file (@todo) {
	chop $file;
#	warn "$count/".$#todo.': '.$file;

	my @path = split/\//,$file;
	my $edition = join("-",$path[1],$path[2],$path[3]);

	my $target = $file;
	$target =~ s/\.jpg//;
	
# skip if we already have it all
#	next if -f "./$target.hocr";

# google api limits us to 20M images and 10M requests
	if (-s "./$file" > 20000000) { 
		warn "\timage to large, skipping"; 
		next; 
	}
		
# fetch google api 
	if (!-f "./$file.json.gz") {
		warn ("\tfetching json");		
		my $json = &gocr("./$file");
		open (OUT, ">./$file.json");
		print OUT $json;
		close OUT;
		system("gzip './$file.json'");
	} else { 
		#warn "\tjson exists, skipping"; 
		$existing++;
	}

# check if json contains description
#	my $json = readpipe("head './$file.json'");
#	if ($json =~ /"description": "(.*?)",\n/) {
#		my $description = $1;
#		push (@{$texts{$edition}}, $description);
# todo: save page description

#	} elsif ($json) {
#		warn "\tcorupt json - no description, deleting";
#		#system("rm ./$file.json");
#	} else { warn "\tno json found"; }	
	
# generate hocr by calling external script
	if (-f "./$file.json.gz") { 
		if (!-f "./$target.hocr") {
			warn "$count/".$#todo.': '.$file;
			warn ("\tgenerating hocr");
			system ("gunzip -c './$file.json.gz' | python3 gcv2hocr2.py - > './$target.hocr'");
		} else { 
			#warn "\thocr exists, skipping"; $existing++; 
		}
	} else { 
		warn "\tno json, skipping"; 
	}

	# fix blank hocr	
	if (-f "./$target.hocr" and -s "./$target.hocr" < 100) { 
		#system("rm ./$target.hocr"); warn "\tremoved empty hocr"; 
		
		# get width and height of the image
		my $info = readpipe("identify $file");
		if ($info =~ /(\d+)x(\d+)/) {
			my $height = $2;
			my $width = $1;

		# open empty.hocr
			my $empty = readpipe("cat empty.hocr");

		# replace macro
			$empty =~ s/<WIDTH>/$width/g;			
			$empty =~ s/<HEIGHT>/$height/g;			

		# save in place of original
			open (HOCR, ">./$target.hocr");
			print HOCR $empty;
			close HOCR;
		}
	}
	
	$count++;
}

# print full texts of all editions (only did this once)
#foreach my $edition (keys(%texts)) {
#	open (E, ">texts/$edition.txt");
#	print E join(" ", @{$texts{$edition}});
#	close E;
#}

sub gocr {
	my ($file) = @_;
	
	use constant API_KEY => 'AIzaSyCHMMfTampPU4Jp9QxOcTtj7Pl1gVhRUl8';
	use constant URL => "https://vision.googleapis.com/v1/images:annotate?key=";
	
	my $request_url = URL.API_KEY;
	my $client = new REST::Client();
	my $json = new JSON();
	
	my $png;
	{    local $/ = undef;
	     open(PNG, $file) or die "Could not open the file: $!";
	     binmode PNG;
	     $png = <PNG>;
	     close(PNG);
	     $png = encode_base64($png);    
	}
	
	my %request;
	$request{requests} = [
	    {image => {content => $png},
	    features => [{type =>  "DOCUMENT_TEXT_DETECTION"}]}
	];
	
	my $json_text = $json->encode(\%request);
	
	$client->POST($request_url, $json_text);
	
	##
	# resonse code is in $client->responseCode();
	# respose content is in $client->responseContent();
	##	
	
	return $client->responseContent();
}