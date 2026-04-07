from flask import jsonify, render_template, request, session


def dashboard(connect_to_database):
    user_id = session.get('user_id')
    department = request.args.get('department')

    if not department:
        department = session.get('department')

    if not department and user_id:
        connection = connect_to_database()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = 'SELECT dept FROM users WHERE userid = %s'
                    cursor.execute(sql, (user_id,))
                    result = cursor.fetchone()
                    if result:
                        department = result[0]
                        session['department'] = department
            except Exception as e:
                print(f'Error fetching department: {e}')
            finally:
                connection.close()

    return render_template('dashboard.html', department=department)


def get_top_performers(connect_to_database):
    acad_years = request.json['academic_year']
    dept = request.json['department']

    print(f'Received academic year: {acad_years}, department: {dept}')

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT t.name, t.total, t.user_id as userid
        FROM total t
        JOIN users u ON t.user_id = u.userid
        WHERE t.acad_years = %s AND t.dept = %s
        ORDER BY t.total DESC
    ''',
        (acad_years, dept),
    )

    results = cursor.fetchall()
    print(f'Query Results: {results}')

    top_performers = [
        {'name': row[0], 'total': row[1], 'userid': row[2]} for row in results
    ]

    cursor.close()
    return jsonify(top_performers)


def get_section_scores(connect_to_database):
    data = request.get_json()
    academic_year = data.get('academic_year')
    department = data.get('department')
    section = data.get('section')

    section_map = {
        'teaching': ('form1_tot', 'teaching'),
        'feedback': ('form1_tot', 'feedback'),
        'dept': ('form2_tot', 'dept'),
        'institute': ('form2_tot', 'institute'),
        'acr': ('form3_tot', 'acr'),
        'society': ('form3_tot', 'society'),
    }
    if section not in section_map:
        return jsonify({'error': 'Invalid section'}), 400

    table, column = section_map[section]

    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        hod_column_map = {
            'teaching': 'hodas1',
            'feedback': 'hodas2',
            'dept': 'hodas3',
            'institute': 'hodas4',
            'acr': 'finalacr',
            'society': 'hodas6',
        }
        hod_column = hod_column_map.get(section)

        query = f'''
            SELECT u.name, u.userid, a.form_id, COALESCE(f.{column}, 0) as score, COALESCE(f.{hod_column}, 0) as hod_score
            FROM acad_years a
            JOIN users u ON a.user_id = u.userid
            LEFT JOIN {table} f ON a.form_id = f.form_id
            WHERE a.acad_years = %s AND u.dept = %s AND u.role = 'Faculty'
            ORDER BY score DESC, u.name ASC
        '''
        cursor.execute(query, (academic_year, department))
        results = cursor.fetchall()

        response = [
            {
                'name': row[0],
                'userid': row[1],
                'form_id': row[2],
                'score': row[3],
                'hod_score': row[4],
            }
            for row in results
        ]
        return jsonify(response)
    finally:
        cursor.close()
        connection.close()
