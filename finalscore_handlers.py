from flask import jsonify, render_template, request


def finalscore_page(connect_to_database, form_id):
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM acad_years WHERE form_id = %s", (form_id,))
            acad_info = cursor.fetchone()

            if not acad_info:
                return "Error: No user ID found for the given form ID", 404

            user_id = acad_info[0]
            return render_template('finalscore.html', form_id=form_id, user_id=user_id)
    finally:
        connection.close()


def get_scores(connect_to_database, form_id):
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, acad_years FROM acad_years WHERE form_id = %s", (form_id,))
            acad_info = cursor.fetchone()

            if not acad_info:
                return jsonify({'error': 'No academic year or user ID found for the given form ID'}), 404

            user_id, acad_years = acad_info

            cursor.execute("SELECT teaching, feedback FROM form1_tot WHERE form_id = %s", (form_id,))
            form1_tot = cursor.fetchone()

            cursor.execute("SELECT dept, institute FROM form2_tot WHERE form_id = %s", (form_id,))
            form2_tot = cursor.fetchone()

            cursor.execute("SELECT acr, society FROM form3_tot WHERE form_id = %s", (form_id,))
            form3_tot = cursor.fetchone()

            response = {
                'user_id': user_id,
                'acad_years': acad_years,
                'teaching': form1_tot[0] if form1_tot else 0,
                'feedback': form1_tot[1] if form1_tot else 0,
                'dept': form2_tot[0] if form2_tot else 0,
                'institute': form2_tot[1] if form2_tot else 0,
                'acr': form3_tot[0] if form3_tot else 0,
                'society': form3_tot[1] if form3_tot else 0,
            }

            return jsonify(response)
    finally:
        connection.close()


def save_fac_total_points(connect_to_database):
    data = request.json
    total_points = data['totalPoints']
    form_id = data['formId']
    user_id = data['userId']

    print(f"Received total_points: {total_points}, form_id: {form_id}, user_id: {user_id}")

    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT acad_years FROM acad_years WHERE form_id = %s", (form_id,))
            acad_data = cursor.fetchone()

            if not acad_data:
                return jsonify({'error': 'Academic year not found for the given form ID'}), 404

            acad_years = acad_data[0]
            print(f"Saving: form_id={form_id}, user_id={user_id}, acad_years={acad_years}, total_points={total_points}")

            query = """
                INSERT INTO forms (form_id, user_id, acad_years, fac_total)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE fac_total = VALUES(fac_total)
            """
            cursor.execute(query, (form_id, user_id, acad_years, total_points))
            connection.commit()

            return jsonify({'message': 'Total points saved successfully!'}), 200
    except Exception as e:
        print(f"Error saving total points: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()
