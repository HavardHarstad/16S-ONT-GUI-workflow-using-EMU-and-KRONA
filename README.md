# **16S-ONT-GUI-workflow-using-EMU-and-KRONA**

A simple GUI python script for analyzing 16S Oxford Nanopore (fastq) reads. Require creating a Conda environment for EMU and KRONA combined.

In Terminal:

> conda create -n emukrona emu krona

If this doesnt work, use mamba:

> mamba create -n emukrona emu krona

Log into Conda environment:

> conda activate emukrona

Update Krona Taxonomy_db:

> ./ updateTaxonomy.sh

Download script from this site _cat_emu_krona.py_ and run while emukrona conda environment is activated:

> python3 cat_emu_krona.py

![catbird2](https://github.com/user-attachments/assets/2fdec70a-640e-4f46-84bd-2101f99cc167)

## **Usage:**

![Screenshot from 2025-07-04 11-51-38](https://github.com/user-attachments/assets/ef481fa0-9b5b-4865-a9ee-6351641db740)




n
