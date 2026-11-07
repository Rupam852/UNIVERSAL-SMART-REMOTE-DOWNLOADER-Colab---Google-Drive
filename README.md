<div align="center">

# 🚀 Universal Smart Remote Uploader
### Direct High-Speed Cloud-to-Cloud Ingestion into Google Drive

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![aria2](https://img.shields.io/badge/Downloader-aria2c-green.svg)](https://aria2.github.io/)
[![MKVToolNix](https://img.shields.io/badge/Remuxer-MKVToolNix-purple.svg)](https://mkvtoolnix.download/)

Transfer massive files (20GB – 50GB+) from web URLs directly into your **Google Drive** in minutes.  
**Zero local bandwidth used • Zero laptop RAM/Disk consumed • 100% Free**

---

</div>

## 📌 Overview

Downloading large files (movies, archives, system images) to a local PC and re-uploading them to Google Drive is slow, consumes personal ISP quota, and strains local storage.

**Universal Smart Remote Uploader** runs in the cloud (via Google Colab), utilizing Google's multi-gigabit datacenter backbone to download, verify, repair container indexes, and instantly flush files straight into your mounted Google Drive.

---

## ✨ Key Features

- **⚡ Datacenter Speeds (80–120 MB/s):** Resolves unthrottled Google Datacenter CDN endpoints (`video-downloads.googleusercontent.com`) for HubCloud/GPDL links.
- **🛡️ 403 Forbidden & IP-Lock Bypass:** Automated headless session management with cookies and correct `Referer` headers to resolve IP-locked stream hosts (Speedostream, Streamwish).
- **🔧 Lossless MKVToolNix Index Repair:** Rebuilds corrupted SeekHead cue tables and timestamp discontinuities using `mkvmerge` without re-encoding (preserves 100% original video/audio quality in ~5 seconds).
- **📊 Real-Time Unbuffered Streaming:** Live download speed (MB/s), % progress, downloaded size, and ETA update dynamically every second in the browser console.
- **🔄 Instant Cloud Flush:** Automatically triggers `drive.flush_and_unmount()` to force Google Drive FUSE synchronization, ensuring files appear immediately on [drive.google.com](https://drive.google.com/).

---

## 📁 Repository Structure

| File | Purpose | Best Used For |
| :--- | :--- | :--- |
| **[`universal_smart_uploader.ipynb`](universal_smart_uploader.ipynb)** | **All-in-One Master Notebook** | General use, Movies & Media (includes MKVToolNix repair) |
| **[`uploader_with_mkvtool.ipynb`](uploader_with_mkvtool.ipynb)** | **MKVToolNix Notebook** | Videos with seek/forward/rewind issues, missing duration |
| **[`uploader_without_mkvtool.ipynb`](uploader_without_mkvtool.ipynb)** | **Pure Fast Transfer Notebook** | Raw files, ZIP/RAR, ISOs, games, software, unaltered media |
| **`universal_smart_uploader.py`** | Standalone Python Script | Script automation and CLI pipelines |
| **`uploader_with_mkvtool.py`** | Standalone Script (with repair) | Media servers, batch script runs |
| **`uploader_without_mkvtool.py`** | Standalone Script (raw transfer) | General data backups |

---

## 🚀 Quick Start Guide (1-Minute Setup)

### Step 1: Open Google Colab
Go to [colab.research.google.com](https://colab.research.google.com/).

### Step 2: Upload the Notebook
1. Click the **Upload** tab.
2. Choose either:
   - **`uploader_with_mkvtool.ipynb`** (for video files with index repair)
   - **`uploader_without_mkvtool.ipynb`** (for raw files/archives)

### Step 3: Run the Cell
1. Click the **Play (▶️)** button on the code cell.
2. Grant permission when prompted to mount your **Google Drive** (`/content/drive/MyDrive`).
3. Paste your download link:
   ```text
   Enter download link: https://speedostream1.com/d/fxr6qv3zf78f_x
   ```
4. Watch the real-time progress update every second. Once finished, your file is synced and immediately accessible in Google Drive!

---

## 🌐 Supported Link Formats

1. **HubCloud 10GBps / GPDL / Cryptonewz Links:**
   - Auto-unwraps redirects to Google Datacenter direct CDNs.
   - Automatically adapts single-range connections to prevent `errorCode=8 Invalid range header`.
2. **Speedostream / Streamwish / Filelions:**
   - Visits base and intermediate landing pages on Colab's datacenter IP.
   - Extracts real media titles (`.mkv`/`.mp4`) from HTML tags.
   - Posts authorization tokens and initiates download with mandatory `Referer` headers.
3. **Generic Direct URLs:**
   - Mediafire, Archive.org, GitHub Releases, direct HTTP/HTTPS endpoints.

---

## 🔧 Technical Details

### Why MKVToolNix Index Repair?
Many web-streamed video files lack keyframe index tables (Cues). When uploaded raw to cloud storage, players cannot seek or fast-forward without buffering from the beginning.
- The `fix_video_index()` function runs:
  ```bash
  mkvmerge -o "output.fixed.mkv" "input.mkv"
  ```
- **Zero Transcoding:** Audio and video streams are copied losslessly bit-for-bit.
- **Fast Execution:** Takes only 5–15 seconds for a 20GB video file on Colab's NVMe drive.

### Real-Time Live Streaming
Colab's web UI buffers standard output from `os.system()`. This project uses an unbuffered `subprocess.Popen` stream with binary chunk reading (`bufsize=0`) and explicit `sys.stdout.flush()`, ensuring live status updates:
```text
[#4fc807 500MiB/2.8GiB(17%) CN:4 DL:3.2MiB ETA:12m10s]
```

---

## ⚙️ Requirements

When running in **Google Colab**, all dependencies (`aria2`, `mkvtoolnix`) are automatically installed on-the-fly via `apt-get`. No manual installation is necessary.

For local or VPS use:
```bash
sudo apt-get update && sudo apt-get install -y aria2 mkvtoolnix python3
```

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it freely.
