# 16S-ONT-GUI-workflow-using-EMU-and-KRONA
#16S Oxford Nanopore GUI workflow using EMU and KRONA

#A simple GUI python script for analyzing 16S Oxford Nanopore (fastq) reads. Require creating a Conda environment for EMU and KRONA combined.

#In Terminal:

#ffffff conda create -n emukrona emu krona

#if this doesnt work, use mamba:

mamba create -n emukrona emu krona

#log into Conda environment:

conda activate emukrona

#Update Krona Taxonomy_db:

updateTaxonomy.sh

#Download script from this site cat_emu_krona.py and run while emukrona conda environment is activated:

python3 cat_emu_krona.py
