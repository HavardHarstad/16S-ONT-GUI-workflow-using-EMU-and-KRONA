import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os

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
        # Check dependencies
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


# GUI setup
root = tk.Tk()
root.title("16S Nanopore Pipeline GUI")

# Load image (replace 'logo.png' with your image path)
try:
    img = Image.open("/home/mikrologen/Documents/nanopore2.jpg")
    img = img.resize((500, 500))  # Resize image as needed
    img_tk = ImageTk.PhotoImage(img)
    img_label = tk.Label(root, image=img_tk)
    img_label.grid(row=0, column=0, columnspan=3, pady=10)
except Exception as e:
    print(f"Image load error: {e}")

# Font
custom_font = ("Arial", 12, "bold")

# Input file selection
tk.Label(root, text="Input FASTQ File:", font=custom_font).grid(row=1, column=0, padx=5, pady=5, sticky='e')
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_input, font=custom_font).grid(row=1, column=2, padx=5, pady=5)

# Output directory selection
tk.Label(root, text="Output Directory:", font=custom_font).grid(row=2, column=0, padx=5, pady=5, sticky='e')
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_output, font=custom_font).grid(row=2, column=2, padx=5, pady=5)

# Run button
tk.Button(root, text="Run Pipeline", font=custom_font, command=run_pipeline, bg="green", fg="white").grid(row=3, column=1, pady=15)

# New concatenate button
tk.Button(root, text="Concatenate FASTQ Files", font=custom_font, command=concatenate_fastq_files, bg="orange", fg="white").grid(row=4, column=1, pady=10)

root.mainloop()
