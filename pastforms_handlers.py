import json

from flask import flash, redirect, render_template, request, session, url_for
from datetime import date


def render_pastforms(connect_to_database):
    user_id = session.get('user_id')
    connection = connect_to_database()
    assessments = {}

    try:
        with connection.cursor() as cursor:
            query = 'SELECT COUNT(*) FROM acad_years WHERE user_id = %s'
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result[0] == 0:
                flash('You have no past forms filled.', 'warning')
                return redirect(url_for('landing'))

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

            cursor.execute(
                'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s',
                (user_id, default_academic_year),
            )
            form_result = cursor.fetchone()

            if form_result:
                form_id = form_result[0]

                cursor.execute(
                    '''
                SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp, profile_image
                FROM users
                WHERE userid = %s
                ''',
                    (user_id,),
                )
                user_data = cursor.fetchone()

                profile_image = (
                    user_data.get('profile_image')
                    if user_data and 'profile_image' in user_data
                    else None
                )

                cursor.execute(
                    '''
                    SELECT semester, course_code, classes_scheduled, classes_held,
                    (classes_held/classes_scheduled)*5 AS totalpoints
                    FROM teaching_process WHERE form_id = %s
                ''',
                    (form_id,),
                )
                teaching_data = cursor.fetchall()

                cursor.execute(
                    '''
                    SELECT semester, course_code, total_points, points_obtained, uploads
                    FROM students_feedback WHERE form_id = %s
                ''',
                    (form_id,),
                )
                feedback_data = cursor.fetchall()

                cursor.execute(
                    '''
                    SELECT semester, activity, points, order_cpy, uploads
                    FROM department_act WHERE form_id = %s
                ''',
                    (form_id,),
                )
                dept_act_data = cursor.fetchall()

                cursor.execute(
                    '''
                    SELECT semester, activity, points, order_cpy, uploads
                    FROM institute_act WHERE form_id = %s
                ''',
                    (form_id,),
                )
                inst_act_data = cursor.fetchall()

                def process_rows(rows):
                    return [tuple('' if val is None else val for val in row) for row in rows]

                cursor.execute(
                    'SELECT srno, title, month, name_of_conf, issn, co_auth, imp_conference, num_of_citations, rating, uploads FROM self_imp WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                self_improvement_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, upload FROM certifications WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                certification_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, month, duration, completion, upload FROM training WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                training_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, month, duration, completion, upload FROM moocs WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                moocs_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, month, duration, completion, upload FROM swayam WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                swayam_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, technology, duration, date, int_ext, name_of_institute, upload FROM webinar WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                webinar_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, month, reg_no, status, category, upload FROM copyright WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                copyright_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, month, reg_no, status, category, upload FROM patent WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                patent_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, dept, name_oi, num_op, upload FROM resource_person WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                resource_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, roles, designation, upload FROM mem_uni WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                committee_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, designation, upload FROM members_conference WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                conference_committee_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, role, `desc`, contribution, university, duration, comments, upload FROM external_projects WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                project_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT srno, name, upload FROM special_mention WHERE form_id = %s ORDER BY srno ASC',
                    (form_id,),
                )
                special_mentions_data = process_rows(cursor.fetchall())

                cursor.execute(
                    'SELECT semester, activity, points, order_cpy, details, uploads FROM contribution_society WHERE form_id = %s',
                    (form_id,),
                )
                contribution_data = process_rows(cursor.fetchall())

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
                    'SELECT self_assessment_marks FROM form3_assessment WHERE form_id = %s',
                    (form_id,),
                )
                self_assessment_result = cursor.fetchone()
                self_assessment_marks = (
                    self_assessment_result[0] if self_assessment_result else ''
                )

                points_data = {
                    'teaching': sum(row[4] for row in teaching_data) if teaching_data else 0,
                    'feedback': sum(float(row[3]) for row in feedback_data)
                    if feedback_data
                    else 0,
                    'dept': sum(float(row[2]) for row in dept_act_data)
                    if dept_act_data
                    else 0,
                    'institute': sum(float(row[2]) for row in inst_act_data)
                    if inst_act_data
                    else 0,
                    'acr': sum(float(row[3]) for row in academic_review_data)
                    if academic_review_data
                    else 0,
                    'society': sum(float(row[2]) for row in contribution_data)
                    if contribution_data
                    else 0,
                }

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

                cursor.execute(
                    'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s',
                    (user_id, default_academic_year),
                )
                form_id_result = cursor.fetchone()

                if form_id_result:
                    form_id = form_id_result[0]
                    print(
                        f'Found form_id: {form_id} for user_id: {user_id}, acad_years: {default_academic_year}'
                    )

                    cursor.execute(
                        'SELECT hodas1, hodas2, hodfeed1, hodfeed2 FROM form1_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    hod_form1 = cursor.fetchone()
                    if hod_form1:
                        print(f'Found form1_tot HOD data: {hod_form1}')
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
                        print(f'Found form2_tot HOD data: {hod_form2}')
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
                        print(f'Found form3_tot HOD data: {hod_form3}')
                        assessments['hodas5'] = (
                            int(hod_form3[0]) if hod_form3[0] is not None else 0
                        )
                        assessments['hodas6'] = (
                            int(hod_form3[1]) if hod_form3[1] is not None else 0
                        )
                        assessments['hodfeed5'] = (
                            hod_form3[2] if hod_form3[2] is not None else ''
                        )

                cursor.execute('SELECT * FROM hod_assessment WHERE form_id = %s', (form_id,))
                hod_assessment = cursor.fetchone()
                if hod_assessment:
                    assessments = {
                        'hodas1': hod_assessment[2],
                        'hodfeed1': hod_assessment[3],
                        'hodas2': hod_assessment[4],
                        'hodfeed2': hod_assessment[5],
                        'hodas3': hod_assessment[6],
                        'hodfeed3': hod_assessment[7],
                        'hodas4': hod_assessment[8],
                        'hodfeed4': hod_assessment[9],
                        'hodas5': hod_assessment[10],
                        'hodfeed5': hod_assessment[11],
                        'hodas6': hod_assessment[12],
                        'hodfeed6': hod_assessment[13],
                        'feedback': hod_assessment[14],
                    }

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
                    print(f'Error fetching custom table data in render_pastforms: {e}')

                return render_template(
                    'principlepast.html',
                    user_id=user_id,
                    user_name=user_data[3],
                    user_data=user_data,
                    selected_year=default_academic_year,
                    form_id=form_id,
                    teaching_data=teaching_data,
                    feedback_data=feedback_data,
                    dept_act_data=dept_act_data,
                    inst_act_data=inst_act_data,
                    self_improvement_data=self_improvement_data,
                    certification_data=certification_data,
                    title_data=title_data,
                    resource_data=resource_data,
                    committee_data=committee_data,
                    conference_committee_data=conference_committee_data,
                    project_data=project_data,
                    contribution_data=contribution_data,
                    special_mentions_data=special_mentions_data,
                    moocs_data=moocs_data,
                    swayam_data=swayam_data,
                    webinar_data=webinar_data,
                    points_data=points_data,
                    assessments=assessments,
                    finalacr_value=0,
                    hod_ratings=[],
                    extra_feedback='',
                    custom_table_data=custom_table_data,
                    custom_table_title=custom_table_title,
                    profile_image=profile_image,
                )
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        connection.close()

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
    custom_table_data = []
    custom_table_title = 'Custom Table'

    return render_template(
        'pastforms.html',
        teaching_data=[],
        selected_year=None,
        user_data=None,
        form_id=None,
        points_data=points_data,
        assessments=assessments,
        finalacr_value=0,
        hod_ratings=[],
        extra_feedback='',
        custom_table_data=custom_table_data,
        custom_table_title=custom_table_title,
        profile_image=None,
    )


def search_pastforms(connect_to_database, app):
    user_id = session.get('user_id')
    selected_year = request.form.get('academicYear')

    connection = connect_to_database()

    teaching_data, feedback_data, dept_act_data, inst_act_data, society_data = [], [], [], [], []
    self_improvement_data, certification_data, resource_data = [], [], []
    committee_data, project_data, contribution_data = [], [], []
    moocs_data, swayam_data, webinar_data = [], [], []
    academic_review_data = []
    training_data = []
    patent_data = []
    conference_committee_data = []
    special_mentions_data = []
    copyright_data = []
    points_data = {}
    acr_data = {}
    form_id = None
    user_data = None
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
    principal_assessments = {
        'prinas1': 0,
        'prinas2': 0,
        'prinas3': 0,
        'prinas4': 0,
        'prinas5': 0,
        'prinas6': 0,
    }
    finalacr_value = 0
    self_assessment_marks = ''
    profile_image = None

    def process_rows(rows):
        if not rows:
            return []
        processed = []
        for row in rows:
            processed_row = tuple('' if val is None else val for val in row)
            processed.append(processed_row)
        return processed

    try:
        with connection.cursor() as cursor:
            sql = 'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s'
            cursor.execute(sql, (user_id, selected_year))
            result = cursor.fetchone()

            if result:
                form_id = result[0]
                sql_user_acad = '''
                SELECT user_id, acad_years FROM acad_years WHERE form_id = %s
                '''
                cursor.execute(sql_user_acad, (form_id,))
                user_acad_result = cursor.fetchone()

                if user_acad_result:
                    user_id, selected_year = user_acad_result
                else:
                    flash('No data found for the provided form ID.', 'warning')
                    return redirect(url_for('pastforms'))

                sql_user = '''
                SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp, profile_image
                FROM users
                WHERE userid = %s
                '''
                cursor.execute(sql_user, (user_id,))
                user_data = cursor.fetchone()

                if not user_data:
                    flash('User not found.', 'warning')
                    return redirect(url_for('pastforms'))

                profile_image = user_data[9] if user_data and len(user_data) > 9 else None

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
                    SELECT teaching, feedback, hodas1, hodas2, hodfeed1, hodfeed2, prinas1, prinas2
                    FROM form1_tot WHERE form_id = %s
                ''',
                    (form_id,),
                )
                form1_tot = cursor.fetchone()

                cursor.execute(
                    '''
                    SELECT dept, institute, hodas3, hodas4, hodfeed3, hodfeed4, prinas3, prinas4
                    FROM form2_tot WHERE form_id = %s
                ''',
                    (form_id,),
                )
                form2_tot = cursor.fetchone()

                cursor.execute(
                    '''
                    SELECT acr, society, hodas5, hodas6, hodfeed5, hodfeed6, finalacr, prinas5, prinas6
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

                if form1_tot and len(form1_tot) > 6:
                    principal_assessments.update(
                        {
                            'prinas1': int(form1_tot[6]) if form1_tot[6] is not None else 0,
                            'prinas2': int(form1_tot[7]) if form1_tot[7] is not None else 0,
                        }
                    )

                if form2_tot and len(form2_tot) > 6:
                    principal_assessments.update(
                        {
                            'prinas3': int(form2_tot[6]) if form2_tot[6] is not None else 0,
                            'prinas4': int(form2_tot[7]) if form2_tot[7] is not None else 0,
                        }
                    )

                if form3_tot and len(form3_tot) > 7:
                    principal_assessments.update(
                        {
                            'prinas5': int(form3_tot[7]) if form3_tot[7] is not None else 0,
                            'prinas6': int(form3_tot[8]) if form3_tot[8] is not None else 0,
                        }
                    )

                cursor.execute('SELECT feedback FROM feedback WHERE form_id = %s', (form_id,))
                feedback_result = cursor.fetchone()
                if feedback_result and feedback_result[0]:
                    assessments['feedback'] = feedback_result[0]

    except Exception as e:
        flash(f'An error occurred while fetching data: {str(e)}', 'danger')
        app.logger.error(f'Error in search_pastforms: {e}', exc_info=True)
    finally:
        if connection and connection.open:
            connection.close()

    user_name = user_data[3] if user_data and len(user_data) > 3 else 'N/A'
    user_dept = user_data[2] if user_data and len(user_data) > 2 else 'N/A'

    custom_table_data = []
    custom_table_title = 'Custom Table'
    connection = connect_to_database()
    if connection and form_id:
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
                                json.loads(columns_data_str) if columns_data_str else {}
                            )
                            headers = json.loads(headers_str) if headers_str else []
                            uploads = json.loads(uploads_str) if uploads_str else {}

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
            print(f'Error fetching custom table data in search_pastforms: {e}')
        finally:
            connection.close()

    return render_template(
        'pastforms.html',
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
        user_data=user_data,
        user_name=user_name,
        user_dept=user_dept,
        selected_year=selected_year,
        form_id=form_id,
        assessments=assessments,
        principal_assessments=principal_assessments,
        finalacr_value=finalacr_value,
        self_assessment_marks=self_assessment_marks,
        str=str,
        custom_table_data=custom_table_data,
        custom_table_title=custom_table_title,
        profile_image=profile_image,
    )
