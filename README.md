# **16S ONT GUI workflow using EMU and KRONA**

A simple GUI python script for analyzing full-length 16S Oxford Nanopore (fastq) reads. Created for Ubuntu OS. Require creating a Conda environment for EMU and KRONA combined. The _--threads_ settings for running EMU is set to 20, if having a less powerful computer decrease this definition in script (line 32) to satisfy your computer hardware.

## Installation:

In Terminal:

```
conda create -n emukrona emu krona
```

If this doesnt work, use mamba:

```
mamba create -n emukrona emu krona
```

Log into Conda environment:

```
conda activate emukrona
```

Update Krona Taxonomy_db:

```
./ updateTaxonomy.sh
```

Download script from this site _cat_emu_krona.py_ and run while _emukrona_ conda environment is activated:

```
python3 cat_emu_krona.py
```

![catbird2](https://github.com/user-attachments/assets/2fdec70a-640e-4f46-84bd-2101f99cc167)

## **Usage:**

This GUI should pop up (probably without the Nanopore image) when running _cat_emu_krona.py_. _#Note_ If Barcodes have been applied in the same ONT sequencing run, the procedure described bellow must performed individually for each Barcode.

![Screenshot from 2025-07-04 11-51-38](https://github.com/user-attachments/assets/ef481fa0-9b5b-4865-a9ee-6351641db740)

1. Concatenate your *.fastq.gz files by pressing yellow button. Browse and define your folder of interest, press OK. This will generate one file called _allfiles.fastq.gz_ in the same folder

2. In main GUI window select the newly created allfiles.fastq.gz as Input FASTQ File

3. Create an output folder where suitable and define this as Output Directory in GUI

4. Press green button Run Pipeline

5. If using Firefox browser the Krona plot will automatically pop up when run is finished. Otherwise all results will be put in _Output Directory_ including Krona.html plot, a .tsv file containing estimated read counts for each species, a .sam file and .txt file
