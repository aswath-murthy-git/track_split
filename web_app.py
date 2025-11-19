from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session, flash
import sys
import os
import glob
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Ensure project root is on sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

# Load environment configuration
try:
    from config import SMTP_CONFIG, APP_CONFIG, validate_email_config
    validate_email_config()
except ImportError:
    print("⚠️  Warning: config.py not found, using defaults")
    SMTP_CONFIG = {
        'server': 'smtp.gmail.com',
        'port': 587,
        'email': os.getenv('SMTP_EMAIL', ''),
        'password': os.getenv('SMTP_PASSWORD', '')
    }
    APP_CONFIG = {
        'secret_key': os.getenv('SECRET_KEY', 'change-this-secret-key'),
        'debug': False
    }

# Import separate_audio if src exists, otherwise skip for deployment
try:
    from src.separate import separate_audio
    SEPARATION_ENABLED = True
except ImportError:
    SEPARATION_ENABLED = False
    print("Warning: Audio separation not available")

app = Flask(__name__)

# Get secret key from environment or config
app.secret_key = APP_CONFIG['secret_key']

UPLOAD_FOLDER = os.path.join(BASE_DIR, "input")
VOCALS_FOLDER = os.path.join(BASE_DIR, "output/vocals")
KARAOKE_FOLDER = os.path.join(BASE_DIR, "output/karaoke")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
PENDING_USERS_FILE = os.path.join(BASE_DIR, "pending_users.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOCALS_FOLDER, exist_ok=True)
os.makedirs(KARAOKE_FOLDER, exist_ok=True)

# Email configuration from SMTP_CONFIG
SMTP_SERVER = SMTP_CONFIG['server']
SMTP_PORT = SMTP_CONFIG['port']
SMTP_EMAIL = SMTP_CONFIG['email']
SMTP_PASSWORD = SMTP_CONFIG['password']


# --------------------- User Management ---------------------

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def load_pending_users():
    """Load pending users from JSON file"""
    if os.path.exists(PENDING_USERS_FILE):
        try:
            with open(PENDING_USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_pending_users(pending_users):
    """Save pending users to JSON file"""
    with open(PENDING_USERS_FILE, 'w') as f:
        json.dump(pending_users, f, indent=2)


def generate_verification_code():
    """Generate a 6-digit verification code"""
    return str(random.randint(100000, 999999))


def send_verification_email(email, code):
    """Send verification code via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = email
        msg['Subject'] = "Verify Your Email - Voice Separation Tool"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h1 style="color: #667eea; text-align: center;">🎵 Voice Separation Tool</h1>
                <h2 style="color: #333;">Verify Your Email</h2>
                <p style="font-size: 16px; color: #666;">Thank you for registering! Please use the verification code below to complete your registration:</p>
                
                <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0; border: 2px solid #667eea;">
                    <h1 style="color: #667eea; font-size: 36px; letter-spacing: 8px; margin: 0;">{code}</h1>
                </div>
                
                <p style="font-size: 14px; color: #999;">This code will expire in 10 minutes.</p>
                <p style="font-size: 14px; color: #999;">If you didn't request this code, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #999; text-align: center;">© 2025 Voice Separation Tool</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# --------------------- Authentication Routes ---------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username")
        password = request.form.get("password")
        
        users = load_users()
        
        # Find user by username or email
        user_found = None
        for username, user_data in users.items():
            if username == username_or_email or user_data.get('email') == username_or_email:
                user_found = username
                break
        
        if user_found:
            user_data = users[user_found]
            
            # Check if email is verified
            if not user_data.get('verified', False):
                return render_template("login.html", error="Please verify your email before logging in")
            
            if check_password_hash(user_data['password'], password):
                session['username'] = user_found
                return redirect(url_for('index'))
            else:
                return render_template("login.html", error="Invalid credentials")
        else:
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not username or not email or not password:
            return render_template("register.html", error="All fields are required")
        
        if len(username) < 3:
            return render_template("register.html", error="Username must be at least 3 characters")
        
        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        users = load_users()
        pending_users = load_pending_users()
        
        if username in users or username in pending_users:
            return render_template("register.html", error="Username already exists")
        
        # Check if email exists
        if any(user_data['email'] == email for user_data in users.values()):
            return render_template("register.html", error="Email already registered")
        
        if any(user_data['email'] == email for user_data in pending_users.values()):
            return render_template("register.html", error="Email already pending verification")
        
        # Generate verification code
        verification_code = generate_verification_code()
        expiry_time = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        # Save to pending users
        pending_users[username] = {
            'email': email,
            'password': generate_password_hash(password),
            'verification_code': verification_code,
            'expiry_time': expiry_time,
            'verified': False
        }
        save_pending_users(pending_users)
        
        # Send verification email
        if send_verification_email(email, verification_code):
            session['pending_username'] = username
            session['pending_email'] = email
            return redirect(url_for('verify_email'))
        else:
            return render_template("register.html", error="Failed to send verification email. Please check your email address.")
    
    return render_template("register.html")


@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    if 'pending_username' not in session:
        return redirect(url_for('register'))
    
    username = session['pending_username']
    email = session['pending_email']
    
    if request.method == "POST":
        code = request.form.get("code")
        
        pending_users = load_pending_users()
        
        if username not in pending_users:
            return render_template("verify_email.html", email=email, error="User not found")
        
        user_data = pending_users[username]
        
        # Check if code expired
        expiry_time = datetime.fromisoformat(user_data['expiry_time'])
        if datetime.now() > expiry_time:
            return render_template("verify_email.html", email=email, error="Verification code expired. Please request a new one.")
        
        # Verify code
        if code == user_data['verification_code']:
            # Move from pending to verified users
            users = load_users()
            users[username] = {
                'email': user_data['email'],
                'password': user_data['password'],
                'verified': True
            }
            save_users(users)
            
            # Remove from pending
            del pending_users[username]
            save_pending_users(pending_users)
            
            # Clear session
            session.pop('pending_username', None)
            session.pop('pending_email', None)
            
            return render_template("login.html", success="Email verified successfully! Please login.")
        else:
            return render_template("verify_email.html", email=email, error="Invalid verification code")
    
    return render_template("verify_email.html", email=email)


@app.route("/resend-code", methods=["POST"])
def resend_code():
    if 'pending_username' not in session:
        return redirect(url_for('register'))
    
    username = session['pending_username']
    email = session['pending_email']
    
    pending_users = load_pending_users()
    
    if username in pending_users:
        # Generate new code
        verification_code = generate_verification_code()
        expiry_time = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        pending_users[username]['verification_code'] = verification_code
        pending_users[username]['expiry_time'] = expiry_time
        save_pending_users(pending_users)
        
        if send_verification_email(email, verification_code):
            return render_template("verify_email.html", email=email, success="New verification code sent!")
        else:
            return render_template("verify_email.html", email=email, error="Failed to send email")
    
    return redirect(url_for('register'))


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('is_guest', None)
    return redirect(url_for('login'))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == "POST":
        email = request.form.get("email")
        
        if not email:
            return render_template("forgot_password.html", error="Email is required")
        
        users = load_users()
        
        # Find user by email
        user_found = None
        for username, user_data in users.items():
            if user_data.get('email') == email:
                user_found = username
                break
        
        if not user_found:
            # Don't reveal if email exists or not (security)
            return render_template("forgot_password.html", 
                                 success="If an account exists with this email, you will receive a reset code.")
        
        # Generate reset code
        reset_code = generate_verification_code()
        expiry_time = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        # Store reset code temporarily
        pending_users = load_pending_users()
        pending_users[f"reset_{user_found}"] = {
            'reset_code': reset_code,
            'expiry_time': expiry_time,
            'username': user_found
        }
        save_pending_users(pending_users)
        
        # Send reset email
        if send_reset_email(email, reset_code):
            session['reset_email'] = email
            session['reset_username'] = user_found
            return redirect(url_for('reset_password'))
        else:
            return render_template("forgot_password.html", 
                                 error="Failed to send email. Please try again.")
    
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Handle password reset with code"""
    if 'reset_username' not in session:
        return redirect(url_for('forgot_password'))
    
    username = session['reset_username']
    email = session['reset_email']
    
    if request.method == "POST":
        code = request.form.get("code")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        if not code or not new_password or not confirm_password:
            return render_template("reset_password.html", email=email, 
                                 error="All fields are required")
        
        if len(new_password) < 6:
            return render_template("reset_password.html", email=email,
                                 error="Password must be at least 6 characters")
        
        if new_password != confirm_password:
            return render_template("reset_password.html", email=email,
                                 error="Passwords do not match")
        
        pending_users = load_pending_users()
        reset_key = f"reset_{username}"
        
        if reset_key not in pending_users:
            return render_template("reset_password.html", email=email,
                                 error="Reset session expired. Please request a new code.")
        
        reset_data = pending_users[reset_key]
        
        # Check if code expired
        expiry_time = datetime.fromisoformat(reset_data['expiry_time'])
        if datetime.now() > expiry_time:
            return render_template("reset_password.html", email=email,
                                 error="Reset code expired. Please request a new one.")
        
        # Verify code
        if code == reset_data['reset_code']:
            # Update password
            users = load_users()
            users[username]['password'] = generate_password_hash(new_password)
            save_users(users)
            
            # Remove reset data
            del pending_users[reset_key]
            save_pending_users(pending_users)
            
            # Clear session
            session.pop('reset_username', None)
            session.pop('reset_email', None)
            
            return render_template("login.html", 
                                 success="Password reset successfully! Please login.")
        else:
            return render_template("reset_password.html", email=email,
                                 error="Invalid reset code")
    
    return render_template("reset_password.html", email=email)


def send_reset_email(email, code):
    """Send password reset code via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = email
        msg['Subject'] = "Password Reset - AI Media Suite"
        
        body = f"""
        <html>
        <body style="font-family: -apple-system, sans-serif; padding: 20px; background-color: #1E1E1E; color: #F1EFEF;">
            <div style="max-width: 600px; margin: 0 auto; background: #595959; padding: 40px; border-radius: 16px; border: 1px solid #A6A6A6;">
                <h1 style="color: #F1EFEF; text-align: center; margin-bottom: 16px;">Password Reset</h1>
                <p style="font-size: 16px; color: #D0D0D0; margin-bottom: 30px;">You requested to reset your password. Use the code below:</p>
                
                <div style="background: #1E1E1E; padding: 24px; border-radius: 8px; text-align: center; margin: 30px 0; border: 1px solid #A6A6A6;">
                    <h1 style="color: #F1EFEF; font-size: 36px; letter-spacing: 8px; margin: 0;">{code}</h1>
                </div>
                
                <p style="font-size: 14px; color: #A6A6A6;">This code will expire in 10 minutes.</p>
                <p style="font-size: 14px; color: #A6A6A6;">If you didn't request this, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #595959; margin: 30px 0;">
                <p style="font-size: 12px; color: #A6A6A6; text-align: center;">AI Media Suite</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending reset email: {e}")
        return False


@app.route("/guest-login")
def guest_login():
    """Allow guest access with limited features"""
    session['username'] = 'Guest'
    session['is_guest'] = True
    return redirect(url_for('index'))


# --------------------- Main App Routes ---------------------

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    is_guest = session.get('is_guest', False)
    
    if request.method == "POST":
        if not SEPARATION_ENABLED:
            return render_template("index.html", username=session['username'], is_guest=is_guest, error="Audio separation is not available")
        
        file = request.files.get("audio")
        
        if file and file.filename:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            try:
                # Determine quality based on user type
                quality = "low" if is_guest else "high"
                
                # Run separation with Demucs (only method available)
                separate_audio(filepath, method="demucs", quality=quality)

                # Prepare download links
                base_name = os.path.splitext(file.filename)[0]
                
                # Look for both WAV and MP3 files
                file_extensions = ['*.wav', '*.mp3']
                vocals_files = []
                karaoke_files = []
                
                for ext in file_extensions:
                    vocals_files.extend(glob.glob(os.path.join(VOCALS_FOLDER, f"{base_name}*_vocals{ext}")))
                    karaoke_files.extend(glob.glob(os.path.join(KARAOKE_FOLDER, f"{base_name}*_karaoke{ext}")))
                
                vocals_files = sorted(vocals_files, key=os.path.getmtime)
                karaoke_files = sorted(karaoke_files, key=os.path.getmtime)
                
                if vocals_files and karaoke_files:
                    vocals_file = vocals_files[-1]
                    karaoke_file = karaoke_files[-1]
                    
                    print(f"✅ Found vocals: {vocals_file}")
                    print(f"✅ Found karaoke: {karaoke_file}")
                    
                    return render_template("result.html",
                                         vocals=os.path.basename(vocals_file),
                                         karaoke=os.path.basename(karaoke_file),
                                         username=session['username'],
                                         is_guest=is_guest)
                else:
                    print(f"❌ Vocals files found: {vocals_files}")
                    print(f"❌ Karaoke files found: {karaoke_files}")
                    return render_template("index.html", username=session['username'], is_guest=is_guest, error="Separation failed - output files not found")
            except Exception as e:
                print(f"Separation error: {e}")
                return render_template("index.html", username=session['username'], is_guest=is_guest, error=f"Separation failed: {str(e)}")
        else:
            return render_template("index.html", username=session['username'], is_guest=is_guest, error="Please select a file")
    
    return render_template("index.html", username=session['username'], is_guest=is_guest)


@app.route("/downloads/<folder>/<filename>")
@login_required
def download_file(folder, filename):
    """Serve download files"""
    try:
        if folder == "vocals":
            folder_path = VOCALS_FOLDER
        elif folder == "karaoke":
            folder_path = KARAOKE_FOLDER
        else:
            return "Invalid folder", 404
        
        file_path = os.path.join(folder_path, filename)
        
        if not os.path.exists(file_path):
            return f"File not found: {filename}", 404
        
        return send_from_directory(folder_path, filename, as_attachment=True)
    except Exception as e:
        print(f"Download error: {e}")
        return f"Download failed: {str(e)}", 500


# Health check endpoint for Render
@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)