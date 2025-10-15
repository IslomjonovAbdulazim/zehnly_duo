#!/usr/bin/env python3
"""
User Lesson Progress Analysis Script
Analyzes user engagement and lesson completion data from the database.
"""

import psycopg2
import json
import os
from datetime import datetime
from dotenv import load_dotenv

def get_database_connection():
    """Get database connection using environment variables."""
    load_dotenv()
    
    # Try to get from environment first, fallback to hardcoded
    database_url = os.getenv('DATABASE_URL', 
                            'postgresql://postgres:ifJCGOyUnbrjzuPZBmXgGwCXfDiaWOSS@shinkansen.proxy.rlwy.net:49685/railway')
    
    return psycopg2.connect(database_url)

def analyze_user_progress():
    """Analyze user lesson progress and return structured data."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    # Query to get user lesson completion statistics
    query = """
        SELECT 
            u.id as user_id,
            u.zehn_id,
            u.first_name,
            u.last_name,
            u.phone_number,
            COUNT(CASE WHEN ulp.is_completed = true THEN 1 END) as completed_lessons,
            COUNT(ulp.id) as total_attempts,
            AVG(CASE WHEN ulp.is_completed = true THEN ulp.score END) as avg_score,
            MAX(ulp.completed_at) as last_completed
        FROM users u
        LEFT JOIN user_lesson_progress ulp ON u.id = ulp.user_id
        GROUP BY u.id, u.zehn_id, u.first_name, u.last_name, u.phone_number
        HAVING COUNT(ulp.id) > 0
        ORDER BY completed_lessons DESC, total_attempts DESC;
    """
    
    cur.execute(query)
    results = cur.fetchall()
    
    # Process results
    user_data = []
    for i, row in enumerate(results, 1):
        user_id, zehn_id, first_name, last_name, phone, completed, total, avg_score, last_completed = row
        full_name = f'{first_name} {last_name}' if first_name and last_name else (first_name or last_name or 'Unknown')
        
        user_data.append({
            'rank': i,
            'user_id': user_id,
            'zehn_id': zehn_id,
            'name': full_name,
            'phone': phone or 'N/A',
            'completed_lessons': completed,
            'total_attempts': total,
            'avg_score': avg_score,
            'last_completed': last_completed
        })
    
    cur.close()
    conn.close()
    
    return user_data

def generate_markdown_report(user_data, output_path='docs/status.md'):
    """Generate a formatted markdown report."""
    
    # Create the markdown content
    md_content = f'''# User Lesson Progress Analysis

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Users with Activity:** {len(user_data)}

## Summary Statistics

- **Most Active User:** {user_data[0]['name'] if user_data else 'N/A'} with {user_data[0]['completed_lessons'] if user_data else 0} completed lessons
- **Total Lesson Completions:** {sum(user['completed_lessons'] for user in user_data)}
- **Average Lessons per User:** {sum(user['completed_lessons'] for user in user_data) / len(user_data) if user_data else 0:.1f}

## Top Users by Completed Lessons

| Rank | Name | Zehn ID | Phone | Completed Lessons | Total Attempts | Avg Score | Last Completed |
|------|------|---------|-------|:----------------:|:---------------:|:---------:|:-------------:|
'''

    # Add top 20 users to the table
    for user in user_data[:20]:
        avg_score = f'{user["avg_score"]:.1f}%' if user['avg_score'] else 'N/A'
        last_completed = user['last_completed'].strftime('%Y-%m-%d') if user['last_completed'] else 'Never'
        
        md_content += f'| {user["rank"]} | {user["name"]} | `{user["zehn_id"]}` | {user["phone"]} | **{user["completed_lessons"]}** | {user["total_attempts"]} | {avg_score} | {last_completed} |\n'

    md_content += '''
## User Engagement Breakdown

### By Completion Count:
'''

    # Count users by lesson completion ranges
    completion_ranges = {
        '20+ lessons': len([u for u in user_data if u['completed_lessons'] >= 20]),
        '10-19 lessons': len([u for u in user_data if 10 <= u['completed_lessons'] < 20]),
        '5-9 lessons': len([u for u in user_data if 5 <= u['completed_lessons'] < 10]),
        '1-4 lessons': len([u for u in user_data if 1 <= u['completed_lessons'] < 5])
    }

    for range_name, count in completion_ranges.items():
        percentage = (count / len(user_data)) * 100 if user_data else 0
        md_content += f'- **{range_name}:** {count} users ({percentage:.1f}%)\n'

    md_content += '''
### Performance Insights:
'''

    # Calculate performance insights
    perfect_scores = len([u for u in user_data if u['avg_score'] and u['avg_score'] >= 100])
    high_performers = len([u for u in user_data if u['avg_score'] and u['avg_score'] >= 90])
    today = datetime.now().strftime('%Y-%m-%d')
    active_today = len([u for u in user_data if u['last_completed'] and u['last_completed'].strftime('%Y-%m-%d') == today])

    md_content += f'''
- **Perfect Score Users:** {perfect_scores} users have 100% average score
- **High Performers (90%+):** {high_performers} users
- **Active Today:** {active_today} users completed lessons today

## All Users Data

<details>
<summary>Click to view complete user list ({len(user_data)} users)</summary>

| Rank | Name | Zehn ID | Phone | Completed | Attempts | Avg Score | Last Activity |
|------|------|---------|-------|:---------:|:--------:|:---------:|:------------:|
'''

    # Add all users
    for user in user_data:
        avg_score = f'{user["avg_score"]:.1f}%' if user['avg_score'] else 'N/A'
        last_completed = user['last_completed'].strftime('%Y-%m-%d') if user['last_completed'] else 'Never'
        
        md_content += f'| {user["rank"]} | {user["name"]} | `{user["zehn_id"]}` | {user["phone"]} | {user["completed_lessons"]} | {user["total_attempts"]} | {avg_score} | {last_completed} |\n'

    md_content += '''
</details>

---
*This report was automatically generated from the user_lesson_progress database table.*
'''

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    return output_path

def print_console_summary(user_data):
    """Print a summary to console."""
    print('User Lesson Progress Analysis')
    print('=' * 80)
    print(f'Total users with lesson activity: {len(user_data)}')
    print()
    
    print('Top 10 Users by Completed Lessons:')
    print('-' * 50)
    
    for i, user in enumerate(user_data[:10], 1):
        avg_score_str = f'{user["avg_score"]:.1f}%' if user['avg_score'] else 'N/A'
        last_str = user['last_completed'].strftime('%Y-%m-%d') if user['last_completed'] else 'Never'
        
        print(f'{i:2d}. {user["name"]} (Zehn ID: {user["zehn_id"]})')
        print(f'    User ID: {user["user_id"]}')
        print(f'    Phone: {user["phone"]}')
        print(f'    Completed Lessons: {user["completed_lessons"]}')
        print(f'    Total Attempts: {user["total_attempts"]}')
        print(f'    Average Score: {avg_score_str}')
        print(f'    Last Completed: {last_str}')
        print()

def main():
    """Main function to run the analysis."""
    try:
        print("🔍 Analyzing user lesson progress...")
        
        # Get user data
        user_data = analyze_user_progress()
        
        if not user_data:
            print("❌ No user data found!")
            return
        
        # Print console summary
        print_console_summary(user_data)
        
        # Generate markdown report
        output_path = generate_markdown_report(user_data)
        
        print(f'✅ Successfully created {output_path} with user lesson progress analysis!')
        print(f'📊 Report includes data for {len(user_data)} users')
        if user_data:
            print(f'🏆 Top performer: {user_data[0]["name"]} with {user_data[0]["completed_lessons"]} lessons')
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()