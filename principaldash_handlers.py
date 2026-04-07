from flask import jsonify, render_template, request, session


def principledash():
    user_id = session.get('user_id')
    department = request.args.get('department')
    return render_template('principaldash.html')


def get_performers_with_hod(connect_to_database):
    acad_years = request.json['academic_year']
    dept = request.json['department']

    print(f'Received academic year: {acad_years}, department: {dept}')

    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT t.name, t.total, t.hodtotal, t.user_id as userid, t.principle_total
        FROM total t
        JOIN users u ON t.user_id = u.userid
        WHERE t.acad_years = %s AND t.dept = %s
        ORDER BY t.total DESC
    ''',
        (acad_years, dept),
    )

    results = cursor.fetchall()
    print(f'Query Results: {results}')

    performers = [
        {
            'name': row[0],
            'total': row[1],
            'hodtotal': row[2],
            'userid': row[3],
            'principle_total': row[4] if row[4] is not None else 0,
        }
        for row in results
    ]

    cursor.close()
    return jsonify(performers)
