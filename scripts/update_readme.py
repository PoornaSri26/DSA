#!/usr/bin/env python3
"""
Advanced DSA Repository Auto-Generator
Features: Topic mastery tracking, performance analytics, smart recommendations, goal tracking
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Topic mapping based on common LeetCode problem patterns
TOPIC_KEYWORDS = {
    'Array': ['array', 'subarray', 'matrix', 'vector', 'elements'],
    'String': ['string', 'substring', 'character', 'text', 'palindrome'],
    'Hash Table': ['hash', 'map', 'dictionary', 'set', 'unordered'],
    'Dynamic Programming': ['dynamic', 'dp', 'memoization', 'subsequence', 'optimization'],
    'Tree': ['tree', 'binary tree', 'bst', 'node', 'leaf', 'root'],
    'Graph': ['graph', 'node', 'edge', 'adjacent', 'path', 'cycle'],
    'Linked List': ['linked list', 'list node', 'pointer', 'head', 'tail'],
    'Stack': ['stack', 'lifo', 'push', 'pop'],
    'Queue': ['queue', 'fifo', 'enqueue', 'dequeue'],
    'Heap': ['heap', 'priority queue', 'min-heap', 'max-heap'],
    'Binary Search': ['binary search', 'search', 'sorted', 'divide'],
    'Greedy': ['greedy', 'minimum', 'maximum', 'optimal'],
    'Backtracking': ['backtrack', 'recursion', 'permutation', 'combination'],
    'Math': ['math', 'number', 'integer', 'division', 'modulo'],
    'Bit Manipulation': ['bit', 'binary', 'xor', 'and', 'or', 'shift'],
    'Trie': ['trie', 'prefix', 'dictionary tree'],
    'Segment Tree': ['segment tree', 'range query', 'lazy propagation'],
    'Union Find': ['union find', 'disjoint set', 'dsu'],
    'Sliding Window': ['sliding window', 'window', 'subarray', 'substring'],
    'Two Pointers': ['two pointer', 'slow', 'fast', 'left', 'right'],
    'Divide and Conquer': ['divide', 'conquer', 'merge', 'partition'],
}

DIFFICULTY_WEIGHTS = {'Easy': 1, 'Medium': 2, 'Hard': 3}

def extract_topics_from_description(content: str) -> List[str]:
    """Extract topics from problem description using keyword matching."""
    content_lower = content.lower()
    found_topics = set()
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content_lower:
                found_topics.add(topic)
                break
    
    return sorted(list(found_topics))

def extract_problem_info(folder_path: Path) -> Dict[str, Any]:
    """Extract comprehensive problem information from folder."""
    readme_path = folder_path / "README.md"
    
    if not readme_path.exists():
        return None
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract problem title and URL
    h2_match = re.search(r'<h2><a href="(https://leetcode\.com/problems/[^"]+)">([^<]+)</a></h2>', content)
    if not h2_match:
        return None
    
    url = h2_match.group(1)
    title = h2_match.group(2).strip()
    
    # Extract difficulty
    difficulty_match = re.search(r"alt='Difficulty: (Easy|Medium|Hard)'", content)
    difficulty = difficulty_match.group(1) if difficulty_match else "Unknown"
    
    # Extract problem number
    folder_name = folder_path.name
    number_match = re.match(r'(\d+)-', folder_name)
    problem_number = int(number_match.group(1)) if number_match else 0
    
    # Extract topics
    topics = extract_topics_from_description(content)
    
    # Find solution file and determine language
    solution_files = list(folder_path.glob("*.cpp")) + list(folder_path.glob("*.py")) + \
                     list(folder_path.glob("*.java")) + list(folder_path.glob("*.js")) + \
                     list(folder_path.glob("*.go")) + list(folder_path.glob("*.rs"))
    solution_file = solution_files[0] if solution_files else None
    
    language = None
    if solution_file:
        ext = solution_file.suffix
        language_map = {'.cpp': 'C++', '.py': 'Python', '.java': 'Java', 
                       '.js': 'JavaScript', '.go': 'Go', '.rs': 'Rust'}
        language = language_map.get(ext, 'Unknown')
    
    # Get file modification time as approximation of solve date
    solve_date = datetime.fromtimestamp(folder_path.stat().st_mtime)
    
    return {
        'number': problem_number,
        'title': title,
        'difficulty': difficulty,
        'url': url,
        'folder': folder_name,
        'solution_file': solution_file.name if solution_file else None,
        'language': language,
        'topics': topics,
        'solve_date': solve_date,
        'weight': DIFFICULTY_WEIGHTS.get(difficulty, 0)
    }

def calculate_topic_mastery(problems: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Calculate mastery level for each topic."""
    topic_stats = defaultdict(lambda: {
        'count': 0,
        'total_weight': 0,
        'problems': [],
        'difficulties': Counter()
    })
    
    for problem in problems:
        for topic in problem['topics']:
            topic_stats[topic]['count'] += 1
            topic_stats[topic]['total_weight'] += problem['weight']
            topic_stats[topic]['problems'].append(problem['number'])
            topic_stats[topic]['difficulties'][problem['difficulty']] += 1
    
    # Calculate mastery levels
    mastery_levels = {}
    for topic, stats in topic_stats.items():
        count = stats['count']
        total_weight = stats['total_weight']
        
        if count >= 10:
            level = "Expert 🏆"
        elif count >= 5:
            level = "Advanced 💪"
        elif count >= 3:
            level = "Intermediate 📈"
        else:
            level = "Beginner 🌱"
        
        mastery_levels[topic] = {
            'level': level,
            'count': count,
            'total_weight': total_weight,
            'problems': stats['problems'],
            'difficulties': dict(stats['difficulties'])
        }
    
    return dict(sorted(mastery_levels.items(), key=lambda x: x[1]['total_weight'], reverse=True))

def calculate_performance_analytics(problems: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate performance analytics and insights."""
    if not problems:
        return {}
    
    # Sort by solve date
    sorted_problems = sorted(problems, key=lambda x: x['solve_date'])
    
    # Time-based analysis
    now = datetime.now()
    last_week = [p for p in problems if (now - p['solve_date']).days <= 7]
    last_month = [p for p in problems if (now - p['solve_date']).days <= 30]
    
    # Streak calculation
    streak = 0
    current_streak = 0
    dates = sorted([p['solve_date'].date() for p in problems])
    
    if dates:
        current_date = now.date()
        for i, date in enumerate(reversed(dates)):
            if (current_date - date).days <= 1:
                current_streak += 1
                current_date = date
            else:
                break
    
    # Difficulty progression
    easy_count = sum(1 for p in problems if p['difficulty'] == 'Easy')
    medium_count = sum(1 for p in problems if p['difficulty'] == 'Medium')
    hard_count = sum(1 for p in problems if p['difficulty'] == 'Hard')
    
    # Language distribution
    languages = Counter(p['language'] for p in problems if p['language'])
    
    return {
        'total_solved': len(problems),
        'last_week': len(last_week),
        'last_month': len(last_month),
        'current_streak': current_streak,
        'difficulty_distribution': {
            'Easy': easy_count,
            'Medium': medium_count,
            'Hard': hard_count
        },
        'language_distribution': dict(languages),
        'first_solve': sorted_problems[0]['solve_date'] if sorted_problems else None,
        'latest_solve': sorted_problems[-1]['solve_date'] if sorted_problems else None
    }

def generate_smart_recommendations(problems: List[Dict[str, Any]], topic_mastery: Dict[str, Dict[str, Any]]) -> List[str]:
    """Generate personalized recommendations based on performance."""
    recommendations = []
    
    if not problems:
        recommendations.append("🎯 Start with easy array and string problems to build foundation")
        return recommendations
    
    # Analyze topic balance
    topic_counts = {topic: stats['count'] for topic, stats in topic_mastery.items()}
    
    if len(topic_counts) < 3:
        recommendations.append("📚 Explore more topics to build well-rounded DSA skills")
    
    # Difficulty balance
    difficulties = Counter(p['difficulty'] for p in problems)
    if difficulties['Easy'] > difficulties['Medium'] * 2:
        recommendations.append("🚀 Challenge yourself with more Medium problems")
    elif difficulties['Medium'] > 5 and difficulties['Hard'] == 0:
        recommendations.append("💪 Ready to tackle your first Hard problem!")
    
    # Topic-specific recommendations
    if 'Dynamic Programming' not in topic_counts or topic_counts['Dynamic Programming'] < 3:
        recommendations.append("🧠 Dynamic Programming is essential for interviews - consider practicing more")
    
    if 'Graph' not in topic_counts:
        recommendations.append("🕸️ Graph algorithms are frequently asked - add them to your practice")
    
    # Streak-based recommendations
    if len(problems) > 0:
        latest = max(p['solve_date'] for p in problems)
        days_since_last = (datetime.now() - latest).days
        if days_since_last > 7:
            recommendations.append("⏰ You haven't solved a problem in over a week - time to practice!")
    
    return recommendations if recommendations else ["🎉 Great progress! Keep up the consistent practice!"]

def generate_progress_badges(analytics: Dict[str, Any]) -> List[str]:
    """Generate achievement badges based on progress."""
    badges = []
    
    if analytics.get('total_solved', 0) >= 100:
        badges.append("🏆 Century Club (100+ problems)")
    elif analytics.get('total_solved', 0) >= 50:
        badges.append("🥇 Half Century (50+ problems)")
    elif analytics.get('total_solved', 0) >= 25:
        badges.append("🥈 Quarter Master (25+ problems)")
    elif analytics.get('total_solved', 0) >= 10:
        badges.append("🥉 Double Digits (10+ problems)")
    
    if analytics.get('current_streak', 0) >= 7:
        badges.append("🔥 Week Warrior (7+ day streak)")
    elif analytics.get('current_streak', 0) >= 3:
        badges.append("⚡ Consistent Coder (3+ day streak)")
    
    if analytics.get('difficulty_distribution', {}).get('Hard', 0) >= 5:
        badges.append("💎 Hard Crusher (5+ Hard problems)")
    
    return badges

def generate_readme(problems: List[Dict[str, Any]], topic_mastery: Dict[str, Dict[str, Any]], 
                   analytics: Dict[str, Any], recommendations: List[str], badges: List[str]) -> str:
    """Generate comprehensive README with all analytics."""
    
    # Generate topic mastery section
    topic_rows = []
    for topic, stats in topic_mastery.items():
        progress_bar = min(20, stats['count'])  # Max 20 characters
        bar = "█" * progress_bar + "░" * (20 - progress_bar)
        topic_rows.append(f"| {topic:20s} | {stats['level']:20s} | {stats['count']:3d} | {bar} |")
    
    topic_table = "\n".join(topic_rows) if topic_rows else "| No topics solved yet | - | 0 | ░░░░░░░░░░░░░░░░░░ |"
    
    # Generate problem table
    sorted_problems = sorted(problems, key=lambda x: x['number'])
    problem_rows = []
    for problem in sorted_problems:
        topics_str = ", ".join(problem['topics'][:3]) if problem['topics'] else "General"
        if len(problem['topics']) > 3:
            topics_str += f" (+{len(problem['topics']) - 3})"
        
        solution_link = f"[{problem['solution_file']}]({problem['folder']}/{problem['solution_file']})" if problem['solution_file'] else "N/A"
        language_badge = f"`{problem['language']}`" if problem['language'] else "N/A"
        
        problem_rows.append(f"| {problem['number']:4d} | {problem['title'][:40]:40s} | {problem['difficulty']:8s} | {language_badge:10s} | {topics_str:30s} | {solution_link} |")
    
    problem_table = "\n".join(problem_rows) if problem_rows else "| No problems solved yet | - | - | - | - | - |"
    
    # Generate badges section
    badges_section = "\n".join([f"- {badge}" for badge in badges]) if badges else "Solve more problems to earn badges!"
    
    # Generate recommendations section
    recommendations_section = "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)]) if recommendations else "Keep up the great work!"
    
    # Generate stats
    total = analytics.get('total_solved', 0)
    easy = analytics.get('difficulty_distribution', {}).get('Easy', 0)
    medium = analytics.get('difficulty_distribution', {}).get('Medium', 0)
    hard = analytics.get('difficulty_distribution', {}).get('Hard', 0)
    streak = analytics.get('current_streak', 0)
    
    readme_content = f"""# 🚀 DSA Mastery Hub

> Advanced Data Structures & Algorithms repository with intelligent analytics and progress tracking

---

## 📊 Performance Dashboard

### Problem Statistics
- **Total Solved**: {total}
- **🟢 Easy**: {easy} | **🟡 Medium**: {medium} | **🔴 Hard**: {hard}
- **🔥 Current Streak**: {streak} days
- **📈 This Week**: {analytics.get('last_week', 0)} | **📅 This Month**: {analytics.get('last_month', 0)}

### 🏆 Achievement Badges
{badges_section}

---

## 🎯 Smart Recommendations
{recommendations_section}

---

## 🧠 Topic Mastery Analysis

| Topic | Mastery Level | Problems | Progress |
|-------|---------------|----------|----------|
{topic_table}

---

## 📋 Complete Problem List

|  #  | Problem Title | Difficulty | Language | Topics | Solution |
|----:|---------------|------------|----------|--------|----------|
{problem_table}

---

## 📈 Performance Analytics

### Language Distribution
{chr(10).join([f"- **{lang}**: {count} problems" for lang, count in analytics.get('language_distribution', {}).items()]) if analytics.get('language_distribution') else "No solutions yet"}

### Learning Journey
- **First Problem**: {analytics.get('first_solve', datetime.now()).strftime('%B %d, %Y') if analytics.get('first_solve') else 'Not started'}
- **Latest Problem**: {analytics.get('latest_solve', datetime.now()).strftime('%B %d, %Y') if analytics.get('latest_solve') else 'Not started'}
- **Active Learning Period**: {(analytics.get('latest_solve', datetime.now()) - analytics.get('first_solve', datetime.now())).days if analytics.get('first_solve') and analytics.get('latest_solve') else 0} days

---

## 🛠️ How to Add New Problems

1. **Create folder**: `{{number}}-problem-name` (e.g., `0001-two-sum`)
2. **Add solution**: Place your solution file (`.cpp`, `.py`, `.java`, etc.)
3. **Add README**: Include LeetCode problem description
4. **Push changes**: Repository README auto-updates with analytics!

---

## 🤖 Automation Features

This repository uses intelligent automation to provide:
- **Topic Extraction**: Automatically identifies DSA topics from problem descriptions
- **Mastery Tracking**: Calculates your expertise level in each topic
- **Smart Recommendations**: Personalized suggestions based on your patterns
- **Performance Analytics**: Detailed insights into your learning journey
- **Achievement System**: Badges and milestones to motivate progress

---

## 📚 Topic Coverage

Current topics tracked: {', '.join(TOPIC_KEYWORDS.keys())}

---

*Repository README automatically generated by advanced analytics engine*  
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return readme_content

def main():
    """Main function to update the README with advanced analytics."""
    repo_root = Path(__file__).parent.parent
    
    # Find all problem folders
    problem_folders = []
    for item in repo_root.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name not in ['scripts', '.github']:
            if re.match(r'^\d+', item.name):
                problem_folders.append(item)
    
    # Extract problem information
    problems = []
    for folder in problem_folders:
        problem_info = extract_problem_info(folder)
        if problem_info:
            problems.append(problem_info)
    
    if not problems:
        print("No problems found!")
        return
    
    # Calculate analytics
    topic_mastery = calculate_topic_mastery(problems)
    analytics = calculate_performance_analytics(problems)
    recommendations = generate_smart_recommendations(problems, topic_mastery)
    badges = generate_progress_badges(analytics)
    
    # Generate README
    readme_content = generate_readme(problems, topic_mastery, analytics, recommendations, badges)
    
    # Write README
    readme_path = repo_root / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Advanced README generated with {len(problems)} problems")
    print(f"   Topics mastered: {len(topic_mastery)}")
    print(f"   Current streak: {analytics.get('current_streak', 0)} days")
    print(f"   Recommendations: {len(recommendations)}")

if __name__ == "__main__":
    main()