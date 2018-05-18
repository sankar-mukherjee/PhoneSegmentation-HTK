#!/usr/local/bin/perl

$old_file = './HMM/hmm4/hmmdefs';	

open (INFILE, $old_file);

# Copy the lines into array @copy
my $startCopying = 0;
my @copy = ();
while (<INFILE>) {
   chomp $_; # removes \n chars from end of lines

   if ($_ eq '~h "sil"') {
      $startCopying = 1;
   }
   elsif ($_ eq '<ENDHMM>') {
      $startCopying = 0;
   }

   push (@copy, $_) if $startCopying;
}

close (INFILE);

open (OUTFILE, ">M");
print OUTFILE join ("\n",@copy);
close (OUTFILE);

open (INFILE, "M");
my $startCopying = 0;
my @copy1 = ();
while(<INFILE>){
chomp $_; # removes \n chars from end of lines

   if ($_ eq '<STATE> 3') {
      $startCopying = 1;
   }
   elsif ($_ eq '<STATE> 4') {
      $startCopying = 0;
   }
	push (@copy1, $_) if $startCopying;
}
close (INFILE);

shift(@copy1);

open (OUTFILE, ">>$old_file");
print OUTFILE '~h "sp"';
print OUTFILE "\n<BEGINHMM>\n<NUMSTATES> 3\n";
print OUTFILE "<STATE> 2\n";
print OUTFILE join ("\n",@copy1);
print OUTFILE "\n<TRANSP> 3\n";
print OUTFILE " 0.0 0.7 0.3\n";
print OUTFILE " 0.0 0.6 0.4\n";
print OUTFILE " 0.0 0.0 0.0\n";
print OUTFILE "<ENDHMM>\n";
close (OUTFILE);

unlink 'M';
