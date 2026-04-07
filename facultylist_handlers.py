from datetime import date

from flask import render_template, request, session


def facultylist(connect_to_database):
    user_id = session.get('user_id')
    department = request.args.get('department')
    selected_year = request.args.get('year')
    print(f"Department received: {department}")

    connection = connect_to_database()
    users = []
    status_list = []
    acad_year_options = []

    # Dynamically determine current academic year (ends first week of June)
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    if (month > 6) or (month == 6 and day > 7):
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year
    current_acad_year = f"{start_year}/{str(end_year)[-2:]}"
    print(f"Detected current academic year: {current_acad_year}")

    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT acad_years FROM acad_years ORDER BY acad_years DESC")
                all_years = [row[0] for row in cursor.fetchall()]

                acad_year_options = []
                for y in all_years:
                    try:
                        db_start, db_end = y.replace('-', '/').split('/') if '-' in y else y.split('/')
                        db_start, db_end = int(db_start), int(db_end)
                        curr_start, curr_end = (
                            current_acad_year.replace('-', '/').split('/')
                            if '-' in current_acad_year
                            else current_acad_year.split('/')
                        )
                        curr_start, curr_end = int(curr_start), int(curr_end)
                        if (db_start < curr_start) or (
                            db_start == curr_start and db_end <= curr_end
                        ):
                            acad_year_options.append(y)
                    except Exception as e:
                        print(f"Error parsing academic year: {y} | {e}")

                sql = "SELECT name, gmail, userid, profile_image FROM users WHERE dept = %s AND role = 'Faculty'"
                cursor.execute(sql, (department,))
                users_raw = cursor.fetchall()
                users = []
                if users_raw:
                    for u_tuple in users_raw:
                        name, gmail, userid, profile_image_db = (
                            u_tuple[0],
                            u_tuple[1],
                            u_tuple[2],
                            u_tuple[3],
                        )
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
                        users.append((name, gmail, userid, processed_profile_image))
                print(f"Users fetched from DB (processed): {users}")

                filter_year = selected_year if selected_year else current_acad_year
                print(f"Filtering by academic year: {filter_year}")

                for user in users:
                    uid = user[2]
                    sql_form_id = "SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s"
                    cursor.execute(sql_form_id, (uid, filter_year))
                    form_id_row = cursor.fetchone()
                    if form_id_row:
                        form_id = form_id_row[0]
                        sql_total = "SELECT COUNT(*) FROM total WHERE form_id = %s"
                        cursor.execute(sql_total, (form_id,))
                        total_filled = cursor.fetchone()[0]
                        status_list.append("Completed" if total_filled > 0 else "Pending")
                    else:
                        status_list.append("Pending")
        except Exception as e:
            print(f"Error querying database: {e}")
        finally:
            connection.close()

    user_statuses = list(zip(users, status_list))
    return render_template(
        'facultylist.html',
        department=department,
        user_statuses=user_statuses,
        acad_year_options=acad_year_options,
        selected_year=selected_year if selected_year else current_acad_year,
    )
