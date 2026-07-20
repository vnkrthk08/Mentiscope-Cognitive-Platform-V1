import os

filepath = r"c:\Users\venka\Desktop\trail iitm\mentiscope-processing-speed-live-integration\src\pages\AssessmentRunner.tsx"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "setLoading" in line or "loading" in line:
        print(f"{idx+1}: {line.strip()}")
