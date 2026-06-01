# Manhuathai Offline Reader

A lightweight offline manga reader with a built-in local web server.

---

## Quick Start

### 1. Clone the repository

```
git clone https://github.com/TiwPhiraphan/manhuathai.git
cd manhuathai
```

---

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Run the application

```
python app.py
```

---

### 4. Open in browser

Go to:

```
http://localhost
```

---

## How It Works

- The app starts a local HTTP server
- Manga images are downloaded and stored in:

```
viewer/images/
```

- Metadata is stored in:

```
viewer/application.json
```

- The browser UI loads data from the local server

---

## Usage

1. Run the app
2. Open the browser
3. Select a manga from the sidebar
4. Click a chapter to start reading

---

## Project Structure

```
.
├── app.py
├── viewer/
│   ├── application.json
│   └── images/
```

---

## Build Executable (Windows)

### Install PyInstaller

```
pip install pyinstaller pyinstaller-hooks-contrib
```

### Build

### Install `pyinstaller`
```
pip install pyinstaller
```

### Build with python
```
python build.py
```

### Output

```
dist/app.exe
```

---

## Notes

- For personal and educational use only
- Commercial use is not allowed
- Ensure required folders exist before running

---

## License

Modified MIT License (Non-Commercial)

You may use, modify, and distribute this software,
but you are NOT allowed to sell or use it commercially.

---
