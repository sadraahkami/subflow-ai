let selectedFile = null;
let currentLanguage = 'fa';
let currentSubtitles = {};

const I18N_DICT = {
  fa: {
    app_subtitle: "استودیوی هوشمند رونویسی گفتار و ساخت خودکار زیرنویس",
    lang_btn: "English",
    drop_title: "فایل صوتی یا ویدیویی را اینجا رها کنید",
    drop_desc: "پشتیبانی از MP3, WAV, MP4, MKV, MOV, FLAC, WebM",
    btn_select_file: "انتخاب فایل...",
    settings_title: "تنظیمات هوش مصنوعی و خروجی",
    model_label: "مدل رونویسی (Whisper Model):",
    opt_model_base: "Base (استاندارد و بالانس - پیشنهادی)",
    opt_model_tiny: "Tiny (فوق‌العاده سریع)",
    opt_model_small: "Small (دقت بالا - کیفیت عالی)",
    opt_model_medium: "Medium (حداکثر دقت)",
    speech_lang_label: "زبان گفتار (Language):",
    opt_lang_auto: "تشخیص خودکار (Auto Detect)",
    sub_fmt_label: "فرمت خروجی زیرنویس:",
    chk_vad: "فیلتر سکوت و تشخیص صدای انسان (VAD Filter)",
    btn_start: "شروع رونویسی و ساخت زیرنویس",
    preview_title: "پیش‌نمایش متن و زیرنویس تولید شده",
    btn_copy: "کپی متن",
    btn_download: "دانلود فایل زیرنویس",
    placeholder_preview: "متن یا زیرنویس تولید شده پس از رونویسی در اینجا نمایش داده می‌شود...",
    status_reading: "در حال خواندن فایل صوتی و آماده‌سازی هوش مصنوعی...",
    status_transcribing: "در حال رونویسی هوشمند و زمان‌بندی دقیق زیرنویس...",
    msg_copied: "زیرنویس با موفقیت در کلیپ‌بورد کپی شد!"
  },
  en: {
    app_subtitle: "Smart Offline Speech Transcription & Automated Subtitle Studio",
    lang_btn: "فارسی",
    drop_title: "Drag & drop audio or video file here",
    drop_desc: "Supports MP3, WAV, MP4, MKV, MOV, FLAC, WebM",
    btn_select_file: "Select Media File...",
    settings_title: "AI & Export Settings",
    model_label: "Whisper Model:",
    opt_model_base: "Base (Standard & Balanced - Recommended)",
    opt_model_tiny: "Tiny (Ultra Fast)",
    opt_model_small: "Small (High Accuracy - Great Quality)",
    opt_model_medium: "Medium (Maximum Precision)",
    speech_lang_label: "Spoken Language:",
    opt_lang_auto: "Auto Detect",
    sub_fmt_label: "Subtitle Export Format:",
    chk_vad: "Voice Activity Detection Filter (VAD)",
    btn_start: "Start Transcription & Generate Subtitles",
    preview_title: "Generated Subtitles Preview",
    btn_copy: "Copy Content",
    btn_download: "Download Subtitle File",
    placeholder_preview: "Generated transcript or subtitle tracks will appear here...",
    status_reading: "Reading media file and initializing local AI model...",
    status_transcribing: "Transcribing speech and generating precision timestamps...",
    msg_copied: "Subtitles copied to clipboard successfully!"
  }
};

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileNameEl = document.getElementById('fileName');
const fileSizeEl = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFileBtn');
const startBtn = document.getElementById('startBtn');
const modelSelect = document.getElementById('modelSelect');
const langSelect = document.getElementById('langSelect');
const formatSelect = document.getElementById('formatSelect');
const chkVad = document.getElementById('chkVad');
const previewText = document.getElementById('previewText');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');
const statusAlert = document.getElementById('statusAlert');
const statusMsg = document.getElementById('statusMsg');
const langToggleBtn = document.getElementById('langToggleBtn');

function applyTranslations(lang) {
  const t = I18N_DICT[lang];
  if (!t) return;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });

  document.getElementById('optModelBase').textContent = t.opt_model_base;
  document.getElementById('optModelTiny').textContent = t.opt_model_tiny;
  document.getElementById('optModelSmall').textContent = t.opt_model_small;
  document.getElementById('optModelMedium').textContent = t.opt_model_medium;
  document.getElementById('optLangAuto').textContent = t.opt_lang_auto;

  previewText.placeholder = t.placeholder_preview;
  langToggleBtn.textContent = t.lang_btn;
}

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
  previewText.value = '';
  copyBtn.disabled = true;
  downloadBtn.disabled = true;
});

formatSelect.addEventListener('change', () => {
  const fmt = formatSelect.value;
  if (currentSubtitles && currentSubtitles[fmt]) {
    previewText.value = currentSubtitles[fmt];
  }
});

startBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  const t = I18N_DICT[currentLanguage];
  startBtn.disabled = true;
  statusAlert.classList.remove('hidden');
  statusMsg.textContent = t.status_reading;

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64Data = e.target.result;
      statusMsg.textContent = t.status_transcribing;

      const payload = {
        fileName: selectedFile.name,
        fileData: base64Data,
        modelSize: modelSelect.value,
        language: langSelect.value,
        format: formatSelect.value,
        vadFilter: chkVad.checked
      };

      const response = await fetch('/api/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(data.error || 'Transcription failed');
      }

      currentSubtitles = data.subtitles || {};
      previewText.value = currentSubtitles[formatSelect.value] || data.text || '';

      copyBtn.disabled = false;
      downloadBtn.disabled = false;
      statusAlert.classList.add('hidden');
      startBtn.disabled = false;
    };

    reader.readAsDataURL(selectedFile);
  } catch (err) {
    statusMsg.textContent = 'Error: ' + err.message;
    statusAlert.classList.remove('hidden');
    startBtn.disabled = false;
  }
});

copyBtn.addEventListener('click', () => {
  const t = I18N_DICT[currentLanguage];
  if (previewText.value) {
    navigator.clipboard.writeText(previewText.value);
    alert(t.msg_copied);
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
  applyTranslations(currentLanguage);
});

// Initialize translations
applyTranslations(currentLanguage);
