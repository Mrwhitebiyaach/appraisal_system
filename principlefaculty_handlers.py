from datetime import datetime

from flask import jsonify, redirect, render_template, request, session, url_for


def principlestaff():
    user_id = request.args.get('userid')
    if user_id:
        session['user_id'] = user_id

    user_name = request.args.get('name')
    if user_name:
        session['user_name'] = user_name

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    if current_month > 6 or (current_month == 6 and now.day >= 10):
        start_year = current_year
    else:
        start_year = current_year - 1

    acad_year_options = []
    for i in range(5):
        sy = start_year - i
        ey = sy + 1
        acad_year_options.append(f"{sy}/{str(ey)[-2:]}")

    selected_year = request.args.get('year', acad_year_options[0])
    department = request.args.get('department', '')

    return redirect(url_for('principlefaculty', year=selected_year, department=department))


def principlefaculty():
    user_id = request.args.get('userid')
    if user_id:
        session['user_id'] = user_id

    user_name = request.args.get('name')
    if user_name:
        session['user_name'] = user_name

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    if current_month > 6 or (current_month == 6 and now.day >= 10):
        start_year = current_year
    else:
        start_year = current_year - 1

    acad_year_options = []
    for i in range(5):
        sy = start_year - i
        ey = sy + 1
        acad_year_options.append(f"{sy}/{str(ey)[-2:]}")

    selected_year = request.args.get('year', acad_year_options[0])

    return render_template(
        'principlefaculty.html',
        acad_year_options=acad_year_options,
        selected_year=selected_year,
    )


def filter_faculty(connect_to_database):
    department = request.args.get('department', '')
    selected_year = request.args.get('academic_year', '')
    print(f"Department received: {department}, Academic Year: {selected_year}")

    connection = connect_to_database()
    users = []

    if connection:
        try:
            with connection.cursor() as cursor:
                sql_params = []

                if selected_year and selected_year != '':
                    if department and department != '':
                        sql = """
                            SELECT DISTINCT u.name, u.gmail, u.userid, u.profile_image,
                                   CASE
                                       WHEN t.hodtotal IS NOT NULL AND t.hodtotal != '' THEN 'Completed'
                                       ELSE 'Incomplete'
                                   END as completion_status,
                                   CASE
                                       WHEN a.userid IS NOT NULL THEN 'Approved'
                                       ELSE 'Pending'
                                   END as approval_status
                            FROM total t
                            JOIN users u ON t.user_id = u.userid
                            LEFT JOIN appraisals a ON u.userid = a.userid
                                AND CONVERT(a.acad_year USING utf8mb4) COLLATE utf8mb4_unicode_ci = CONVERT(t.acad_years USING utf8mb4) COLLATE utf8mb4_unicode_ci
                                AND a.form_id = t.form_id
                            WHERE u.dept = %s AND CONVERT(t.acad_years USING utf8mb4) COLLATE utf8mb4_unicode_ci = %s AND u.role = 'Faculty'
                        """
                        sql_params = [department, selected_year]
                    else:
                        sql = """
                            SELECT DISTINCT u.name, u.gmail, u.userid, u.profile_image,
                                   CASE
                                       WHEN t.hodtotal IS NOT NULL AND t.hodtotal != '' THEN 'Completed'
                                       ELSE 'Incomplete'
                                   END as completion_status,
                                   CASE
                                       WHEN a.userid IS NOT NULL THEN 'Approved'
                                       ELSE 'Pending'
                                   END as approval_status
                            FROM total t
                            JOIN users u ON t.user_id = u.userid
                            LEFT JOIN appraisals a ON u.userid = a.userid
                                AND CONVERT(a.acad_year USING utf8mb4) COLLATE utf8mb4_unicode_ci = CONVERT(t.acad_years USING utf8mb4) COLLATE utf8mb4_unicode_ci
                                AND a.form_id = t.form_id
                            WHERE CONVERT(t.acad_years USING utf8mb4) COLLATE utf8mb4_unicode_ci = %s AND u.role = 'Faculty'
                        """
                        sql_params = [selected_year]
                else:
                    if department and department != '':
                        sql = """
                            SELECT DISTINCT u.name, u.gmail, u.userid, u.profile_image,
                                   'Incomplete' as completion_status,
                                   'Pending' as approval_status
                            FROM users u
                            WHERE u.dept = %s AND u.role = 'Faculty'
                        """
                        sql_params = [department]
                    else:
                        sql = """
                            SELECT DISTINCT u.name, u.gmail, u.userid, u.profile_image,
                                   'Incomplete' as completion_status,
                                   'Pending' as approval_status
                            FROM users u
                            WHERE u.role = 'Faculty'
                        """
                        sql_params = []

                cursor.execute(sql, tuple(sql_params))
                users_raw = cursor.fetchall()

                users = []
                if users_raw:
                    for u_tuple in users_raw:
                        if len(u_tuple) == 6:
                            (
                                name,
                                gmail,
                                userid,
                                profile_image_db,
                                completion_status,
                                approval_status,
                            ) = u_tuple
                        else:
                            name, gmail, userid, profile_image_db = u_tuple[:4]
                            completion_status = 'Incomplete'
                            approval_status = 'Pending'

                        processed_profile_image = None
                        if profile_image_db and isinstance(profile_image_db, str):
                            temp_image_path = profile_image_db.strip()
                            normalized_path = temp_image_path.replace('\\', '/')
                            prefix_to_remove = 'static/profile_images/'
                            if normalized_path.startswith(prefix_to_remove):
                                processed_profile_image = normalized_path[len(prefix_to_remove):]
                            elif 'profile_images/' in normalized_path:
                                processed_profile_image = normalized_path.split('profile_images/', 1)[-1]
                            else:
                                processed_profile_image = temp_image_path

                        users.append(
                            [
                                name,
                                gmail,
                                userid,
                                processed_profile_image,
                                '',
                                approval_status,
                                completion_status,
                            ]
                        )

                print(f"Users fetched from DB (processed): {users}")

        except Exception as e:
            print(f"Error querying database: {e}")
            if connection:
                connection.rollback()
            users = []
        finally:
            if connection:
                connection.close()

    return jsonify({'users': users})


def filter_staff(connect_to_database):
    department = request.args.get('department', '')
    selected_year = request.args.get('year', '')
    print(f"Filter_staff route - Department received: {department}, Academic Year: {selected_year}")

    connection = connect_to_database()
    users = []

    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    AND table_name = 'form_status'
                """
                )
                table_exists = cursor.fetchone()[0] > 0

                sql_params = []

                if table_exists:
                    if selected_year and selected_year != '':
                        sql = """
                            SELECT u.name, u.gmail, u.userid, u.profile_image,
                                   CASE
                                       WHEN fs.principal_submitted = 1 THEN 'Completed'
                                       ELSE 'Pending'
                                   END as status
                            FROM users u
                            LEFT JOIN form_status fs ON u.userid = fs.userid
                            LEFT JOIN acad_years ay ON u.userid = ay.user_id
                            WHERE u.dept = %s AND u.role = 'Faculty'
                            AND (ay.acad_years = %s OR ay.acad_years IS NULL)
                        """
                        sql_params = [department, selected_year]
                    else:
                        sql = """
                            SELECT u.name, u.gmail, u.userid, u.profile_image,
                                   CASE
                                       WHEN fs.principal_submitted = 1 THEN 'Completed'
                                       ELSE 'Pending'
                                   END as status
                            FROM users u
                            LEFT JOIN form_status fs ON u.userid = fs.userid
                            WHERE u.dept = %s AND u.role = 'Faculty'
                        """
                        sql_params = [department]
                else:
                    print("form_status table doesn't exist, using default 'Pending' status")
                    if selected_year and selected_year != '':
                        sql = """
                            SELECT u.name, u.gmail, u.userid, u.profile_image, 'Pending' as status
                            FROM users u
                            LEFT JOIN acad_years ay ON u.userid = ay.user_id
                            WHERE u.dept = %s AND u.role = 'Faculty'
                            AND (ay.acad_years = %s OR ay.acad_years IS NULL)
                        """
                        sql_params = [department, selected_year]
                    else:
                        sql = """
                            SELECT name, gmail, userid, 'Pending' as status
                            FROM users
                            WHERE dept = %s AND role = 'Faculty'
                        """
                        sql_params = [department]

                cursor.execute(sql, tuple(sql_params))
                users = cursor.fetchall()
                print(f"Users fetched from DB: {users}")
        except Exception as e:
            print(f"Error querying database: {e}")
            if connection:
                connection.rollback()
            users = []
        finally:
            if connection:
                connection.close()

    return jsonify({'users': users})
