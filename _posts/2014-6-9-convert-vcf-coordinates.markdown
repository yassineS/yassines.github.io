---
title:  "Convert VCF file's Variants Coordinates"
date:   2014-06-09 
description: How to convert the genomic coordinates of a VCF file
---

You've all faced the case where you downloaded from the 1000 Genome Project, TCGA or got from a colleague a VCF file with coordinates from a different reference genome than the one you are using.

This could represent an issue especially if you are building a database, comparing variants or using [GATK](https://www.broadinstitute.org/gatk/).

link:https://github.com/yassineS/VCF-RefChange[VCF-RefChange] is a Pyhton script solve the problem of the conversion of a vcf variants coordinates from one reference genome version to another.

It relies on the output of [NCBI's BLAST](http://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastSearch&PROG_DEF=blastn&BLAST_PROG_DEF=megaBlast&BLAST_SPEC=blast2seq), it works better with small sequences (ie. human mithochondrial dna).

If you'd like to use the script with larger files (Whole exome or genome), we reccomend that you split the vcf file by chromosome or smaller chuncks.
