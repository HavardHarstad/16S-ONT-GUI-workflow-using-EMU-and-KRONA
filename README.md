# **16S ONT GUI workflow using EMU and KRONA**

A simple GUI python script for analyzing full-length 16S Oxford Nanopore (fastq) reads. Created for Ubuntu OS. Require creating a Conda environment for EMU and KRONA combined. The _--threads_ settings for running EMU is set to 20, if having a less powerful computer decrease this definition in script (line 32) to satisfy your computer hardware.

If not having Conda follow https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html before further installation.

## Installation:

In Terminal:

```
conda create -n emukrona emu krona
```

If this doesnt work, use mamba:

```
mamba create -n emukrona emu krona
```

Activate Conda environment:

```
conda activate emukrona
```
Follow instructions at https://github.com/treangenlab/emu to download EMU database.

Update Krona Taxonomy_db (probably found at _/home/$user/miniforge3/envs/emukrona/bin_)

```
./ updateTaxonomy.sh
```

Download script from this site _cat_emu_krona.py_ and run while _emukrona_ conda environment is activated:

```
python3 cat_emu_krona.py
```

![catbird2](https://github.com/user-attachments/assets/2fdec70a-640e-4f46-84bd-2101f99cc167)

## **Usage:**

This GUI should pop up when running _cat_emu_krona.py_. To dislay Nanopore image, download _nanopore.jpg_ from this site and add the local path to line 157 in _cat_emu_krona.py script_. _#Note_ If Barcodes have been applied in the same ONT sequencing run, the procedure described bellow must performed individually for each Barcode.

<img width="649" height="931" alt="Screenshot from 2025-10-22 10-29-53" src="https://github.com/user-attachments/assets/ce146cd3-8660-4170-adb6-3351531f0d2a" />

1. Concatenate your *.fastq.gz files by pressing yellow button "Concatenate FASTQ Files" . Browse and define your folder of interest, press OK. This will generate one file called _allfiles.fastq.gz_ in the same folder.

2. In main GUI window select the newly created _allfiles.fastq.gz_ as Input FASTQ File

3. Create an output folder where suitable and define this as Output Directory in GUI

4. Press green button "Run Pipeline"

5. If using Firefox browser the Krona plot will automatically pop up when run is finished. Otherwise all results will be put in _Output Directory_ including Krona.html plot, a .tsv file containing estimated read counts for each species, a .sam file and .txt file.

6. Visualize the number of reads per microbe by selecting your *.tsv file from Output Directory and press blue button "Generate Column Count Plot"

7. Press red "Clear all" button before analyzing a new dataset.

## **Contacts:**

Optimizing/edits are very welcome. Shout at everlonghh@gmail.com
