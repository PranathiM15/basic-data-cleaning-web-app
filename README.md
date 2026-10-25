# CLEARCUT — Basic Data Cleaning Web App

A small, local-first CSV cleaning project for **Task 25: Basic Data Cleaning**. It uses **Python and Pandas** for the cleaning workflow and a custom HTML/CSS/JavaScript dashboard for uploading, previewing, and exporting datasets. It does **not** use Jupyter Notebook, Flask, or any other third-party web framework.

## What it does

- Accepts a CSV upload in the web dashboard (up to 5 MB for this demo) or loads the included student-performance sample.
- Inspects a dataset and displays row/column quality metrics and an eight-row preview.
- Trims whitespace and recognises common missing-value tokens such as blank, `NA`, `N/A`, `null`, `-`, and `?`.
- Removes completely empty records and duplicate rows after whitespace trimming.
- Converts recognisable numeric, boolean, and date/time columns to suitable data types while keeping identifier-like columns as text.
- Fills missing numeric values with the column median and other missing values with the most common value. If an entire column is empty, it uses `Unknown`.
- Exports a cleaned CSV and a readable `.txt` audit report.
- Also supports a terminal-only cleaning workflow through `clean_dataset.py`.

## Project layout

```text
Basic-Data-Cleaning-Web-App/
├── app.py                               # Local web server (Python standard library)
├── app.js                               # Upload flow, metrics, table and downloads
├── index.html                           # Web app layout
├── styles.css                           # Responsive UI styling
├── cleaning.py                          # Shared Pandas cleaning rules
├── clean_dataset.py                     # Terminal cleaning command
├── requirements.txt                     # Pandas dependency only
├── data/
│   └── original_student_performance.csv # Original sample with realistic issues
└── outputs/
    ├── cleaned_student_performance.csv  # Example cleaned output
    └── cleaning_report.txt              # Example audit report
```

## Requirements

- Windows 10/11 (PowerShell) or another operating system with Python 3.10+.
- Python and pip. On Windows, the `py` launcher is used in the examples.
- Git for the optional GitHub push steps.
- Internet is only needed to install Pandas if it is not already installed. The app itself runs locally.

## Run the web app (Windows PowerShell)

1. Extract the ZIP. Open the extracted `Basic-Data-Cleaning-Web-App` folder in File Explorer.
2. Click the folder address bar, type `powershell`, and press Enter. PowerShell opens in that folder.
3. Check Python:

   ```powershell
   py --version
   ```

4. Install the one required package:

   ```powershell
   py -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   py app.py
   ```

6. Keep the terminal open and visit **http://127.0.0.1:8000** in Chrome.
7. Click **Try sample data** to run the prepared example, or upload a CSV and click **Clean dataset**.
8. Click **Download audit report** and **Download cleaned CSV** to export the results.
9. To stop the server, return to PowerShell and press `Ctrl+C`.

Do not double-click `index.html` to open it. The page needs the local Python server for the cleaning endpoint.

## Run cleaning from the terminal (no browser or notebook required)

From the project folder:

```powershell
py clean_dataset.py data/original_student_performance.csv
```

The default output is saved to `outputs/cleaned_dataset.csv`, with the audit report at `outputs/cleaning_report.txt`.

For a different CSV file, use quoted paths if a folder or file name includes spaces:

```powershell
py clean_dataset.py "C:\Users\YourName\Downloads\my_dataset.csv" --output "outputs\my_cleaned_data.csv" --report "outputs\my_cleaning_report.txt"
```

The input is not overwritten. Cleaning results are saved to the output paths you specify.

## How to create and push the GitHub repository

1. Sign in to GitHub as **PranathiM15** and open **https://github.com/new**.
2. Repository name: `basic-data-cleaning-web-app`.
3. Description: `A Python and Pandas data-cleaning web app for handling missing values, removing duplicates, correcting data types, and exporting a cleaning audit report.`
4. Choose **Public** if your course needs a public repository. Do **not** initialise it with a README, `.gitignore`, or licence because this project already contains its files.
5. After creating the empty repository, run these commands in PowerShell from the extracted project folder:

   ```powershell
   git --version
   git init
   git add .
   git commit -m "Build basic data cleaning web app"
   git branch -M main
   git remote add origin https://github.com/PranathiM15/basic-data-cleaning-web-app.git
   git push -u origin main
   ```

6. If GitHub prompts you to sign in, finish the browser sign-in. Refresh the repository page to verify that `app.py`, `cleaning.py`, `clean_dataset.py`, `index.html`, `styles.css`, `app.js`, `data`, and `outputs` are visible.

**Troubleshooting:** If `git --version` says that `git` is not recognised, install Git for Windows and reopen PowerShell, or use GitHub's **Add file → Upload files** page to upload the extracted project files. If `remote origin already exists` appears, run `git remote -v`; if it points to the wrong repository, use `git remote set-url origin https://github.com/PranathiM15/basic-data-cleaning-web-app.git` instead of adding the remote again. If `git commit` asks for identity, configure it once with `git config --global user.name "PranathiM15"` and `git config --global user.email "YOUR_GITHUB_EMAIL"` (replace the placeholder with the email attached to your GitHub account).

## Cleaning approach and limitations

The included sample intentionally contains missing entries, mixed number/text fields, inconsistent whitespace/capitalisation, a duplicate record, and a date with a different separator. This makes the cleaning steps visible in the results. The app applies simple rules intended for a learning task; always review the report and cleaned output before using any dataset for a real decision. For large files, unusual encodings, highly ambiguous columns, or advanced statistical imputation, extend the rules and validate them against the dataset's meaning.

## Suggested task explanation

> I built a local data-cleaning web app using Python and Pandas. It inspects a CSV, handles missing values, removes duplicate records, corrects recognisable data types, and exports both a cleaned dataset and an audit report. I also provided a terminal-based script so the same workflow can run without a notebook.
