import platform, subprocess

system = platform.system()

cmd = [
    "python",
    "-m",
    "PyInstaller",
    "-F",
    "app.py",
    "--collect-all", "pyclack",
    "--copy-metadata", "readchar"
]

if system == "Windows":
    cmd.extend(["--icon=favicon.ico"])

subprocess.run(cmd, check=True)
