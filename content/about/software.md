---
title: Software
weight: 8
# layout: docs
sidebar:
  open: true
---

A selection of open-source software I have led, contributed to, or co-released alongside collaborators.

## PolyLinkR

Prototype R package for gene-based pathway enrichment analysis, with explicit support for linkage disequilibrium between adjacent loci within pathways. Useful as evidence for polygenic selection when paired with selection-scan output (e.g. SweepFinder2). A modern and more efficient successor is in development by Raymond Tobler.

**Code:** [github.com/ACAD-UofA/PolyLink](https://github.com/ACAD-UofA/PolyLink)
**Preprint:** [arxiv.org/abs/2004.03224](https://arxiv.org/abs/2004.03224)

## taxonomicfiltering

Workflow that uses Kraken2 metagenomic classification to filter contaminating sequences *before* mapping in ancient DNA pipelines. Up to ~94% reduction in mapping runtime with negligible loss of endogenous data; usable on personal machines. Released alongside Ravishankar et al., *Briefings in Bioinformatics* 26, bbae646 (2024).

**Code:** [github.com/shyama-mama/taxonomicfiltering](https://github.com/shyama-mama/taxonomicfiltering)

## cellular-constraint

Analysis code for the conserved facultative heterochromatin study identifying disease regulatory sequences. Released alongside Sinniah et al., *Nucleic Acids Research* 53(20) (2025).

**Code:** [github.com/enakshi-sinniah/cellular-constraint](https://github.com/enakshi-sinniah/cellular-constraint)

## Adelaide Open Food Map

Interactive ML-driven map of Adelaide eateries that ranks "underrated" venues by combining Google Maps ratings with review counts. A side project, building on initial work by Lauren Leek.

**Live tool:** [ysouilmi.com/adelaide_open_food_map](https://www.ysouilmi.com/adelaide_open_food_map/)
**Code:** [github.com/yassineS/adelaide_open_food_map](https://github.com/yassineS/adelaide_open_food_map)

## COSMOS

{{< callout emoji="⚠︎" >}}
This project is no longer actively maintained. For new pipeline work I recommend [Nextflow](https://www.nextflow.io/).
{{< /callout >}}

COSMOS is a Python library for building scientific pipelines that run on distributed computing clusters. It was originally designed for bioinformatics workflows but is general enough for any DAG-based distributed work, including image processing. The API uses plain Python rather than a domain-specific language, which I still consider a strength.

COSMOS was first published as an Application Note in [*Bioinformatics*](http://bioinformatics.oxfordjournals.org/content/early/2014/06/29/bioinformatics.btu385). Since then it has been re-written and open-sourced through a collaboration between The Lab for Personalized Medicine at Harvard Medical School, the [Wall Lab at Stanford University](https://wall-lab.stanford.edu/), and [Invitae](http://invitae.com/), where it ran in production processing hundreds of thousands of clinical samples.

**Code:** [github.com/Mizzou-CBMI/COSMOS2](https://github.com/Mizzou-CBMI/COSMOS2)
**Documentation:** [mizzou-cbmi.github.io/COSMOS2](https://mizzou-cbmi.github.io/COSMOS2/)

### Pipelines built on COSMOS

- **GenomeKey** — GATK best-practices variant calling pipeline.
- **PV-Key** — somatic tumour/normal variant calling pipeline.
- **MC-Key** — multi-cloud implementation of GenomeKey.
