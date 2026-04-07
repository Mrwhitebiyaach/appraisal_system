from flask import jsonify, render_template, request, session
import json
import os
import random
import time
from werkzeug.utils import secure_filename


def submit_academic_year(connect_to_database):
    selected_academic_year = request.form['academicYear']
    user_id = session.get('user_id')

    connection = connect_to_database()
    with connection.cursor() as cursor:
        cursor.execute("SELECT dept FROM users WHERE userid = %s", (user_id,))
        department = cursor.fetchone()

        if not department:
            return "Department not found for the user.", 400

        department = department[0]

        cursor.execute(
            "SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s",
            (user_id, selected_academic_year),
        )
        existing_form = cursor.fetchone()
        if existing_form:
            form_id = existing_form[0]

            cursor.execute(
                "SELECT principle_total, hodtotal FROM total WHERE user_id = %s AND form_id = %s AND acad_years = %s",
                (user_id, form_id, selected_academic_year)
            )
            totals = cursor.fetchone()

            if totals and any(total is not None and total != '' for total in totals):
                connection.close()
                return render_template(
                    'form_locked.html',
                    message="Your appraisal form has been assessed by the Principal or HOD and cannot be edited.",
                    academic_year=selected_academic_year,
                    form_id=form_id,
                )

            cursor.execute(
                """
                SELECT semester, course_code, classes_scheduled, classes_held,
                       (classes_held / classes_scheduled) * 5 AS totalpoints
                FROM teaching_process WHERE form_id = %s
                """,
                (form_id,),
            )
            teaching_data = cursor.fetchall()

            cursor.execute(
                """
                SELECT srno, academic_review1, academic_review2, avg_score
                FROM numeric_points_attained
                WHERE form_id = %s
                ORDER BY srno
                """,
                (form_id,),
            )
            academic_review_data = cursor.fetchall()

            cursor.execute(
                """
                SELECT semester, course_code, total_points, points_obtained, uploads
                FROM students_feedback WHERE form_id = %s
                """,
                (form_id,),
            )
            feedback_data = cursor.fetchall()

        else:
            form_id = random.randint(100000, 999999)
            cursor.execute("SELECT COUNT(*) FROM acad_years WHERE form_id = %s", (form_id,))
            while cursor.fetchone()[0] > 0:
                form_id = random.randint(100000, 999999)

            cursor.execute(
                "INSERT INTO acad_years (form_id, user_id, acad_years) VALUES (%s, %s, %s)",
                (form_id, user_id, selected_academic_year),
            )
            connection.commit()
            teaching_data = []
            feedback_data = []
            academic_review_data = []

    connection.close()

    return render_template(
        'from.html',
        department=department,
        form_id=form_id,
        user_id=user_id,
        teaching_data=teaching_data,
        feedback_data=feedback_data,
        academic_review_data=academic_review_data,
    )


def form_page(connect_to_database, form_id):
    user_id = session.get('user_id')
    department = request.args.get('department')

    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            if not department:
                cursor.execute("SELECT dept FROM users WHERE userid = %s", (user_id,))
                dept_result = cursor.fetchone()
                department = dept_result[0] if dept_result else None

            cursor.execute(
                """
                SELECT semester, course_code, classes_scheduled, classes_held,
                       (classes_held / classes_scheduled) * 5 AS totalpoints
                FROM teaching_process WHERE form_id = %s
                """,
                (form_id,),
            )
            teaching_data = cursor.fetchall()

            cursor.execute(
                """
                SELECT semester, course_code, total_points, points_obtained, uploads
                FROM students_feedback WHERE form_id = %s
                """,
                (form_id,),
            )
            feedback_data = cursor.fetchall()

            cursor.execute(
                """
                SELECT srno, academic_review1, academic_review2, avg_score
                FROM numeric_points_attained
                WHERE form_id = %s
                ORDER BY srno
                """,
                (form_id,),
            )
            academic_review_data = cursor.fetchall()

            return render_template(
                'from.html',
                form_id=form_id,
                user_id=user_id,
                department=department,
                teaching_data=teaching_data,
                feedback_data=feedback_data,
                academic_review_data=academic_review_data,
            )

    except Exception as e:
        print(f"Error in form_page: {e}")
        return "Error loading form data", 500
    finally:
        if connection:
            connection.close()


def save_form_data(connect_to_database, app, allowed_file):
    conn = None
    cursor = None
    teaching_data = []
    feedback_entries = []

    try:
        teaching_data = request.form.get('teachingData')
        form_id = request.form.get('formId')
        feedback_entries = request.form.getlist('feedback[]')
        academic_review_entries = request.form.getlist('academicReview[]')

        deleted_teaching_rows = request.form.get('deletedTeachingRows')
        deleted_feedback_rows = request.form.get('deletedFeedbackRows')
        deleted_academic_review_rows = request.form.get('deletedAcademicReviewRows')

        teaching_data = teaching_data and json.loads(teaching_data) or []
        feedback_entries = [json.loads(entry) if isinstance(entry, str) else entry for entry in feedback_entries]
        academic_review_entries = [json.loads(entry) if isinstance(entry, str) else entry for entry in academic_review_entries]

        deleted_teaching_rows = json.loads(deleted_teaching_rows) if deleted_teaching_rows else []
        deleted_feedback_rows = json.loads(deleted_feedback_rows) if deleted_feedback_rows else []
        deleted_academic_review_rows = json.loads(deleted_academic_review_rows) if deleted_academic_review_rows else []

        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM teaching_process WHERE form_id = %s", (form_id,))
        cursor.execute("DELETE FROM students_feedback WHERE form_id = %s", (form_id,))
        cursor.execute("DELETE FROM numeric_points_attained WHERE form_id = %s", (form_id,))

        for row in teaching_data:
            cursor.execute(
                """
                INSERT INTO teaching_process (form_id, srno, semester, course_code, classes_scheduled, classes_held, totalpoints)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (form_id, row['srno'], row['semester'], row['course'], row['scheduled'], row['held'], row['points']),
            )

        for entry in academic_review_entries:
            srno = entry.get('srno')
            review1 = int(entry.get('review1') or entry.get('academic_review1') or 0)
            review2 = int(entry.get('review2') or entry.get('academic_review2') or 0)
            avg_score = int(entry.get('avgScore') or entry.get('avg_score') or 0)

            cursor.execute(
                """
                INSERT INTO numeric_points_attained (form_id, srno, academic_review1, academic_review2, avg_score)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (form_id, srno, review1, review2, avg_score),
            )

        for index, entry in enumerate(feedback_entries):
            srno = entry['srno']
            semester = str(entry['semester'])
            course = entry['course']
            total_points = entry['totalPoints']
            points_obtained = entry['pointsObtained']

            upload_path = None
            file_key = f'files[{index}]'
            file = request.files.get(file_key)

            if file and allowed_file(file.filename):
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(secure_filename(file.filename))
                unique_filename = f"feedback_{form_id}_{srno}_{timestamp}_{name}{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                upload_path = f"uploads/{unique_filename}"

            cursor.execute(
                """
                INSERT INTO students_feedback (form_id, srno, semester, course_code, total_points, points_obtained, uploads)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (form_id, srno, semester, course, total_points, points_obtained, upload_path),
            )

        conn.commit()
        return jsonify({'status': 'success', 'message': 'Data saved successfully!'})

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while saving data.'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_teaching_row(connect_to_database):
    conn = None
    cursor = None
    try:
        srno = request.form.get('srno')
        form_id = request.form.get('form_id')
        if not srno or not form_id:
            return jsonify({'status': 'error', 'message': 'Sr. No. and Form ID are required'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teaching_process WHERE srno = %s AND form_id = %s", (srno, form_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': f'Teaching row with Sr. No. {srno} and Form ID {form_id} deleted successfully.'})

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while deleting the teaching row.'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_academic_review_row(connect_to_database):
    conn = None
    cursor = None
    try:
        srno = request.form.get('srno')
        form_id = request.form.get('form_id')
        if not srno or not form_id:
            return jsonify({'status': 'error', 'message': 'Sr. No. and Form ID are required'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM numeric_points_attained WHERE srno = %s AND form_id = %s", (srno, form_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': f'Academic Review row with Sr. No. {srno} and Form ID {form_id} deleted successfully.'})

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while deleting the academic review row.'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_feedback_row(connect_to_database):
    conn = None
    cursor = None
    try:
        srno = request.form.get('srno')
        form_id = request.form.get('form_id')
        if not srno or not form_id:
            return jsonify({'status': 'error', 'message': 'Sr. No. and Form ID are required'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students_feedback WHERE srno = %s AND form_id = %s", (srno, form_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': f'Feedback row with Sr. No. {srno} and Form ID {form_id} deleted successfully.'})

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while deleting the feedback row.'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def reset_form(connect_to_database):
    conn = None
    cursor = None
    try:
        form_id = request.form.get('formId')
        if not form_id:
            return jsonify({'status': 'error', 'message': 'Form ID is required'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teaching_process WHERE form_id = %s", (form_id,))
        cursor.execute("DELETE FROM students_feedback WHERE form_id = %s", (form_id,))
        cursor.execute("DELETE FROM numeric_points_attained WHERE form_id = %s", (form_id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Form reset successfully'})

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error resetting form: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while resetting the form.'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_total_point(connect_to_database):
    connection = None
    cursor = None
    try:
        data = request.get_json()
        form_id = data['form_id']
        total = data['total']
        teaching = data['teaching']
        feedback = data['feedback']

        session['current_form_id'] = form_id

        connection = connect_to_database()
        cursor = connection.cursor()

        sql = """
            INSERT INTO form1_tot (form_id, total, teaching, feedback)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE total = VALUES(total), teaching = VALUES(teaching), feedback = VALUES(feedback)
        """
        cursor.execute(sql, (form_id, total, teaching, feedback))
        connection.commit()

        return jsonify({"success": True, "message": "Total points saved successfully."})

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error saving total points: {e}")
        return jsonify({"success": False, "message": "An error occurred while saving total points."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
