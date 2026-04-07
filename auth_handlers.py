import os
import re
from datetime import datetime, timedelta

from flask import flash, redirect, render_template, request, session, url_for
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


def generate_verification_token(serializer, email):
    return serializer.dumps(email, salt='email-verification-salt')


def send_verification_email(mail_client, email, token):
    try:
        if not mail_client:
            print('Email system not initialized')
            return False

        verify_url = url_for('verify_email', token=token, _external=True)
        msg = Message(
            'Confirm Your APSIT Appraisal System Registration',
            recipients=[email],
        )
        msg.body = f'''Thank you for registering with the APSIT Appraisal System.

Please click the link below to verify your email address:
{verify_url}

This link will expire in 24 hours.

If you did not register for an account, please ignore this email.
'''
        mail_client.send(msg)
        print(f'Verification email sent successfully to {email}')
        return True
    except Exception as e:
        print(f'Error sending verification email: {e}')
        return False


def store_verification_token(connect_to_database, user_id, email, token):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                'DELETE FROM email_verification WHERE user_id = %s OR email = %s',
                (user_id, email),
            )
            expires_at = datetime.now() + timedelta(hours=24)
            cursor.execute(
                '''
            INSERT INTO email_verification (user_id, email, token, expires_at)
            VALUES (%s, %s, %s, %s)
            ''',
                (user_id, email, token, expires_at),
            )
            connection.commit()
            return True
        except Exception as e:
            print(f'Error storing verification token: {e}')
            return False
        finally:
            cursor.close()
            connection.close()
    return False


def register(connect_to_database, serializer, mail_client):
    if request.method == 'POST':
        user_id = request.form['userId']
        email_prefix = request.form['emailPrefix']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        role = request.form['role']
        department = request.form['department']

        gmail = email_prefix + '@apsit.edu.in'

        if not user_id or not role or not department:
            flash('User ID, Role, and Department are required fields!', 'error')
            return redirect(url_for('register'))

        email_regex = r'^[a-zA-Z0-9._%+-]+@apsit\.edu\.in$'
        if not re.match(email_regex, gmail):
            flash('Please enter a valid APSIT email address!', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    'SELECT * FROM users WHERE userid = %s OR gmail = %s',
                    (user_id, gmail),
                )
                existing_user = cursor.fetchone()
                if existing_user:
                    flash('User ID or email already exists!', 'error')
                    return redirect(url_for('register'))
            except Exception as e:
                print(f'Error checking existing user: {e}')
            finally:
                cursor.close()
                connection.close()

        token = generate_verification_token(serializer, gmail)
        if store_verification_token(connect_to_database, user_id, gmail, token):
            if send_verification_email(mail_client, gmail, token):
                session['register_data'] = {
                    'user_id': user_id,
                    'gmail': gmail,
                    'password': password,
                    'role': role,
                    'department': department,
                    'verified': False,
                }
                flash(
                    'Please check your email to verify your account before continuing.',
                    'info',
                )
                return render_template('verify_email_sent.html', email=gmail)

            flash('Failed to send verification email. Please try again.', 'error')
            return redirect(url_for('register'))

        flash('Error processing your registration. Please try again.', 'error')
        return redirect(url_for('register'))

    return render_template('signup.html')


def verify_email(connect_to_database, serializer, token):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        cursor.execute(
            'SELECT user_id, email, expires_at FROM email_verification WHERE token = %s',
            (token,),
        )
        token_data = cursor.fetchone()

        if not token_data:
            flash('Invalid or expired verification link.', 'error')
            return redirect(url_for('register'))

        user_id, email, expires_at = token_data

        if datetime.now() > expires_at:
            cursor.execute('DELETE FROM email_verification WHERE token = %s', (token,))
            connection.commit()
            flash('Verification link has expired. Please register again.', 'error')
            return redirect(url_for('register'))

        try:
            email_from_token = serializer.loads(
                token, salt='email-verification-salt', max_age=86400
            )
            if email_from_token != email:
                raise Exception("Token doesn't match email")
        except Exception:
            flash('Invalid verification link.', 'error')
            return redirect(url_for('register'))

        if 'register_data' in session and session['register_data'].get('user_id') == user_id:
            session['register_data']['verified'] = True
            flash('Email verified successfully! Please complete your registration.', 'success')
            return redirect(url_for('details'))

        session['verified_email'] = email
        session['verified_user_id'] = user_id

        cursor.execute('DELETE FROM email_verification WHERE token = %s', (token,))
        connection.commit()

        flash('Email verified successfully! Please complete your registration.', 'success')
        return redirect(url_for('register'))

    except Exception as e:
        print(f'Error in email verification: {e}')
        flash('An error occurred during verification. Please try again.', 'error')
        return redirect(url_for('register'))
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()


def details(connect_to_database):
    if 'register_data' not in session:
        flash('Please complete the registration form first.', 'error')
        return redirect(url_for('register'))

    if not session['register_data'].get('verified', False):
        flash('Please verify your email before continuing.', 'error')
        return redirect(url_for('register'))

    if request.method == 'POST':
        register_data = session.get('register_data')
        user_id = register_data['user_id']

        name = request.form['facultyName']
        designation = request.form['designation']
        doj = request.form['doj']
        dob = request.form['dob']
        qualifications = request.form['qualifications']
        experience = request.form['experience']

        profile_image_path = None
        if 'profile_image' in request.files:
            profile_image = request.files['profile_image']
            if profile_image and profile_image.filename:
                filename = f"{user_id}_{secure_filename(profile_image.filename)}"
                profile_image_path = os.path.join('static/profile_images', filename)
                os.makedirs('static/profile_images', exist_ok=True)
                profile_image.save(profile_image_path)

        if not name or not designation or not doj or not dob:
            flash('All fields are required!', 'error')
            return redirect(url_for('details'))

        connection = connect_to_database()
        if connection is None:
            flash('Could not connect to the database.', 'error')
            return redirect(url_for('details'))

        cursor = connection.cursor()

        try:
            hashed_password = generate_password_hash(register_data['password'])
            query = '''
            INSERT INTO users (userid, gmail, password, role, dept, name, designation, d_o_j, dob, edu_q, exp, profile_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(
                query,
                (
                    register_data['user_id'],
                    register_data['gmail'],
                    hashed_password,
                    register_data['role'],
                    register_data['department'],
                    name,
                    designation,
                    doj,
                    dob,
                    qualifications,
                    experience,
                    profile_image_path,
                ),
            )
            connection.commit()
            flash('Registration successful!', 'success')
            session.pop('register_data', None)
        except Exception as e:
            print(f'Error inserting data into the database: {e}')
            flash(f'An error occurred while registering. Error: {str(e)}', 'error')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('login'))

    return render_template('details.html')


def login(connect_to_database):
    session.pop('_flashes', None)
    if request.method == 'POST':
        username = request.form['loginId']
        gmail = f'{username}@apsit.edu.in'
        password = request.form['password']

        connection = connect_to_database()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE gmail=%s', (gmail,))
            user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['role'] = user[3]

            role = user[3]
            if role == 'Higher Authority':
                flash('Login successful! Redirecting to higher authority landing.', 'info')
                return redirect(url_for('highlanding'))
            if role == 'Faculty':
                flash('Login successful! Redirecting to instructions.', 'info')
                return redirect(url_for('landing'))
            if role == 'Principal':
                flash('Login successful! Redirecting to principal faculty view.', 'info')
                return render_template('principlefaculty.html')
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')
