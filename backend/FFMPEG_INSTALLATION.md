# 🎵 FFmpeg Installation Guide

**Required for:** Audio format conversion (WebM → MP3/WAV)

---

## Why FFmpeg?

The audio converter service uses `pydub`, which requires `ffmpeg` to convert audio formats. WebM files recorded in the browser need to be converted to MP3/WAV for the Reverie API.

---

## Installation

### macOS (using Homebrew)
```bash
brew install ffmpeg
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
1. Download from: https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Or use Chocolatey: `choco install ffmpeg`

### Verify Installation
```bash
ffmpeg -version
```

---

## What It Does

When a user records audio in the browser:
1. Browser creates WebM file ✅
2. Backend receives WebM ✅
3. **FFmpeg converts WebM → MP3** ✅
4. MP3 sent to Reverie API ✅
5. Transcription works! ✅

---

## Error Handling

If FFmpeg is not installed, you'll see:
```
Failed to convert webm audio. Please ensure ffmpeg is installed
```

**Solution:** Install FFmpeg using the commands above.

---

**Status:** Required dependency for audio conversion

