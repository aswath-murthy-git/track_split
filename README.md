# Voice Separation Web App

This project lets you separate audio files into:
- Vocals
- Instrumental / Karaoke

Accessible through a web interface.

## Installation Steps

1. Copy all files to their correct locations.
2. Keep your existing .env file (update values as needed).
3. Install dependencies:
   pip3 install -r requirements.txt
4. Run the web app:
   python3 web_app.py

The app should now be accessible via http://localhost:5000 (or the port you configure).

## Folder & File Structure

Root:
- web_app.py – main Flask application
- config.py – loads environment variables
- .env – configuration file for secrets and SMTP
- requirements.txt – all dependencies

Source:
- separate.py – audio separation functions

Templates:
- index.html – main input page with progress bar
- result.html – download page for separated audio
- login.html – login page
- register.html – registration page
- forgot_password.html – password recovery page
- reset_password.html – password reset page

Example .env values (.env.example):

# Email configuration

SMTP_SERVER=smtp.gmail.com

SMTP_PORT=587

SMTP_EMAIL=your-email@gmail.com

SMTP_PASSWORD=your-app-password-here

# App configuration

SECRET_KEY=your-secret-key-here

DEBUG=False

## Usage

1. Open the web app in your browser.
2. Upload a song through the web interface.
3. Wait for the separation process to complete.
4. Download your separated files:
   - output/vocals/
   - output/karaoke/

Temporary files are automatically removed after each run.

## Compatibility

- macOS – verified
- Windows / Linux – not verified

## License

MIT License

Copyright (c) 2025 Aswath Murthy

You can use, copy, modify, and distribute the software as long as the original author is credited.
