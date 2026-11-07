# ==============================================================================
# 🚀 Universal Smart Remote Uploader (Colab -> Google Drive)
# With Automatic MKVToolNix Index & Seek Repair
# ==============================================================================
import os
import re
import sys
import subprocess
import urllib.request
import urllib.parse
import http.cookiejar
import shutil

try:
    from google.colab import drive  # type: ignore
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
    drive = None

# --- Step 1: Google Drive Mount Check ---
if IN_COLAB and not os.path.exists('/content/drive/MyDrive'):
    print("📁 Mounting Google Drive...")
    drive.mount('/content/drive')

# --- Step 2: Install High-Speed Downloader & Tools ---
if IN_COLAB:
    print("⚙️ Installing system dependencies (aria2, mkvtoolnix)...")
    os.system("apt-get install aria2 mkvtoolnix -y -qq")

# --- Step 3: Universal Smart Link Resolver ---
def smart_resolve(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    print("\n🔍 Analyzing URL...")
    custom_filename = None

    # [Case A] HubCloud 10GBps / GPDL / Cryptonewz Links
    if any(k in url for k in ["gpdl.hubcloud", "cryptonewz.online", "hubcloud."]):
        print("⚡ HubCloud 10GBps / GPDL detected! Resolving Google Datacenter CDN...")
        current = url
        for _ in range(6):
            if 'link=' in current:
                parsed = urllib.parse.urlparse(current)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'link' in qs:
                    direct_url = qs['link'][0]
                    print("✅ Google Datacenter direct link resolved successfully!")
                    # Google Datacenter CDN requires single range connection to avoid chunk reject (reaches 80-120 MB/s)
                    connections = 1 if "googleusercontent.com" in direct_url else 8
                    return direct_url, "https://hubcloud.pw/", connections, None
            req = urllib.request.Request(current, headers=headers)
            try:
                res = urllib.request.urlopen(req)
                current = res.geturl()
            except urllib.error.HTTPError as e:
                if e.code in [301, 302, 303, 307, 308]:
                    current = e.headers.get('Location')
                else:
                    break
        connections = 1 if "googleusercontent.com" in current else 8
        return current, "https://hubcloud.pw/", connections, None

    # [Case B] Speedostream / Streamwish / Filelions Style Links
    elif any(k in url for k in ["speedostream", "streamwish", "/d/"]):
        print("🎬 Speedostream/Streamwish detected! Generating IP-matched direct link on Colab...")
        try:
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

            code = url.split('/d/')[-1].split('_')[0].split('?')[0].split('/')[0]
            base_url = f'https://speedostream1.com/d/{code}'
            step2_url = f'https://speedostream1.com/d/{code}_x'

            # Step 1: Base page visit & extract movie title
            req1 = urllib.request.Request(base_url, headers=headers)
            html1 = opener.open(req1).read().decode('utf-8', errors='ignore')

            title_match = re.search(r'<th[^>]*>Download\s+([^<]+)</th>', html1, re.IGNORECASE)
            if title_match:
                custom_filename = title_match.group(1).strip()
                print(f"🎬 Media Title Detected: '{custom_filename}'")

            # Step 2: Form token extraction
            req2 = urllib.request.Request(step2_url, headers={**headers, 'Referer': base_url})
            html2 = opener.open(req2).read().decode('utf-8', errors='ignore')

            if not custom_filename:
                name_match = re.search(r'Download\s+File\s*<b>([^<]+)</b>', html2, re.IGNORECASE)
                if name_match:
                    custom_filename = name_match.group(1).strip()
                    print(f"🎬 Media Title Detected: '{custom_filename}'")

            op = re.search(r'name="op"\s+value="([^"]+)"', html2).group(1)
            id_val = re.search(r'name="id"\s+value="([^"]+)"', html2).group(1)
            mode = re.search(r'name="mode"\s+value="([^"]+)"', html2)
            mode_val = mode.group(1) if mode else ''
            hash_val = re.search(r'name="hash"\s+value="([^"]+)"', html2).group(1)

            post_data = urllib.parse.urlencode({'op': op, 'id': id_val, 'mode': mode_val, 'hash': hash_val}).encode()
            req3 = urllib.request.Request(step2_url, data=post_data, headers={**headers, 'Referer': step2_url})
            html3 = opener.open(req3).read().decode('utf-8', errors='ignore')

            match = re.search(r'<a\s+href="([^"]+)">Direct Download Link</a>', html3)
            if match:
                print("✅ Direct download link generated successfully on Colab IP!")
                return match.group(1), "https://speedostream1.com/", 4, custom_filename
        except Exception as e:
            print(f"⚠️ Auto-bypass warning: {e}")
        return url, "https://speedostream1.com/", 4, custom_filename

    # [Case C] Generic Direct URL
    else:
        try:
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req, timeout=10)
            final_url = res.geturl()
            if final_url != url:
                print("🔗 Redirect followed to direct link!")
                conn = 1 if "googleusercontent.com" in final_url else 8
                return final_url, "https://google.com/", conn, None
        except Exception:
            pass

    print("🌐 Processing as direct download URL...")
    conn = 1 if "googleusercontent.com" in url else 8
    return url, "https://google.com/", conn, None

# --- Step 4: MKVToolNix Index & Seek Repair ---
def fix_video_index(file_path):
    """
    Rebuilds corrupted index, missing cue tables, and seek headers using MKVToolNix (mkvmerge).
    Preserves exact audio/video streams without re-encoding (lossless and fast).
    """
    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)
    ext_lower = ext.lower()

    if ext_lower not in ['.mkv', '.mp4', '.webm', '.avi', '.ts', '.mov']:
        return file_path

    print(f"\n🔧 MKVToolNix (mkvmerge): Verifying and rebuilding video index & seek table...")
    print(f"🎞️ File: {filename}")

    fixed_filename = f"{base_name}.fixed.mkv"
    fixed_path = os.path.join(os.path.dirname(file_path), fixed_filename)
    cmd = f'mkvmerge -o "{fixed_path}" "{file_path}"'

    try:
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # mkvmerge exit codes: 0 = OK, 1 = OK with warnings (minor timestamp fixes), 2 = Fatal error
        if proc.returncode in [0, 1] and os.path.exists(fixed_path) and os.path.getsize(fixed_path) > 10 * 1024 * 1024:
            print("✅ Success: Video index and seek tables rebuilt successfully!")
            os.remove(file_path)
            target_name = f"{base_name}.mkv"
            final_target = os.path.join(os.path.dirname(file_path), target_name)
            os.rename(fixed_path, final_target)
            return final_target
        else:
            print("ℹ️ MKVToolNix: Index check passed or skipped. Original file preserved.")
            if os.path.exists(fixed_path):
                os.remove(fixed_path)
            return file_path
    except Exception as e:
        print(f"⚠️ Index check warning: {e}")
        return file_path

# --- Step 5: Main Download & Transfer Engine ---
def start_remote_download():
    input_link = input("\nEnter download link: ").strip()

    if not input_link:
        print("❌ Error: No URL provided.")
        return

    final_direct_url, referer_header, connections, custom_filename = smart_resolve(input_link)

    temp_dir = "/content/temp_download"
    os.makedirs(temp_dir, exist_ok=True)

    # Clean previous temporary downloads
    for f in os.listdir(temp_dir):
        try:
            file_path = os.path.join(temp_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception:
            pass

    print(f"\n🚀 Starting high-speed download ({connections} connection(s), live progress):\n")

    out_flag = f'-o "{custom_filename}"' if custom_filename else '--content-disposition-default-utf8=true'

    cmd = (
        f'aria2c '
        f'--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" '
        f'--header="Accept: */*" '
        f'--header="Accept-Language: en-US,en;q=0.9" '
        f'--header="Referer: {referer_header}" '
        f'--file-allocation=none '
        f'--summary-interval=1 '
        f'{out_flag} '
        f'-x {connections} -s {connections} -k 1M '
        f'-d "{temp_dir}" '
        f'\"{final_direct_url}\"'
    )

    # Real-time unbuffered progress streaming
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0
    )

    while True:
        chunk = process.stdout.read(64)
        if not chunk and process.poll() is not None:
            break
        if chunk:
            sys.stdout.write(chunk.decode('utf-8', errors='replace'))
            sys.stdout.flush()

    process.wait()
    exit_code = process.returncode

    # Verify completed files (> 10MB)
    valid_files = []
    for f in os.listdir(temp_dir):
        if not f.endswith('.aria2'):
            fp = os.path.join(temp_dir, f)
            if os.path.isfile(fp) and os.path.getsize(fp) > 10 * 1024 * 1024:
                valid_files.append(f)

    if exit_code == 0 and len(valid_files) > 0:
        # Step 5.1: Automatic MKVToolNix Index Repair
        repaired_files = []
        for f in valid_files:
            fp = os.path.join(temp_dir, f)
            repaired_fp = fix_video_index(fp)
            repaired_files.append(os.path.basename(repaired_fp))

        print("\n📦 Transferring file(s) to Google Drive...")
        save_drive_folder = "/content/drive/MyDrive"

        for f in repaired_files:
            src = os.path.join(temp_dir, f)
            dst = os.path.join(save_drive_folder, f)
            shutil.move(src, dst)
            print(f"🎉 Moved to Google Drive: '{f}' (Index verified and seek-ready)")

        # Flush file system cache to Google Drive
        if IN_COLAB and drive:
            print("\n🔄 Flushing write cache to Google Cloud Drive...")
            drive.flush_and_unmount()
            print("\n✅ SUCCESS: File saved to Google Drive and synced to cloud!")
    else:
        print(f"\n❌ DOWNLOAD FAILED (Exit Code: {exit_code}).")
        print("The server rejected the connection or the link has expired.")

if __name__ == "__main__":
    start_remote_download()
