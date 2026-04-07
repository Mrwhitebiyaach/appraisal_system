from flask import Flask, render_template, request, redirect, url_for, flash,  send_from_directory
import os
from dotenv import load_dotenv
load_dotenv()
import re
import time
import hashlib
import random
import json
import datetime
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from form1_handlers import (
    submit_academic_year as form1_submit_academic_year,
    form_page as form1_form_page,
    save_form_data as form1_save_form_data,
    delete_teaching_row as form1_delete_teaching_row,
    delete_academic_review_row as form1_delete_academic_review_row,
    delete_feedback_row as form1_delete_feedback_row,
    reset_form as form1_reset_form,
    save_total_point as form1_save_total_point,
)
from form2_handlers import (
    form2_page as form2_page_handler,
    save_form2_data as form2_save_form_data_handler,
    delete_institute_row as form2_delete_institute_row,
    delete_dept_row as form2_delete_dept_row,
    save_2total_points as form2_save_2total_points,
    reset_form2 as form2_reset_form2,
)
from form3_handlers import (
    save_3total_points as form3_save_3total_points,
    form3_page as form3_page_handler,
    save_form3_data as form3_save_form3_data,
    reset_form3 as form3_reset_form3,
)
from auth_handlers import (
    register as register_handler,
    verify_email as verify_email_handler,
    details as details_handler,
    login as login_handler,
)
from password_handlers import (
    forgotpass_page as forgotpass_page_handler,
    reset_with_token as reset_with_token_handler,
    submit_forgot_password as submit_forgot_password_handler,
)
from pastforms_handlers import (
    render_pastforms as pastforms_render_handler,
    search_pastforms as pastforms_search_handler,
)
from hodpast_handlers import (
    hodpastform as hodpastform_handler,
    search_pastforms2 as hodpast_search_handler,
)
from principlepast_handlers import (
    principlepastform as principlepastform_handler,
    principle_pastforms as principle_pastforms_handler,
)
from facultylist_handlers import facultylist as facultylist_handler
from principlefaculty_handlers import (
    principlestaff as principlestaff_handler,
    principlefaculty as principlefaculty_handler,
    filter_faculty as filter_faculty_handler,
    filter_staff as filter_staff_handler,
)
from dashboard_handlers import (
    dashboard as dashboard_handler,
    get_top_performers as get_top_performers_handler,
    get_section_scores as get_section_scores_handler,
)
from principaldash_handlers import (
    principledash as principledash_handler,
    get_performers_with_hod as get_performers_with_hod_handler,
)
from review_handlers import (
    review as review_handler,
    submit_review as submit_review_handler,
)
from finalscore_handlers import (
    finalscore_page as finalscore_page_handler,
    get_scores as get_scores_handler,
    save_fac_total_points as save_fac_total_points_handler,
)
from assessment_handlers import (
    submit_assessment as submit_assessment_handler,
    get_saved_ratings as get_saved_ratings_handler,
    save_assessment as save_assessment_handler,
    save_principal_assessment as save_principal_assessment_handler,
    query_faculty_ratings as query_faculty_ratings_handler,
)
import pymysql
import secrets
from flask import session
from flask import request, jsonify
import os 
from werkzeug.utils import secure_filename
import time
from flask import  abort
import sys
import traceback
import logging
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta, date
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# First create the Flask app
app = Flask(__name__)
app.secret_key = 'mayank'
s = URLSafeTimedSerializer(app.secret_key)  # Required for token generation and verification

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Set max content length for all requests (including multipart/form-data)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload (increased for safety)

# Configure werkzeug for large file handling
from werkzeug.formparser import FormDataParser
from werkzeug.http import parse_options_header
from werkzeug.formparser import default_stream_factory

# Monkey patch the default max form memory size from 1MB to 20MB
import werkzeug
werkzeug.formparser.DEFAULT_MAX_FORM_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB for PDF files

# Add custom Jinja2 filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string in Jinja2 templates"""
    try:
        return json.loads(value) if value else {}
    except (json.JSONDecodeError, TypeError):
        return {}

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'appraisal.system.apsit@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'your-app-specific-password'  # Your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = ('APSIT Appraisal System', 'appraisal.system.apsit@gmail.com')

# Add error handling for email configuration
try:
    mail = Mail(app)
    print("Email configuration initialized successfully")
except Exception as e:
    print(f"Error initializing email configuration: {e}")
    mail = None

# Set allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'}

# Function to check if file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper to validate and save uploaded files consistently across forms
# Returns (upload_path, success_flag, error_message)
# upload_path is a relative path like "uploads/<unique_filename>" so it can be stored in DB and served by /uploads route.

def validate_and_save_file(file, prefix, form_id, srno):
    """Validate file extension and save with a unique name.

    Args:
        file (werkzeug.datastructures.FileStorage): File object from request.files
        prefix (str): Category prefix (e.g., 'moocs', 'swayam', 'conf')
        form_id (str|int): Current form id used in file name
        srno (str|int): Serial number / row index to differentiate files

    Returns:
        tuple: (upload_path, success_flag, error_message)
    """
    # Sanity checks
    if file is None or file.filename == '':
        return (None, False, "No file selected")

    if not allowed_file(file.filename):
        return (None, False, "Invalid file type. Allowed: " + ", ".join(ALLOWED_EXTENSIONS))

    try:
        # Ensure upload directory exists
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Create a secure unique filename
        original_filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{prefix}_{form_id}_{timestamp}_{srno}_{original_filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        # Save the file
        file.save(file_path)

        # Return path relative to app root (used elsewhere in code)
        return (os.path.join(upload_folder, unique_filename).replace('\\', '/'), True, None)

    except Exception as e:
        # Log full traceback for easier debugging
        print(f"Error while saving file: {e}")
        traceback.print_exc()
        return (None, False, str(e))

# Create the folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Create the profile images folder
if not os.path.exists('static/profile_images'):
    os.makedirs('static/profile_images')

# Create a table for storing email verification tokens if it doesn't exist
def create_verification_table():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            # Create the email_verification table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verification (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                token VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user (user_id),
                UNIQUE KEY unique_email (email),
                UNIQUE KEY unique_token (token)
            )
            """)
            connection.commit()
            print("Email verification table created or already exists.")
        except Exception as e:
            print(f"Error creating email verification table: {e}")
        finally:
            cursor.close()
            connection.close()

# Database connection details loaded from environment variables
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Function to connect to the database using PyMySQL
def connect_to_database():
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        print("Database connection successful!")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


# Route to serve home.html
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return register_handler(connect_to_database, s, mail)



@app.route('/verify-email/<token>')
def verify_email(token):
    return verify_email_handler(connect_to_database, s, token)

@app.route('/details', methods=['GET', 'POST'])
def details():
    return details_handler(connect_to_database)



@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_handler(connect_to_database)


@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



@app.route('/instructions')
def instructions():
    user_id = session.get('user_id')
    return render_template('instructions.html')


@app.route('/submit_academic_year', methods=['POST'])
def submit_academic_year():
    return form1_submit_academic_year(connect_to_database)


@app.route('/form/<int:form_id>')
def form_page(form_id):
    return form1_form_page(connect_to_database, form_id)


@app.route('/save-form-data', methods=['POST'])
def save_form_data():
    return form1_save_form_data(connect_to_database, app, allowed_file)




@app.route('/delete-teaching-row', methods=['POST'])
def delete_teaching_row():
    return form1_delete_teaching_row(connect_to_database)


@app.route('/delete-academic-review-row', methods=['POST'])
def delete_academic_review_row():
    return form1_delete_academic_review_row(connect_to_database)


@app.route('/delete-feedback-row', methods=['POST'])
def delete_feedback_row():
    return form1_delete_feedback_row(connect_to_database)



@app.route('/reset-form', methods=['POST'])
def reset_form():
    return form1_reset_form(connect_to_database)


@app.route('/save-total-points', methods=['POST'])
def save_total_point():
    return form1_save_total_point(connect_to_database)


@app.route('/form2/<int:form_id>')
def form2_page(form_id):
    return form2_page_handler(connect_to_database, form_id)

@app.route('/save-form2-data', methods=['POST'])
def save_form2_data():
    return form2_save_form_data_handler(connect_to_database, allowed_file)

@app.route('/save-3total-points', methods=['POST'])
def save_3total_points():
    return form3_save_3total_points(connect_to_database)


@app.route('/review/<form_id>')
def review(form_id):
    return review_handler(connect_to_database, form_id)




@app.route('/finalscore/<int:form_id>')
def finalscore_page(form_id):
    return finalscore_page_handler(connect_to_database, form_id)



@app.route('/get_scores/<form_id>', methods=['GET'])
def get_scores(form_id):
    return get_scores_handler(connect_to_database, form_id)

@app.route('/save_total_points', methods=['POST'])
def save_fac_total_points():
    return save_fac_total_points_handler(connect_to_database)


@app.route('/landing')
def landing():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to access your profile', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT name, profile_image FROM users WHERE userid = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('User not found', 'danger')
            return redirect(url_for('login'))
        
        profile_image = user_data.get('profile_image', None)
        
        cursor.close()
        connection.close()
        
        return render_template('landingpage.html', user_data=user_data, profile_image=profile_image)
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('landing'))

@app.route('/pastforms', methods=['GET'])
def render_pastforms():
    return pastforms_render_handler(connect_to_database)

@app.route('/pastforms/search', methods=['POST'])
def search_pastforms():
    return pastforms_search_handler(connect_to_database, app)

# Route to serve uploaded files - FIXED VERSION
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded files with proper security and error handling
    """
    try:
        # Ensure the filename is safe and exists in the upload directory
        safe_filename = secure_filename(filename)  # Use secure_filename from werkzeug
        
        # Check if UPLOAD_FOLDER is configured
        if not app.config.get('UPLOAD_FOLDER'):
            app.logger.error("UPLOAD_FOLDER not configured")
            abort(500, description="Upload folder not configured")
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        # Debug logging
        app.logger.info(f"Attempting to serve file: {safe_filename}")
        app.logger.info(f"Full file path: {file_path}")
        app.logger.info(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            abort(404, description=f"File '{safe_filename}' not found")
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            app.logger.error(f"File not readable: {file_path}")
            abort(403, description="File access denied")
        
        # Get file size for logging
        file_size = os.path.getsize(file_path)
        app.logger.info(f"File size: {file_size} bytes")
        
        # Determine mimetype
        mimetype = None
        if safe_filename.lower().endswith('.pdf'):
            mimetype = 'application/pdf'
        elif safe_filename.lower().endswith(('.jpg', '.jpeg')):
            mimetype = 'image/jpeg'
        elif safe_filename.lower().endswith('.png'):
            mimetype = 'image/png'
        elif safe_filename.lower().endswith('.doc'):
            mimetype = 'application/msword'
        elif safe_filename.lower().endswith('.docx'):
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Send file with proper headers
        response = send_from_directory(
            app.config['UPLOAD_FOLDER'], 
            safe_filename, 
            as_attachment=False,
            mimetype=mimetype
        )
        
        # Set additional headers for PDFs
        if safe_filename.lower().endswith('.pdf'):
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{safe_filename}"'
            # Add headers to prevent caching issues
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        app.logger.info(f"Successfully serving file: {safe_filename}")
        return response
        
    except Exception as e:
        app.logger.error(f"Error serving file {filename}: {str(e)}", exc_info=True)
        abort(500, description=f"Server error while serving file: {str(e)}")


# Alternative route for debugging - you can temporarily use this
@app.route('/debug/uploads/<filename>')
def debug_uploaded_file(filename):
    """
    Debug version with more detailed logging
    """
    safe_filename = secure_filename(filename)
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    file_path = os.path.join(upload_folder, safe_filename)
    
    debug_info = {
        'filename': filename,
        'safe_filename': safe_filename,
        'upload_folder': upload_folder,
        'file_path': file_path,
        'file_exists': os.path.exists(file_path),
        'file_readable': os.access(file_path, os.R_OK) if os.path.exists(file_path) else False,
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'current_working_directory': os.getcwd(),
        'upload_folder_exists': os.path.exists(upload_folder),
        'upload_folder_contents': os.listdir(upload_folder) if os.path.exists(upload_folder) else []
    }
    
    return f"<pre>{json.dumps(debug_info, indent=2)}</pre>"


# Make sure you have this import at the top of your file
from werkzeug.utils import secure_filename
import json






@app.route('/highlanding')
def highlanding():
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")

    if user_id:
        connection = connect_to_database()

        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT dept FROM users WHERE userid = %s"
                    print(f"Executing SQL: {sql} with user_id: {user_id}")
                    cursor.execute(sql, (user_id,))
                    result = cursor.fetchone()
                    print(f"Result fetched from DB: {result}")

                    if result:
                        # Adjust here based on how the result is structured
                        department = result[0]  # Accessing department based on index
                        print(f"Department fetched from DB: {department}")
                    else:
                        department = None

            except Exception as e:
                print(f"Error querying database: {e}")
                department = None
            finally:
                connection.close()  # Ensure the connection is closed

        else:
            department = None

        print(f"Department fetched: {department}")
        return render_template('highlanding.html', department=department)

    return redirect(url_for('login'))

@app.route('/facultylist')
def facultylist():
    return facultylist_handler(connect_to_database)

@app.route('/hodpastform')
def hodpastform():
    return hodpastform_handler(connect_to_database)

@app.route('/search_pastforms', methods=['POST'])
def search_pastforms2():
    return hodpast_search_handler(connect_to_database)

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    return submit_assessment_handler(connect_to_database)


@app.route('/get_saved_ratings', methods=['POST'])
def get_saved_ratings():
    return get_saved_ratings_handler(connect_to_database)

@app.route('/save_assessment', methods=['POST'])
def save_assessment():
    return save_assessment_handler(connect_to_database)

@app.route('/dashboard')
def dashboard():
    return dashboard_handler(connect_to_database)

# Your existing routes and database connection logic
@app.route('/get_top_performers', methods=['POST'])
def get_top_performers():
    return get_top_performers_handler(connect_to_database)

# Add the after_request handler here to prevent caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



@app.route('/principlestaff')
def principlestaff():
    return principlestaff_handler()

@app.route('/filter_faculty', methods=['GET'])
def filter_faculty():
    return filter_faculty_handler(connect_to_database)

# Add route to serve profile images
from flask import send_from_directory
import os

@app.route('/static/profile_images/<filename>')
def profile_image(filename):
    profile_images_dir = os.path.join(app.root_path, 'static', 'profile_images')
    return send_from_directory(profile_images_dir, filename)


@app.route('/principlepastform')
def principlepastform():
    return principlepastform_handler(connect_to_database)

@app.route('/principle_pastforms', methods=['POST'])
def principle_pastforms():
    return principle_pastforms_handler(connect_to_database)

@app.route('/principledash')
def principledash():
    return principledash_handler()


@app.route('/get_performers_with_hod', methods=['POST'])
def get_performers_with_hod():
    return get_performers_with_hod_handler(connect_to_database)

# Reuse the after_request handler to prevent caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



@app.route('/forgotpass')
def forgotpass():
    return forgotpass_page_handler()




@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    return reset_with_token_handler(connect_to_database, s, token)




@app.route('/submit-forgot-password', methods=['POST'])
def submit_forgot_password():
    return submit_forgot_password_handler(connect_to_database, s, mail)




app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP server for Gmail
app.config['MAIL_PORT'] = 587  # Use port 587 for TLS
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USERNAME'] = 'facultyappraisal14@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'vydx kmna cxgs yjxp'  # Use an App Password if you have 2FA enabled
app.config['MAIL_DEFAULT_SENDER'] = 'facultyappraisal14@gmail.com'  # Default sender address

mail = Mail(app)


@app.route('/save_principal_assessment', methods=['POST'])
def save_principal_assessment():
    return save_principal_assessment_handler(connect_to_database)

@app.route('/giveappraisal', methods=['GET', 'POST'])
def give_appraisal():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if data is None:
            user_id = request.form.get('user_id')
            form_id = request.form.get('form_id')
            acad_years = request.form.get('acad_years')
        else:
            user_id = data.get('user_id')
            form_id = data.get('form_id')
            acad_years = data.get('acad_years')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'No user ID provided.'}), 400
        connection = connect_to_database()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT gmail FROM users WHERE userid = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    user_email = result[0]
                    # Fetch user_data
                    cursor.execute("SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp FROM users WHERE userid = %s", (user_id,))
                    user_data = cursor.fetchone()
                    if not user_data:
                        return jsonify({'status': 'error', 'message': 'User not found.'}), 404

                    try:
                        form_id = int(form_id) if form_id else None
    
                        save_sql = '''
                            INSERT INTO appraisals (userid, form_id, acad_year, status, approval_date)
                            VALUES (%s, %s, %s, 'approved', NOW())
                            ON DUPLICATE KEY UPDATE
                                form_id = VALUES(form_id),
                                acad_year = VALUES(acad_year),
                                status = 'approved',
                                approval_date = NOW()
                        '''
                        cursor.execute(save_sql, (user_id, form_id, acad_years))
                        connection.commit()
                    except Exception as e:
                        print(f"Error inserting into appraisals: {str(e)}")
                        connection.rollback()

                    appraisal_html = generate_appraisal_html(user_id, form_id=form_id, acad_years=acad_years)
                    return jsonify({'message': 'Assessment approved and email sent!', 'redirect_url': '/principlefaculty?approved=1'})
                else:
                    return jsonify({'status': 'error', 'message': 'User not found.'}), 404
        finally:
            connection.close()
    else:
        user_id = request.args.get('userid')
        form_id = request.args.get('form_id')
        acad_years = request.args.get('acad_years')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'No user ID provided.'}), 400
        connection = connect_to_database()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT gmail FROM users WHERE userid = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    user_email = result[0]
                    appraisal_html = generate_appraisal_html(user_id, form_id=form_id, acad_years=acad_years)
                    return jsonify({'status': 'success', 'message': 'Appraisal data fetched (no email sent).'})
                else:
                    return jsonify({'status': 'error', 'message': 'User not found.'}), 404
        finally:
            connection.close()

def generate_appraisal_html(user_id, form_id=None, acad_years=None):
    """Generate the complete appraisal HTML with all data for the given user and (optionally) a specified form_id or academic year."""
    points_data = {
        'teaching': 0,
        'feedback': 0,
        'dept': 0,
        'institute': 0,
        'acr': 0,
        'society': 0
    }
   
    assessments = {
        'hodas1': 0,
        'hodas2': 0,
        'hodas3': 0,
        'hodas4': 0,
        'hodas5': 0,
        'hodas6': 0,
        'principle_feedback': '',
        'hod_feedback': ''
    }

    finalacr_value = 0
    teaching_data, feedback_data, dept_act_data, inst_act_data = [], [], [], []
    self_improvement_data, certification_data, title_data = [], [], []
    resource_data, committee_data, project_data, contribution_data = [], [], [], []
    moocs_data, swayam_data, webinar_data = [], [], []
    user_data = None
    hod_ratings = None
    selected_year = None

    from datetime import datetime
    current_date = datetime.now().strftime('%d-%m-%Y')

    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                # First, fetch user data to ensure it exists
                cursor.execute("""
                    SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp 
                    FROM users WHERE userid = %s
                """, (user_id,))
                user_data = cursor.fetchone()
                print(f"[LOG] user_data: {user_data}")
                
                if not user_data:
                    print(f"[ERROR] User not found for user_id: {user_id}")
                    return f"<h1>User not found for ID: {user_id}</h1>"

                if form_id:
                    # Fetch acad_years for this form_id
                    cursor.execute("SELECT acad_years FROM acad_years WHERE form_id = %s", (form_id,))
                    result = cursor.fetchone()
                    selected_year = result[0] if result else None
                    print(f"[LOG] Using form_id: {form_id} (forced by input), selected_year: {selected_year}")
                elif acad_years:
                    # Fetch form_id for this user and year
                    cursor.execute("SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s", (user_id, acad_years))
                    result = cursor.fetchone()
                    if not result:
                        print(f"[LOG] No appraisal data found for user_id={user_id} and acad_years={acad_years}")
                        return f"<h1>No appraisal data found for user {user_id} in year {acad_years}.</h1>"
                    form_id = result[0]
                    selected_year = acad_years
                    print(f"[LOG] Using selected_year: {selected_year}, form_id: {form_id} (forced by acad_years)")
                else:
                    # Get the latest filled form for the user (ensure form is filled)
                    cursor.execute("""
                        SELECT a.acad_years, a.form_id
                        FROM acad_years a
                        JOIN form1_tot f1 ON a.form_id = f1.form_id
                        JOIN form2_tot f2 ON a.form_id = f2.form_id
                        JOIN form3_tot f3 ON a.form_id = f3.form_id
                        LEFT JOIN feedback fb ON a.form_id = fb.form_id
                        WHERE a.user_id = %s
                          AND (
                            (COALESCE(f1.teaching,0) + COALESCE(f1.feedback,0) +
                             COALESCE(f2.dept,0) + COALESCE(f2.institute,0) +
                             COALESCE(f3.acr,0) + COALESCE(f3.society,0)) > 0
                            OR (fb.feedback IS NOT NULL AND fb.feedback != '')
                            OR (fb.principle_feedback IS NOT NULL AND fb.principle_feedback != '')
                          )
                        ORDER BY a.acad_years DESC, a.form_id DESC LIMIT 1
                    """, (user_id,))
                    year_result = cursor.fetchone()
                    if not year_result:
                        print(f"[LOG] No filled appraisal data found for user_id={user_id}")
                        return "<h1>No appraisal data found for this user.</h1>"
                    selected_year = year_result[0]
                    form_id = year_result[1]
                    print(f"[LOG] Using selected_year: {selected_year}, form_id: {form_id}")

                # Fetch HOD ratings
                cursor.execute("SELECT r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r_avg FROM feedback WHERE form_id = %s", (form_id,))
                ratings_row = cursor.fetchone()
                print(f"[DEBUG] ratings_row: {ratings_row}")
                if ratings_row:
                    hod_ratings = {f"r{i+1}": ratings_row[i] for i in range(10)}
                    hod_ratings["r_avg"] = ratings_row[10]
                else:
                    hod_ratings = {f"r{i+1}": None for i in range(10)}
                    hod_ratings["r_avg"] = None
                print(f"[LOG] hod_ratings: {hod_ratings}")

                # Fetch feedback data
                cursor.execute("SELECT feedback, principle_feedback FROM feedback WHERE form_id = %s", (form_id,))
                feedback_result = cursor.fetchone()
                print(f"[DEBUG] feedback_result: {feedback_result}")
                if feedback_result:
                    if feedback_result[0]:
                        assessments['hod_feedback'] = feedback_result[0]
                    if feedback_result[1]:
                        assessments['principle_feedback'] = feedback_result[1]
                print(f"[LOG] assessments after feedback: {assessments}")

                # Fetch teaching process data
                cursor.execute("""
                    SELECT semester, course_code, classes_scheduled, classes_held, (classes_held / classes_scheduled) * 5 AS totalpoints
                    FROM teaching_process WHERE form_id = %s
                """, (form_id,))
                teaching_data = cursor.fetchall() or []

                # Fetch student feedback data
                cursor.execute("""
                    SELECT semester, course_code, total_points, points_obtained, uploads
                    FROM students_feedback WHERE form_id = %s
                """, (form_id,))
                feedback_data = cursor.fetchall() or []

                # Fetch departmental activities data
                cursor.execute("""
                    SELECT semester, activity, points, order_cpy, uploads
                    FROM department_act WHERE form_id = %s
                """, (form_id,))
                dept_act_data = cursor.fetchall() or []

                # Fetch institute activity data
                cursor.execute("""
                    SELECT semester, activity, points, order_cpy, uploads
                    FROM institute_act WHERE form_id = %s
                """, (form_id,))
                inst_act_data = cursor.fetchall() or []

                # Fetch MOOCS data
                cursor.execute("SELECT srno, name, month, duration, completion FROM moocs WHERE form_id = %s", (form_id,))
                moocs_data = cursor.fetchall() or []

                # Fetch SWAYAM data
                cursor.execute("SELECT srno, name, month, duration, completion FROM swayam WHERE form_id = %s", (form_id,))
                swayam_data = cursor.fetchall() or []

                # Fetch Webinar data - FIXED: Use 'webinar' not 'webinars' and correct column names
                cursor.execute("SELECT srno, name, technology, duration, date, int_ext, name_of_institute FROM webinar WHERE form_id = %s", (form_id,))
                webinar_data = cursor.fetchall() or []

                # Fetch self-improvement data
                cursor.execute("SELECT title, month, name_of_conf, issn, co_auth, imp_conference, num_of_citations, rating FROM self_imp WHERE form_id = %s", (form_id,))
                self_improvement_data = cursor.fetchall() or []

                # Fetch certification data
                cursor.execute("SELECT name, uploads FROM certifications WHERE form_id = %s", (form_id,))
                certification_data = cursor.fetchall() or []

                # Fetch title data
                cursor.execute("SELECT name, month, reg_no FROM copyright WHERE form_id = %s", (form_id,))
                title_data = cursor.fetchall() or []

                # Fetch resource person data
                cursor.execute("SELECT name, dept, name_oi, num_op FROM resource_person WHERE form_id = %s", (form_id,))
                resource_data = cursor.fetchall() or []

                # Fetch university committee data
                cursor.execute("SELECT name, roles, designation FROM mem_uni WHERE form_id = %s", (form_id,))
                committee_data = cursor.fetchall() or []

                # Fetch external projects data
                cursor.execute("SELECT role, `desc`, contribution, university, duration, comments FROM external_projects WHERE form_id = %s", (form_id,))
                project_data = cursor.fetchall() or []

                # Fetch contribution data
                cursor.execute("SELECT semester, activity, points, order_cpy, uploads FROM contribution_to_society WHERE form_id = %s", (form_id,))
                contribution_data = cursor.fetchall() or []

                # Fetch totals data
                cursor.execute("SELECT teaching, feedback, hodas1, hodas2, hodfeed1, hodfeed2, prinas1, prinas2, prinfeed1, prinfeed2 FROM form1_tot WHERE form_id = %s", (form_id,))
                form1_tot = cursor.fetchone()
                print(f"[DEBUG] form1_tot: {form1_tot}")
                cursor.execute("SELECT dept, institute, hodas3, hodas4, hodfeed3, hodfeed4, prinas3, prinas4, prinfeed3, prinfeed4 FROM form2_tot WHERE form_id = %s", (form_id,))
                form2_tot = cursor.fetchone()
                print(f"[DEBUG] form2_tot: {form2_tot}")
                cursor.execute("SELECT acr, society, hodas5, hodas6, hodfeed5, hodfeed6, prinas5, prinas6, prinfeed5, prinfeed6, finalacr FROM form3_tot WHERE form_id = %s", (form_id,))
                form3_tot = cursor.fetchone()
                print(f"[DEBUG] form3_tot: {form3_tot}")

                # Extract finalacr_value
                if form3_tot and len(form3_tot) > 10 and form3_tot[10] is not None:
                    finalacr_value = int(form3_tot[10])
                else:
                    finalacr_value = 0
                print(f"[LOG] finalacr_value: {finalacr_value}")

                # Populate points_data
                points_data = {
                    'teaching': int(form1_tot[0]) if form1_tot and form1_tot[0] else 0,
                    'feedback': int(form1_tot[1]) if form1_tot and form1_tot[1] else 0,
                    'dept': int(form2_tot[0]) if form2_tot and form2_tot[0] else 0,
                    'institute': int(form2_tot[1]) if form2_tot and form2_tot[1] else 0,
                    'acr': int(form3_tot[0]) if form3_tot and form3_tot[0] else 0,
                    'society': int(form3_tot[1]) if form3_tot and form3_tot[1] else 0,
                }
                print(f"[LOG] points_data: {points_data}")

                # Populate assessments
                assessments.update({
                    'hodas1': int(form1_tot[2]) if form1_tot and form1_tot[2] is not None else 0,
                    'hodas2': int(form1_tot[3]) if form1_tot and form1_tot[3] is not None else 0,
                    'hodas3': int(form2_tot[2]) if form2_tot and form2_tot[2] is not None else 0,
                    'hodas4': int(form2_tot[3]) if form2_tot and form2_tot[3] is not None else 0,
                    'hodas5': int(form3_tot[2]) if form3_tot and form3_tot[2] is not None else 0,
                    'hodas6': int(form3_tot[3]) if form3_tot and form3_tot[3] is not None else 0,
                    'hodfeed1': form1_tot[4] if form1_tot and len(form1_tot) > 4 else '',
                    'hodfeed2': form1_tot[5] if form1_tot and len(form1_tot) > 5 else '',
                    'hodfeed3': form2_tot[4] if form2_tot and len(form2_tot) > 4 else '',
                    'hodfeed4': form2_tot[5] if form2_tot and len(form2_tot) > 5 else '',
                    'hodfeed5': form3_tot[4] if form3_tot and len(form3_tot) > 4 else '',
                    'hodfeed6': form3_tot[5] if form3_tot and len(form3_tot) > 5 else '',
                    'prinas1': int(form1_tot[6]) if form1_tot and len(form1_tot) > 6 and form1_tot[6] is not None else 0,
                    'prinas2': int(form1_tot[7]) if form1_tot and len(form1_tot) > 7 and form1_tot[7] is not None else 0,
                    'prinas3': int(form2_tot[6]) if form2_tot and len(form2_tot) > 6 and form2_tot[6] is not None else 0,
                    'prinas4': int(form2_tot[7]) if form2_tot and len(form2_tot) > 7 and form2_tot[7] is not None else 0,
                    'prinas5': int(form3_tot[6]) if form3_tot and len(form3_tot) > 6 and form3_tot[6] is not None else 0,
                    'prinas6': int(form3_tot[7]) if form3_tot and len(form3_tot) > 7 and form3_tot[7] is not None else 0,
                    'prinfeed1': form1_tot[8] if form1_tot and len(form1_tot) > 8 and form1_tot[8] is not None else '',
                    'prinfeed2': form1_tot[9] if form1_tot and len(form1_tot) > 9 and form1_tot[9] is not None else '',
                    'prinfeed3': form2_tot[8] if form2_tot and len(form2_tot) > 8 and form2_tot[8] is not None else '',
                    'prinfeed4': form2_tot[9] if form2_tot and len(form2_tot) > 9 and form2_tot[9] is not None else '',
                    'prinfeed5': form3_tot[8] if form3_tot and len(form3_tot) > 8 and form3_tot[8] is not None else '',
                    'prinfeed6': form3_tot[9] if form3_tot and len(form3_tot) > 9 and form3_tot[9] is not None else ''
                })
                print(f"[LOG] assessments after totals: {assessments}")

        except Exception as e:
            print(f"Error fetching data in generate_appraisal_html: {e}")
            return f"<h1>Error generating appraisal: {str(e)}</h1>"
        finally:
            connection.close()

    # Ensure user_data is not None before proceeding
    if not user_data:
        print(f"[ERROR] user_data is None, cannot proceed with email generation")
        return "<h1>Error: Unable to fetch user data</h1>"

    # Calculate summary totals
    total_earned_points = (
        points_data['teaching'] +
        points_data['feedback'] +
        points_data['dept'] +
        points_data['institute'] +
        points_data['acr'] +
        points_data['society']
    )
    subject = "Your Appraisal Assessment - Approved"

    # Extract user email from user_data tuple - NOW SAFE
    user_email = user_data[1]
    
    # Create a text version for email clients that don't support HTML
    text_message = '''
    Dear Employee,
    
    We are pleased to inform you that your appraisal form has been reviewed and approved.
    Please find your complete appraisal assessment attached in this email.
    
    Congratulations on your appraisal!
    
    Best Regards,
    HR Team
    '''
    
    # Map fetched data to template variable names for rendering
    department_activities = dept_act_data
    institute_activities = inst_act_data
    self_improvement = self_improvement_data
    certifications = certification_data
    titles = title_data
    resource_person = resource_data
    committee_memberships = committee_data
    external_projects = project_data
    contributions_to_society = contribution_data
    assessments_data = assessments
    # Use finalacr_value instead of assessments['hodas5'] for ACR in HOD total
    total_hod_points = (
        assessments.get('hodas1', 0) + assessments.get('hodas2', 0) +
        assessments.get('hodas3', 0) + assessments.get('hodas4', 0) +
        float(finalacr_value) + assessments.get('hodas6', 0)
    )
    total_principal_points = (
        assessments.get('prinas1', 0) + assessments.get('prinas2', 0) +
        assessments.get('prinas3', 0) + assessments.get('prinas4', 0) +
        assessments.get('prinas5', 0) + assessments.get('prinas6', 0)
    )

    # Render the HTML content for the email
    # Prepare user_name and pass user_id and selected_year for template
    user_name = user_data[3] if user_data else ''
    html_content = render_template(
        'email_appraisal_template.html',
        assessments=assessments,
        teaching_data=teaching_data,
        feedback_data=feedback_data,
        department_activities=department_activities,
        institute_activities=institute_activities,
        self_improvement=self_improvement,
        certifications=certifications,
        titles=titles,
        resource_person=resource_person,
        committee_memberships=committee_memberships,
        external_projects=external_projects,
        contributions_to_society=contributions_to_society,
        user_data=user_data,
        points_data=points_data,
        assessments_data=assessments_data,
        hod_ratings=hod_ratings,
        finalacr_value=finalacr_value,
        total_earned_points=total_earned_points,
        total_hod_points=total_hod_points,
        total_principal_points=total_principal_points,
        current_date=current_date,
        user_id=user_id,
        user_name=user_name,
        selected_year=selected_year,
        moocs_data=moocs_data,
        swayam_data=swayam_data,
        webinar_data=webinar_data
    )
    print('[DEBUG] Rendered appraisal email HTML (truncated):', html_content[:1000])

    # Create the email message with both text and HTML content
    msg = Message(
        subject=subject,
        recipients=[user_email],
        body=text_message,
        html=html_content
    )
    
    # Attach the logo image to the email
   # Attach the logo image to the email for inline display
    # Attach the logo image to the email for inline display
    # Convert image to base64 and embed in HTML
    try:
        import os
        import base64
        
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as fp:
                logo_data = fp.read()
                logo_b64 = base64.b64encode(logo_data).decode('utf-8')
                
            # Pass the base64 string to your template
            html_content = render_template(
                'email_appraisal_template.html',
                # ... your other variables ...
                logo_base64=logo_b64
            )
    except Exception as e:
        print(f'[ERROR] Failed to process logo: {str(e)}')



    
    mail.send(msg)
    return html_content 


@app.route('/about_us')
def aboutus():
    return render_template('aboutus.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to access your profile', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        gmail = request.form.get('gmail')
        dept = request.form.get('dept')
        designation = request.form.get('designation')
        d_o_j = request.form.get('d_o_j')
        dob = request.form.get('dob')
        edu_q = request.form.get('edu_q')
        exp = request.form.get('exp')
        new_userid = request.form.get('userid')
        if not new_userid:
            flash('User ID cannot be empty', 'danger')
            cursor.close()
            connection.close()
            return redirect(url_for('profile'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if email changed and if it's already in use
        cursor.execute("SELECT gmail FROM users WHERE userid != %s AND gmail = %s", (user_id, gmail))
        existing_email = cursor.fetchone()
        if existing_email:
            flash('Email already in use by another user', 'danger')
            cursor.close()
            connection.close()
            return redirect(url_for('profile'))
        
        # Handle password change if provided
        password_update = ""
        if password and password == confirm_password:
            password_update = ", password = %s"
        elif password and password != confirm_password:
            flash('Passwords do not match', 'danger')
            cursor.close()
            connection.close()
            return redirect(url_for('profile'))
        
        # Handle profile image upload if provided
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            file = request.files['profile_image']
            if file and file.filename:
                # Create a secure filename
                filename = str(user_id) + '_' + secure_filename(file.filename)
                filepath = os.path.join('static/profile_images', filename)
                # Save the file
                file.save(filepath)
                
                # Update the user's profile image in the database
                cursor.execute("UPDATE users SET profile_image = %s WHERE userid = %s", (filepath, user_id))
        
        # Validate uniqueness if user ID is changed
        if str(new_userid) != str(user_id):
            cursor.execute("SELECT userid FROM users WHERE userid = %s", (new_userid,))
            existing_userid = cursor.fetchone()
            if existing_userid:
                flash('The new User ID is already taken. Please choose another one.', 'danger')
                cursor.close()
                connection.close()
                return redirect(url_for('profile'))

        # Update user information, including optional User ID change
        update_query = f"UPDATE users SET userid = %s, name = %s, gmail = %s, dept = %s, designation = %s, d_o_j = %s, dob = %s, edu_q = %s, exp = %s{password_update} WHERE userid = %s"
        
        update_values = [new_userid, name, gmail, dept, designation, d_o_j, dob, edu_q, exp]
        if password_update:
            update_values.append(password)
        update_values.append(user_id)
        
        cursor.execute(update_query, update_values)
        
        # If User ID changed, update session
        if str(new_userid) != str(user_id):
            session['user_id'] = new_userid
        connection.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # GET request - display profile
    try:
        cursor.execute("SELECT * FROM users WHERE userid = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('User not found', 'danger')
            return redirect(url_for('login'))
        
        # Check if profile image exists
        profile_image = user_data.get('profile_image', None)
        
        cursor.close()
        connection.close()
        
        return render_template('profile.html', user_data=user_data, profile_image=profile_image)
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('landing'))

@app.route('/delete-institute-row', methods=['POST'])
def delete_institute_row():
    return form2_delete_institute_row(connect_to_database)

@app.route('/delete-dept-row', methods=['POST'])
def delete_dept_row():
    return form2_delete_dept_row(connect_to_database)

@app.route('/save-2total-points', methods=['POST'])
def save_2total_points():
    return form2_save_2total_points(connect_to_database)

@app.route('/form3/<int:form_id>')
def form3_page(form_id):
    return form3_page_handler(connect_to_database, form_id)

@app.route('/save-form3-data', methods=['POST'])
def save_form3_data():
    return form3_save_form3_data(connect_to_database, app, allowed_file)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    return submit_review_handler(connect_to_database)



@app.route('/reset-form2', methods=['POST'])
def reset_form2():
    return form2_reset_form2(connect_to_database)

@app.route('/pastform/<int:form_id>')
def pastform(form_id):
    try:
        # Connect to database
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Get form details
        cursor.execute("SELECT academic_year FROM forms WHERE id = %s", (form_id,))
        form_info = cursor.fetchone()
        selected_year = form_info[0] if form_info else "Unknown"
        
        # Get user data associated with this form
        cursor.execute("""
            SELECT u.id, u.email, u.department, u.name, u.designation, 
                   u.date_of_joining, u.date_of_birth, u.qualification, u.experience
            FROM users u
            JOIN forms f ON u.id = f.user_id
            WHERE f.id = %s
        """, (form_id,))
        user_data = cursor.fetchone()
        
        # Fetch Form 1 data
        cursor.execute("SELECT semester, subject, subject_code, class, type, no_of_students, pass_percentage, feedback FROM teaching_process WHERE form_id = %s", (form_id,))
        form1_data = cursor.fetchall()
        
        # Fetch Form 2 - Department Activities
        cursor.execute("SELECT semester, activity, points, order_cpy FROM department_act WHERE form_id = %s", (form_id,))
        form2_dept_data = cursor.fetchall()
        
        # Fetch Form 2 - Institute Activities
        cursor.execute("SELECT semester, activity, points, order_cpy FROM institute_act WHERE form_id = %s", (form_id,))
        form2_inst_data = cursor.fetchall()
        
        # Fetch custom table data
        custom_table_data = []
        custom_table_title = "Custom Table"
        try:
            # Create custom_table table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    form_id VARCHAR(100),
                    srno VARCHAR(10),
                    columns_data TEXT,
                    headers TEXT,
                    uploads TEXT,
                    table_title VARCHAR(255) DEFAULT 'Custom Table',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Fetch custom table data for the current form_id
            form_id_str = str(form_id)
            cursor.execute("SELECT srno, columns_data, headers, uploads, table_title FROM custom_table WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
            custom_table_rows = cursor.fetchall()
            
            if custom_table_rows:
                # Use the first row's table_title as the display title
                custom_table_title = custom_table_rows[0][4] if len(custom_table_rows[0]) > 4 and custom_table_rows[0][4] else "Custom Table"
                
                for row in custom_table_rows:
                    srno = row[0]
                    columns_data_str = row[1] if len(row) > 1 else '{}'
                    headers_str = row[2] if len(row) > 2 else '[]'
                    uploads_str = row[3] if len(row) > 3 else '{}'
                    
                    try:
                        columns_data = json.loads(columns_data_str) if columns_data_str else {}
                        headers = json.loads(headers_str) if headers_str else []
                        uploads = json.loads(uploads_str) if uploads_str else {}
                        
                        # Merge upload info with text data
                        merged_columns = columns_data.copy()
                        for col_name, file_info in uploads.items():
                            if col_name in merged_columns:
                                merged_columns[col_name] = {
                                    'type': 'file',
                                    'filename': file_info.get('filename', ''),
                                    'filepath': file_info.get('filepath', '')
                                }
                        
                        custom_table_data.append({
                            'srno': srno,
                            'columns_data': json.dumps(merged_columns),
                            'headers': headers
                        })
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON for row {srno}: {e}")
                        continue
        except Exception as e:
            print(f"Error fetching custom table data in pastform: {e}")
        
        cursor.close()
        conn.close()
        
        return render_template('pastform.html', 
                               user_data=user_data, 
                               form_id=form_id, 
                               selected_year=selected_year,
                               form1_data=form1_data,
                               form2_dept_data=form2_dept_data,
                               form2_inst_data=form2_inst_data,
                               custom_table_data=custom_table_data,
                               custom_table_title=custom_table_title)
    except Exception as e:
        print(f"Error fetching past form data: {e}")
        # Initialize custom table data for error state
        custom_table_data = []
        custom_table_title = "Custom Table"
        
        return render_template('pastform.html', 
                               user_data=None, 
                               form_id=form_id,
                               selected_year=None,
                               error=str(e),
                               custom_table_data=custom_table_data,
                               custom_table_title=custom_table_title)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'filename': filename}), 200
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'error': 'Error saving file'}), 500

@app.route('/reset-form3', methods=['POST'])
def reset_form3():
    return form3_reset_form3(connect_to_database)

@app.route('/get_section_scores', methods=['POST'])
def get_section_scores():
    return get_section_scores_handler(connect_to_database)

@app.route('/principlefaculty')
def principlefaculty():
    return principlefaculty_handler()

@app.route('/filter_staff', methods=['GET'])
def filter_staff():
    return filter_staff_handler(connect_to_database)

@app.route('/query_faculty_ratings', methods=['POST'])
def query_faculty_ratings():
    return query_faculty_ratings_handler(connect_to_database)

if __name__ == '__main__':
    # Create email verification table
    create_verification_table()
    # Run the app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)


