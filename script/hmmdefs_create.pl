#!/usr/local/bin/perl
# sankar Mukherjee
$old_file = './HMM/hmm0/proto';	$old_m_file = './HMM/hmm0/vFloors';	$phoneme_file = './HMM/hmm0/hmmdefs';	$macro_file = './HMM/hmm0/macros';
    
$x = './monophones0';
open(FILE, $x) || die("Could not open file!");
@lines = <FILE>;
close (FILE);

open(FILE, $old_file) || die("Could not open file!");
@ll = <FILE>;
close (FILE);

open(FILE, "$old_m_file") || die("Could not open file!");
@mm = <FILE>;
close (FILE);

open(FILE, ">$macro_file") || die("Could not open file!");
print FILE $ll[0];
print FILE $ll[1];
print FILE $ll[2];
print FILE @mm;
close (FILE);

shift(@ll);shift(@ll);shift(@ll);

if (-e $phoneme_file) {
 unlink $phoneme_file;
 } 
open (LAB,">>$phoneme_file");
foreach $lines (@lines){
chomp $lines;
			foreach $ll(@ll){
				$lll = $ll;
				$lll =~ s/proto/$lines/g;
				print LAB $lll;		
				}		
	}
close (LAB);
