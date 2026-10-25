const fileInput = document.getElementById('file-input');
const dropzone = document.getElementById('dropzone');
const browseBtn = document.getElementById('browse-btn');
const sampleBtn = document.getElementById('sample-btn');
const cleanBtn = document.getElementById('clean-btn');
const downloadBtn = document.getElementById('download-btn');
const reportBtn = document.getElementById('report-btn');
const selectedFile = document.getElementById('selected-file');
const selectedFileName = document.getElementById('selected-file-name');
const previewWrap = document.getElementById('preview-wrap');
const schemaList = document.getElementById('schema-list');
const runState = document.getElementById('run-state');
const toast = document.getElementById('toast');

let selectedDataset = null;
let latestResult = null;
let toastTimeout = null;

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle('error', isError);
  toast.classList.add('show');
  window.clearTimeout(toastTimeout);
  toastTimeout = window.setTimeout(() => toast.classList.remove('show'), 3600);
}

function prettyBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function setSelectedFile(file, text = null) {
  selectedDataset = { file, text };
  latestResult = null;
  selectedFile.classList.add('has-file');
  selectedFileName.textContent = `${file.name} · ${prettyBytes(file.size)}`;
  cleanBtn.disabled = false;
  downloadBtn.disabled = true;
  reportBtn.disabled = true;
  runState.classList.remove('completed');
  runState.innerHTML = '<span></span> READY TO CLEAN';
  showToast(`${file.name} is ready. Select “Clean dataset” to begin.`);
}

function resetResults() {
  ['metric-rows', 'metric-missing', 'metric-duplicates', 'metric-types'].forEach((id) => {
    document.getElementById(id).innerHTML = '—<small> waiting</small>';
  });
  document.getElementById('metric-rows-foot').textContent = 'Ready when your file is';
  document.getElementById('metric-missing-foot').textContent = 'Gaps handled by rules';
  document.getElementById('metric-types-foot').textContent = 'Numbers, dates, booleans';
  previewWrap.innerHTML = '<div class="empty-state"><div class="empty-grid">▦</div><strong>Your preview will appear here</strong><span>Load a dataset to inspect the cleaned rows.</span></div>';
  document.getElementById('preview-count').textContent = 'No rows to show';
  schemaList.innerHTML = '<div class="schema-empty">Column details will appear after cleaning.</div>';
}

function safeText(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function renderPreview(result) {
  const headers = result.columns.map((column) => `<th>${safeText(column)}</th>`).join('');
  const rows = result.preview_rows.map((row) => `<tr>${row.map((cell) => `<td title="${safeText(cell)}">${safeText(cell) || '<span class="cell-empty">—</span>'}</td>`).join('')}</tr>`).join('');
  previewWrap.innerHTML = `<table class="data-table"><thead><tr>${headers}</tr></thead><tbody>${rows || ''}</tbody></table>`;
  document.getElementById('preview-count').textContent = `Showing ${Math.min(result.preview_rows.length, 8)} of ${result.summary.cleaned_rows} cleaned rows`;
}

function typeClass(dtype) {
  const type = dtype.toLowerCase();
  if (type.includes('int') || type.includes('float') || type.includes('number')) return 'number';
  if (type.includes('bool')) return 'bool';
  if (type.includes('date') || type.includes('time')) return 'date';
  return 'text';
}

function friendlyType(dtype) {
  const type = dtype.toLowerCase();
  if (type.includes('int')) return 'INTEGER';
  if (type.includes('float') || type.includes('number')) return 'NUMBER';
  if (type.includes('bool')) return 'BOOLEAN';
  if (type.includes('date') || type.includes('time')) return 'DATE / TIME';
  return 'TEXT';
}

function renderSchema(result) {
  if (!result.schema.length) {
    schemaList.innerHTML = '<div class="schema-empty">No columns were found.</div>';
    return;
  }
  schemaList.innerHTML = result.schema.map((item) => {
    const cls = typeClass(item.dtype);
    return `<div class="schema-item"><span class="schema-name" title="${safeText(item.column)}">${safeText(item.column)}</span><span class="schema-type ${cls}">${friendlyType(item.dtype)}</span><span class="schema-detail">Example: ${safeText(item.sample || '—')} · Missing after cleaning: ${item.missing}</span></div>`;
  }).join('');
}

function renderMetrics(result) {
  const s = result.summary;
  document.getElementById('metric-rows').innerHTML = `${s.cleaned_rows}<small> rows</small>`;
  document.getElementById('metric-rows-foot').textContent = `${s.original_rows - s.cleaned_rows} rows removed overall`;
  document.getElementById('metric-missing').innerHTML = `${s.missing_before}<small> found</small>`;
  document.getElementById('metric-missing-foot').textContent = `${s.missing_after} gaps remain after cleaning`;
  document.getElementById('metric-duplicates').innerHTML = `${s.duplicates_removed}<small> rows</small>`;
  document.getElementById('metric-types').innerHTML = `${s.type_changes.length}<small> columns</small>`;
  document.getElementById('metric-types-foot').textContent = s.type_changes.length ? s.type_changes.map((item) => item.column).slice(0, 2).join(', ') : 'No changes required';
}

async function processSelectedDataset() {
  if (!selectedDataset) return;
  cleanBtn.disabled = true;
  cleanBtn.innerHTML = 'Cleaning… <span class="button-arrow">↻</span>';
  runState.classList.remove('completed');
  runState.innerHTML = '<span></span> PROCESSING DATA';
  try {
    const csvText = selectedDataset.text ?? await selectedDataset.file.text();
    const response = await fetch('/api/clean', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body: csvText,
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The dataset could not be cleaned.');
    latestResult = result;
    renderMetrics(result);
    renderPreview(result);
    renderSchema(result);
    downloadBtn.disabled = false;
    reportBtn.disabled = false;
    runState.classList.add('completed');
    runState.innerHTML = '<span></span> CLEANING COMPLETE';
    showToast(`Cleaning complete — ${result.summary.cleaned_rows} rows are ready to export.`);
  } catch (error) {
    runState.classList.remove('completed');
    runState.innerHTML = '<span></span> CLEANING FAILED';
    showToast(error.message || 'Something went wrong while cleaning this file.', true);
  } finally {
    cleanBtn.disabled = !selectedDataset;
    cleanBtn.innerHTML = 'Clean dataset <span class="button-arrow">↗</span>';
  }
}

function downloadBlob(content, fileName, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function safeFilename(name) {
  return (name || 'dataset').replace(/\.csv$/i, '').replace(/[^a-z0-9_-]+/gi, '_').replace(/^_+|_+$/g, '') || 'dataset';
}

browseBtn.addEventListener('click', (event) => { event.stopPropagation(); fileInput.click(); });
dropzone.addEventListener('click', (event) => { if (event.target !== browseBtn) fileInput.click(); });
dropzone.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); fileInput.click(); } });
fileInput.addEventListener('change', () => {
  const file = fileInput.files?.[0];
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.csv')) { showToast('Please select a .csv file.', true); return; }
  if (file.size > 5 * 1024 * 1024) { showToast('Choose a CSV smaller than 5 MB for this local demo.', true); return; }
  setSelectedFile(file);
});
['dragenter', 'dragover'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => { event.preventDefault(); dropzone.classList.add('drag-over'); }));
['dragleave', 'drop'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => { event.preventDefault(); dropzone.classList.remove('drag-over'); }));
dropzone.addEventListener('drop', (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.csv')) { showToast('Please drop a .csv file.', true); return; }
  if (file.size > 5 * 1024 * 1024) { showToast('Choose a CSV smaller than 5 MB for this local demo.', true); return; }
  setSelectedFile(file);
});
sampleBtn.addEventListener('click', async () => {
  sampleBtn.disabled = true;
  try {
    const response = await fetch('/data/original_student_performance.csv');
    if (!response.ok) throw new Error('Sample data could not be loaded. Check that the app is running from its project folder.');
    const text = await response.text();
    const file = new File([text], 'original_student_performance.csv', { type: 'text/csv' });
    setSelectedFile(file, text);
    await processSelectedDataset();
  } catch (error) {
    showToast(error.message || 'Unable to load sample data.', true);
  } finally {
    sampleBtn.disabled = false;
  }
});
cleanBtn.addEventListener('click', processSelectedDataset);
downloadBtn.addEventListener('click', () => {
  if (!latestResult) return;
  downloadBlob(latestResult.cleaned_csv, `${safeFilename(selectedDataset?.file.name)}_cleaned.csv`, 'text/csv;charset=utf-8');
  showToast('Cleaned CSV download started.');
});
reportBtn.addEventListener('click', () => {
  if (!latestResult) return;
  downloadBlob(latestResult.report_text, `${safeFilename(selectedDataset?.file.name)}_cleaning_report.txt`, 'text/plain;charset=utf-8');
  showToast('Cleaning audit report download started.');
});

resetResults();
