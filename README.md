# Voice Separation Tool

This project separates an audio file into:

- vocals
- karaoke (instrumental)

You can choose between **Demucs** and **Spleeter**.

---

## 📦 Installation

### 1. Install dependencies

``` pip install -r requirements.txt ```


Or run: bash install.sh


---

## 📁 Folder Structure
- ``` input/ place your .mp3 file here ```
- ``` output/vocals/ extracted vocals ```
- ``` output/karaoke/ instrumental ```
- ``` src/separate.py main program ``` 


---

## ▶️ Usage

1. Put your song inside the **input** folder.  
2. Run: python src/separate.py or python3 src/separate.py accordingly
3. enter the song name when prompted
4. enter the method to use when prompted Options: "spleeter" or "demucs" Works better with demucs



Your results appear in:

- `output/vocals/`
- `output/karaoke/`

---

## 🧹 Auto-cleaning

Temporary files are removed after each run.

---

## 🛠 Compatible With

- macOS - verified
- Windows - not verified 
- Linux - not verified 

---

## License

MIT

Copyright (c) 2025 <Aswath Murthy>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, **provided that the original author <Aswath Murthy> is credited**.
...