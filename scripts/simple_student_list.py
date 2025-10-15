#!/usr/bin/env python3
"""
Simple Student List Script
Fetches all students sorted by lessons completed and generates a markdown list.
"""

import psycopg2
import os
import re
from dotenv import load_dotenv

def format_phone_number(phone):
    """Format phone number to (XX) XXX-XX-XX format, removing +998 prefix."""
    if not phone:
        return 'No contact'
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', str(phone))
    
    # Remove +998 country code if present
    if digits.startswith('998') and len(digits) >= 12:
        digits = digits[3:]  # Remove 998 prefix
    
    # Check if we have enough digits for formatting (9 digits after removing +998)
    if len(digits) >= 9:
        # Format as (XX) XXX-XX-XX
        return f"({digits[:2]}) {digits[2:5]}-{digits[5:7]}-{digits[7:]}"
    else:
        # Return plain number if not enough digits
        return phone

def get_database_connection():
    """Get database connection using environment variables."""
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL', 
                            'postgresql://postgres:ifJCGOyUnbrjzuPZBmXgGwCXfDiaWOSS@shinkansen.proxy.rlwy.net:49685/railway')
    
    return psycopg2.connect(database_url)

def get_all_students():
    """Fetch all students with their lesson completion data."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            u.first_name,
            u.last_name,
            u.phone_number,
            COUNT(CASE WHEN ulp.is_completed = true THEN 1 END) as completed_lessons
        FROM users u
        LEFT JOIN user_lesson_progress ulp ON u.id = ulp.user_id
        GROUP BY u.id, u.first_name, u.last_name, u.phone_number
        ORDER BY completed_lessons DESC, u.first_name ASC;
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    students = []
    for row in results:
        first_name, last_name, phone, completed = row
        full_name = f'{first_name} {last_name}' if first_name and last_name else (first_name or last_name or 'Unknown')
        contact = phone if phone else 'No contact'
        
        students.append({
            'name': full_name,
            'contact': format_phone_number(phone),
            'lessons_completed': completed
        })
    
    cur.close()
    conn.close()
    
    return students

def generate_simple_markdown(students):
    """Generate a markdown table."""
    md_content = f"""# Student List - Sorted by Lessons Completed

Total Students: {len(students)}

| Order | Full Name | Lessons Completed | Contact |
|-------|-----------|------------------|---------|
"""
    
    for i, student in enumerate(students, 1):
        md_content += f"| {i} | {student['name']} | {student['lessons_completed']} | {student['contact']} |\n"
    
    return md_content

def main():
    try:
        print("Fetching all students...")
        students = get_all_students()
        
        print(f"Found {len(students)} students")
        
        # Generate markdown
        md_content = generate_simple_markdown(students)
        
        # Write to file
        output_path = 'student_list.md'
        with open(output_path, 'w') as f:
            f.write(md_content)
        
        print(f"✅ Created {output_path}")
        
        # Print first 10 to console
        print("\nTop 10 students by lessons completed:")
        for i, student in enumerate(students[:10], 1):
            print(f"{i}. {student['name']} - {student['lessons_completed']} lessons - {student['contact']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()