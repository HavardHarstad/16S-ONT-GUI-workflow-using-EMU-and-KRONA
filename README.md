# **16S ONT GUI workflow using EMU and KRONA**

A GUI python script for analyzing full-length 16S Oxford Nanopore (fastq) reads, includes Quality Check (QC) of your data. Created for Ubuntu OS. Require creating a Conda environment for EMU and KRONA combined. The _--threads_ settings for running EMU is set to 20, if having a less powerful computer decrease this definition in script (line 194) to satisfy your computer hardware. The MIN-MAX settings for amplicon lenght is set to 1000bp-2000bp when running EMU, changes in these parameters can be done in line 18 and 186. The QC check will show all of your data.

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
Follow instructions at https://github.com/treangenlab/emu to download EMU database. Custom updated databases can be created, just follow instructions on same site. 

Update Krona Taxonomy_db (probably found at _/home/$user/miniforge3/envs/emukrona/bin_)

```
./ ktUpdateTaxonomy.sh
```

Download script from this site _QC_Emu_Krona.py_ and run while _emukrona_ conda environment is activated:

```
python3 QC_Emu_Krona.py
```

![catbird2](https://github.com/user-attachments/assets/2fdec70a-640e-4f46-84bd-2101f99cc167)

## **Usage:**

This GUI should pop up when running _QC_Emu_Krona.py_. To dislay Nanopore image, download _nanopore.jpg_ from this site and add the local path to line 341 in _QC_Emu_Krona.py script_. _#Note_ If Barcodes have been applied in the same ONT sequencing run, the procedure described bellow must performed individually for each Barcode.

<p align="center">
<img width="649" height="931" alt="Screenshot from 2026-03-26 10-13-16" src="https://github.com/user-attachments/assets/e23af672-27cf-4d32-a6bd-5fa2a0f217d0" />
</p>

1. Concatenate your *.fastq.gz files by pressing yellow button "Concatenate FASTQ Files" . Browse and define your folder of interest, press OK. This will generate one file called _allfiles.fastq.gz_ in the same folder.

2. In main GUI window select the newly created _allfiles.fastq.gz_ as Input FASTQ File

3. Create an output folder where suitable and define this as Output Directory in GUI

4. Press green button "Run QC and Emu Pipeline"

5. If using Firefox browser the Krona plot will automatically pop up when run is finished. Otherwise all results will be put in _Output Directory_ including QC.pdf report, a Krona.html plot, a .sam file and .txt file.

6. In main GUI window visualize the number of reads per microbe by selecting your *.tsv file from Output Directory as Input TSV File and press blue button "Generate Column Count Plot"

7. Press red "Clear all" button before analyzing a new dataset.

## **Example of output files:**

QC report:
<p align="center">
<img width="1268" height="1076" alt="Screenshot from 2026-03-26 11-25-44" src="https://github.com/user-attachments/assets/0b117637-a521-416d-84a3-ff9479868758" />
</p>

Krona plot:
<img width="1265" height="1068" alt="Screenshot from 2026-03-26 10-59-06" src="https://github.com/user-attachments/assets/1d5f8d50-945d-48eb-9d87-cf3729d81ad1" />

Number of reads:
<img width="3295" height="1274" alt="Screenshot from 2026-03-26 11-19-30" src="https://github.com/user-attachments/assets/87f742c5-4990-4133-83c6-72670585389b" />


## **Contacts:**

Optimizing/edits are very welcome. Shout at everlonghh@gmail.com
