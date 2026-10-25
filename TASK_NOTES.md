# Task 25 — Basic Data Cleaning

## Objective
Combine fundamental data-cleaning techniques into one practical, documented workflow.

## Dataset
`data/original_student_performance.csv` is a small student-performance dataset supplied with this project. It includes deliberate data-quality issues for demonstration and practice; it is synthetic sample data.

## Cleaning steps
1. Inspect row and column counts and count missing cells.
2. Trim surrounding spaces from cell values and headers.
3. Standardise common missing-value placeholders.
4. Remove fully empty rows and duplicate rows (keep the first matching record).
5. Convert recognisable boolean, numeric, and date/time columns to appropriate types; keep identifier-like columns as text.
6. Impute numeric gaps using the median and other gaps using the mode; use a documented fallback when an entire column is empty.
7. Export the cleaned CSV and an audit report.

## Deliverables
- Original sample dataset: `data/original_student_performance.csv`
- Example cleaned dataset: `outputs/cleaned_student_performance.csv`
- Cleaning log: `outputs/cleaning_report.txt`
- Web application: `app.py`, `index.html`, `styles.css`, and `app.js`
- Terminal script: `clean_dataset.py`

## Interview questions — practice answers

**What is data cleaning?**  
Data cleaning is the process of finding and correcting data-quality problems such as missing values, duplicate records, inconsistent text, and incorrect data types.

**Why is data cleaning important before machine learning?**  
Poor-quality inputs can distort summary statistics, cause model-training errors, introduce bias, and reduce the reliability of predictions. Cleaning makes the input more consistent and suitable for analysis.

**What problems can poor-quality data cause?**  
It can lead to misleading conclusions, failed calculations, unreliable dashboards, inaccurate model predictions, and wasted time investigating errors later.
