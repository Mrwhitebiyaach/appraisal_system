from flask import redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash


def forgotpass_page():
    return render_template('forgotpass.html')


def generate_reset_token(serializer, email):
    return serializer.dumps(email, salt='password-reset-salt')


def send_reset_email(serializer, mail_client, user_email):
    print(f'Sending email to {user_email}')
    token = generate_reset_token(serializer, user_email)
    reset_link = url_for('reset_with_token', token=token, _external=True)

    message = f'''
    Hi,
    To reset your password, click the following link:
    {reset_link}

    If you did not request this, please ignore this email.
    '''

    try:
        mail_client.send_message(
            subject='Password Reset Request', recipients=[user_email], body=message
        )
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')


def reset_with_token(connect_to_database, serializer, token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        return render_template(
            'error.html', message='The reset link is invalid or has expired.'
        )

    if request.method == 'POST':
        new_password = request.form['password']

        connection = connect_to_database()
        try:
            with connection.cursor() as cursor:
                hashed_password = generate_password_hash(new_password)
                sql = 'UPDATE users SET password = %s WHERE gmail = %s'
                cursor.execute(sql, (hashed_password, email))
                connection.commit()

            return redirect(url_for('login', status='reset_success'))
        finally:
            connection.close()

    return render_template('reset_password.html', token=token)


def submit_forgot_password(connect_to_database, serializer, mail_client):
    email = request.form['email']

    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM users WHERE gmail = %s'
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

        if user:
            send_reset_email(serializer, mail_client, email)
            return redirect(url_for('forgotpass', status='success'))

        return redirect(url_for('forgotpass', status='error'))
    finally:
        connection.close()
