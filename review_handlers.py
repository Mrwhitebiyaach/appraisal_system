from flask import flash, jsonify, redirect, render_template, request
import json
import traceback


def review(connect_to_database, form_id):
    # Initialize all variables to ensure they have default values
    teaching_data, feedback_data, dept_act_data, inst_act_data = [], [], [], []
    academic_review_data = []
    points_data = {}
    user_data = {}
    selected_year = ""

    # Form3 data variables - using same structure as form3 route
    self_improvement_data = []
    certification_data = []
    training_data = []
    moocs_data = []
    swayam_data = []
    webinar_data = []
    copyright_data = []
    patent_data = []
    resource_data = []
    committee_data = []
    conference_committee_data = []
    project_data = []
    contribution_data = []
    self_assessment_marks = ""
    special_mentions_data = []

    custom_table_data = []
    custom_table_title = "Custom Table"

    connection = connect_to_database()

    if connection:
        try:
            with connection.cursor() as cursor:
                sql_user_acad = """
                SELECT user_id, acad_years FROM acad_years WHERE form_id = %s
                """
                cursor.execute(sql_user_acad, (form_id,))
                user_acad_result = cursor.fetchone()

                if user_acad_result:
                    print(f"[REVIEW DEBUG] user_acad_result for form_id={form_id}: {user_acad_result}")
                    user_id, selected_year = user_acad_result
                else:
                    print(f"[REVIEW DEBUG] No data found for the provided form ID {form_id}. Redirecting to /landing.")
                    flash("No data found for the provided form ID.", "warning")
                    return redirect("/landing")

                sql_user = """
                SELECT userid, gmail, dept, name, designation, d_o_j, dob, edu_q, exp
                FROM users
                WHERE userid = %s
                """
                cursor.execute(sql_user, (user_id,))
                user_data = cursor.fetchone()
                print(f"[REVIEW DEBUG] user_data for user_id={user_id}: {user_data}")

                if user_data:
                    user_name = user_data[3]
                    user_dept = user_data[2]
                else:
                    print(f"[REVIEW DEBUG] User not found for user_id={user_id}, form_id={form_id}. Redirecting to /landing.")
                    flash("User not found.", "warning")
                    return redirect("/landing")

                cursor.execute(
                    """
                    SELECT semester, course_code, classes_scheduled, classes_held,
                    (classes_held/classes_scheduled)*5 AS totalpoints
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

                cursor.execute(
                    """
                    SELECT semester, activity, points, order_cpy, uploads
                    FROM department_act WHERE form_id = %s
                    """,
                    (form_id,),
                )
                dept_act_data = cursor.fetchall()

                cursor.execute(
                    """
                    SELECT semester, activity, points, order_cpy, uploads
                    FROM institute_act WHERE form_id = %s
                    """,
                    (form_id,),
                )
                inst_act_data = cursor.fetchall()

                form_id_str = str(form_id)

                def safe_get(row, index, default=""):
                    if index >= len(row) or row[index] is None:
                        return default
                    return row[index]

                def process_rows(rows):
                    if not rows:
                        return []

                    processed = []
                    for row in rows:
                        processed_row = tuple("" if val is None else val for val in row)
                        processed.append(processed_row)

                    return processed

                cursor.execute(
                    "SELECT srno, title, month, name_of_conf, issn, co_auth, imp_conference, num_of_citations, rating, uploads, form_id FROM self_imp WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                self_improvement_data = process_rows(cursor.fetchall())

                cursor.execute("SELECT * FROM certifications WHERE form_id = %s", (form_id_str,))
                certification_data = process_rows(cursor.fetchall())

                cursor.execute(
                    "SELECT srno, name, technology, duration, date, organizing_institute, mode, upload FROM short_term_training WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                training_data = process_rows(cursor.fetchall())

                cursor.execute(
                    "SELECT srno, name, month, duration, completion, upload FROM moocs WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                moocs_data = process_rows(cursor.fetchall())

                cursor.execute(
                    "SELECT srno, name, month, duration, completion, upload FROM swayam WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                swayam_data = process_rows(cursor.fetchall())

                cursor.execute(
                    "SELECT srno, name, technology, duration, date, int_ext, name_of_institute, upload FROM webinar WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                webinar_data = process_rows(cursor.fetchall())

                cursor.execute(
                    """
                    SELECT
                        srno,
                        COALESCE(name, '') as name,
                        COALESCE(month, '') as month,
                        COALESCE(reg_no, '') as reg_no,
                        COALESCE(filed_pub_grant, '') as filed_pub_grant,
                        COALESCE(category, '') as category,
                        COALESCE(uploads, '') as uploads
                    FROM copyright
                    WHERE form_id = %s
                    ORDER BY srno ASC
                    """,
                    (form_id_str,),
                )
                copyright_data = cursor.fetchall()
                copyright_data = [tuple(row) for row in copyright_data]

                cursor.execute(
                    """
                    SELECT
                        srno,
                        COALESCE(name, '') as name,
                        COALESCE(month, '') as month,
                        COALESCE(reg_no, '') as reg_no,
                        COALESCE(filed_pub_grant, '') as filed_pub_grant,
                        COALESCE(category, '') as category,
                        COALESCE(uploads, '') as uploads
                    FROM patents
                    WHERE form_id = %s
                    ORDER BY srno ASC
                    """,
                    (form_id_str,),
                )
                patent_data = cursor.fetchall()
                patent_data = [tuple(row) for row in patent_data]

                cursor.execute("SELECT * FROM resource_person WHERE form_id = %s", (form_id_str,))
                resource_data = process_rows(cursor.fetchall())

                cursor.execute("SELECT * FROM mem_uni WHERE form_id = %s", (form_id_str,))
                committee_data = process_rows(cursor.fetchall())

                cursor.execute(
                    "SELECT srno, name, designation, upload FROM members_conference WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                conference_committee_raw = process_rows(cursor.fetchall())
                conference_committee_data = [
                    {
                        "srno": row[0],
                        "name": row[1],
                        "designation": row[2],
                        "upload": row[3],
                    }
                    for row in conference_committee_raw
                ]

                cursor.execute("SELECT * FROM external_projects WHERE form_id = %s", (form_id_str,))
                project_data = process_rows(cursor.fetchall())

                cursor.execute(
                    "SELECT semester, activity, points, order_cpy, order_no, details, COALESCE(uploads, '') as uploads FROM contribution_to_society WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                contribution_data = process_rows(cursor.fetchall())

                try:
                    cursor.execute("SELECT self_assessment_marks FROM form3_assessment WHERE form_id = %s", (form_id_str,))
                    assessment_result = cursor.fetchone()
                    self_assessment_marks = safe_get(assessment_result, 0, "") if assessment_result else ""
                except Exception as e:
                    print(f"Error fetching self assessment marks: {e}")
                    self_assessment_marks = ""

                cursor.execute(
                    "SELECT srno, name, roles, uploads FROM special_mentions WHERE form_id = %s ORDER BY srno ASC",
                    (form_id_str,),
                )
                special_mentions_raw = process_rows(cursor.fetchall())
                special_mentions_data = [
                    {
                        "srno": row[0],
                        "name": row[1],
                        "roles": row[2],
                        "uploads": row[3],
                    }
                    for row in special_mentions_raw
                ]

                try:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS custom_table (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            form_id VARCHAR(45) NOT NULL,
                            srno INT NOT NULL,
                            columns_data TEXT,
                            headers TEXT,
                            uploads TEXT,
                            table_title VARCHAR(255) DEFAULT 'Custom Table',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            INDEX idx_form_id (form_id),
                            INDEX idx_form_srno (form_id, srno)
                        )
                        """
                    )

                    cursor.execute(
                        "SELECT srno, columns_data, headers, uploads, table_title FROM custom_table WHERE form_id = %s ORDER BY srno ASC",
                        (form_id_str,),
                    )
                    custom_table_rows = cursor.fetchall()

                    if custom_table_rows and len(custom_table_rows[0]) >= 5 and custom_table_rows[0][4]:
                        custom_table_title = custom_table_rows[0][4]

                    for row in custom_table_rows:
                        try:
                            srno = row[0]
                            columns_data_str = row[1] if len(row) > 1 else "{}"
                            headers_str = row[2] if len(row) > 2 else "[]"
                            uploads_str = row[3] if len(row) > 3 else "{}"

                            columns_data = json.loads(columns_data_str) if columns_data_str else {}
                            headers = json.loads(headers_str) if headers_str else []
                            uploads = json.loads(uploads_str) if uploads_str else {}

                            merged_columns = columns_data.copy()
                            for col_name, upload_path in uploads.items():
                                if col_name in merged_columns:
                                    merged_columns[col_name] = {"text": merged_columns[col_name], "upload": upload_path}
                                else:
                                    merged_columns[col_name] = {"text": "", "upload": upload_path}

                            custom_table_data.append(
                                {
                                    "srno": srno,
                                    "columns_data": json.dumps(merged_columns),
                                    "headers": headers,
                                }
                            )
                        except (json.JSONDecodeError, TypeError, ValueError) as e:
                            print(f"Error processing custom table row {row}: {e}")
                            custom_table_data.append(
                                {
                                    "srno": row[0] if row else 0,
                                    "columns_data": "{}",
                                    "headers": [],
                                }
                            )
                except Exception as e:
                    print(f"Error querying custom table: {e}")
                    custom_table_data = []
                    custom_table_title = "Custom Table"

                cursor.execute(
                    "SELECT teaching, feedback, hodas1, hodas2, hodfeed1, hodfeed2 FROM form1_tot WHERE form_id = %s",
                    (form_id,),
                )
                form1_tot = cursor.fetchone()

                cursor.execute(
                    "SELECT dept, institute, hodas3, hodas4, hodfeed3, hodfeed4 FROM form2_tot WHERE form_id = %s",
                    (form_id,),
                )
                form2_tot = cursor.fetchone()
                print("Fetched Form2 Totals:", form2_tot)

                cursor.execute(
                    "SELECT acr, society, hodas5, hodas6, hodfeed5, hodfeed6 FROM form3_tot WHERE form_id = %s",
                    (form_id,),
                )
                form3_tot = cursor.fetchone()
                print("Fetched Form3 Totals:", form3_tot)

                points_data = {
                    "teaching": int(form1_tot[0]) if form1_tot and form1_tot[0] else 0,
                    "feedback": int(form1_tot[1]) if form1_tot and form1_tot[1] else 0,
                    "academic_review": 0,
                    "dept": int(form2_tot[0]) if form2_tot and form2_tot[0] else 0,
                    "institute": int(form2_tot[1]) if form2_tot and form2_tot[1] else 0,
                    "acr": int(form3_tot[0]) if form3_tot and form3_tot[0] else 0,
                    "society": int(form3_tot[1]) if form3_tot and form3_tot[1] else 0,
                }

                if academic_review_data:
                    academic_review_total = sum(float(row[3]) for row in academic_review_data if row[3])
                    points_data["academic_review"] = academic_review_total

                total_points = sum(points_data.values())

                sql_total = """
                    INSERT INTO total (form_id, user_id, acad_years, total, name, dept)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total = %s,
                        name = %s,
                        dept = %s
                """
                cursor.execute(
                    sql_total,
                    (form_id, user_id, selected_year, total_points, user_name, user_dept, total_points, user_name, user_dept),
                )

                connection.commit()

        except Exception as e:
            connection.rollback()
            print(f"[REVIEW DEBUG] Exception in review route: {str(e)}")
            print(f"[REVIEW DEBUG] Exception traceback: {traceback.format_exc()}")
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect("/landing")
        finally:
            connection.close()

    return render_template(
        "reviewform.html",
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
        self_assessment_marks=self_assessment_marks,
        custom_table_data=custom_table_data,
        custom_table_title=custom_table_title,
        user_data=user_data,
        selected_year=selected_year,
        form_id=form_id,
    )


def submit_review(connect_to_database):
    try:
        data = request.json
        user_id = data.get("user_id")
        form_id = data.get("form_id")
        acad_years = data.get("acad_years")
        total_points = data.get("total_points")
        name = data.get("name")
        dept = data.get("dept")

        print(f"[SUBMIT DEBUG] Received data: user_id={user_id}, form_id={form_id}, total={total_points}")

        if not all([user_id, form_id, acad_years, total_points is not None, name, dept]):
            return jsonify({"success": False, "message": "Missing required data"}), 400

        connection = connect_to_database()
        with connection.cursor() as cursor:
            sql_total = """
                INSERT INTO total (form_id, user_id, acad_years, total, name, dept)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total = %s,
                    name = %s,
                    dept = %s
            """
            cursor.execute(sql_total, (form_id, user_id, acad_years, total_points, name, dept, total_points, name, dept))

            connection.commit()
            print(f"[SUBMIT DEBUG] Successfully saved total: {total_points}")

        connection.close()

        return jsonify(
            {
                "success": True,
                "message": "Review submitted successfully!",
                "total_points": total_points,
            }
        )

    except Exception as e:
        print(f"[SUBMIT DEBUG] Error in submit_review: {str(e)}")
        print(f"[SUBMIT DEBUG] Exception traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
