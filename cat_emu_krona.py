import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import pandas as pd
import plotly.express as px
import webbrowser

# ------------------------
# PIPELINE FUNCTION
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

        subprocess.run([
            "emu", "abundance", input_file,
            "--output-dir", output_dir,
            "--keep-files", "--keep-counts", "--threads", "20"
        ], check=True)

        emu_output = os.path.join(output_dir, "allfiles.fastq_rel-abundance.tsv")
        krona_input = os.path.join(output_dir, "krona_input.txt")
        with open(emu_output, "r") as infile, open(krona_input, "w") as outfile:
            for line in infile:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    outfile.write(f"{parts[0]}\t{parts[1]}\n")

        krona_output = os.path.join(output_dir, "krona_plot.html")
        subprocess.run([
            "ktImportTaxonomy", "-o", krona_output, krona_input, "-t", "1", "-m", "2"
        ], check=True)

        subprocess.run(["firefox", krona_output])
        messagebox.showinfo("Success", f"✅ Pipeline completed!\nKrona plot saved to:\n{krona_output}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def browse_input():
    file_path = filedialog.askopenfilename(filetypes=[("FASTQ.GZ", "*.fastq.gz"), ("FASTQ files", "*.fastq"), ("All files", "*.*")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)


def browse_output():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, dir_path)


def concatenate_fastq_files():
    # Select folder
    folder_path = filedialog.askdirectory(title="Select Directory with FASTQ Files to Concatenate")
    if not folder_path:
        return

    output_file = os.path.join(folder_path, "allfiles.fastq.gz")

    try:
        # Run the bash concatenation using subprocess
        subprocess.run(f"cat {folder_path}/*.fastq.gz > {output_file}", shell=True, check=True)
        messagebox.showinfo("Success", f"✅ Files successfully concatenated into:\n{output_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "❌ Concatenation failed. Please check the directory and files.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

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
# GUI SETUP
# ------------------------
root = tk.Tk()
root.title("16S Nanopore Pipeline")

# IMAGE
try:
    img = Image.open("/home/mikrologen/Documents/nanopore2.jpg")
    img = img.resize((500, 500))
    img_tk = ImageTk.PhotoImage(img)
    img_label = tk.Label(root, image=img_tk)
    img_label.grid(row=0, column=0, columnspan=3, pady=10)
except Exception as e:
    print(f"Image load error: {e}")

custom_font = ("Arial", 12, "bold")

# Pipeline input
tk.Label(root, text="Input FASTQ File:", font=custom_font).grid(row=2, column=0, padx=5, pady=5, sticky='e')
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", font=custom_font,
          command=lambda: input_entry.insert(0, filedialog.askopenfilename(filetypes=[("FASTQ.GZ", "*.fastq.gz")]))).grid(row=2, column=2, padx=5, pady=5)

# Output dir
tk.Label(root, text="Output Directory:", font=custom_font).grid(row=3, column=0, padx=5, pady=5, sticky='e')
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=3, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", font=custom_font,
          command=lambda: output_entry.insert(0, filedialog.askdirectory())).grid(row=3, column=2, padx=5, pady=5)

# Run pipeline button
tk.Button(root, text="Run Emu Pipeline", font=custom_font, command=run_pipeline,
          bg="green", fg="white").grid(row=4, column=1, pady=15)

# New concatenate button
tk.Button(root, text="Concatenate FASTQ Files", font=custom_font, command=concatenate_fastq_files, bg="orange", fg="white").grid(row=1, column=1, pady=10)

# TSV plotting section
tk.Label(root, text="Input TSV File:", font=custom_font).grid(row=5, column=0, padx=5, pady=5, sticky='e')
tsv_entry = tk.Entry(root, width=50)
tsv_entry.grid(row=5, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", font=custom_font, command=browse_tsv).grid(row=5, column=2, padx=5, pady=5)

# Column plot button
tk.Button(root, text="Generate Column Count Plot", font=custom_font, command=generate_column_plot,
          bg="blue", fg="white").grid(row=6, column=1, pady=15)

root.mainloop()
