# PDF Story Text Extractor
# Author: Peter Lambden

A simple desktop tool for extracting the written text from a PDF and saving it as a plain `.txt` file. Built for use at Twinkl, but usable with any text-based PDF.

---

## What This Tool Does

- Lets you select any PDF file from your computer
- Lets you choose a start and end page (useful for skipping front matter or back pages)
- Lets you specify words or phrases to remove from the extracted text
- Lets you optionally **pre-split double-page spreads** into separate left/right pages before extracting.
- Saves the cleaned text as a `.txt` file wherever you choose

---

## How to Run the App (Windows)

This tool comes as a `.exe` file, which means it runs directly on Windows — **you do not need to install Python or any other software**.

Simply double-click `pdf_extractor.exe` to open it.

### ⚠️ Windows Security Warning

When you run the app for the first time, Windows may show a warning message such as:

> *"Windows protected your PC"*
> *"Microsoft Defender SmartScreen prevented an unrecognised app from starting."*

**This is normal and does not mean the app is dangerous.** This warning appears because the app has not been signed with a paid Microsoft certificate — it does not mean it contains a virus or harmful code.

To run it anyway:

1. Click **"More info"** on the warning screen
2. Click **"Run anyway"**

You should only need to do this once. After that, Windows will remember that you've approved it.

If your workplace IT policy blocks `.exe` files entirely, you may need to contact your IT team to whitelist it.

---

## Using the Ignore Strings Feature

The **"Ignore strings"** field lets you type words or phrases that you want removed from the extracted text. Separate multiple entries with a comma, like this:


Monster Surprise, Twinkl Educational Publishing, ChristmasA


### ⚠️ Important: This Removes the Exact Characters Everywhere

The tool does a simple find-and-replace — it finds every occurrence of the string you enter and removes it from the text. This means you need to be careful with short or common strings.

**Example of unintended consequences:**

If you enter `the`, the tool will remove those three letters from **every place they appear** — including inside other words:

| Original | After removing `the` |
|---|---|
| `the cat sat` | ` cat sat` |
| `they went home` | `y went home` |
| `in the cathedral` | `in  cal` |

**Tips for avoiding this:**

- Be as specific as possible — use a full phrase rather than a single short word where you can
- If removing a single word, include a space either side of it (e.g. ` Nook ` instead of `Nook`) to avoid it matching inside longer words — though note this may leave occasional extra spaces
- Always check your output `.txt` file after extraction to make sure the result looks as expected

---

## Page Range

- **Start page** — enter the page number you want extraction to begin from (useful for skipping title pages, copyright notices, etc.)
- **End page** — enter the last page you want extracted, or leave blank to go to the end of the document

---

## Handling Double-Page Spreads

Some picture book PDFs are laid out as **spreads**, where one PDF page contains two book pages side by side (left and right). This can cause the text from both sides to be jumbled together when extracted.

To improve this, the app includes:

### “Pre-split double-page spreads before extracting” (checkbox)

If this box is **checked**:

- The app looks for **landscape** pages (wider than they are tall).
- It automatically splits each of those pages into two separate pages:
  - A **left** half.
  - A **right** half.
- Text extraction then runs on this split version, so left-page text and right-page text stay separate.

If the box is **not** checked:

- The app uses the PDF exactly as it is, with no extra splitting.
- This is usually fine for standard single-page layouts.

Use this checkbox when:

- You are working with **picture-book spreads** or other PDFs where each page visibly contains two facing pages.
- You are seeing text jumbled or interleaved from the left and right sides of a spread.

The splitting is done in a temporary copy of your PDF:

- Your original file is never modified.
- The temporary split file is cleaned up automatically when you close the app.

---

## Notes

- The tool works best with standard text-based PDFs. It will not work on scanned PDFs where the pages are images.
- Page numbers that appear alone on a line are automatically removed.
- The tool does not modify your original PDF in any way.

---

## Feedback or Issues

If something isn't working as expected, please raise an issue in this repository or get in touch directly with peterlambden@gmail.com
