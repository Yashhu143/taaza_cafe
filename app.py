import os
import time
import uuid
import pymysql
import random
import datetime
import urllib.parse
import urllib.request
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Helper to load .env variables securely without external dependencies
def load_env():
    filename = '.env'
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()

# Load environment configuration
load_env()

# Initialize MySQL database
import db
db.init_db()

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'taaza_cafe_secret_key_session_secure'

# Set UPLOAD_FOLDER to images subdirectory inside project workspace
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Establish and return MySQL database connection."""
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'taaza_cafe')
    
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def send_confirmation_sms(order_id, phone, name, amount):
    """Send order confirmation SMS via Fast2SMS and log the result locally."""
    clean_phone = ''.join(filter(str.isdigit, phone))
    if len(clean_phone) > 10:
        clean_phone = clean_phone[-10:]
        
    message = f"Dear {name}, your Taaza Cafe order {order_id} has been confirmed. Total Paid: Rs {amount:.2f}. Thank you!"
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Log locally to sms_log.txt
    log_line = f"[{timestamp}] [SMS SENT] To: +91-{clean_phone} | Message: {message}\n"
    with open('sms_log.txt', 'a', encoding='utf-8') as f:
        f.write(log_line)
    print(log_line)

    # 2. Trigger Real SMS via Fast2SMS API Key
    api_key = os.getenv('FAST2SMS_API_KEY')
    if not api_key:
        print("Fast2SMS API Key missing in environment settings!")
        return

    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "route": "q",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": clean_phone
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print(f"[{timestamp}] [Fast2SMS Status] Phone: {clean_phone} | Response: {res_json}")
    except Exception as e:
        print(f"[{timestamp}] [Fast2SMS Error] Failed to send SMS to {clean_phone}: {e}")

def send_otp_email(recipient_email, recipient_name, otp):
    """Sends a verification email with the OTP using python SMTP."""
    smtp_user = os.getenv('SMTP_USER', '').strip()
    smtp_pass = os.getenv('SMTP_PASSWORD', '').strip()
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com').strip()
    smtp_port_str = os.getenv('SMTP_PORT', '587').strip()

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Prepare message body
    subject = "Taaza Cafe - Email Verification Code"
    body_text = f"Dear {recipient_name},\n\nYour registration verification code is: {otp}\n\nThank you for choosing Taaza Cafe!"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #2c3e50; padding: 24px; background-color: #f9f9f9;">
        <div style="max-width: 500px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
          <div style="background-color: #4e6c50; color: #ffffff; padding: 24px; text-align: center;">
            <h2 style="margin: 0; font-size: 20px; font-weight: 700; letter-spacing: 0.5px;">Taaza Cafe</h2>
          </div>
          <div style="padding: 24px;">
            <p style="font-size: 15px; margin-top: 0;">Dear <strong>{recipient_name}</strong>,</p>
            <p style="font-size: 14px; color: #4a5568;">Thank you for registering an account with Taaza Cafe. To complete your account verification, please enter the 6-digit verification code below on the registration page:</p>
            
            <div style="background: #f7fafc; border: 1px dashed #cbd5e0; border-radius: 8px; font-size: 28px; font-weight: 800; text-align: center; padding: 18px; margin: 24px 0; color: #4e6c50; letter-spacing: 6px;">
              {otp}
            </div>
            
            <p style="font-size: 12px; color: #a0aec0; margin-bottom: 0;">This code is valid for 15 minutes. If you did not request this verification, please ignore this email.</p>
          </div>
          <div style="background-color: #edf2f7; color: #718096; padding: 16px; text-align: center; font-size: 12px; border-top: 1px solid #e2e8f0;">
            Warm regards, <strong style="color: #4a5568;">Taaza Cafe Team</strong>
          </div>
        </div>
      </body>
    </html>
    """

    # If SMTP credentials are not set, print warning log and write to local otp_log.txt
    if not smtp_user or not smtp_pass:
        print(f"[{timestamp}] [SMTP SKIPPED - Credentials Not Set in .env] To: {recipient_email} | OTP: {otp}")
        return False

    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        smtp_port = 587

    # Create MIMEMultipart message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Taaza Cafe <{smtp_user}>"
    msg['To'] = recipient_email

    msg.attach(MIMEText(body_text, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()
        print(f"[{timestamp}] [EMAIL SENT SUCCESSFULLY] To: {recipient_email} | OTP: {otp}")
        return True
    except Exception as e:
        print(f"[{timestamp}] [SMTP ERROR] Failed to send email to {recipient_email}: {e}")
        return False

def validate_password_strength(password):
    """
    Verify password contains at least 8 characters, 
    one uppercase, one lowercase, one number, and one special character.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&]", password):
        return False
    return True

@app.route('/')
def index():
    """Serve the index.html page."""
    return send_from_directory('.', 'index.html')

@app.route('/owner')
def owner_dashboard():
    """Serve the owner.html dashboard page."""
    return send_from_directory('.', 'owner.html')

@app.route('/api/menu')
def get_menu():
    """Return list of menu items from the MySQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_items")
    menu = cursor.fetchall()
    conn.close()
    return jsonify(menu)

# ================= AUTHENTICATION APIs =================

@app.route('/api/register/request-otp', methods=['POST'])
def register_request_otp():
    """Step 1: Validate registration inputs, password complexity, and send OTP to Email."""
    data = request.json or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not name or not phone or not email or not password or not confirm_password:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"success": False, "error": "Passwords do not match."}), 400

    if len(phone) != 10 or not phone.isdigit():
        return jsonify({"success": False, "error": "Mobile number must be a valid 10-digit number"}), 400

    # Validate password complexity
    if not validate_password_strength(password):
        return jsonify({
            "success": False,
            "error": "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (e.g. @$!%*?&)."
        }), 400

    # Verify if email or phone is already registered in MySQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s OR phone = %s', (email, phone))
    existing = cursor.fetchone()
    conn.close()

    if existing:
        if existing['email'] == email:
            return jsonify({"success": False, "error": "Email address already registered"}), 400
        else:
            return jsonify({"success": False, "error": "Mobile number already registered"}), 400

    # Generate a single 6-digit verification code
    reg_otp = str(random.randint(100000, 999999))

    # Temporarily store signup data in session
    session['temp_reg_data'] = {
        "name": name,
        "phone": phone,
        "email": email,
        "password": password,
        "reg_otp": reg_otp
    }

    # Dispatch simulated OTP log (free development testing fallback)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    otp_log_line = f"[{timestamp}] [VERIFICATION OTP] For {name} (Phone: {phone} / Email: {email}): Code = {reg_otp}\n"
    with open('otp_log.txt', 'a', encoding='utf-8') as f:
        f.write(otp_log_line)
    print(otp_log_line)

    # Send real verification OTP via Email
    send_otp_email(email, name, reg_otp)

    return jsonify({"success": True, "message": "Verification code sent to your email address!"})

@app.route('/api/register/verify-otp', methods=['POST'])
def register_verify_otp():
    """Step 2: Validate the single OTP and insert user into MySQL."""
    data = request.json or {}
    reg_otp = data.get('reg_otp', '').strip()

    temp_data = session.get('temp_reg_data')
    if not temp_data:
        return jsonify({"success": False, "error": "Session expired. Please request verification again."}), 400

    if reg_otp != temp_data['reg_otp']:
        return jsonify({"success": False, "error": "Incorrect verification code."}), 400

    # Save user to MySQL
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(temp_data['password'])
    
    try:
        cursor.execute(
            'INSERT INTO users (name, phone, email, password_hash) VALUES (%s, %s, %s, %s)',
            (temp_data['name'], temp_data['phone'], temp_data['email'], password_hash)
        )
        conn.commit()
        
        # Query newly created user
        cursor.execute('SELECT * FROM users WHERE email = %s', (temp_data['email'],))
        new_user = cursor.fetchone()
        
        # Log user in
        session['user_id'] = new_user['id']
        session['name'] = new_user['name']
        session['phone'] = new_user['phone']
        session['email'] = new_user['email']
        
        # Clear temp registration data
        session.pop('temp_reg_data', None)
        
        return jsonify({
            "success": True,
            "user": {
                "name": new_user['name'],
                "phone": new_user['phone'],
                "email": new_user['email']
            }
        })
    except Exception as e:
        conn.rollback()
        print("Database error during register verification:", e)
        return jsonify({"success": False, "error": "Failed to create user in database."}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate credentials and establish session."""
    data = request.json or {}
    login_id = data.get('login_id', '').strip()
    password = data.get('password', '').strip()

    if not login_id or not password:
        return jsonify({"success": False, "error": "Username/Email and Password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM users WHERE email = %s OR phone = %s',
        (login_id, login_id)
    )
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        # Establish session
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['phone'] = user['phone']
        session['email'] = user['email']
        
        return jsonify({
            "success": True,
            "user": {
                "name": user['name'],
                "phone": user['phone'],
                "email": user['email']
            },
            "message": f"Welcome back, {user['name']}!"
        })
    else:
        return jsonify({"success": False, "error": "Invalid email/mobile number or password"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Clear session data."""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/api/session', methods=['GET'])
def get_session():
    """Return currently active user session profile."""
    if 'user_id' in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "name": session['name'],
                "phone": session['phone'],
                "email": session['email']
            }
        })
    return jsonify({"logged_in": False})

@app.route('/api/user/orders', methods=['GET'])
def get_user_orders():
    """Fetch all orders placed by the currently logged-in user (Protected)."""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
    orders = cursor.fetchall()
    
    result = []
    for order in orders:
        order_id = order['id']
        cursor.execute('SELECT * FROM order_items WHERE order_id = %s', (order_id,))
        items = cursor.fetchall()
        
        items_list = []
        for item in items:
            items_list.append({
                "item_name": item['item_name'],
                "quantity": item['quantity'],
                "price": item['price']
            })
            
        result.append({
            "id": order['id'],
            "order_type": order['order_type'],
            "table_number": order['table_number'],
            "total_amount": order['total_amount'],
            "payment_status": order['payment_status'],
            "created_at": order['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(order['created_at'], datetime.datetime) else str(order['created_at']),
            "items": items_list
        })
        
    conn.close()
    return jsonify(result)

# ================= GOOGLE AUTHENTICATION APIs =================

@app.route('/api/auth/google/client-id', methods=['GET'])
def get_google_client_id():
    """Expose Google OAuth Client ID config."""
    return jsonify({"client_id": os.getenv('GOOGLE_CLIENT_ID')})

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Verify Google ID token and log in / automatically register user."""
    data = request.json or {}
    id_token = data.get('id_token', '').strip()
    
    if not id_token:
        return jsonify({"success": False, "error": "Google ID Token is missing"}), 400
        
    try:
        verification_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        req = urllib.request.Request(verification_url)
        with urllib.request.urlopen(req, timeout=5) as response:
            user_info = json.loads(response.read().decode('utf-8'))
            
        google_email = user_info.get('email')
        google_name = user_info.get('name')
        google_sub = user_info.get('sub') # Google Account ID
        
        if not google_email:
            return jsonify({"success": False, "error": "Failed to retrieve email from Google Account"}), 400
            
    except Exception as e:
        print("Google token verification failed:", e)
        return jsonify({"success": False, "error": "Invalid Google Identity Token"}), 401
        
    # Check if user exists in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (google_email,))
    user = cursor.fetchone()
    
    if not user:
        mock_phone = f"G-{google_sub[:8]}"
        dummy_hash = generate_password_hash(str(uuid.uuid4()))
        
        try:
            cursor.execute(
                'INSERT INTO users (name, phone, email, password_hash) VALUES (%s, %s, %s, %s)',
                (google_name, mock_phone, google_email, dummy_hash)
            )
            conn.commit()
            
            # Fetch newly created user profile
            cursor.execute('SELECT * FROM users WHERE email = %s', (google_email,))
            user = cursor.fetchone()
        except Exception as e:
            conn.rollback()
            conn.close()
            print("Failed to auto-register Google User profile:", e)
            return jsonify({"success": False, "error": "Failed to create Google user registry in database"}), 500
            
    conn.close()
    
    # Establish session
    session['user_id'] = user['id']
    session['name'] = user['name']
    session['phone'] = user['phone']
    session['email'] = user['email']
    
    return jsonify({
        "success": True,
        "user": {
            "name": user['name'],
            "phone": user['phone'],
            "email": user['email']
        }
    })

# ================= ORDER & CHECKOUT APIs =================

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """
    Handle checkout: calculates sum, saves order as 'pending' in database, 
    and returns a dynamic UPI payment link.
    """
    data = request.json or {}
    cart_items = data.get('items', [])
    customer_name = data.get('name', '').strip()
    customer_phone = data.get('phone', '').strip()
    order_type = data.get('order_type', 'dine-in')
    table_number = data.get('table_number', 'N/A')

    if not cart_items:
        return jsonify({"success": False, "error": "Cart is empty"}), 400
    
    if not customer_name or not customer_phone:
        return jsonify({"success": False, "error": "Name and phone number are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query current menu prices from MySQL to prevent price-tampering
    cursor.execute("SELECT id, price, name FROM menu_items")
    db_items = cursor.fetchall()
    menu_dict = {item['id']: item for item in db_items}
    
    total_amount = 0
    items_to_save = []

    for cart_item in cart_items:
        item_id = cart_item.get('id')
        qty = cart_item.get('quantity', 1)
        menu_item = menu_dict.get(item_id)
        if menu_item:
            price = menu_item['price']
            total_amount += price * qty
            items_to_save.append({
                "id": item_id,
                "name": menu_item['name'],
                "quantity": qty,
                "price": price
            })

    order_id = f"TZ-{uuid.uuid4().hex[:6].upper()}"
    user_id = session.get('user_id', None)
    
    try:
        # Save order
        cursor.execute(
            '''INSERT INTO orders (id, user_id, customer_name, customer_phone, order_type, table_number, total_amount, payment_status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (order_id, user_id, customer_name, customer_phone, order_type, table_number if order_type == 'dine-in' else 'N/A', total_amount, 'pending')
        )
        
        # Save order items
        for item in items_to_save:
            cursor.execute(
                '''INSERT INTO order_items (order_id, item_id, item_name, quantity, price)
                   VALUES (%s, %s, %s, %s, %s)''',
                (order_id, item['id'], item['name'], item['quantity'], item['price'])
            )
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("Database error during checkout:", e)
        return jsonify({"success": False, "error": "Failed to create order in database"}), 500

    conn.close()

    # Dynamic UPI QR VPA destination
    merchant_upi = "9603022334@pthdfc"
    merchant_name = "Taaza Cafe"
    encoded_name = urllib.parse.quote(merchant_name)
    payment_note = f"Order {order_id} - Taaza Cafe"
    encoded_note = urllib.parse.quote(payment_note)
    
    upi_uri = f"upi://pay?pa={merchant_upi}&pn={encoded_name}&am={total_amount:.2f}&cu=INR&tn={encoded_note}"

    # Simulating network delay
    time.sleep(1.0)

    return jsonify({
        "success": True,
        "order_id": order_id,
        "customer_name": customer_name,
        "order_type": order_type,
        "table_number": table_number if order_type == 'dine-in' else 'Takeaway',
        "total_amount": total_amount,
        "upi_uri": upi_uri,
        "message": "Order created in database! Awaiting payment."
    })

@app.route('/api/payment/status/<order_id>', methods=['GET'])
def get_payment_status(order_id):
    """
    Check if the order payment is completed or failed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        return jsonify({"success": False, "error": "Order not found"}), 404
        
    status = order['payment_status']
    
    if status == 'paid':
        return jsonify({"success": True, "paid": True, "failed": False, "total_amount": order['total_amount']})
    elif status == 'failed':
        return jsonify({"success": True, "paid": False, "failed": True, "total_amount": order['total_amount']})
    else:
        return jsonify({"success": True, "paid": False, "failed": False})

@app.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    """
    Verify payment by validating the 12-digit UPI UTR.
    """
    data = request.json or {}
    order_id = data.get('order_id', '').strip()
    upi_utr = data.get('upi_utr', '').strip()

    if not order_id or not upi_utr:
        return jsonify({"success": False, "error": "Order ID and UPI UTR are required"}), 400

    if len(upi_utr) != 12 or not upi_utr.isdigit():
        return jsonify({"success": False, "error": "Invalid UTR format. Must be a 12-digit transaction ID."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return jsonify({"success": False, "error": "Order not found"}), 404
        
    if order['payment_status'] == 'paid':
        conn.close()
        return jsonify({"success": True, "message": "Order has already been verified as paid!"})

    try:
        cursor.execute(
            'UPDATE orders SET payment_status = %s, upi_utr = %s WHERE id = %s',
            ('paid', upi_utr, order_id)
        )
        conn.commit()
        
        # Send confirmation SMS message log and Fast2SMS call
        send_confirmation_sms(order_id, order['customer_phone'], order['customer_name'], order['total_amount'])
        
        time.sleep(1.2)
        return jsonify({
            "success": True,
            "message": "Payment verified successfully! Order is now confirmed.",
            "order_id": order_id,
            "total_amount": order['total_amount']
        })
    except Exception as e:
        conn.rollback()
        print("Database error during verification:", e)
        return jsonify({"success": False, "error": "Failed to update order payment status"}), 500
    finally:
        conn.close()

# ================= OWNER DASHBOARD APIs =================

@app.route('/api/owner/login', methods=['POST'])
def owner_login():
    """Authenticate restaurant owner credentials."""
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    config_user = os.getenv('ADMIN_USER', 'admin')
    config_pass = os.getenv('ADMIN_PASSWORD', 'taazaowner')
    
    if username == config_user and password == config_pass:
        session['admin_logged_in'] = True
        return jsonify({"success": True, "message": "Admin session unlocked."})
    else:
        return jsonify({"success": False, "error": "Invalid owner login credentials."}), 401

@app.route('/api/owner/session', methods=['GET'])
def get_owner_session():
    """Verify if the owner session is authenticated."""
    is_logged_in = session.get('admin_logged_in', False)
    return jsonify({"logged_in": is_logged_in})

@app.route('/api/owner/logout', methods=['POST'])
def owner_logout():
    """Clear owner authentication session."""
    session.pop('admin_logged_in', None)
    return jsonify({"success": True, "message": "Admin logged out."})

@app.route('/api/owner/orders', methods=['GET'])
def get_owner_orders():
    """Fetch all orders including nested items (Protected API)."""
    # Authorization gate
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
    orders = cursor.fetchall()
    
    result = []
    for order in orders:
        order_id = order['id']
        cursor.execute('SELECT * FROM order_items WHERE order_id = %s', (order_id,))
        items = cursor.fetchall()
        
        items_list = []
        for item in items:
            items_list.append({
                "item_name": item['item_name'],
                "quantity": item['quantity'],
                "price": item['price']
            })
            
        result.append({
            "id": order['id'],
            "customer_name": order['customer_name'],
            "customer_phone": order['customer_phone'],
            "order_type": order['order_type'],
            "table_number": order['table_number'],
            "total_amount": order['total_amount'],
            "payment_status": order['payment_status'],
            "upi_utr": order['upi_utr'],
            "created_at": order['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(order['created_at'], datetime.datetime) else str(order['created_at']),
            "items": items_list
        })
        
    conn.close()
    return jsonify(result)

@app.route('/api/owner/menu/save', methods=['POST'])
def owner_save_menu_item():
    """Protected API: Add new menu item or update details and image file uploads."""
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    item_id = request.form.get('id', '').strip()
    name = request.form.get('name', '').strip()
    price_str = request.form.get('price', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()

    if not name or not price_str or not category:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        price = float(price_str)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid price value"}), 400

    is_new = (item_id == '' or item_id == 'NEW')

    conn = get_db_connection()
    cursor = conn.cursor()

    image_filename = 'images/cafe_interior.jpg'

    if is_new:
        cat_prefix = category[0].lower() if category else 'c'
        item_id = f"{cat_prefix}_{uuid.uuid4().hex[:6].upper()}"
    else:
        cursor.execute("SELECT image FROM menu_items WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if not item:
            conn.close()
            return jsonify({"success": False, "error": "Menu item not found"}), 404
        image_filename = item['image']

    # Handle image file upload if selected by owner
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            clean_name = f"custom_{item_id}_{int(time.time())}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], clean_name))
            # Prepend images/ subdirectory so the frontend points to http://localhost:5000/images/custom_...
            image_filename = f"images/{clean_name}"

    try:
        if is_new:
            cursor.execute(
                'INSERT INTO menu_items (id, name, price, category, description, image) VALUES (%s, %s, %s, %s, %s, %s)',
                (item_id, name, price, category, description, image_filename)
            )
        else:
            cursor.execute(
                '''UPDATE menu_items 
                   SET name = %s, price = %s, category = %s, description = %s, image = %s 
                   WHERE id = %s''',
                (name, price, category, description, image_filename, item_id)
            )
        conn.commit()
        return jsonify({"success": True, "message": "Menu item updated successfully.", "id": item_id})
    except Exception as e:
        conn.rollback()
        print("Database error during menu update/insert:", e)
        return jsonify({"success": False, "error": "Failed to save item in database."}), 500
    finally:
        conn.close()

@app.route('/api/owner/menu/delete/<item_id>', methods=['POST'])
def owner_delete_menu_item(item_id):
    """Protected API: Delete any menu item from the MySQL database."""
    if not session.get('admin_logged_in', False):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM menu_items WHERE id = %s', (item_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Menu item deleted successfully."})
    except Exception as e:
        conn.rollback()
        print("Database error during menu delete:", e)
        return jsonify({"success": False, "error": "Failed to delete item from database."}), 500
    finally:
        conn.close()

# ================= SIMULATION APIs =================

@app.route('/api/payment/simulate/<order_id>/<outcome>', methods=['POST'])
def simulate_payment(order_id, outcome):
    """Simulate payment success or failure outcomes (Developer tool)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return jsonify({"success": False, "error": "Order not found"}), 404
        
    if outcome == 'success':
        mock_utr = f"3065{random.randint(10000000, 99999999)}"
        cursor.execute(
            "UPDATE orders SET payment_status = 'paid', upi_utr = %s WHERE id = %s",
            (mock_utr, order_id)
        )
        conn.commit()
        
        # Send confirmation SMS message log and Fast2SMS call
        send_confirmation_sms(order_id, order['customer_phone'], order['customer_name'], order['total_amount'])
        status = 'paid'
    elif outcome == 'failed':
        cursor.execute(
            "UPDATE orders SET payment_status = 'failed' WHERE id = %s",
            (order_id,)
        )
        conn.commit()
        status = 'failed'
    else:
        conn.close()
        return jsonify({"success": False, "error": "Invalid outcome"}), 400
        
    conn.close()
    return jsonify({"success": True, "status": status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
