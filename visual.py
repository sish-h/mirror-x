import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def plot_subject_distribution(df):
    if df.empty:
        return
    
    subject_hours = df.groupby('subject')['hours'].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    subject_hours.plot(kind='bar', color='steelblue')
    plt.title('Study Hours by Subject', fontsize=14, fontweight='bold')
    plt.xlabel('Subject')
    plt.ylabel('Total Hours')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis='y', alpha=0.3)
    plt.show()

def plot_daily_hours(df):
    if df.empty:
        return
    
    daily_hours = df.groupby('date')['hours'].sum()
    daily_hours.index = pd.to_datetime(daily_hours.index)
    daily_hours = daily_hours.sort_index()
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily_hours.index, daily_hours.values, marker='o', linewidth=2, markersize=6, color='crimson')
    plt.title('Daily Study Hours', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Hours Studied')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
