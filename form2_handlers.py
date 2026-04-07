from flask import jsonify, render_template, request, session
import os
import time
from werkzeug.utils import secure_filename


def form2_page(connect_to_database, form_id):
    session['current_form_id'] = form_id

    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        dept_sql = """
            SELECT semester, activity, points, order_cpy, uploads, order_no
            FROM department_act
            WHERE form_id = %s
        """
        cursor.execute(dept_sql, (form_id,))
        dept_activities_data = cursor.fetchall()

        inst_sql = """
            SELECT semester, activity, points, order_cpy, uploads, order_no
            FROM institute_act
            WHERE form_id = %s
        """
        cursor.execute(inst_sql, (form_id,))
        institute_activities_data = cursor.fetchall()

        return render_template(
            'form2.html',
            form_id=form_id,
            dept_activities_data=dept_activities_data,
            institute_activities_data=institute_activities_data,
        )
    except Exception as e:
        print(f"Error loading form2 data: {e}")
        return "Error loading form data", 500
    finally:
        cursor.close()
        connection.close()


def save_form2_data(connect_to_database, allowed_file):
    conn = None
    cursor = None

    try:
        if request.form.get('testMode') == 'true':
            return jsonify({'success': True, 'message': 'Test save successful'})

        if request.is_json:
            data = request.get_json()
            form_id = data.get('formId')
        else:
            form_id = request.form.get('formId')

        if not form_id:
            return jsonify({'error': 'Form ID is required'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("START TRANSACTION")

        cursor.execute("SELECT srno, uploads FROM department_act WHERE form_id = %s", (form_id,))
        dept_existing_uploads = {row[0]: row[1] for row in cursor.fetchall() if row[1]}

        cursor.execute("SELECT srno, uploads FROM institute_act WHERE form_id = %s", (form_id,))
        inst_existing_uploads = {row[0]: row[1] for row in cursor.fetchall() if row[1]}

        cursor.execute("DELETE FROM department_act WHERE form_id = %s", (form_id,))
        cursor.execute("DELETE FROM institute_act WHERE form_id = %s", (form_id,))

        department_activities = []
        for key in list(request.form.keys()):
            values = request.form.getlist(key)
            value = values[0] if values else ''
            if key.startswith('departmentActivities'):
                parts = key.split('[')
                if len(parts) >= 3:
                    index = int(parts[1].split(']')[0])
                    while len(department_activities) <= index:
                        department_activities.append({})
                    field_name = parts[2].strip('[').strip(']')
                    department_activities[index][field_name] = value

        for i, activity in enumerate(department_activities):
            if not activity:
                continue

            semester = activity.get('semester', '')
            act_name = activity.get('activity', '')
            points = activity.get('points', 0)
            order_number = activity.get('orderNumber', '')
            order_copy = activity.get('orderCopy', '')
            upload_path = None

            file_key = f'departmentActivities[{i}][file]'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename and allowed_file(file.filename):
                    timestamp = str(int(time.time()))
                    name, ext = os.path.splitext(secure_filename(file.filename))
                    unique_filename = f"dept_{form_id}_{i+1}_{timestamp}_{name}{ext}"
                    upload_path = f'uploads/{unique_filename}'
                    file_path = os.path.join('static', upload_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)

            upload_field_key = f'departmentActivities[{i}][uploaded_file]'
            if not upload_path and upload_field_key in request.form:
                upload_path = request.form[upload_field_key]
            elif not upload_path:
                upload_path = dept_existing_uploads.get(i + 1)

            cursor.execute(
                """
                INSERT INTO department_act (form_id, srno, semester, activity, points, order_cpy, uploads, order_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (form_id, i + 1, semester, act_name, points, order_copy, upload_path, order_number),
            )

        institute_activities = []
        for key in list(request.form.keys()):
            values = request.form.getlist(key)
            value = values[0] if values else ''
            if key.startswith('instituteActivities'):
                parts = key.split('[')
                if len(parts) >= 3:
                    index = int(parts[1].split(']')[0])
                    while len(institute_activities) <= index:
                        institute_activities.append({})
                    field_name = parts[2].strip('[').strip(']')
                    institute_activities[index][field_name] = value

        for i, activity in enumerate(institute_activities):
            if not activity:
                continue

            semester = activity.get('semester', '')
            act_name = activity.get('activity', '')
            points = activity.get('points', 0)
            order_number = activity.get('orderNumber', '')
            order_copy = activity.get('orderCopy', '')
            upload_path = None

            file_key = f'instituteActivities[{i}][file]'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename and allowed_file(file.filename):
                    timestamp = str(int(time.time()))
                    name, ext = os.path.splitext(secure_filename(file.filename))
                    unique_filename = f"inst_{form_id}_{i+1}_{timestamp}_{name}{ext}"
                    upload_path = f'uploads/{unique_filename}'
                    file_path = os.path.join('static', upload_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)

            upload_field_key = f'instituteActivities[{i}][uploaded_file]'
            if not upload_path and upload_field_key in request.form:
                upload_path = request.form[upload_field_key]
            elif not upload_path:
                upload_path = inst_existing_uploads.get(i + 1)

            cursor.execute(
                """
                INSERT INTO institute_act (form_id, srno, semester, activity, points, order_cpy, uploads, order_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (form_id, i + 1, semester, act_name, points, order_copy, upload_path, order_number),
            )

        conn.commit()
        return jsonify({'success': True, 'message': 'Form data saved successfully'})

    except ValueError as ve:
        if conn:
            conn.rollback()
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_institute_row(connect_to_database):
    try:
        data = request.get_json()
        form_id = data.get('form_id')
        srno = data.get('srno')

        if not form_id or srno is None:
            return jsonify({'success': False, 'message': 'Missing form_id or srno'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM institute_act WHERE form_id = %s AND srno = %s", (form_id, srno))
            conn.commit()
            return jsonify({'success': True, 'message': 'Row deleted successfully'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def delete_dept_row(connect_to_database):
    try:
        data = request.get_json()
        form_id = data.get('form_id')
        srno = data.get('srno')

        if not form_id or srno is None:
            return jsonify({'success': False, 'message': 'Missing form_id or srno'}), 400

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM department_act WHERE form_id = %s AND srno = %s", (form_id, srno))
            conn.commit()
            return jsonify({'success': True, 'message': 'Row deleted successfully'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def save_2total_points(connect_to_database):
    connection = None
    cursor = None
    try:
        data = request.get_json()
        form_id = data.get('form_id')
        total = data.get('total')
        dept = data.get('dept')
        institute = data.get('institute')

        if not form_id or total is None:
            return jsonify({"success": False, "message": "Invalid form ID or total points."}), 400

        connection = connect_to_database()
        cursor = connection.cursor()

        sql = """
                INSERT INTO form2_tot (form_id, total, dept, institute)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE total = VALUES(total), dept = VALUES(dept), institute = VALUES(institute)
             """
        cursor.execute(sql, (form_id, total, dept, institute))

        connection.commit()
        return jsonify({"success": True, "message": "Form2 total points saved successfully."})

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def reset_form2(connect_to_database):
    try:
        form_id = request.form.get('formId')

        if not form_id:
            return jsonify({"status": "error", "message": "Form ID is required"}), 400

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            cursor.execute("START TRANSACTION")
            cursor.execute("DELETE FROM department_act WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM institute_act WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM form2_tot WHERE form_id = %s", (form_id,))
            conn.commit()
            return jsonify({"status": "success", "message": "Form data has been reset"})

        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
