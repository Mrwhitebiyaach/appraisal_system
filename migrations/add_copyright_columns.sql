-- Add new columns to copyright table
ALTER TABLE copyright 
ADD COLUMN filed_pub_grant VARCHAR(20) AFTER reg_no,
ADD COLUMN category VARCHAR(20) AFTER filed_pub_grant,
ADD COLUMN uploads VARCHAR(255) AFTER category;
