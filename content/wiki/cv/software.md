---
title: Software
layout: docs
---

## PolyLinkr


## Containerisation 

## COSMOS
{{< callout emoji="⚠︎" >}}
  The project is no longer maintained. I recommend using [Nextflow](https://www.nextflow.io/) for your bioinformatics pipelines.
{{< /callout >}}

Cosmos is a python library for creating scientific pipelines that run on a distributed computing cluster. It is primarily designed and used for bioinformatics pipelines, but is general enough for any type of distributed computing workflow and is also used in fields such as image processing. Cosmos provides a simple api to specify any job DAG using simple python code making it extremely flexible and inuitive - you do not specify your DAG using json, CWL, groovy, or some other domain specific language.

![](https://raw.githubusercontent.com/Mizzou-CBMI/COSMOS2/master/docs/source/_static/imgs/web_interface.png)

Cosmos was published as an Application Note in the journal [Bioinformatics](http://bioinformatics.oxfordjournals.org/), but has evolved a lot since its original inception. If you use Cosmos for research, please cite its [manuscript](http://bioinformatics.oxfordjournals.org/content/early/2014/06/29/bioinformatics.btu385).

Since the original publication, it has been re-written and open-sourced by the original author, in a collaboration between The Lab for Personalized Medicine at Harvard Medical School, the [Wall Lab at Stanford University](https://wall-lab.stanford.edu/), and [Invitae](http://invitae.com/). Invitae is a leading clinical genetic sequencing diagnostics laboratory where Cosmos is deployed in production and has processed hundreds of thousands of samples. It is also used by various research groups around the world; if you use it for cool stuff please let us know!

### Features
- Simple API for job DAG specification
- Flexibility for various workflows
- Suitable for bioinformatics and image processing

**Code**: https://github.com/Mizzou-CBMI/COSMOS2?tab=readme-ov-file
**Documentation**: https://mizzou-cbmi.github.io/COSMOS2/

### Pipelines
Alongside the library, the team has built a number of bioinformatics pipelines using the library. These include:
- GenomeKey - A GATK best practices variant calling pipeline.
- PV-Key - Somatic Tumor/normal variant calling pipeline.
- MC-Key - Multi-cloud implementation of GenomeKey
