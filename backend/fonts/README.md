# Tamil/Telugu Fonts for PDF Generation

This directory should contain TrueType (TTF) font files for Tamil and Telugu text rendering in PDFs.

## Required Fonts

- `NotoSansTamil-Regular.ttf` - For Tamil text
- `NotoSansTelugu-Regular.ttf` - For Telugu text

## How to Download

### Option 1: Manual Download (Recommended)

1. Go to https://fonts.google.com/noto/specimen/Noto+Sans+Tamil
2. Click "Download family" 
3. Extract the ZIP file
4. Copy `NotoSansTamil-Regular.ttf` to this directory

Repeat for Telugu: https://fonts.google.com/noto/specimen/Noto+Sans+Telugu

### Option 2: Using Homebrew (macOS)

```bash
brew install font-noto-sans-tamil
brew install font-noto-sans-telugu
```

Then copy fonts from `/Library/Fonts/` or `~/Library/Fonts/`

### Option 3: Direct Download Links

**Tamil:**
- https://github.com/google/fonts/blob/main/ofl/notosanstamil/NotoSansTamil-Regular.ttf
  - Click "Download" button on GitHub page

**Telugu:**
- https://github.com/google/fonts/blob/main/ofl/notosanstelugu/NotoSansTelugu-Regular.ttf
  - Click "Download" button on GitHub page

## Verification

After downloading, verify the font file:

```bash
file NotoSansTamil-Regular.ttf
# Should show: "TrueType font data" or "OpenType font data"
# NOT: "HTML document" or "text"
```

## Troubleshooting

If you see "Not a recognized TrueType font" error:
1. The file might be corrupted or HTML redirect
2. Delete the file and re-download manually
3. Make sure it's a `.ttf` file, not `.woff2` or `.otf`

