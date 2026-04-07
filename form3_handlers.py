from flask import jsonify, render_template, request
import json
import os
import time
import traceback
from werkzeug.utils import secure_filename


def save_3total_points(connect_to_database):
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        form_id = data.get('form_id')
        total = data.get('total')
        acr = data.get('acr')
        society = data.get('society')

        if not form_id or total is None:
            return jsonify({"success": False, "message": "Invalid form data"}), 400

        insert_query = """
            INSERT INTO form3_tot (form_id, total, acr, society)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total = VALUES(total),
                acr = VALUES(acr),
                society = VALUES(society)
        """
        cursor.execute(insert_query, (form_id, total, acr, society))
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Total points saved successfully!",
            "redirect_url": f"/review/{form_id}",
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "An error occurred while saving data"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def form3_page(connect_to_database, form_id):
    try:
        form_id_str = str(form_id)

        conn = connect_to_database()
        cursor = conn.cursor()

        def safe_get(row, index, default=''):
            if index >= len(row) or row[index] is None:
                return default
            return row[index]

        def process_rows(rows):
            if not rows:
                return []
            return [tuple('' if val is None else val for val in row) for row in rows]

        cursor.execute("SELECT srno, title, month, name_of_conf, issn, co_auth, imp_conference, num_of_citations, rating, uploads, form_id FROM self_imp WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        self_improvement_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT * FROM certifications WHERE form_id = %s", (form_id_str,))
        certification_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT srno, name, technology, duration, date, organizing_institute, mode, upload FROM short_term_training WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        training_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT srno, name, month, duration, completion, upload FROM moocs WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        moocs_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT srno, name, month, duration, completion, upload FROM swayam WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        swayam_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT srno, name, technology, duration, date, int_ext, name_of_institute, upload FROM webinar WHERE form_id = %s", (form_id_str,))
        webinar_data = process_rows(cursor.fetchall())

        cursor.execute("""
            SELECT srno, COALESCE(name, ''), COALESCE(month, ''), COALESCE(reg_no, ''),
                   COALESCE(filed_pub_grant, ''), COALESCE(category, ''), COALESCE(uploads, '')
            FROM copyright WHERE form_id = %s ORDER BY srno ASC
        """, (form_id_str,))
        copyright_data = [tuple(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT srno, COALESCE(name, ''), COALESCE(month, ''), COALESCE(reg_no, ''),
                   COALESCE(filed_pub_grant, ''), COALESCE(category, ''), COALESCE(uploads, '')
            FROM patents WHERE form_id = %s ORDER BY srno ASC
        """, (form_id_str,))
        patent_data = [tuple(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM resource_person WHERE form_id = %s", (form_id_str,))
        resource_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT * FROM mem_uni WHERE form_id = %s", (form_id_str,))
        committee_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT srno, name, designation, upload FROM members_conference WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        conference_committee_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT * FROM external_projects WHERE form_id = %s", (form_id_str,))
        project_data = process_rows(cursor.fetchall())

        cursor.execute("SELECT semester, activity, points, order_cpy, order_no, details, COALESCE(uploads, '') as uploads FROM contribution_to_society WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        contribution_data = process_rows(cursor.fetchall())

        try:
            cursor.execute("SELECT self_assessment_marks FROM form3_assessment WHERE form_id = %s", (form_id_str,))
            assessment_result = cursor.fetchone()
            self_assessment_marks = safe_get(assessment_result, 0, '') if assessment_result else ''
        except Exception:
            self_assessment_marks = ''

        cursor.execute("SELECT srno, name, roles, uploads FROM special_mentions WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
        special_mentions_rows = process_rows(cursor.fetchall())
        special_mentions_data = [{"srno": r[0], "name": r[1], "roles": r[2], "uploads": r[3]} for r in special_mentions_rows]

        conference_committee_data = [{"srno": r[0], "name": r[1], "designation": r[2], "upload": r[3]} for r in conference_committee_data]

        custom_table_rows = []
        custom_table_data = []
        custom_table_title = 'Custom Table'
        try:
            cursor.execute("""
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
            """)
            cursor.execute("SELECT srno, columns_data, headers, uploads, table_title FROM custom_table WHERE form_id = %s ORDER BY srno ASC", (form_id_str,))
            custom_table_rows = cursor.fetchall()
            if custom_table_rows and len(custom_table_rows[0]) >= 5 and custom_table_rows[0][4]:
                custom_table_title = custom_table_rows[0][4]
        except Exception:
            custom_table_rows = []

        for row in custom_table_rows:
            try:
                srno = row[0]
                columns_data = json.loads(row[1]) if row[1] else {}
                headers = json.loads(row[2]) if row[2] else []
                uploads = json.loads(row[3]) if row[3] else {}
                merged_columns = columns_data.copy()
                for col_name, upload_path in uploads.items():
                    if col_name in merged_columns:
                        merged_columns[col_name] = {'text': merged_columns[col_name], 'upload': upload_path}
                    else:
                        merged_columns[col_name] = {'text': '', 'upload': upload_path}
                custom_table_data.append({'srno': srno, 'columns_data': json.dumps(merged_columns), 'headers': headers})
            except Exception:
                custom_table_data.append({'srno': row[0] if row else 0, 'columns_data': '{}', 'headers': []})

        cursor.close()
        conn.close()

        return render_template(
            'form3.html',
            form_id=form_id,
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
            project_data=project_data,
            contribution_data=contribution_data,
            special_mentions_data=special_mentions_data,
            conference_committee_data=conference_committee_data,
            custom_table_data=custom_table_data,
            custom_table_title=custom_table_title,
            self_assessment_marks=self_assessment_marks,
        )

    except Exception as e:
        print(f"Error loading form3 data: {e}")
        traceback.print_exc()
        return render_template('form3.html', form_id=form_id)


def reset_form3(connect_to_database):
    try:
        form_id = request.form.get('formId')

        if not form_id:
            return jsonify({"status": "error", "message": "Form ID is required"}), 400

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            cursor.execute("START TRANSACTION")
            cursor.execute("DELETE FROM self_imp WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM certifications WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM copyright WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM resource_person WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM mem_uni WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM external_projects WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM contribution_to_society WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM moocs WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM swayam WHERE form_id = %s", (form_id,))
            cursor.execute("DELETE FROM webinar WHERE form_id = %s", (form_id,))
            try:
                cursor.execute("DELETE FROM form3_assessment WHERE form_id = %s", (form_id,))
            except Exception:
                pass
            cursor.execute("DELETE FROM form3_tot WHERE form_id = %s", (form_id,))

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

def save_form3_data(connect_to_database, app, allowed_file):
    """
    Handle form3 data submission and save to database
    """
    conn = None
    cursor = None
    
    try:
        # Debug form data first
        # debug_form_data(request)  # Removed undefined debug function
        
        form_id = request.form.get('formId')
        if not form_id:
            return jsonify({'status': 'error', 'message': 'Form ID is required'}), 400
            
        form_id = str(form_id)
        print(f"Processing form3 data for form_id: {form_id}")
        
        # Connect to database
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("START TRANSACTION")
        
        # Ensure form3_assessment table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS form3_assessment (
                form_id VARCHAR(45) PRIMARY KEY,
                self_assessment_marks VARCHAR(45) DEFAULT '0'
            )
        """)
        
        # Create custom_table table if it doesn't exist
        cursor.execute("""
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
        """)
        
        # ===== PROCESS SELF IMPROVEMENT DATA =====
        self_improvement_entries = []
        for key in request.form.keys():
            if key.startswith('selfImprovement[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    self_improvement_entries.append(entry)
                    print(f"Processed self-improvement entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing selfImprovement entry: {e}")
        
        # Always delete old self-improvement data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, uploads FROM self_imp WHERE form_id = %s", (form_id,))
        old_selfimp_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM self_imp WHERE form_id = %s", (form_id,))
        
        # Fixed self-improvement data processing
        if self_improvement_entries:
            
            for idx, item in enumerate(self_improvement_entries, start=1):
                upload_path = None
                
                # Get srno from the item data
                srno = str(item.get('srno', idx))
                
                # Check for file upload using multiple possible naming patterns
                possible_file_keys = [
                    f"selfImprovement_{srno}_file",
                    f"selfImprovement_{idx}_file",
                    f"selfImprovement_{idx-1}_file"  # In case of 0-based indexing
                ]
                
                file_found = False
                for file_key in possible_file_keys:
                    if file_key in request.files:
                        file = request.files[file_key]
                        if file and file.filename and allowed_file(file.filename):
                            try:
                                filename = secure_filename(file.filename)
                                timestamp = str(int(time.time()))
                                name, ext = os.path.splitext(filename)
                                unique_filename = f"selfimp_{form_id}_{timestamp}_{srno}_{name}{ext}"
                                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)
                                upload_path = f"uploads/{unique_filename}"
                                print(f"Saved self-improvement file: {unique_filename} using key: {file_key}")
                                file_found = True
                                break
                            except Exception as e:
                                print(f"Error saving self-improvement file: {e}")
                
                # If no new file found, use previous upload
                if not upload_path:
                    upload_path = old_selfimp_uploads.get(srno, None)
                    print(f"No new file for self-improvement srno '{srno}', using previous upload: {upload_path}")
                
                cursor.execute("""
                    INSERT INTO self_imp (srno, title, month, name_of_conf, issn, co_auth, imp_conference, num_of_citations, rating, form_id, uploads)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.get('srno', idx),
                    item.get('title', ''),
                    item.get('month', ''),
                    item.get('name_of_conf', ''),
                    item.get('issn', ''),
                    item.get('co_auth', ''),
                    item.get('imp_conference', ''),
                    item.get('num_of_citations', ''),
                    item.get('rating', ''),
                    form_id,
                    upload_path
                ))
            print(f"Inserted {len(self_improvement_entries)} self improvement records")
            print(f"Inserted {len(self_improvement_entries)} self improvement records")

        # ===== PROCESS SHORT-TERM TRAINING DATA =====
        training_entries = []
        training_files = {}
        
        for key in request.form.keys():
            if key.startswith('training[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    index = key[9:-1]
                    training_entries.append((index, entry))
                    print(f"Processed training entry from key: {key}, index: {index}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing training entry: {e}")

        for key in request.files.keys():
            if key.startswith('trainingFile[') and key.endswith(']'):
                index = key[13:-1]
                file = request.files[key]
                if file and file.filename and file.filename.strip():
                    training_files[index] = file
                    print(f"Added training file for index {index}: {file.filename}")

        # Always delete old short-term training data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM short_term_training WHERE form_id = %s", (form_id,))
        old_training_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM short_term_training WHERE form_id = %s", (form_id,))
        
        if training_entries:
            for index, item in training_entries:
                upload_path = None
                srno = str(item.get('srno', index))
                if index in training_files:
                    file = training_files[index]
                    if allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"training_{form_id}_{timestamp}_{index}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved training file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving training file: {e}")
                if not upload_path:
                    upload_path = old_training_uploads.get(srno, None)
                    print(f"No new file for training srno '{srno}', using previous upload: {upload_path}")
                cursor.execute("""
                    INSERT INTO short_term_training (srno, form_id, name, technology, duration, date, organizing_institute, mode, upload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.get('srno', index),
                    form_id,
                    item.get('name', ''),
                    item.get('technology', ''),
                    item.get('duration', ''),
                    item.get('date', ''),
                    item.get('organizing_institute', ''),
                    item.get('mode', ''),
                    upload_path
                ))
            print(f"Inserted {len(training_entries)} training records")

                  

        # ===== PROCESS SWAYAM DATA =====
        swayam_entries = []
        for key in request.form.keys():
            if key.startswith('swayam[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    index = key[7:-1]
                    swayam_entries.append((index, entry))
                    print(f"Processed swayam entry from key: {key}, index: {index}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing swayam entry: {e}")
        
        swayam_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('swayam_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 2:
                    srno = parts[1]
                    swayam_files[srno] = request.files[file_key]
                    print(f"Found SWAYAM file for srno {srno}: {request.files[file_key].filename}")
        
        # Always delete old SWAYAM data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM swayam WHERE form_id = %s", (form_id,))
        old_swayam_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM swayam WHERE form_id = %s", (form_id,))
        
        if swayam_entries:
            
            for index, item in swayam_entries:
                srno = str(item.get('srno', index))
                upload_path = None
                
                # Enhanced file handling for SWAYAM
                if srno in swayam_files:
                    file = swayam_files[srno]
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            # Reset file stream position to beginning
                            file.seek(0)
                            
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"swayam_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            
                            # Read file content and write it
                            file_content = file.read()
                            print(f"SWAYAM file content size: {len(file_content)} bytes")
                            
                            with open(file_path, 'wb') as f:
                                f.write(file_content)
                            
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved SWAYAM file: {unique_filename} ({len(file_content)} bytes)")
                        except Exception as e:
                            print(f"Error saving SWAYAM file: {e}")
                
                if not upload_path:
                    upload_path = old_swayam_uploads.get(srno, None)
                    print(f"No new file for SWAYAM srno '{srno}', using previous upload: {upload_path}")
                
                # Map frontend keys to DB columns
                name = item.get('name_of_swayam_course_undertaken', '') or item.get('name', '')
                month = item.get('month/year', '') or item.get('month', '')
                duration = item.get('duration_of_course', '') or item.get('duration', '')
                completion = item.get('certification_status', '') or item.get('completion', '')
                
                cursor.execute("""
                    INSERT INTO swayam (srno, name, month, duration, completion, form_id, upload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.get('srno', index),
                    name,
                    month,
                    duration,
                    completion,
                    form_id,
                    upload_path
                ))
            print(f"Inserted {len(swayam_entries)} SWAYAM records")

        # ===== PROCESS CERTIFICATION DATA =====
        certification_entries = []
        certification_files = {}
        
        for key in request.form.keys():
            if key.startswith('certification[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    index = key[14:-1]
                    certification_entries.append((index, entry))
                    print(f"Processed certification entry from key: {key}, index: {index}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing certification entry: {e}")
        
        for key in request.files.keys():
            if key.startswith('certificationFile[') and key.endswith(']'):
                index = key[18:-1]
                file = request.files[key]
                if file and file.filename and file.filename.strip():
                    certification_files[index] = file
                    print(f"Added certification file for index {index}: {file.filename}")
        
        # Always delete old certification data for this form_id (even if no new entries)
        cursor.execute("SELECT name, uploads FROM certifications WHERE form_id = %s", (form_id,))
        old_cert_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM certifications WHERE form_id = %s", (form_id,))
        
        if certification_entries:
            for index, item in certification_entries:
                upload_path = None
                cert_name = str(item.get('name', ''))
                if index in certification_files:
                    file = certification_files[index]
                    if allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"cert_{form_id}_{timestamp}_{index}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved certification file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving certification file: {e}")
                # If no new file, try to use existing upload sent from frontend or fallback to previous DB value
                if not upload_path:
                    upload_path = item.get('uploads') or old_cert_uploads.get(cert_name)
                    print(f"No new file for certification '{cert_name}', using upload: {upload_path}")
                cursor.execute("""
                    INSERT INTO certifications (form_id, name, uploads)
                    VALUES (%s, %s, %s)
                """, (
                    form_id,
                    cert_name,
                    upload_path
                ))
            print(f"Inserted {len(certification_entries)} certification records")

        # ===== PROCESS COPYRIGHT DATA =====
        copyright_entries = []
        copyright_files = {}
        
        # Debug: Print all form keys
        print("\n==== DEBUG: All form keys ====")
        for key in request.form.keys():
            print(f"Form key: {key}")
        
        print("\n==== DEBUG: Copyright form data ====")
        for key in request.form.keys():
            if key.startswith('copyright['):
                print(f"Copyright key: {key} = {request.form.get(key)[:100]}...")
                
        # Process copyright entries
        for key in request.form.keys():
            if key.startswith('copyright[') and key.endswith(']'):
                try:
                    raw_data = request.form.get(key)
                    print(f"Raw data for {key}: {raw_data[:100]}...")
                    
                    entry = json.loads(raw_data)
                    index = key[10:-1]
                    copyright_entries.append((index, entry))
                    print(f"Successfully processed copyright entry from key: {key}, index: {index}, data: {entry}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing copyright entry from key {key}: {e}")
                    print(f"Problematic data: {request.form.get(key)[:100]}...")
                except Exception as e:
                    print(f"Unexpected error processing copyright entry {key}: {str(e)}")
        
        # Process copyright files
        print("\n==== DEBUG: Copyright file uploads ====")
        for file_key in request.files:
            if file_key.startswith('copyright_') and file_key.endswith('_file'):
                index = file_key[10:-5]
                file = request.files[file_key]
                if file and file.filename and file.filename.strip():
                    copyright_files[index] = file
                    print(f"Added copyright file for index {index}: {file.filename}")
                    
        print(f"\nTotal copyright entries found: {len(copyright_entries)}")
        print(f"Total copyright files found: {len(copyright_files)}")
        
        if not copyright_entries:
            print("WARNING: No copyright entries were processed successfully!")
        
        # Always delete old copyright data for this form_id (even if no new entries)
        cursor.execute("SELECT reg_no, uploads FROM copyright WHERE form_id = %s", (form_id,))
        old_copyright_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        # Get existing copyright entries for debugging
        cursor.execute("SELECT COUNT(*) FROM copyright WHERE form_id = %s", (form_id,))
        existing_count = cursor.fetchone()[0]
        print(f"\nDeleting {existing_count} existing copyright entries for form_id {form_id}")
        
        # Delete existing entries
        cursor.execute("DELETE FROM copyright WHERE form_id = %s", (form_id,))
        
        if copyright_entries:
            print(f"\nInserting {len(copyright_entries)} new copyright entries:")
            for idx, (index, item) in enumerate(copyright_entries, start=1):
                print(f"Processing entry {idx}, index: {index}, name: {item.get('name', '')[:20]}...")
                upload_path = None
                if index in copyright_files:
                    file = copyright_files[index]
                    if allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"copyright_{form_id}_{timestamp}_{index}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved copyright file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving copyright file: {e}")
                # If no new file, try to use previous upload path by reg_no
                if not upload_path:
                    reg_no = str(item.get('reg_no', ''))
                    upload_path = old_copyright_uploads.get(reg_no, None)
                try:
                    cursor.execute("""
                        INSERT INTO copyright (srno, form_id, name, month, reg_no, filed_pub_grant, category, uploads)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        idx,
                        form_id,
                        item.get('name', ''),
                        item.get('month', ''),
                        item.get('reg_no', ''),
                        item.get('filed_pub_grant', ''),
                        item.get('category', ''),
                        upload_path
                    ))
                    print(f"Successfully inserted copyright entry {idx}")
                except Exception as e:
                    print(f"Error inserting copyright entry {idx}: {str(e)}")
                    # Continue with other entries instead of failing completely
                    conn.rollback()
                    cursor.execute('START TRANSACTION')
            print(f"Inserted {len(copyright_entries)} copyright records")

        # ===== PROCESS PATENT DATA =====
        patent_entries = []
        patent_files = {}
        
        for key in request.form.keys():
            if key.startswith('patent[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    index = key[7:-1]
                    patent_entries.append((index, entry))
                    print(f"Processed patent entry from key: {key}, index: {index}, data: {entry}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing patent entry {key}: {e}")
        
        for file_key in request.files.keys():
            if file_key.startswith('patent_') and file_key.endswith('_file'):
                index = file_key[7:-5]
                file = request.files[file_key]
                if file and file.filename and file.filename.strip():
                    patent_files[index] = file
                    print(f"Added patent file for index {index}: {file.filename}")
        
        # Always delete old patent data for this form_id (even if no new entries)
        cursor.execute("SELECT reg_no, uploads FROM patents WHERE form_id = %s", (form_id,))
        old_patent_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM patents WHERE form_id = %s", (form_id,))
        
        if patent_entries:
            print(f"Found {len(patent_entries)} patent entries to process")
            for idx, (index, item) in enumerate(patent_entries, start=1):
                upload_path = None
                if index in patent_files:
                    file = patent_files[index]
                    if allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"patent_{form_id}_{timestamp}_{index}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved patent file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving patent file for index {index}: {e}")
                # If no new file, try to use previous upload path by reg_no
                if not upload_path:
                    reg_no = str(item.get('reg_no', ''))
                    upload_path = old_patent_uploads.get(reg_no, None)
                cursor.execute("""
                    INSERT INTO patents (srno, form_id, name, month, reg_no, filed_pub_grant, category, uploads)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('name', ''),
                    item.get('month', ''),
                    item.get('reg_no', ''),
                    item.get('filed_pub_grant', ''),
                    item.get('category', ''),
                    upload_path
                ))
            print(f"Successfully inserted {len(patent_entries)} patent records")
        
        # Verify what was saved
        cursor.execute("SELECT srno, name, uploads FROM patents WHERE form_id = %s ORDER BY srno", (form_id,))
        saved_patents = cursor.fetchall()
        print(f"Verified: {len(saved_patents)} patent records saved in database")

        # ===== PROCESS RESOURCE PERSON DATA (with file uploads) =====
        resource_entries = []
        for key in request.form.keys():
            if key.startswith('resourcePerson[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    resource_entries.append(entry)
                    print(f"Processed resource person entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing resource person entry: {e}")
        
        # Collect uploaded files for resource person rows
        resource_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('resource_person_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 3:
                    srno = parts[2]  # pattern resource_person_<srno>_file
                    resource_files[srno] = request.files[file_key]
        
        # Always delete old resource person data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM resource_person WHERE form_id = %s", (form_id,))
        old_resource_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM resource_person WHERE form_id = %s", (form_id,))
        
        if resource_entries:

            for idx, item in enumerate(resource_entries, start=1):
                srno = str(item.get('srno', idx))
                upload_path = None

                # Handle file upload
                if srno in resource_files:
                    file = resource_files[srno]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"resource_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved resource person file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving resource person file for srno {srno}: {e}")
                # If no new file, use previous path if available
                if not upload_path:
                    upload_path = old_resource_uploads.get(srno, None)

                cursor.execute("""
                    INSERT INTO resource_person (srno, form_id, name, dept, name_oi, num_op, upload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('topic', ''),
                    item.get('department', ''),
                    item.get('institute', ''),
                    item.get('participants', 0),
                    upload_path
                ))
            print(f"Inserted {len(resource_entries)} resource person records with file uploads")

        # ===== PROCESS UNIVERSITY COMMITTEE DATA (with file uploads) =====
        committee_entries = []
        for key in request.form.keys():
            if key.startswith('universityCommittee[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    committee_entries.append(entry)
                    print(f"Processed committee entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing universityCommittee entry: {e}")
        
        # Collect uploaded files for committee rows
        committee_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('university_committee_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 3:
                    srno = parts[2]  # pattern university_committee_<srno>_file
                    committee_files[srno] = request.files[file_key]
        
        # Always delete old university committee data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM mem_uni WHERE form_id = %s", (form_id,))
        old_committee_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM mem_uni WHERE form_id = %s", (form_id,))
        
        if committee_entries:
            for idx, item in enumerate(committee_entries, start=1):
                srno = str(item.get('srno', idx))
                upload_path = None
                if srno in committee_files:
                    file = committee_files[srno]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"committee_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved committee file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving committee file for srno {srno}: {e}")
                if not upload_path:
                    upload_path = old_committee_uploads.get(srno, None)
                cursor.execute("""
                    INSERT INTO mem_uni (srno, form_id, name, roles, designation, upload)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('committee', ''),
                    item.get('responsibilities', ''),
                    item.get('designation', ''),
                    upload_path
                ))
            print(f"Inserted {len(committee_entries)} committee records with file uploads")

        # ===== PROCESS EXTERNAL PROJECTS DATA (with file uploads) =====
        project_entries = []
        for key in request.form.keys():
            if key.startswith('externalProjects[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    project_entries.append(entry)
                    print(f"Processed project entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing externalProjects entry: {e}")
        
        # Collect files
        project_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('external_projects_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 3:
                    srno = parts[2]  # external_projects_<srno>_file
                    project_files[srno] = request.files[file_key]
        
        # Always delete old external projects data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM external_projects WHERE form_id = %s", (form_id,))
        old_proj_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM external_projects WHERE form_id = %s", (form_id,))
        
        if project_entries:
            for idx, item in enumerate(project_entries, start=1):
                srno = str(item.get('srno', idx))
                upload_path = None
                if srno in project_files:
                    file = project_files[srno]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"external_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved external project file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving external project file for srno {srno}: {e}")
                if not upload_path:
                    upload_path = old_proj_uploads.get(srno, None)
                cursor.execute("""
                    INSERT INTO external_projects (srno, form_id, role, `desc`, contribution, university, duration, comments, upload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('role', ''),
                    item.get('description', ''),
                    item.get('contribution', ''),
                    item.get('university', ''),
                    item.get('duration', ''),
                    item.get('comments', ''),
                    upload_path
                ))
            print(f"Inserted {len(project_entries)} external project records with file uploads")

        # ===== PROCESS MEMBER OF CONFERENCE/JOURNAL COMMITTEE DATA =====
        conference_entries = []
        for key in request.form.keys():
            if key.startswith('conferenceCommittee[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    conference_entries.append(entry)
                    print(f"Processed conference committee entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing conference committee entry: {e}")

        conference_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('conference_committee_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 3:
                    srno = parts[2]  # pattern: conference_committee_{srno}_file
                    conference_files[srno] = request.files[file_key]

        # Always delete old conference committee data for this form_id (even if no new entries)
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members_conference (
                srno INT,
                form_id VARCHAR(45),
                name TEXT,
                designation TEXT,
                upload TEXT
            )
        """)
        cursor.execute("SELECT srno, upload FROM members_conference WHERE form_id = %s", (form_id,))
        old_conf_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM members_conference WHERE form_id = %s", (form_id,))
        
        if conference_entries:

            for idx, item in enumerate(conference_entries, start=1):
                srno = str(item.get('srno', idx))
                upload_path = None
                if srno in conference_files:
                    file = conference_files[srno]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name_part, ext = os.path.splitext(filename)
                            unique_filename = f"conf_{form_id}_{timestamp}_{srno}_{name_part}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved conference committee file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving conference committee file for srno {srno}: {e}")
                if not upload_path:
                    upload_path = old_conf_uploads.get(srno, None)
                cursor.execute("""
                    INSERT INTO members_conference (srno, form_id, name, designation, upload)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('name', ''),
                    item.get('designation', ''),
                    upload_path
                ))
            print(f"Inserted {len(conference_entries)} conference committee records with file uploads")

# ===== PROCESS SPECIAL MENTIONS DATA (with file uploads) =====
        special_mention_entries = []
        for key in request.form.keys():
            if key.startswith('specialMentions[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    special_mention_entries.append(entry)
                    print(f"Processed special mention entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing special mention entry: {e}")

        special_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('special_mentions_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 3:
                    srno = parts[2]  # pattern: special_mentions_{srno}_file
                    special_files[srno] = request.files[file_key]

        # Always delete old special mentions data for this form_id (even if no new entries)
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS special_mentions (
                srno INT,
                form_id VARCHAR(45),
                name TEXT,
                roles TEXT,
                uploads TEXT
            )
        """)
        cursor.execute("SELECT srno, uploads FROM special_mentions WHERE form_id = %s", (form_id,))
        old_special_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM special_mentions WHERE form_id = %s", (form_id,))
        
        if special_mention_entries:
            for idx, item in enumerate(special_mention_entries, start=1):
                srno = str(item.get('srno', idx))
                upload_path = None
                if srno in special_files:
                    file = special_files[srno]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name_part, ext = os.path.splitext(filename)
                            unique_filename = f"special_{form_id}_{timestamp}_{srno}_{name_part}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved special mention file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving special mention file for srno {srno}: {e}")
                if not upload_path:
                    upload_path = old_special_uploads.get(srno, None)
                cursor.execute("""
                    INSERT INTO special_mentions (srno, form_id, name, roles, uploads)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('name', ''),
                    item.get('roles', ''),
                    upload_path
                ))
            print(f"Inserted {len(special_mention_entries)} special mention records")

        # ===== PROCESS CONTRIBUTION TO SOCIETY DATA (with file uploads) =====
        contribution_entries = []
        for key in request.form.keys():
            if key.startswith('contribution[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    contribution_entries.append(entry)
                    print(f"Processed contribution entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing contribution entry: {e}")

        contribution_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('contribution_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 2:
                    srno = parts[1]
                    contribution_files[srno] = request.files[file_key]

        # Always delete old contribution to society data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, uploads FROM contribution_to_society WHERE form_id = %s", (form_id,))
        old_contrib_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM contribution_to_society WHERE form_id = %s", (form_id,))
        
        if contribution_entries:
            for idx, item in enumerate(contribution_entries, start=1):
                srno = str(item.get('srno', idx))
                upload_path = None
                if srno in contribution_files:
                    file = contribution_files[srno]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"contrib_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved contribution file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving contribution file for srno {srno}: {e}")
                if not upload_path:
                    upload_path = old_contrib_uploads.get(srno, None)
                cursor.execute("""
                    INSERT INTO contribution_to_society (srno, form_id, semester, activity, points, order_cpy, order_no, details, uploads)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    idx,
                    form_id,
                    item.get('semester', ''),
                    item.get('activity', ''),
                    item.get('points', ''),
                    item.get('order_cpy', ''),
                    item.get('order_no', ''),
                    item.get('details', ''),
                    upload_path
                ))
            print(f"Inserted {len(contribution_entries)} contribution records with file uploads")

                # ===== PROCESS MOOCS DATA =====
        moocs_entries = []
        for key in request.form.keys():
            if key.startswith('moocs[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    index = key[6:-1]
                    moocs_entries.append((index, entry))
                    print(f"Processed moocs entry from key: {key}, index: {index}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing moocs entry: {e}")
        
        # Gather files
        moocs_files = {}
        for file_key in request.files.keys():
            if file_key.startswith('moocs_') and file_key.endswith('_file'):
                parts = file_key.split('_')
                if len(parts) >= 2:
                    srno = parts[1]
                    moocs_files[srno] = request.files[file_key]
                    print(f"Found MOOCS file for srno {srno}: {request.files[file_key].filename}")
        
        # Always delete old MOOCS data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM moocs WHERE form_id = %s", (form_id,))
        old_moocs_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM moocs WHERE form_id = %s", (form_id,))
        
        if moocs_entries:
            
            for index, item in moocs_entries:
                srno = str(item.get('srno', index))
                upload_path = None                # Enhanced file handling for MOOCS
                if srno in moocs_files:
                    file = moocs_files[srno]
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            # Reset file stream position to beginning
                            file.seek(0)
                            
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"moocs_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            
                            # Read file content and write it
                            file_content = file.read()
                            print(f"MOOCS file content size: {len(file_content)} bytes")
                            
                            with open(file_path, 'wb') as f:
                                f.write(file_content)
                            
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved MOOCS file: {unique_filename} ({len(file_content)} bytes)")
                        except Exception as e:
                            print(f"Error saving MOOCS file: {e}")
                
                if not upload_path:
                    upload_path = old_moocs_uploads.get(srno, None)
                    print(f"No new file for MOOCS srno '{srno}', using previous upload: {upload_path}")
                
                # Map frontend keys to DB columns
                name = item.get('name_of_moocs_course_undertaken', '') or item.get('name', '')
                month = item.get('month/year', '') or item.get('month', '')
                duration = item.get('duration_of_course', '') or item.get('duration', '')
                completion = item.get('certification_status', '') or item.get('completion', '')
                
                cursor.execute("""
                    INSERT INTO moocs (srno, name, month, duration, completion, form_id, upload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.get('srno', index),
                    name,
                    month,
                    duration,
                    completion,
                    form_id,
                    upload_path
                ))
            print(f"Inserted {len(moocs_entries)} MOOCS records")

        # ===== PROCESS WEBINAR DATA =====
        webinar_entries = []
        for key in request.form.keys():
            if key.startswith('webinar[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    webinar_entries.append(entry)
                    print(f"Processed Webinar entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing Webinar entry: {e}")
        
        # Always delete old webinar data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, upload FROM webinar WHERE form_id = %s", (form_id,))
        old_webinar_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM webinar WHERE form_id = %s", (form_id,))
        
        if webinar_entries:
            for item in webinar_entries:
                upload_path = None
                srno = str(item.get('srno', ''))
                file_key = f"webinar_{srno}_file"
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"webinar_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved Webinar file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving Webinar file: {e}")
                if not upload_path:
                    upload_path = old_webinar_uploads.get(srno, None)
                    print(f"No new file for Webinar srno '{srno}', using previous upload: {upload_path}")
                cursor.execute("""
                    INSERT INTO webinar (form_id, name, technology, duration, date, int_ext, name_of_institute, srno, upload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    form_id,
                    item.get('name', ''),
                    item.get('technology', ''),
                    item.get('duration', ''),
                    item.get('date', ''),
                    item.get('int_ext', ''),
                    item.get('name_of_institute', ''),
                    item.get('srno', ''),
                    upload_path
                ))
            print(f"Inserted {len(webinar_entries)} webinar records")

        # ===== PROCESS CONTRIBUTION TO SOCIETY DATA =====
        contribution_entries = []
        for key in request.form.keys():
            if key.startswith('contributionToSociety[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    contribution_entries.append(entry)
                    print(f"Processed contribution entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing contribution entry: {e}")
        
        if contribution_entries:
            # Fetch previous uploads for this form_id by srno
            cursor.execute("SELECT srno, upload FROM contribution_to_society WHERE form_id = %s", (form_id,))
            old_contribution_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
            cursor.execute("DELETE FROM contribution_to_society WHERE form_id = %s", (form_id,))
            for item in contribution_entries:
                upload_path = None
                srno = str(item.get('srno', ''))
                file_key = f"contribution_{srno}_file"
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            name, ext = os.path.splitext(filename)
                            unique_filename = f"contribution_{form_id}_{timestamp}_{srno}_{name}{ext}"
                            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                            file.save(file_path)
                            upload_path = f"uploads/{unique_filename}"
                            print(f"Saved Contribution file: {unique_filename}")
                        except Exception as e:
                            print(f"Error saving Contribution file: {e}")
                if not upload_path:
                    upload_path = old_contribution_uploads.get(srno, None)
                    print(f"No new file for Contribution srno '{srno}', using previous upload: {upload_path}")
                cursor.execute("""
                    INSERT INTO contribution_to_society (form_id, activity, description, impact, srno, upload)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    form_id,
                    item.get('activity', ''),
                    item.get('description', ''),
                    item.get('impact', ''),
                    srno,
                    upload_path
                ))
            print(f"Inserted {len(contribution_entries)} contribution records")

        # ===== PROCESS CUSTOM TABLE DATA =====
        custom_table_entries = []
        for key in request.form.keys():
            if key.startswith('customTable[') and key.endswith(']'):
                try:
                    entry = json.loads(request.form.get(key))
                    custom_table_entries.append(entry)
                    print(f"Processed custom table entry from key: {key}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing custom table entry: {e}")
        
        # Always delete old custom table data for this form_id (even if no new entries)
        cursor.execute("SELECT srno, uploads FROM custom_table WHERE form_id = %s", (form_id,))
        old_custom_uploads = {str(row[0]): row[1] for row in cursor.fetchall() if row[0] is not None}
        cursor.execute("DELETE FROM custom_table WHERE form_id = %s", (form_id,))
        
        if custom_table_entries:
            # Get the table title
            table_title = request.form.get('customTableTitle', 'Custom Table')
            print(f"Custom table title: {table_title}")
            
            for item in custom_table_entries:
                uploads_data = {}
                srno = str(item.get('srno', ''))
                columns_data = item.get('columns_data', {})
                headers = item.get('headers', [])
                
                # Process file uploads for each column
                for column_name in headers:
                    file_key = f"customTable_{srno}_{column_name}_file"
                    if file_key in request.files:
                        file = request.files[file_key]
                        if file and file.filename and allowed_file(file.filename):
                            try:
                                filename = secure_filename(file.filename)
                                timestamp = str(int(time.time()))
                                name, ext = os.path.splitext(filename)
                                unique_filename = f"custom_{form_id}_{timestamp}_{srno}_{column_name}_{name}{ext}"
                                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)
                                uploads_data[column_name] = f"uploads/{unique_filename}"
                                print(f"Saved custom table file: {unique_filename} for column: {column_name}")
                            except Exception as e:
                                print(f"Error saving custom table file for column {column_name}: {e}")
                
                # If no new uploads, use previous uploads
                if not uploads_data and srno in old_custom_uploads:
                    try:
                        uploads_data = json.loads(old_custom_uploads[srno]) if old_custom_uploads[srno] else {}
                        print(f"No new files for custom table srno '{srno}', using previous uploads: {uploads_data}")
                    except (json.JSONDecodeError, TypeError):
                        uploads_data = {}
                
                cursor.execute("""
                    INSERT INTO custom_table (form_id, srno, columns_data, headers, uploads, table_title)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    form_id,
                    item.get('srno', ''),
                    json.dumps(columns_data),
                    json.dumps(headers),
                    json.dumps(uploads_data),
                    table_title
                ))
            print(f"Inserted {len(custom_table_entries)} custom table records")

        # ===== SAVE SELF-ASSESSMENT MARKS =====
        self_assessment_marks = request.form.get('selfAssessmentMarks', '0')
        print(f"Self-assessment marks: {self_assessment_marks}")
        
        cursor.execute("""
            INSERT INTO form3_assessment (form_id, self_assessment_marks) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE self_assessment_marks = %s
        """, (form_id, self_assessment_marks, self_assessment_marks))
        
        # Commit all changes
        conn.commit()
        print("Form3 data saved successfully!")
        
        return jsonify({
            'status': 'success', 
            'message': 'Form 3 data saved successfully',
            'debug': {
                'self_improvement_records': len(self_improvement_entries),
                'training_records': len(training_entries),
                'certification_records': len(certification_entries),
                'copyright_records': len(copyright_entries),
                'patent_records': len(patent_entries),
                'resource_records': len(resource_entries),
                'committee_records': len(committee_entries),
                'project_records': len(project_entries),
                'moocs_records': len(moocs_entries),
                'swayam_records': len(swayam_entries),
                'webinar_records': len(webinar_entries),
                'contribution_records': len(contribution_entries),
                'custom_table_records': len(custom_table_entries),
                'special_mention_records': len(special_mention_entries)
            }
        })
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error saving form3 data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
