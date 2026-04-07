import json
from datetime import date

from flask import jsonify, render_template, request, session


def hodpastform(connect_to_database):
    points_data = {
        'teaching': 0,
        'feedback': 0,
        'dept': 0,
        'institute': 0,
        'acr': 0,
        'society': 0,
    }
    assessments = {
        'hodas1': 0,
        'hodas2': 0,
        'hodas3': 0,
        'hodas4': 0,
        'hodas5': 0,
        'hodas6': 0,
        'hodfeed1': '',
        'hodfeed2': '',
        'hodfeed3': '',
        'hodfeed4': '',
        'hodfeed5': '',
        'hodfeed6': '',
        'feedback': '',
    }
    user_id = request.args.get('userid')
    session['user_id'] = user_id

    user_name = request.args.get('name')
    session['user_name'] = user_name

    department = request.args.get('department')
    if department:
        session['department'] = department

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
    default_academic_year = f"{start_year}/{str(end_year)[-2:]}"

    connection = connect_to_database()
    teaching_data, feedback_data, dept_act_data, inst_act_data = [], [], [], []
    self_improvement_data, certification_data, title_data = [], [], []
    resource_data, committee_data, project_data, contribution_data = [], [], [], []
    moocs_data, swayam_data, webinar_data = [], [], []

    if connection and user_id:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s',
                    (user_id, default_academic_year),
                )
                result = cursor.fetchone()

                if result:
                    form_id = result[0]

                    cursor.execute(
                        '''
                        SELECT semester, course_code, classes_scheduled, classes_held,
                               (classes_held / classes_scheduled) * 5 AS totalpoints
                        FROM teaching_process
                        WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    teaching_data = cursor.fetchall()

                    cursor.execute(
                        '''
                        SELECT semester, course_code, total_points, points_obtained, uploads
                        FROM students_feedback
                        WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    feedback_data = cursor.fetchall()

                    cursor.execute(
                        '''
                        SELECT semester, activity, points, order_cpy, uploads
                        FROM department_act
                        WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    dept_act_data = cursor.fetchall()

                    cursor.execute(
                        '''
                        SELECT semester, activity, points, order_cpy, uploads
                        FROM institute_act
                        WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    inst_act_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT title, month, name_of_conf, issn, co_auth, imp_conference, num_of_citations, rating FROM self_imp WHERE form_id = %s',
                        (form_id,),
                    )
                    self_improvement_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT name, uploads FROM certifications WHERE form_id = %s',
                        (form_id,),
                    )
                    certification_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT name, month, reg_no FROM copyright WHERE form_id = %s',
                        (form_id,),
                    )
                    title_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT name, dept, name_oi, num_op FROM resource_person WHERE form_id = %s',
                        (form_id,),
                    )
                    resource_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT name, roles, designation FROM mem_uni WHERE form_id = %s',
                        (form_id,),
                    )
                    committee_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT role, `desc`, contribution, university, duration, comments FROM external_projects WHERE form_id = %s',
                        (form_id,),
                    )
                    project_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT semester, activity, points, order_cpy, uploads FROM contribution_to_society WHERE form_id = %s',
                        (form_id,),
                    )
                    contribution_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT srno, name, month, duration, completion FROM moocs WHERE form_id = %s',
                        (form_id,),
                    )
                    moocs_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT srno, name, month, duration, completion FROM swayam WHERE form_id = %s',
                        (form_id,),
                    )
                    swayam_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT srno, name, technology, duration, date, int_ext, name_of_institute FROM webinar WHERE form_id = %s',
                        (form_id,),
                    )
                    webinar_data = cursor.fetchall()

                    cursor.execute(
                        'SELECT teaching, feedback FROM form1_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    form1_tot = cursor.fetchone()

                    cursor.execute(
                        'SELECT dept, institute FROM form2_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    form2_tot = cursor.fetchone()

                    cursor.execute(
                        'SELECT acr, society FROM form3_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    form3_tot = cursor.fetchone()

                    points_data = {
                        'teaching': int(form1_tot[0]) if form1_tot and form1_tot[0] else 0,
                        'feedback': int(form1_tot[1]) if form1_tot and form1_tot[1] else 0,
                        'dept': int(form2_tot[0]) if form2_tot and form2_tot[0] else 0,
                        'institute': int(form2_tot[1]) if form2_tot and form2_tot[1] else 0,
                        'acr': int(form3_tot[0]) if form3_tot and form3_tot[0] else 0,
                        'society': int(form3_tot[1]) if form3_tot and form3_tot[1] else 0,
                    }

                    cursor.execute(
                        'SELECT hodas1, hodas2, hodfeed1, hodfeed2 FROM form1_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    hod_form1 = cursor.fetchone()
                    if hod_form1:
                        assessments['hodas1'] = (
                            int(hod_form1[0]) if hod_form1[0] is not None else 0
                        )
                        assessments['hodas2'] = (
                            int(hod_form1[1]) if hod_form1[1] is not None else 0
                        )
                        assessments['hodfeed1'] = (
                            hod_form1[2] if hod_form1[2] is not None else ''
                        )
                        assessments['hodfeed2'] = (
                            hod_form1[3] if hod_form1[3] is not None else ''
                        )

                    cursor.execute(
                        'SELECT hodas3, hodas4, hodfeed3, hodfeed4 FROM form2_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    hod_form2 = cursor.fetchone()
                    if hod_form2:
                        assessments['hodas3'] = (
                            int(hod_form2[0]) if hod_form2[0] is not None else 0
                        )
                        assessments['hodas4'] = (
                            int(hod_form2[1]) if hod_form2[1] is not None else 0
                        )
                        assessments['hodfeed3'] = (
                            hod_form2[2] if hod_form2[2] is not None else ''
                        )
                        assessments['hodfeed4'] = (
                            hod_form2[3] if hod_form2[3] is not None else ''
                        )

                    cursor.execute(
                        'SELECT hodas5, hodas6, hodfeed5, hodfeed6 FROM form3_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    hod_form3 = cursor.fetchone()
                    if hod_form3:
                        assessments['hodas5'] = (
                            int(hod_form3[0]) if hod_form3[0] is not None else 0
                        )
                        assessments['hodas6'] = (
                            int(hod_form3[1]) if hod_form3[1] is not None else 0
                        )
                        assessments['hodfeed5'] = (
                            hod_form3[2] if hod_form3[2] is not None else ''
                        )
                        assessments['hodfeed6'] = (
                            hod_form3[3] if hod_form3[3] is not None else ''
                        )

                    cursor.execute('SELECT feedback FROM feedback WHERE form_id = %s', (form_id,))
                    feedback_result = cursor.fetchone()
                    if feedback_result and feedback_result[0]:
                        assessments['feedback'] = feedback_result[0]

                    cursor.execute(
                        '''
                        SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp
                        FROM users WHERE userid = %s
                    ''',
                        (user_id,),
                    )
                    user_data = cursor.fetchone()
                    print(f'Debug - User Data in hodpastform default year: {user_data}')

                    finalacr_value = 0
                    cursor.execute(
                        'SELECT finalacr FROM form3_tot WHERE form_id = %s', (form_id,)
                    )
                    finalacr_row = cursor.fetchone()
                    if finalacr_row and finalacr_row[0] is not None:
                        finalacr_value = int(finalacr_row[0])

                    custom_table_data = []
                    custom_table_title = 'Custom Table'
                    try:
                        cursor.execute(
                            '''
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
                        '''
                        )

                        form_id_str = str(form_id)
                        cursor.execute(
                            'SELECT srno, columns_data, headers, uploads, table_title FROM custom_table WHERE form_id = %s ORDER BY srno ASC',
                            (form_id_str,),
                        )
                        custom_table_rows = cursor.fetchall()

                        if custom_table_rows:
                            custom_table_title = (
                                custom_table_rows[0][4]
                                if len(custom_table_rows[0]) > 4
                                and custom_table_rows[0][4]
                                else 'Custom Table'
                            )

                            for row in custom_table_rows:
                                srno = row[0]
                                columns_data_str = row[1] if len(row) > 1 else '{}'
                                headers_str = row[2] if len(row) > 2 else '[]'
                                uploads_str = row[3] if len(row) > 3 else '{}'

                                try:
                                    columns_data = (
                                        json.loads(columns_data_str)
                                        if columns_data_str
                                        else {}
                                    )
                                    headers = (
                                        json.loads(headers_str) if headers_str else []
                                    )
                                    uploads = (
                                        json.loads(uploads_str) if uploads_str else {}
                                    )

                                    merged_columns = columns_data.copy()
                                    for col_name, upload_path in uploads.items():
                                        if col_name in merged_columns:
                                            merged_columns[col_name] = {
                                                'type': 'file',
                                                'filename': file_info.get('filename', ''),
                                                'filepath': file_info.get('filepath', ''),
                                            }

                                    custom_table_data.append(
                                        {
                                            'srno': srno,
                                            'columns_data': json.dumps(merged_columns),
                                            'headers': headers,
                                        }
                                    )

                                except json.JSONDecodeError as e:
                                    print(f'Error parsing JSON for row {srno}: {e}')
                                    continue
                    except Exception as e:
                        print(f'Error fetching custom table data in hodpastform: {e}')

                    return render_template(
                        'hodpastform.html',
                        user_id=user_id,
                        user_name=user_name,
                        points_data=points_data,
                        assessments=assessments,
                        department=department if department else (user_data[2] if user_data else None),
                        selected_year=default_academic_year,
                        form_id=form_id,
                        teaching_data=teaching_data,
                        feedback_data=feedback_data,
                        dept_act_data=dept_act_data,
                        inst_act_data=inst_act_data,
                        user_data=user_data,
                        finalacr_value=finalacr_value,
                        custom_table_data=custom_table_data,
                        custom_table_title=custom_table_title,
                    )
        except Exception as e:
            print(f'Error loading default data: {e}')
        finally:
            connection.close()

    user_data = None
    connection = connect_to_database()
    if connection and user_id:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp
                    FROM users WHERE userid = %s
                ''',
                    (user_id,),
                )
                user_data = cursor.fetchone()
                print(f'Debug - User Data in hodpastform: {user_data}')
                print(f'Debug - User ID: {user_id}')
        except Exception as e:
            print(f'Error fetching user data: {str(e)}')
            user_data = None
        finally:
            connection.close()

    print('Debug - About to render initial hodpastform template with:')
    print(f'Debug - user_data: {user_data}')
    print(f'Debug - user_id: {user_id}')

    finalacr_value = 0

    custom_table_data = []
    custom_table_title = 'Custom Table'

    return render_template(
        'hodpastform.html',
        user_id=user_id,
        user_name=user_name,
        points_data=points_data,
        assessments=assessments,
        department=department if department else (user_data[2] if user_data else None),
        user_data=user_data,
        finalacr_value=finalacr_value,
        custom_table_data=custom_table_data,
        custom_table_title=custom_table_title,
    )


def search_pastforms2(connect_to_database):
    points_data = {
        'teaching': 0,
        'feedback': 0,
        'dept': 0,
        'institute': 0,
        'acr': 0,
        'society': 0,
    }

    assessments = {
        'hodas1': 0,
        'hodas2': 0,
        'hodas3': 0,
        'hodas4': 0,
        'hodas5': 0,
        'hodas6': 0,
        'hodfeed1': '',
        'hodfeed2': '',
        'hodfeed3': '',
        'hodfeed4': '',
        'hodfeed5': '',
        'hodfeed6': '',
        'feedback': '',
    }

    finalacr_value = 0
    self_assessment_marks = ''
    user_id = session.get('user_id')
    selected_year = request.form.get('academicYear')

    no_data_found = False

    if not user_id or not selected_year:
        return jsonify({'success': False, 'message': 'User ID or Academic Year is missing!'})

    teaching_data, feedback_data, dept_act_data, inst_act_data = [], [], [], []
    academic_review_data = []
    self_improvement_data, certification_data, resource_data = [], [], []
    committee_data, project_data, contribution_data = [], [], []
    moocs_data, swayam_data, webinar_data = [], [], []
    training_data, patent_data, conference_committee_data = [], [], []
    special_mentions_data, copyright_data = [], []

    def process_rows(rows):
        if not rows:
            return []
        processed = []
        for row in rows:
            processed_row = tuple('' if val is None else val for val in row)
            processed.append(processed_row)
        return processed

    connection = connect_to_database()

    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s',
                    (user_id, selected_year),
                )
                result = cursor.fetchone()

                if not result:
                    no_data_found = True
                    form_id = None
                else:
                    form_id = result[0]

                    cursor.execute(
                        '''
                        SELECT semester, course_code, classes_scheduled, classes_held,
                        (classes_held/classes_scheduled)*5 AS totalpoints
                        FROM teaching_process WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    teaching_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, course_code, total_points, points_obtained, uploads
                        FROM students_feedback WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    feedback_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, activity, points, order_cpy, uploads
                        FROM department_act WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    dept_act_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, activity, points, order_cpy, uploads
                        FROM institute_act WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    inst_act_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, academic_review1, academic_review2, avg_score
                        FROM numeric_points_attained
                        WHERE form_id = %s
                        ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    academic_review_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, title, month, name_of_conf, issn, co_auth, imp_conference,
                               num_of_citations, rating, uploads
                        FROM self_imp WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    self_improvement_data = process_rows(cursor.fetchall())

                    cursor.execute('SELECT * FROM certifications WHERE form_id = %s', (form_id,))
                    certification_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, technology, duration, date, organizing_institute, mode, upload
                        FROM short_term_training WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    training_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, month, duration, completion, upload
                        FROM moocs WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    moocs_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, month, duration, completion, upload
                        FROM swayam WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    swayam_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, technology, duration, date, int_ext, name_of_institute, upload
                        FROM webinar WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    webinar_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, month, reg_no, filed_pub_grant, category, uploads
                        FROM copyright WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    copyright_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, month, reg_no, filed_pub_grant, category, uploads
                        FROM patents WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    patent_data = process_rows(cursor.fetchall())

                    cursor.execute('SELECT * FROM resource_person WHERE form_id = %s', (form_id,))
                    resource_data = process_rows(cursor.fetchall())

                    cursor.execute('SELECT * FROM mem_uni WHERE form_id = %s', (form_id,))
                    committee_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, designation, upload
                        FROM members_conference WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    conference_committee_data = process_rows(cursor.fetchall())
                    print('Conference Committee Data:', conference_committee_data)

                    cursor.execute('SELECT * FROM external_projects WHERE form_id = %s', (form_id,))
                    project_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, activity, points, order_cpy, details, uploads
                        FROM contribution_to_society WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    contribution_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT srno, name, roles, uploads
                        FROM special_mentions WHERE form_id = %s ORDER BY srno
                    ''',
                        (form_id,),
                    )
                    special_mentions_data = process_rows(cursor.fetchall())
                    print('Special Mentions Data:', special_mentions_data)

                    cursor.execute(
                        '''
                        SELECT self_assessment_marks
                        FROM form3_assessment
                        WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    sa_result = cursor.fetchone()
                    self_assessment_marks = sa_result[0] if sa_result and sa_result[0] else ''

                    cursor.execute(
                        '''
                        SELECT teaching, feedback, hodas1, hodas2, hodfeed1, hodfeed2
                        FROM form1_tot WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    form1_tot = cursor.fetchone()

                    cursor.execute(
                        '''
                        SELECT dept, institute, hodas3, hodas4, hodfeed3, hodfeed4
                        FROM form2_tot WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    form2_tot = cursor.fetchone()

                    cursor.execute(
                        '''
                        SELECT acr, society, hodas5, hodas6, hodfeed5, hodfeed6, finalacr
                        FROM form3_tot WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    form3_tot = cursor.fetchone()

                    points_data = {
                        'teaching': int(form1_tot[0]) if form1_tot and form1_tot[0] else 0,
                        'feedback': int(form1_tot[1]) if form1_tot and form1_tot[1] else 0,
                        'dept': int(form2_tot[0]) if form2_tot and form2_tot[0] else 0,
                        'institute': int(form2_tot[1]) if form2_tot and form2_tot[1] else 0,
                        'acr': int(form3_tot[0]) if form3_tot and form3_tot[0] else 0,
                        'society': int(form3_tot[1]) if form3_tot and form3_tot[1] else 0,
                    }

                    if form1_tot:
                        assessments.update(
                            {
                                'hodas1': int(form1_tot[2]) if form1_tot[2] is not None else 0,
                                'hodas2': int(form1_tot[3]) if form1_tot[3] is not None else 0,
                                'hodfeed1': form1_tot[4] if form1_tot[4] else '',
                                'hodfeed2': form1_tot[5] if form1_tot[5] else '',
                            }
                        )

                    if form2_tot:
                        assessments.update(
                            {
                                'hodas3': int(form2_tot[2]) if form2_tot[2] is not None else 0,
                                'hodas4': int(form2_tot[3]) if form2_tot[3] is not None else 0,
                                'hodfeed3': form2_tot[4] if form2_tot[4] else '',
                                'hodfeed4': form2_tot[5] if form2_tot[5] else '',
                            }
                        )

                    if form3_tot:
                        assessments.update(
                            {
                                'hodas5': int(form3_tot[2]) if form3_tot[2] is not None else 0,
                                'hodas6': int(form3_tot[3]) if form3_tot[3] is not None else 0,
                                'hodfeed5': form3_tot[4] if form3_tot[4] else '',
                                'hodfeed6': form3_tot[5] if form3_tot[5] else '',
                            }
                        )
                        finalacr_value = (
                            int(form3_tot[6])
                            if form3_tot and form3_tot[6] is not None
                            else 0
                        )

                    cursor.execute('SELECT feedback FROM feedback WHERE form_id = %s', (form_id,))
                    feedback_result = cursor.fetchone()
                    if feedback_result and feedback_result[0]:
                        assessments['feedback'] = feedback_result[0]

    except Exception as e:
        print(f'Error in search_pastforms2: {e}')
        return jsonify(
            {
                'success': False,
                'message': f'An error occurred while fetching data: {str(e)}',
            }
        )

    finally:
        if connection:
            connection.close()

    user_data = None
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp
                    FROM users WHERE userid = %s
                ''',
                    (user_id,),
                )
                user_data = cursor.fetchone()
        except Exception as e:
            print(f'Error fetching user data: {str(e)}')
        finally:
            connection.close()

    user_name = user_data[3] if user_data and len(user_data) > 3 else 'N/A'
    user_dept = user_data[2] if user_data and len(user_data) > 2 else 'N/A'

    custom_table_data = []
    custom_table_title = 'Custom Table'
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
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
                '''
                )

                if not no_data_found:
                    form_id_str = str(form_id)
                    cursor.execute(
                        'SELECT srno, columns_data, headers, uploads, table_title FROM custom_table WHERE form_id = %s ORDER BY srno ASC',
                        (form_id_str,),
                    )
                    custom_table_rows = cursor.fetchall()

                    if custom_table_rows:
                        custom_table_title = (
                            custom_table_rows[0][4]
                            if len(custom_table_rows[0]) > 4 and custom_table_rows[0][4]
                            else 'Custom Table'
                        )

                        for row in custom_table_rows:
                            srno = row[0]
                            columns_data_str = row[1] if len(row) > 1 else '{}'
                            headers_str = row[2] if len(row) > 2 else '[]'
                            uploads_str = row[3] if len(row) > 3 else '{}'

                            try:
                                columns_data = (
                                    json.loads(columns_data_str)
                                    if columns_data_str
                                    else {}
                                )
                                headers = (
                                    json.loads(headers_str) if headers_str else []
                                )
                                uploads = (
                                    json.loads(uploads_str) if uploads_str else {}
                                )

                                merged_columns = columns_data.copy()
                                for col_name, upload_path in uploads.items():
                                    if col_name in merged_columns:
                                        merged_columns[col_name] = {
                                            'text': merged_columns[col_name],
                                            'upload': upload_path,
                                        }
                                    else:
                                        merged_columns[col_name] = {
                                            'text': '',
                                            'upload': upload_path,
                                        }

                                custom_table_data.append(
                                    {
                                        'srno': srno,
                                        'columns_data': json.dumps(merged_columns),
                                        'headers': headers,
                                    }
                                )

                            except json.JSONDecodeError as e:
                                print(f'Error parsing JSON for row {srno}: {e}')
                                continue
        except Exception as e:
            print(f'Error fetching custom table data in search_pastforms2: {e}')
        finally:
            connection.close()

    academic_years = []
    connection = connect_to_database()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT DISTINCT acad_years FROM acad_years WHERE user_id = %s ORDER BY acad_years DESC',
                    (user_id,),
                )
                academic_years = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f'Error fetching academic years: {e}')
        finally:
            connection.close()

    return render_template(
        'hodpastform.html',
        teaching_data=teaching_data,
        feedback_data=feedback_data,
        academic_review_data=academic_review_data,
        dept_act_data=dept_act_data,
        inst_act_data=inst_act_data,
        points_data=points_data,
        self_improvement_data=self_improvement_data,
        certification_data=certification_data,
        training_data=training_data,
        moocs_data=moocs_data,
        swayam_data=swayam_data,
        webinar_data=webinar_data,
        copyright_data=copyright_data,
        patent_data=patent_data,
        resource_data=resource_data,
        committee_data=committee_data,
        conference_committee_data=conference_committee_data,
        project_data=project_data,
        contribution_data=contribution_data,
        special_mentions_data=special_mentions_data,
        selected_year=selected_year,
        form_id=form_id,
        user_name=user_name,
        assessments=assessments,
        user_id=user_id,
        user_data=user_data,
        department=user_dept,
        finalacr_value=finalacr_value,
        self_assessment_marks=self_assessment_marks,
        custom_table_data=custom_table_data,
        custom_table_title=custom_table_title,
        academic_years=academic_years,
        no_data_found=no_data_found,
    )
