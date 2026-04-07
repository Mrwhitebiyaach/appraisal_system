import json

from flask import flash, redirect, render_template, request, session, url_for


def principlepastform(connect_to_database):
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
        'prinas1': 0,
        'prinas2': 0,
        'prinas3': 0,
        'prinas4': 0,
        'prinas5': 0,
        'prinas6': 0,
        'prinfeed1': '',
        'prinfeed2': '',
        'prinfeed3': '',
        'prinfeed4': '',
        'prinfeed5': '',
        'prinfeed6': '',
        'hodfeed1': '',
        'hodfeed2': '',
        'hodfeed3': '',
        'hodfeed4': '',
        'hodfeed5': '',
        'hodfeed6': '',
        'principle_feedback': '',
        'hod_feedback': '',
    }
    user_id = session.get('user_id')
    department = request.args.get('department')
    user_id = request.args.get('userid')
    session['user_id'] = user_id

    user_name = request.args.get('name')
    session['user_name'] = user_name

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
                print(f'Debug - Initial user data fetch: {user_data}')
        except Exception as e:
            print(f'Error fetching user data: {str(e)}')
        finally:
            connection.close()

    hod_ratings = {f'r{i+1}': 0 for i in range(10)}
    hod_ratings['r_avg'] = 0
    acad_year = request.args.get('year') or request.args.get('acad_years')
    if not acad_year:
        acad_year = session.get('selected_year')
    try:
        connection = connect_to_database()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s',
                    (user_id, acad_year),
                )
                result = cursor.fetchone()
                if result:
                    form_id = result[0]
                    cursor.execute(
                        'SELECT r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r_avg FROM feedback WHERE form_id = %s',
                        (form_id,),
                    )
                    ratings_row = cursor.fetchone()
                    if ratings_row:
                        hod_ratings = {f'r{i+1}': ratings_row[i] for i in range(10)}
                        hod_ratings['r_avg'] = ratings_row[10]
                        print(
                            f'[LOG] /principlepastform GET: Found ratings for user_id={user_id}, acad_year={acad_year}: {hod_ratings}'
                        )
                    else:
                        print(
                            f'[LOG] /principlepastform GET: No ratings found for form_id={form_id}'
                        )

                    cursor.execute(
                        'SELECT feedback, principle_feedback FROM feedback WHERE form_id = %s',
                        (form_id,),
                    )
                    feedback_result = cursor.fetchone()
                    if feedback_result:
                        if feedback_result[0]:
                            assessments['hod_feedback'] = feedback_result[0]
                        if feedback_result[1]:
                            assessments['principle_feedback'] = feedback_result[1]

    except Exception as e:
        print('Error fetching HOD ratings in /principlepastform:', e)
    finally:
        if connection:
            connection.close()

    finalacr_value = 0
    try:
        connection = connect_to_database()
        if connection:
            with connection.cursor() as cursor:
                if 'form_id' in locals():
                    cursor.execute(
                        'SELECT finalacr FROM form3_tot WHERE form_id = %s', (form_id,)
                    )
                    acr_row = cursor.fetchone()
                    if acr_row and acr_row[0] is not None:
                        finalacr_value = acr_row[0]
    except Exception as e:
        print(f'Error fetching finalacr in /principlepastform: {e}')
    finally:
        if connection:
            connection.close()

    teaching_data, feedback_data, dept_act_data, inst_act_data = [], [], [], []
    academic_review_data = []
    self_improvement_data, certification_data = [], []
    resource_data, committee_data, project_data, contribution_data = [], [], [], []
    moocs_data, swayam_data, webinar_data = [], [], []
    training_data, patent_data, conference_committee_data = [], [], []
    special_mentions_data, copyright_data = [], []
    hodas_data = {}
    extra_feedback = ''

    if 'form_id' in locals() and form_id:

        def process_rows(rows):
            processed = []
            for row in rows:
                processed_row = list(row)
                if processed_row and processed_row[-1]:
                    upload_path = processed_row[-1]
                    processed_row[-1] = upload_path
                processed.append(processed_row)
            return processed

        try:
            connection = connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT semester, coursecode, coursename, totmarks, markobt, uploads
                        FROM teaching WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    teaching_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, coursecode, totmarks, markobt, uploads
                        FROM feedback_form WHERE form_id = %s
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
                        SELECT semester, program, course, activity, uploads
                        FROM academic_review WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    academic_review_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, activity, details, uploads
                        FROM self_improvement WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    self_improvement_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, certification, uploads
                        FROM certification WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    certification_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, topic, department, institute, participants, uploads
                        FROM resource_person WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    resource_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, committee, dept_institute, role, uploads
                        FROM committee WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    committee_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, role, description, contribution, university, duration, comments, uploads
                        FROM external_project WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    project_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, activity, points, order_cpy, details, uploads
                        FROM contribution WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    contribution_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, course_name, month_year, duration, certification, uploads
                        FROM moocs WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    moocs_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, course_name, month_year, duration, certification, uploads
                        FROM swayam WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    swayam_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, topic, organisation, duration, date, uploads
                        FROM webinar WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    webinar_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, training_type, organiser, duration, date, uploads
                        FROM training WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    training_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, title, patent_number, status, date, uploads
                        FROM patent WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    patent_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, conference, role, organisation, date, uploads
                        FROM conference_committee WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    conference_committee_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, achievement, description, uploads
                        FROM special_mentions WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    special_mentions_data = process_rows(cursor.fetchall())

                    cursor.execute(
                        '''
                        SELECT semester, title, copyright_number, status, date, uploads
                        FROM copyright WHERE form_id = %s
                    ''',
                        (form_id,),
                    )
                    copyright_data = process_rows(cursor.fetchall())

                    print(
                        f'[LOG] /principlepastform: Fetched all custom table data for form_id={form_id}'
                    )

        except Exception as e:
            print(f'Error fetching custom table data in /principlepastform: {e}')
        finally:
            if connection:
                connection.close()

    total_hod_points = (
        float(assessments.get('hodas1', 0))
        + float(assessments.get('hodas2', 0))
        + float(assessments.get('hodas3', 0))
        + float(assessments.get('hodas4', 0))
        + float(finalacr_value or 0)
        + float(assessments.get('hodas6', 0))
    )
    print(
        f'[LOG] Rendering principlepast.html with hod_ratings: {hod_ratings}, finalacr_value: {finalacr_value}, total_hod_points: {total_hod_points}'
    )

    return render_template(
        'principlepast.html',
        user_name=user_name,
        user_id=user_id,
        department=department,
        selected_year=acad_year,
        points_data=points_data,
        assessments=assessments,
        user_data=user_data,
        hod_ratings=hod_ratings,
        finalacr_value=finalacr_value,
        total_hod_points=total_hod_points,
        teaching_data=teaching_data,
        feedback_data=feedback_data,
        dept_act_data=dept_act_data,
        inst_act_data=inst_act_data,
        academic_review_data=academic_review_data,
        self_improvement_data=self_improvement_data,
        certification_data=certification_data,
        resource_data=resource_data,
        committee_data=committee_data,
        project_data=project_data,
        contribution_data=contribution_data,
        moocs_data=moocs_data,
        swayam_data=swayam_data,
        webinar_data=webinar_data,
        training_data=training_data,
        patent_data=patent_data,
        conference_committee_data=conference_committee_data,
        special_mentions_data=special_mentions_data,
        copyright_data=copyright_data,
        hodas_data=hodas_data,
        extra_feedback=extra_feedback,
    )


def principle_pastforms(connect_to_database):
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
        'principle_feedback': '',
        'hod_feedback': '',
        'prinas1': 0,
        'prinas2': 0,
        'prinas3': 0,
        'prinas4': 0,
        'prinas5': 0,
        'prinas6': 0,
        'hodfeed1': '',
        'hodfeed2': '',
        'hodfeed3': '',
        'hodfeed4': '',
        'hodfeed5': '',
        'hodfeed6': '',
        'prinfeed1': '',
        'prinfeed2': '',
        'prinfeed3': '',
        'prinfeed4': '',
        'prinfeed5': '',
        'prinfeed6': '',
    }

    finalacr_value = 0
    self_assessment_marks = ''
    no_data_found = False
    total_hod_points = 0

    user_id = session.get('user_id')
    selected_year = request.form.get('academicYear')
    user_name = session.get('user_name')
    print(
        f'[LOG] POST /principle_pastforms: user_id={user_id}, selected_year={selected_year}, user_name={user_name}'
    )

    if not user_id or not selected_year:
        print(
            f'[LOG] Missing user_id or selected_year! user_id={user_id}, selected_year={selected_year}'
        )
        flash('User ID or Academic Year is missing!', 'danger')
        return redirect(url_for('principlepastform'))

    teaching_data, feedback_data, dept_act_data, inst_act_data = [], [], [], []
    academic_review_data = []
    self_improvement_data, certification_data = [], []
    resource_data, committee_data, project_data, contribution_data = [], [], [], []
    moocs_data, swayam_data, webinar_data = [], [], []
    training_data, patent_data, conference_committee_data = [], [], []
    special_mentions_data, copyright_data = [], []
    hodas_data = {}
    extra_feedback = ''
    user_data = None
    form_id = None
    hod_ratings = {f'r{i+1}': None for i in range(10)}
    hod_ratings['r_avg'] = None

    def process_rows(rows):
        if not rows:
            return []
        processed = []
        for row in rows:
            processed_row = tuple('' if val is None else val for val in row)
            processed.append(processed_row)
        return processed

    connection = connect_to_database()
    print(f"[LOG] Database connection: {'OK' if connection else 'FAILED'}")

    if connection:
        try:
            with connection.cursor() as cursor:
                print(
                    f'[LOG] Executing: SELECT form_id FROM acad_years WHERE user_id = {user_id} AND acad_years = {selected_year}'
                )
                cursor.execute(
                    'SELECT form_id FROM acad_years WHERE user_id = %s AND acad_years = %s',
                    (user_id, selected_year),
                )
                result = cursor.fetchone()
                print(f'[LOG] form_id query result: {result}')

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
                        'SELECT r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r_avg FROM feedback WHERE form_id = %s',
                        (form_id,),
                    )
                    ratings_row = cursor.fetchone()
                    if ratings_row:
                        hod_ratings = {f'r{i+1}': ratings_row[i] for i in range(10)}
                        hod_ratings['r_avg'] = ratings_row[10]
                    else:
                        hod_ratings = {f'r{i+1}': None for i in range(10)}
                        hod_ratings['r_avg'] = None

                    cursor.execute(
                        'SELECT feedback, principle_feedback FROM feedback WHERE form_id = %s',
                        (form_id,),
                    )
                    feedback_result = cursor.fetchone()
                    if feedback_result:
                        if feedback_result[0]:
                            extra_feedback = feedback_result[0]
                            assessments['hod_feedback'] = feedback_result[0]
                        if feedback_result[1]:
                            assessments['principle_feedback'] = feedback_result[1]

                    cursor.execute(
                        'SELECT teaching, feedback, hodas1, hodas2, hodfeed1, hodfeed2, prinas1, prinas2, prinfeed1, prinfeed2 FROM form1_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    form1_tot = cursor.fetchone()

                    cursor.execute(
                        'SELECT dept, institute, hodas3, hodas4, hodfeed3, hodfeed4, prinas3, prinas4, prinfeed3, prinfeed4 FROM form2_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    form2_tot = cursor.fetchone()

                    cursor.execute(
                        'SELECT acr, society, hodas5, hodas6, hodfeed5, hodfeed6, prinas5, prinas6, prinfeed5, prinfeed6, finalacr FROM form3_tot WHERE form_id = %s',
                        (form_id,),
                    )
                    form3_tot = cursor.fetchone()

                    if form3_tot and len(form3_tot) > 10 and form3_tot[10] is not None:
                        finalacr_value = int(form3_tot[10])
                    else:
                        finalacr_value = 0

                    points_data = {
                        'teaching': int(form1_tot[0]) if form1_tot and form1_tot[0] else 0,
                        'feedback': int(form1_tot[1]) if form1_tot and form1_tot[1] else 0,
                        'dept': int(form2_tot[0]) if form2_tot and form2_tot[0] else 0,
                        'institute': int(form2_tot[1]) if form2_tot and form2_tot[1] else 0,
                        'acr': int(form3_tot[0]) if form3_tot and form3_tot[0] else 0,
                        'society': int(form3_tot[1]) if form3_tot and form3_tot[1] else 0,
                    }

                    total_hod_points = (
                        float(assessments.get('hodas1', 0))
                        + float(assessments.get('hodas2', 0))
                        + float(assessments.get('hodas3', 0))
                        + float(assessments.get('hodas4', 0))
                        + float(finalacr_value or 0)
                        + float(assessments.get('hodas6', 0))
                    )

                    assessments.update(
                        {
                            'hodas1': int(form1_tot[2])
                            if form1_tot and form1_tot[2] is not None
                            else 0,
                            'hodas2': int(form1_tot[3])
                            if form1_tot and form1_tot[3] is not None
                            else 0,
                            'hodas3': int(form2_tot[2])
                            if form2_tot and form2_tot[2] is not None
                            else 0,
                            'hodas4': int(form2_tot[3])
                            if form2_tot and form2_tot[3] is not None
                            else 0,
                            'hodas5': int(form3_tot[2])
                            if form3_tot and form3_tot[2] is not None
                            else 0,
                            'hodas6': int(form3_tot[3])
                            if form3_tot and form3_tot[3] is not None
                            else 0,
                            'hodfeed1': form1_tot[4]
                            if form1_tot and len(form1_tot) > 4
                            else '',
                            'hodfeed2': form1_tot[5]
                            if form1_tot and len(form1_tot) > 5
                            else '',
                            'hodfeed3': form2_tot[4]
                            if form2_tot and len(form2_tot) > 4
                            else '',
                            'hodfeed4': form2_tot[5]
                            if form2_tot and len(form2_tot) > 5
                            else '',
                            'hodfeed5': form3_tot[4]
                            if form3_tot and len(form3_tot) > 4
                            else '',
                            'hodfeed6': form3_tot[5]
                            if form3_tot and len(form3_tot) > 5
                            else '',
                            'prinas1': int(form1_tot[6])
                            if form1_tot and len(form1_tot) > 6 and form1_tot[6] is not None
                            else 0,
                            'prinas2': int(form1_tot[7])
                            if form1_tot and len(form1_tot) > 7 and form1_tot[7] is not None
                            else 0,
                            'prinas3': int(form2_tot[6])
                            if form2_tot and len(form2_tot) > 6 and form2_tot[6] is not None
                            else 0,
                            'prinas4': int(form2_tot[7])
                            if form2_tot and len(form2_tot) > 7 and form2_tot[7] is not None
                            else 0,
                            'prinas5': int(form3_tot[6])
                            if form3_tot and len(form3_tot) > 6 and form3_tot[6] is not None
                            else 0,
                            'prinas6': int(form3_tot[7])
                            if form3_tot and len(form3_tot) > 7 and form3_tot[7] is not None
                            else 0,
                            'prinfeed1': form1_tot[8]
                            if form1_tot and len(form1_tot) > 8 and form1_tot[8] is not None
                            else '',
                            'prinfeed2': form1_tot[9]
                            if form1_tot and len(form1_tot) > 9 and form1_tot[9] is not None
                            else '',
                            'prinfeed3': form2_tot[8]
                            if form2_tot and len(form2_tot) > 8 and form2_tot[8] is not None
                            else '',
                            'prinfeed4': form2_tot[9]
                            if form2_tot and len(form2_tot) > 9 and form2_tot[9] is not None
                            else '',
                            'prinfeed5': form3_tot[8]
                            if form3_tot and len(form3_tot) > 8 and form3_tot[8] is not None
                            else '',
                            'prinfeed6': form3_tot[9]
                            if form3_tot and len(form3_tot) > 9 and form3_tot[9] is not None
                            else '',
                        }
                    )

        except Exception as e:
            flash(f'Error fetching data: {str(e)}', 'danger')
            print(f'Error in principle_pastforms: {e}')
        finally:
            if connection:
                connection.close()

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
            if connection:
                connection.close()

    user_name = user_data[3] if user_data and len(user_data) > 3 else 'N/A'
    user_dept = user_data[2] if user_data and len(user_data) > 2 else 'N/A'

    custom_table_data = []
    custom_table_title = 'Custom Table'

    if form_id:
        connection = connect_to_database()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        CREATE TABLE IF NOT EXISTS custom_table (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            form_id VARCHAR(255),
                            srno VARCHAR(255),
                            columns_data TEXT,
                            headers TEXT,
                            uploads TEXT,
                            table_title TEXT,
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

                    for row in custom_table_rows:
                        srno = row[0]
                        columns_data_str = row[1] if len(row) > 1 else '{}'
                        headers_str = row[2] if len(row) > 2 else '[]'
                        uploads_str = row[3] if len(row) > 3 else '{}'
                        table_title_from_row = row[4] if len(row) > 4 else 'Custom Table'

                        if not custom_table_data:
                            custom_table_title = (
                                table_title_from_row
                                if table_title_from_row
                                else 'Custom Table'
                            )

                        try:
                            columns_data = (
                                json.loads(columns_data_str)
                                if columns_data_str
                                else {}
                            )
                            headers = json.loads(headers_str) if headers_str else []
                            uploads = json.loads(uploads_str) if uploads_str else {}

                            merged_columns = columns_data.copy()
                            for col_name, upload_info in uploads.items():
                                if col_name in merged_columns:
                                    merged_columns[col_name] = {
                                        'text': merged_columns[col_name],
                                        'upload': upload_info,
                                    }
                                else:
                                    merged_columns[col_name] = {'upload': upload_info}

                            custom_table_data.append(
                                {
                                    'srno': srno,
                                    'columns_data': json.dumps(merged_columns),
                                    'headers': headers,
                                }
                            )
                        except json.JSONDecodeError:
                            print(f'Error parsing JSON for custom table row {srno}')
                            continue

            except Exception as e:
                print(f'Error fetching custom table data: {str(e)}')
            finally:
                connection.close()

    if 'total_hod_points' not in locals():
        total_hod_points = (
            float(assessments.get('hodas1', 0))
            + float(assessments.get('hodas2', 0))
            + float(assessments.get('hodas3', 0))
            + float(assessments.get('hodas4', 0))
            + float(finalacr_value or 0)
            + float(assessments.get('hodas6', 0))
        )

    if no_data_found:
        flash(f'No form exists for the selected academic year: {selected_year}', 'info')

    return render_template(
        'principlepast.html',
        assessments=assessments,
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
        custom_table_data=custom_table_data,
        custom_table_title=custom_table_title,
        selected_year=selected_year,
        user_name=user_name,
        user_id=user_id,
        user_data=user_data,
        form_id=form_id,
        hod_ratings=hod_ratings,
        finalacr_value=finalacr_value,
        total_hod_points=total_hod_points,
        self_assessment_marks=self_assessment_marks,
        extra_feedback=extra_feedback,
        no_data_found=no_data_found,
    )
