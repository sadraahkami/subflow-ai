let selectedFile = null;
let currentSubtitles = {};
let currentLanguage = 'fa';

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileNameEl = document.getElementById('fileName');
const fileSizeEl = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFileBtn');
const startBtn = document.getElementById('startBtn');
const previewText = document.getElementById('previewText');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');
const statusAlert = document.getElementById('statusAlert');
const statusMsg = document.getElementById('statusMsg');
const formatSelect = document.getElementById('formatSelect');
const langToggleBtn = document.getElementById('langToggleBtn');

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) {
    handleFileSelect(e.dataTransfer.files[0]);
  }
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handleFileSelect(e.target.files[0]);
  }
});

function handleFileSelect(file) {
  selectedFile = file;
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = formatBytes(file.size);
  fileInfo.classList.remove('hidden');
  startBtn.disabled = false;
}

removeFileBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  selectedFile = null;
  fileInput.value = '';
  fileInfo.classList.add('hidden');
  startBtn.disabled = true;
});

formatSelect.addEventListener('change', () => {
  const fmt = formatSelect.value;
  if (currentSubtitles && currentSubtitles[fmt]) {
    previewText.value = currentSubtitles[fmt];
  }
});

startBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  startBtn.disabled = true;
  statusAlert.classList.remove('hidden');
  statusMsg.textContent = 'در حال خواندن فایل و بارگذاری مدل هوش مصنوعی...';

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64Data = e.target.result;

      statusMsg.textContent = 'در حال پردازش گفتار و تولید زیرنویس...';

      const payload = {
        fileName: selectedFile.name,
        fileData: base64Data,
        model: document.getElementById('modelSelect').value,
        language: document.getElementById('langSelect').value,
        format: formatSelect.value,
        vad: document.getElementById('chkVad').checked
      };

      const response = await fetch('/api/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(data.error || 'خطا در رونویسی');
      }

      currentSubtitles = data.subtitles;
      const activeFmt = formatSelect.value;
      previewText.value = currentSubtitles[activeFmt] || data.fullText;

      copyBtn.disabled = false;
      downloadBtn.disabled = false;
      statusAlert.classList.add('hidden');
      startBtn.disabled = false;
    };

    reader.readAsDataURL(selectedFile);
  } catch (err) {
    statusMsg.textContent = 'خطا: ' + err.message;
    statusAlert.classList.remove('hidden');
    startBtn.disabled = false;
  }
});

copyBtn.addEventListener('click', () => {
  if (previewText.value) {
    navigator.clipboard.writeText(previewText.value);
    alert('متن با موفقیت در کلیپ‌بورد کپی شد!');
  }
});

downloadBtn.addEventListener('click', () => {
  const fmt = formatSelect.value;
  const content = currentSubtitles[fmt] || previewText.value;
  if (!content) return;

  const stem = selectedFile ? selectedFile.name.replace(/\.[^/.]+$/, '') : 'subtitles';
  const filename = `${stem}.${fmt}`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

langToggleBtn.addEventListener('click', () => {
  currentLanguage = currentLanguage === 'fa' ? 'en' : 'fa';
  document.documentElement.dir = currentLanguage === 'fa' ? 'rtl' : 'ltr';
  document.documentElement.lang = currentLanguage;
  langToggleBtn.textContent = currentLanguage === 'fa' ? 'English' : 'فارسی';
});
