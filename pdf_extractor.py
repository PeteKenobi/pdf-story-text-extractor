import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import os
import tempfile


def split_spreads(input_pdf_path):
    """
    Create a temporary PDF where landscape (spread) pages are split into
    two pages (left + right). Returns the path to the temp PDF.
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Create a temp file path
    fd, tmp_path = tempfile.mkstemp(suffix="_split.pdf")
    os.close(fd)  # we will reopen via pypdf

    for page in reader.pages:
        mb = page.mediabox
        width = float(mb.right) - float(mb.left)
        height = float(mb.top) - float(mb.bottom)

        if width > height:
            # LEFT HALF
            left_page = page
            left_mb = RectangleObject(
                (mb.left, mb.bottom, mb.left + width / 2, mb.top)
            )
            left_page.mediabox = left_mb
            left_page.cropbox = left_mb
            writer.add_page(left_page)

            # RIGHT HALF
            right_page = page
            right_mb = RectangleObject(
                (mb.left + width / 2, mb.bottom, mb.right, mb.top)
            )
            right_page.mediabox = right_mb
            right_page.cropbox = right_mb
            writer.add_page(right_page)
        else:
            writer.add_page(page)

    with open(tmp_path, "wb") as out_f:
        writer.write(out_f)

    return tmp_path


def extract_story_text(pdf_path, start_page=1, end_page=None, output_path=None, ignore_strings=None):
    if start_page < 1:
        start_page = 1

    ignore_set = set(ignore_strings) if ignore_strings else set()

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    if start_page > num_pages:
        raise ValueError(f"Start page {start_page} is beyond the last page ({num_pages}).")

    if end_page is None or end_page > num_pages:
        end_page = num_pages
    if end_page < start_page:
        raise ValueError(f"End page {end_page} cannot be before start page {start_page}.")

    if output_path is None:
        base, _ = os.path.splitext(pdf_path)
        output_path = base + "_story.txt"

    all_text_parts = []

    for page_index in range(start_page - 1, end_page):
        page = reader.pages[page_index]
        raw_text = page.extract_text() or ""

        lines = [line.strip() for line in raw_text.splitlines()]

        cleaned_lines = []
        for line in lines:
            # Skip pure page-number-only lines
            if line.isdigit():
                continue
            # Remove each ignore string from within the line
            for ignore_str in ignore_set:
                line = line.replace(ignore_str, "")
            if line.strip():
                cleaned_lines.append(line.strip())

        page_text = "\n".join(cleaned_lines).strip()
        if page_text:
            all_text_parts.append(page_text)

    final_text = "\n\n".join(all_text_parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    return output_path


class PdfExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Story Text Extractor")
        self.root.geometry("500x340")

        self.pdf_path = None
        self.split_temp_path = None  # track temp split file so we can clean up

        # PDF selection
        self.choose_btn = tk.Button(root, text="Choose PDF...", command=self.choose_pdf)
        self.choose_btn.pack(pady=10)

        self.pdf_label = tk.Label(root, text="No PDF selected", wraplength=480)
        self.pdf_label.pack(pady=5)

        # Page range input (start + end)
        page_frame = tk.Frame(root)
        page_frame.pack(pady=5)

        tk.Label(page_frame, text="Start page:").grid(row=0, column=0, padx=2)
        self.start_entry = tk.Entry(page_frame, width=6)
        self.start_entry.grid(row=0, column=1, padx=2)
        self.start_entry.insert(0, "1")

        tk.Label(page_frame, text="End page:").grid(row=0, column=2, padx=2)
        self.end_entry = tk.Entry(page_frame, width=6)
        self.end_entry.grid(row=0, column=3, padx=2)
        self.end_entry.insert(0, "")

        # Ignore strings input
        ignore_frame = tk.Frame(root)
        ignore_frame.pack(pady=5)

        tk.Label(ignore_frame, text="Ignore strings (comma-separated):").grid(row=0, column=0, padx=2, sticky="w")
        self.ignore_entry = tk.Entry(ignore_frame, width=50)
        self.ignore_entry.grid(row=1, column=0, padx=2, pady=3)

        # Checkbox: pre-split spreads
        self.split_var = tk.BooleanVar(value=False)
        self.split_checkbox = tk.Checkbutton(
            root,
            text="Pre-split double-page spreads before extracting",
            variable=self.split_var
        )
        self.split_checkbox.pack(pady=5)

        # Extract button
        self.extract_btn = tk.Button(root, text="Extract text", command=self.run_extraction)
        self.extract_btn.pack(pady=10)

        # Status label
        self.status_label = tk.Label(root, text="", fg="blue", wraplength=480)
        self.status_label.pack(pady=5)

        # Clean up temp file on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.split_temp_path and os.path.exists(self.split_temp_path):
            try:
                os.remove(self.split_temp_path)
            except OSError:
                pass
        self.root.destroy()

    def parse_ignore_strings(self):
        raw = self.ignore_entry.get().strip()
        if not raw:
            return []
        return [s.strip() for s in raw.split(",") if s.strip()]

    def choose_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.pdf_path = path
            self.pdf_label.config(text=path)
            self.status_label.config(text="")

    def run_extraction(self):
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please choose a PDF file first.")
            return

        start_text = self.start_entry.get().strip()
        if not start_text.isdigit():
            messagebox.showerror("Invalid page", "Start page must be a positive whole number.")
            return
        start_page = int(start_text)
        if start_page < 1:
            messagebox.showerror("Invalid page", "Start page must be at least 1.")
            return

        end_text = self.end_entry.get().strip()
        end_page = None
        if end_text:
            if not end_text.isdigit():
                messagebox.showerror("Invalid page", "End page must be a positive whole number or left blank.")
                return
            end_page = int(end_text)
            if end_page < start_page:
                messagebox.showerror("Invalid range", "End page cannot be before start page.")
                return

        ignore_strings = self.parse_ignore_strings()

        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        default_filename = base_name + "_story.txt"

        save_path = filedialog.asksaveasfilename(
            title="Save story text as...",
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not save_path:
            return

        try:
            self.status_label.config(text="Extracting text, please wait...")
            self.root.update_idletasks()

            # Decide which PDF to use: original vs split
            source_pdf = self.pdf_path

            if self.split_var.get():
                # Create temp split PDF
                self.split_temp_path = split_spreads(self.pdf_path)
                source_pdf = self.split_temp_path

            output_path = extract_story_text(
                source_pdf,
                start_page=start_page,
                end_page=end_page,
                output_path=save_path,
                ignore_strings=ignore_strings,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")
            self.status_label.config(text="")
            return

        self.status_label.config(text=f"Done. Saved story text to:\n{output_path}")
        messagebox.showinfo("Finished", f"Saved story text to:\n{output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PdfExtractorGUI(root)
    root.mainloop()
