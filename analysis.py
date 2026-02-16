import pandas as pd
from collections import Counter
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

def get_recent_data(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    if df.empty:
        return df
    
    cutoff_date = pd.to_datetime(df['date']).max() - pd.Timedelta(days=days-1)
    recent_df = df[pd.to_datetime(df['date']) >= cutoff_date]
    return recent_df

def calculate_streak(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    
    df_sorted = df.sort_values('date')
    dates = pd.to_datetime(df_sorted['date']).dt.date.unique()
    dates = sorted(dates, reverse=True)
    
    streak = 0
    current_date = datetime.now().date()
    
    for study_date in dates:
        if study_date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif study_date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak

def analyze_study_data(df: pd.DataFrame) -> Dict:
    if df.empty:
        return {}
    
    analysis = {}
    
    # Total study hours
    analysis['total_hours'] = df['hours'].sum()
    
    # Subject-wise distribution
    subject_hours = df.groupby('subject')['hours'].sum().to_dict()
    analysis['subject_hours'] = subject_hours
    
    # Most ignored subject (least hours)
    if subject_hours:
        analysis['most_ignored'] = min(subject_hours, key=subject_hours.get)
    
    # Consistency analysis
    unique_days = df['date'].nunique()
    date_range = pd.to_datetime(df['date']).max() - pd.to_datetime(df['date']).min()
    total_days = date_range.days + 1 if date_range.days > 0 else 1
    analysis['consistency'] = (unique_days / total_days) * 100 if total_days > 0 else 0
    
    # Difficulty distribution
    difficulty_hours = df.groupby('difficulty')['hours'].sum().to_dict()
    analysis['difficulty_hours'] = difficulty_hours
    
    # Study patterns
    analysis['avg_hours_per_session'] = df['hours'].mean()
    analysis['total_sessions'] = len(df)
    
    # Recent data analysis
    recent_df = get_recent_data(df, 7)
    if not recent_df.empty:
        recent_subject_hours = recent_df.groupby('subject')['hours'].sum().to_dict()
        if recent_subject_hours:
            analysis['recent_most_ignored'] = min(recent_subject_hours, key=recent_subject_hours.get)
            analysis['recent_most_studied'] = max(recent_subject_hours, key=recent_subject_hours.get)
        
        analysis['recent_total_hours'] = recent_df['hours'].sum()
        analysis['recent_sessions'] = len(recent_df)
    
    # Streak analysis
    analysis['current_streak'] = calculate_streak(df)
    
    # Missed days calculation
    if not df.empty:
        date_range = pd.to_datetime(df['date']).max() - pd.to_datetime(df['date']).min()
        total_days = date_range.days + 1
        study_days = df['date'].nunique()
        analysis['missed_days'] = max(0, total_days - study_days)
    
    return analysis

def detect_behavioral_patterns(analysis: Dict) -> List[str]:
    patterns = []
    
    if not analysis:
        return patterns
    
    # Over-focus on easy subjects
    if 'difficulty_hours' in analysis:
        total = sum(analysis['difficulty_hours'].values())
        if total > 0:
            easy_percentage = (analysis['difficulty_hours'].get('easy', 0) / total) * 100
            if easy_percentage > 60:
                patterns.append("over_focus_easy")
    
    # Lack of balance
    if 'subject_hours' in analysis and len(analysis['subject_hours']) > 1:
        hours = list(analysis['subject_hours'].values())
        max_hours = max(hours)
        min_hours = min(hours)
        if max_hours > 0 and (min_hours / max_hours) < 0.2:
            patterns.append("lack_balance")
    
    # Irregular study
    if 'consistency' in analysis:
        if analysis['consistency'] < 40:
            patterns.append("irregular_study")
    
    # Hard subject avoidance
    if 'difficulty_hours' in analysis:
        total = sum(analysis['difficulty_hours'].values())
        if total > 0:
            hard_hours = analysis['difficulty_hours'].get('hard', 0)
            if hard_hours == 0:
                patterns.append("hard_subject_avoidance")
            elif (hard_hours / total) < 0.15:
                patterns.append("hard_subject_avoidance")
    
    # Fake consistency (low hours but frequent logs)
    if 'recent_total_hours' in analysis and 'recent_sessions' in analysis:
        if analysis['recent_sessions'] > 5 and analysis['recent_total_hours'] < 10:
            patterns.append("fake_consistency")
    
    # Spike then crash pattern
    if 'recent_total_hours' in analysis and 'total_hours' in analysis:
        if analysis['total_hours'] > 0:
            recent_ratio = analysis['recent_total_hours'] / analysis['total_hours']
            if recent_ratio > 0.8 and analysis['consistency'] < 30:
                patterns.append("spike_then_crash")
    
    return patterns
