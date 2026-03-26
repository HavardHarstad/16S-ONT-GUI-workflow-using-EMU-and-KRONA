import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import pandas as pd
import plotly.express as px
import webbrowser
import gzip
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import glob

# ------------------------
# FASTQ FILTER FUNCTION (NEW)
# ------------------------
def filter_fastq(input_fastq, output_fastq, min_len=1000, max_len=1800):

    kept = 0
    total = 0

    with gzip.open(input_fastq, "rt") as infile, gzip.open(output_fastq, "wt") as out:
        buffer = []

        for i, line in enumerate(infile):
            buffer.append(line)

            if (i + 1) % 4 == 0:
                total += 1
                seq = buffer[1].strip()

                if min_len <= len(seq) <= max_len:
                    out.writelines(buffer)
                    kept += 1

                buffer = []

    print(f"Filtering complete: {kept}/{total} reads kept")


# ------------------------
# NANOPore QC FUNCTION
# ------------------------
def run_nanopore_qc(fastq_file, output_pdf):

    read_lengths = []
    read_qualities = []

    with gzip.open(fastq_file, "rt") as f:
        line_num = 0

        for line in f:
            line_num += 1

            if line_num % 4 == 2:
                read_lengths.append(len(line.strip()))

            if line_num % 4 == 0:
                qual = line.strip()
                phred = np.array([ord(c) - 33 for c in qual])
                error_probs = 10 ** (-phred / 10)
                mean_error = np.mean(error_probs)
                read_q = -10 * np.log10(mean_error)
                read_qualities.append(read_q)

    read_lengths = np.array(read_lengths)
    read_qualities = np.array(read_qualities)

    mean_len = int(np.mean(read_lengths))
    median_len = int(np.median(read_lengths))
    max_len = int(np.max(read_lengths))

    sorted_lengths = np.sort(read_lengths)[::-1]
    cumsum = np.cumsum(sorted_lengths)
    total_bases = cumsum[-1]

    def calc_N(p):
        return sorted_lengths[np.where(cumsum >= total_bases * (p/100))[0][0]]

    N10, N25, N50, N75 = calc_N(10), calc_N(25), calc_N(50), calc_N(75)

    mean_q = round(np.mean(read_qualities), 2)
    median_q = round(np.median(read_qualities), 2)

    sorted_len = np.sort(read_lengths)
    cumulative_bases = np.cumsum(sorted_len)
    yield_curve = np.cumsum(read_lengths)

    fig = plt.figure(figsize=(12,10))

    # ------------------------
    # READ LENGTH HISTOGRAM
    # ------------------------
    ax1 = fig.add_subplot(221)
    ax1.set_title("Read Length Distribution", pad=20)
    ax1.text(0.5, 1.01,
             f"Reads={len(read_lengths)} | Mean={mean_len} bp | Median={median_len} bp | Max={max_len} bp | N50={N50}",
             transform=ax1.transAxes, ha="center", fontsize=9)
    ax1.hist(read_lengths, bins=200)
    ax1.set_xlim(0,2100)

    ax1.set_xlabel("Read Length (bp)")
    ax1.set_ylabel("Number of Reads")

    # ------------------------
    # QUALITY SCORE HISTOGRAM
    # ------------------------
    ax2 = fig.add_subplot(222)
    ax2.set_title("Quality Score Distribution", pad=20)
    ax2.text(0.5, 1.01,
             f"Mean Q={mean_q} | Median Q={median_q}",
             transform=ax2.transAxes, ha="center", fontsize=9)
    ax2.hist(read_qualities, bins=50, range=(0,20))

    ax2.set_xlabel("Mean Read Quality (Phred Score)")
    ax2.set_ylabel("Number of Reads")

    # ------------------------
    # CUMULATIVE YIELD
    # ------------------------
    ax3 = fig.add_subplot(223)
    ax3.set_title("Cumulative Yield", pad=20)
    ax3.text(0.5, 1.01,
             f"Total bases={total_bases:,}",
             transform=ax3.transAxes, ha="center", fontsize=9)
    ax3.plot(sorted_len, cumulative_bases)

    ax3.set_xlabel("Read Length (bp)")
    ax3.set_ylabel("Cumulative Bases")

    # ------------------------
    # YIELD CURVE
    # ------------------------
    ax4 = fig.add_subplot(224)
    ax4.set_title("Sequencing Yield Curve", pad=20)
    ax4.text(0.5, 1.01,
             f"N10={N10} | N25={N25} | N50={N50} | N75={N75}",
             transform=ax4.transAxes, ha="center", fontsize=9)
    ax4.plot(yield_curve)

    ax4.set_xlabel("Read Index")
    ax4.set_ylabel("Cumulative Bases")

    plt.tight_layout()

    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig)

    plt.close()

# ------------------------
# PIPELINE FUNCTION (UPDATED)
# ------------------------
def run_pipeline():
    input_file = input_entry.get()
    output_dir = output_entry.get()

    if not input_file or not os.path.isfile(input_file):
        messagebox.showerror("Error", "Please select a valid input FASTQ file.")
        return
    if not output_dir:
        messagebox.showerror("Error", "Please select a valid output directory.")
        return

    try:
        subprocess.run(["which", "emu"], check=True, stdout=subprocess.PIPE)
        subprocess.run(["which", "ktImportTaxonomy"], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Missing dependency: Emu or Krona not installed.")
        return

    try:
        os.makedirs(output_dir, exist_ok=True)

        # ------------------------
        # STEP 1: QC RAW DATA
        # ------------------------
        raw_qc = os.path.join(output_dir, "nanopore_qc_raw.pdf")
        run_nanopore_qc(input_file, raw_qc)

        # ------------------------
        # STEP 2: FILTER READS
        # ------------------------
        filtered_fastq = os.path.join(output_dir, "filtered.fastq.gz")
        filter_fastq(input_file, filtered_fastq, 1000, 1800)

        # ------------------------
        # STEP 3: EMU ON FILTERED DATA
        # ------------------------
        subprocess.run([
            "emu", "abundance", filtered_fastq,
            "--output-dir", output_dir,
            "--keep-files", "--keep-counts", "--threads", "20"
        ], check=True)

        # ------------------------
        # STEP 4: FIND EMU OUTPUT (ROBUST)
        # ------------------------
        emu_files = glob.glob(os.path.join(output_dir, "*rel-abundance.tsv"))

        if not emu_files:
            raise FileNotFoundError("EMU output not found.")

        emu_output = emu_files[0]

        # ------------------------
        # STEP 5: KRONA
        # ------------------------
        krona_input = os.path.join(output_dir, "krona_input.txt")

        with open(emu_output, "r") as infile, open(krona_input, "w") as outfile:
            for line in infile:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    outfile.write(f"{parts[0]}\t{parts[1]}\n")

        krona_output = os.path.join(output_dir, "krona_plot.html")

        subprocess.run([
            "ktImportTaxonomy",
            "-o", krona_output,
            krona_input,
            "-t", "1",
            "-m", "2"
        ], check=True)

        subprocess.run(["firefox", krona_output])

        messagebox.showinfo(
            "Success",
            f"✅ Pipeline completed!\n\n"
            f"Raw QC:\n{raw_qc}\n\n"
            f"Filtered FASTQ:\n{filtered_fastq}\n\n"
            f"Krona:\n{krona_output}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ------------------------
# ORIGINAL FUNCTIONS (UNCHANGED)
# ------------------------
def browse_input():
    file_path = filedialog.askopenfilename(filetypes=[("FASTQ.GZ", "*.fastq.gz"), ("FASTQ", "*.fastq")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)

def browse_output():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, dir_path)

def concatenate_fastq_files():
    folder_path = filedialog.askdirectory(title="Select FASTQ folder")
    if not folder_path:
        return

    output_file = os.path.join(folder_path, "allfiles.fastq.gz")

    try:
        subprocess.run(
            f"zcat {folder_path}/*.fastq.gz | gzip > {output_file}",
            shell=True, check=True
        )
        messagebox.showinfo("Success", f"Created:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ------------------------
# TSV COLUMN PLOT FUNCTION
# ------------------------
def browse_tsv():
    file_path = filedialog.askopenfilename(
        filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")]
    )
    if file_path:
        tsv_entry.delete(0, tk.END)
        tsv_entry.insert(0, file_path)

def generate_column_plot():
    tsv_file = tsv_entry.get()

    if not tsv_file or not os.path.isfile(tsv_file):
        messagebox.showerror("Error", "Please select a valid TSV file.")
        return

    try:
        df = pd.read_csv(tsv_file, sep="\t")

        if len(df.columns) < 14:
            messagebox.showerror("Error", "The file must have at least 14 columns.")
            return

        x_col = df.columns[2]   # Column 3
        y_col = df.columns[13]  # Column 14

        output_html = os.path.join(os.path.dirname(tsv_file), "column_plot.html")
        fig = px.bar(
            df, x=x_col, y=y_col,
            title=f"{x_col} vs {y_col}",
            labels={x_col: x_col, y_col: y_col}
        )

        # Custom styling
        fig.update_traces(marker_color='navy')
        fig.update_layout(
            plot_bgcolor='gray',
            paper_bgcolor='white',
            font=dict(color='black', size=20),  # global font size
            title=dict(font=dict(size=20)),      # title font size
            xaxis=dict(title_font=dict(size=16), tickfont=dict(size=16)),
            yaxis=dict(title_font=dict(size=16), tickfont=dict(size=16))
        )

        fig.write_html(output_html)
        webbrowser.open(f"file://{os.path.abspath(output_html)}")
        messagebox.showinfo("Success", f"✅ Column plot saved to:\n{output_html}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ------------------------
# CLEAR FUNCTION
# ------------------------
def clear_inputs():
    input_entry.delete(0, tk.END)
    output_entry.delete(0, tk.END)
    tsv_entry.delete(0, tk.END)

# ------------------------
# GUI (FULLY RESTORED)
# ------------------------
root = tk.Tk()
root.title("16S Nanopore Pipeline")

try:
    img = Image.open("/home/mikrologen/Documents/nanopore.jpg")
    img = img.resize((500, 500))
    img_tk = ImageTk.PhotoImage(img)
    tk.Label(root, image=img_tk).grid(row=0, column=0, columnspan=3, pady=10)
except:
    pass

font = ("Arial", 12, "bold")

tk.Button(root, text="Concatenate FASTQ Files", font=font,
          command=concatenate_fastq_files, bg="orange", fg="white").grid(row=1, column=1, pady=10)

tk.Label(root, text="Input FASTQ File:", font=font).grid(row=2, column=0, padx=5, pady=5, sticky='e')
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", font=font,
          command=lambda: input_entry.insert(0, filedialog.askopenfilename(filetypes=[("FASTQ.GZ", "*.fastq.gz"), ("FASTQ files", "*.fastq")]))).grid(row=2, column=2, padx=5, pady=5)

tk.Label(root, text="Output Directory:", font=font).grid(row=3, column=0, padx=5, pady=5, sticky='e')
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=3, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", font=font,
          command=lambda: output_entry.insert(0, filedialog.askdirectory())).grid(row=3, column=2, padx=5, pady=5)

tk.Button(root, text="Run QC and Emu Pipeline", font=font,
          command=run_pipeline, bg="green", fg="white").grid(row=4, column=1, pady=15)

tk.Label(root, text="Input TSV File:", font=font).grid(row=5, column=0, padx=5, pady=5, sticky='e')
tsv_entry = tk.Entry(root, width=50)
tsv_entry.grid(row=5, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", font=font, command=browse_tsv).grid(row=5, column=2, padx=5, pady=5)

tk.Button(root, text="Generate Column Count Plot", font=font, command=generate_column_plot,
          bg="blue", fg="white").grid(row=6, column=1, pady=15)

tk.Button(root, text="Clear All", font=font, command=clear_inputs,
          bg="red", fg="white").grid(row=7, column=1, pady=10)

root.mainloop()
