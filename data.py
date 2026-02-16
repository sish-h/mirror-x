import csv
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = 'study_data.csv'

def initialize_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'subject', 'hours', 'difficulty'])

def log_study_session(subject: str, hours: float, difficulty: str) -> bool:
    try:
        if hours < 0 or hours > 12:
            return False
        if difficulty not in ['easy', 'medium', 'hard']:
            return False
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        with open(DATA_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, subject, hours, difficulty])
        return True
    except:
        return False

def load_study_data() -> List[Dict]:
    data = []
    try:
        with open(DATA_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['hours'] = float(row['hours'])
                data.append(row)
    except:
        pass
    return data

def get_available_subjects() -> List[str]:
    return ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'Literature', 'History']
