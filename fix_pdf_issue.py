#!/usr/bin/env python3
"""
Script to fix the PDF viewing issue by:
1. Removing duplicate route definitions
2. Adding proper PDF content-type headers
"""

import os
import re

def fix_app_py():
    app_file = r'c:\Users\mayank salvi\Desktop\appraisal_system-main\app.py'
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and remove the duplicate download_file function
    # Look for the pattern that matches the duplicate
    pattern = r'@app\.route\(\'/uploads/<filename>\'\)\ndef download_file\(filename\):\s+return send_from_directory\(app\.config\[\'UPLOAD_FOLDER\'\], filename\)'
    
    # Replace it with nothing (remove it)
    content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Now enhance the uploaded_file function with proper content-type handling
    old_function = '''@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Ensure the filename is safe and exists in the upload directory
    safe_filename = os.path.basename(filename)  # Prevent directory traversal attacks
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    try:
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=False)
        else:
            abort(404, description="File not found")
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")'''
    
    new_function = '''@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Ensure the filename is safe and exists in the upload directory
    safe_filename = os.path.basename(filename)  # Prevent directory traversal attacks
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    try:
        if os.path.exists(file_path):
            # Determine the mimetype for proper browser handling
            from flask import Response
            
            response = send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=False)
            
            # Set proper content-type for PDFs
            if safe_filename.lower().endswith('.pdf'):
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=' + safe_filename
            
            return response
        else:
            abort(404, description="File not found")
    except Exception as e:
        print(f"Error serving file {safe_filename}: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")'''
    
    # Replace the old function with the new one
    content = content.replace(old_function, new_function)
    
    # Write the fixed content back to the file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed duplicate route and enhanced PDF serving!")
    print("✅ Added proper Content-Type headers for PDF files")
    print("✅ Enhanced error logging for file serving issues")

if __name__ == "__main__":
    fix_app_py()
