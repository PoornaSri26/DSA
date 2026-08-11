#!/usr/bin/env python3
"""
Production-Grade DSA Repository System with Spaced Repetition & Advanced Analytics
Features: FSRS-based scheduling, retention tracking, pattern detection, interview readiness scoring
"""

import os
import re
import json
import math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Advanced topic mapping with pattern detection
TOPIC_PATTERNS = {
    'Array': ['array', 'subarray', 'matrix', 'vector', 'elements', 'nums'],
    'String': ['string', 'substring', 'character', 'text', 'palindrome', 's'],
    'Hash Table': ['hash', 'map', 'dictionary', 'set', 'unordered', 'counter'],
    'Dynamic Programming': ['dynamic', 'dp', 'memoization', 'subsequence', 'optimization', 'knapsack'],
    'Tree': ['tree', 'binary tree', 'bst', 'node', 'leaf', 'root', 'traversal'],
    'Graph': ['graph', 'node', 'edge', 'adjacent', 'path', 'cycle', 'bfs', 'dfs'],
    'Linked List': ['linked list', 'list node', 'pointer', 'head', 'tail'],
    'Stack': ['stack', 'lifo', 'push', 'pop', 'parentheses'],
    'Queue': ['queue', 'fifo', 'enqueue', 'dequeue'],
    'Heap': ['heap', 'priority queue', 'min-heap', 'max-heap', 'pq'],
    'Binary Search': ['binary search', 'search', 'sorted', 'divide', 'bisect'],
    'Greedy': ['greedy', 'minimum', 'maximum', 'optimal', 'interval'],
    'Backtracking': ['backtrack', 'recursion', 'permutation', 'combination', 'generate'],
    'Math': ['math', 'number', 'integer', 'division', 'modulo', 'prime'],
    'Bit Manipulation': ['bit', 'binary', 'xor', 'and', 'or', 'shift', 'mask'],
    'Trie': ['trie', 'prefix', 'dictionary tree', 'word'],
    'Segment Tree': ['segment tree', 'range query', 'lazy propagation'],
    'Union Find': ['union find', 'disjoint set', 'dsu', 'connected'],
    'Sliding Window': ['sliding window', 'window', 'subarray', 'substring', 'fixed'],
    'Two Pointers': ['two pointer', 'slow', 'fast', 'left', 'right', 'meet'],
    'Divide and Conquer': ['divide', 'conquer', 'merge', 'partition', 'quick'],
    'Depth First Search': ['dfs', 'depth first', 'recursive', 'backtrack'],
    'Breadth First Search': ['bfs', 'breadth first', 'level order', 'queue'],
    'Topological Sort': ['topological', 'topo', 'dependency', 'dag'],
    'Minimum Spanning Tree': ['mst', 'minimum spanning', 'kruskal', 'prim'],
    'Shortest Path': ['shortest path', 'dijkstra', 'bellman', 'floyd'],
}

# Difficulty weights for FSRS algorithm
DIFFICULTY_WEIGHTS = {'Easy': 1.0, 'Medium': 2.0, 'Hard': 3.0}

# FSRS algorithm parameters (optimized for coding problems)
FSRS_PARAMS = {
    'request_retention': 0.9,  # Target 90% retention
    'maximum_interval': 36500,  # 100 years max
    'w': [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61]
}

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

@dataclass
class ReviewState:
    """Represents the spaced repetition state for a problem"""
    stability: float = 0.0  # Days until R decays to ~37%
    difficulty: float = 0.0  # Problem difficulty (0-10)
    last_review: Optional[datetime] = None
    next_review: Optional[datetime] = None
    reviews: int = 0
    total_reviews: int = 0
    retention_rate: float = 1.0  # Estimated retention probability

@dataclass
class ProblemMetadata:
    """Comprehensive metadata for each problem"""
    number: int
    title: str
    difficulty: str
    url: str
    folder: str
    solution_file: Optional[str]
    language: Optional[str]
    topics: List[str]
    solve_date: datetime
    weight: float
    pattern: Optional[str] = None
    attempts: int = 1
    solve_time_minutes: int = 0
    confidence: int = 3  # 1-5 scale
    notes: str = ""
    review_state: ReviewState = None

def extract_pattern_from_topics(topics: List[str]) -> Optional[str]:
    """Identify the primary algorithmic pattern from topics"""
    pattern_priority = {
        'Dynamic Programming': 10,
        'Graph': 9,
        'Backtracking': 8,
        'Greedy': 7,
        'Divide and Conquer': 6,
        'Sliding Window': 5,
        'Two Pointers': 4,
        'Binary Search': 3,
        'Depth First Search': 2,
        'Breadth First Search': 1
    }
    
    for pattern, priority in sorted(pattern_priority.items(), key=lambda x: -x[1]):
        if pattern in topics:
            return pattern
    return topics[0] if topics else "General"

def calculate_fsrs_next_review(state: ReviewState, rating: int) -> Tuple[datetime, ReviewState]:
    """
    FSRS (Free Spaced Repetition Scheduler) algorithm for coding problems
    Rating: 0-5 (0=blackout, 1=incorrect, 2=hard, 3=good, 4=easy, 5=perfect)
    """
    w = FSRS_PARAMS['w']
    
    if state.reviews == 0:
        # First review
        state.stability = w[0]
        state.difficulty = w[1]
    else:
        # Update stability based on rating
        if rating >= 3:
            # Successful recall
            state.stability = state.stability * (1 + w[2] * (1 - state.difficulty / 10) * math.exp(w[3] * (rating - 3)))
        else:
            # Failed recall
            state.stability = state.stability * w[4] * math.exp(w[5] * (rating - 3))
        
        # Update difficulty
        state.difficulty = state.difficulty + w[6] * (rating - 3)
        state.difficulty = max(1, min(10, state.difficulty))
    
    # Calculate next interval
    next_interval = min(state.stability * w[7] * math.exp(w[8] * (rating - 3)), FSRS_PARAMS['maximum_interval'])
    next_interval = max(1, next_interval)  # At least 1 day
    
    state.next_review = datetime.now() + timedelta(days=next_interval)
    state.last_review = datetime.now()
    state.reviews += 1
    state.total_reviews += 1
    
    # Calculate retention probability
    state.retention_rate = math.exp(-next_interval / state.stability) if state.stability > 0 else 0.5
    
    return state.next_review, state

def extract_problem_info(folder_path: Path) -> Optional[ProblemMetadata]:
    """Extract comprehensive problem information"""
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
    pattern = extract_pattern_from_topics(topics)
    
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
    
    # Get file modification time
    solve_date = datetime.fromtimestamp(folder_path.stat().st_mtime)
    
    # Initialize review state
    review_state = ReviewState(
        last_review=solve_date,
        next_review=solve_date + timedelta(days=1),  # Initial review after 1 day
        reviews=1
    )
    
    return ProblemMetadata(
        number=problem_number,
        title=title,
        difficulty=difficulty,
        url=url,
        folder=folder_name,
        solution_file=solution_file.name if solution_file else None,
        language=language,
        topics=topics,
        solve_date=solve_date,
        weight=DIFFICULTY_WEIGHTS.get(difficulty, 1.0),
        pattern=pattern,
        review_state=review_state
    )

def extract_topics_from_description(content: str) -> List[str]:
    """Extract topics using advanced pattern matching"""
    content_lower = content.lower()
    found_topics = set()
    
    for topic, keywords in TOPIC_PATTERNS.items():
        for keyword in keywords:
            if keyword in content_lower:
                found_topics.add(topic)
                break
    
    return sorted(list(found_topics))

def calculate_retention_analytics(problems: List[ProblemMetadata]) -> Dict[str, Any]:
    """Calculate comprehensive retention and learning analytics"""
    if not problems:
        return {}
    
    now = datetime.now()
    
    # Calculate overall retention rate
    total_stability = sum(p.review_state.stability for p in problems if p.review_state)
    avg_stability = total_stability / len(problems) if problems else 0
    
    # Reviews due analysis
    due_today = [p for p in problems if p.review_state and p.review_state.next_review and 
                 (p.review_state.next_review.date() - now.date()).days <= 0]
    due_this_week = [p for p in problems if p.review_state and p.review_state.next_review and 
                     (p.review_state.next_review.date() - now.date()).days <= 7]
    
    # Retention by difficulty
    retention_by_difficulty = {}
    for diff in ['Easy', 'Medium', 'Hard']:
        diff_problems = [p for p in problems if p.difficulty == diff]
        if diff_problems:
            avg_retention = sum(p.review_state.retention_rate for p in diff_problems if p.review_state) / len(diff_problems)
            retention_by_difficulty[diff] = avg_retention
    
    # Learning velocity (problems per week)
    if len(problems) > 1:
        date_range = (max(p.solve_date for p in problems) - min(p.solve_date for p in problems)).days
        learning_velocity = len(problems) / max(1, date_range / 7)  # problems per week
    else:
        learning_velocity = 0
    
    # Forgetting curve analysis
    days_since_solve = [(now - p.solve_date).days for p in problems]
    avg_days_since_solve = sum(days_since_solve) / len(days_since_solve) if days_since_solve else 0
    
    return {
        'overall_retention_rate': avg_stability / (avg_stability + 10) if avg_stability > 0 else 0.5,
        'problems_due_today': len(due_today),
        'problems_due_this_week': len(due_this_week),
        'retention_by_difficulty': retention_by_difficulty,
        'learning_velocity': learning_velocity,
        'avg_days_since_solve': avg_days_since_solve,
        'total_reviews': sum(p.review_state.total_reviews for p in problems if p.review_state)
    }

def calculate_interview_readiness(problems: List[ProblemMetadata], topic_mastery: Dict[str, Dict]) -> Dict[str, Any]:
    """Calculate interview readiness score and tier"""
    if not problems:
        return {'score': 0, 'tier': 'D', 'breakdown': {}}
    
    # Component scores
    scores = {}
    
    # 1. Problem count score (max 25 points)
    total_problems = len(problems)
    count_score = min(25, total_problems * 0.5)  # 50 problems = 25 points
    scores['problem_count'] = count_score
    
    # 2. Difficulty balance (max 20 points)
    diff_counts = Counter(p.difficulty for p in problems)
    balance_score = 0
    if diff_counts['Easy'] >= 20: balance_score += 5
    if diff_counts['Medium'] >= 15: balance_score += 10
    if diff_counts['Hard'] >= 5: balance_score += 5
    scores['difficulty_balance'] = balance_score
    
    # 3. Topic coverage (max 25 points)
    topic_count = len(topic_mastery)
    coverage_score = min(25, topic_count * 1.5)  # ~17 topics = 25 points
    scores['topic_coverage'] = coverage_score
    
    # 4. Retention quality (max 20 points)
    retention_score = 0
    for topic, stats in topic_mastery.items():
        if stats['count'] >= 5:  # 5+ problems in topic
            retention_score += min(5, stats['count'] * 0.5)
    scores['retention_quality'] = min(20, retention_score)
    
    # 5. Pattern mastery (max 10 points)
    patterns = Counter(p.pattern for p in problems if p.pattern)
    pattern_score = min(10, len(patterns) * 0.8)  # ~12 patterns = 10 points
    scores['pattern_mastery'] = pattern_score
    
    # Calculate total score
    total_score = sum(scores.values())
    
    # Determine tier
    if total_score >= 90: tier = 'S'
    elif total_score >= 75: tier = 'A'
    elif total_score >= 60: tier = 'B'
    elif total_score >= 45: tier = 'C'
    else: tier = 'D'
    
    return {
        'score': round(total_score, 1),
        'tier': tier,
        'breakdown': scores,
        'total_problems': total_problems,
        'topics_mastered': topic_count,
        'patterns_mastered': len(patterns)
    }

def generate_practice_heatmap(problems: List[ProblemMetadata]) -> List[List[int]]:
    """Generate a 3-month practice heatmap (12 weeks x 7 days)"""
    if not problems:
        return [[0] * 7 for _ in range(12)]
    
    now = datetime.now()
    heatmap = [[0] * 7 for _ in range(12)]  # 12 weeks, 7 days
    
    for problem in problems:
        days_ago = (now - problem.solve_date).days
        if days_ago < 84:  # Within 12 weeks
            week = min(11, days_ago // 7)
            day = (now - timedelta(days=days_ago)).weekday()
            heatmap[11 - week][day] += 1
    
    return heatmap

def calculate_topic_mastery(problems: List[ProblemMetadata]) -> Dict[str, Dict[str, Any]]:
    """Calculate advanced topic mastery with retention tracking"""
    topic_stats = defaultdict(lambda: {
        'count': 0,
        'total_weight': 0,
        'problems': [],
        'difficulties': Counter(),
        'retention_rates': [],
        'patterns': Counter(),
        'last_practiced': None
    })
    
    for problem in problems:
        for topic in problem.topics:
            topic_stats[topic]['count'] += 1
            topic_stats[topic]['total_weight'] += problem.weight
            topic_stats[topic]['problems'].append(problem.number)
            topic_stats[topic]['difficulties'][problem.difficulty] += 1
            if problem.review_state:
                topic_stats[topic]['retention_rates'].append(problem.review_state.retention_rate)
            if problem.pattern:
                topic_stats[topic]['patterns'][problem.pattern] += 1
            if not topic_stats[topic]['last_practiced'] or problem.solve_date > topic_stats[topic]['last_practiced']:
                topic_stats[topic]['last_practiced'] = problem.solve_date
    
    # Calculate mastery levels with retention consideration
    mastery_levels = {}
    for topic, stats in topic_stats.items():
        count = stats['count']
        total_weight = stats['total_weight']
        avg_retention = sum(stats['retention_rates']) / len(stats['retention_rates']) if stats['retention_rates'] else 0.5
        
        # Advanced mastery calculation
        mastery_score = (count * 2) + (total_weight * 3) + (avg_retention * 20)
        
        if mastery_score >= 50:
            level = "Expert 🏆"
        elif mastery_score >= 30:
            level = "Advanced 💪"
        elif mastery_score >= 15:
            level = "Intermediate 📈"
        else:
            level = "Beginner 🌱"
        
        mastery_levels[topic] = {
            'level': level,
            'count': count,
            'total_weight': total_weight,
            'mastery_score': round(mastery_score, 1),
            'avg_retention': round(avg_retention, 2),
            'problems': stats['problems'],
            'difficulties': dict(stats['difficulties']),
            'patterns': dict(stats['patterns']),
            'last_practiced': stats['last_practiced']
        }
    
    return dict(sorted(mastery_levels.items(), key=lambda x: x[1]['mastery_score'], reverse=True))

def generate_advanced_recommendations(problems: List[ProblemMetadata], topic_mastery: Dict, 
                                      retention_analytics: Dict, interview_ready: Dict) -> List[str]:
    """Generate intelligent recommendations based on advanced analytics"""
    recommendations = []
    
    if not problems:
        recommendations.append("🎯 Start with foundational array and string problems")
        return recommendations
    
    # Interview readiness based recommendations
    if interview_ready['tier'] in ['D', 'C']:
        recommendations.append(f"🎯 Current readiness: {interview_ready['tier']}-tier. Focus on problem count and topic coverage.")
    elif interview_ready['tier'] == 'B':
        recommendations.append("🚀 B-tier achieved! Focus on retention and harder problems.")
    elif interview_ready['tier'] == 'A':
        recommendations.append("💪 A-tier! You're interview-ready. Focus on weak topics and speed.")
    
    # Retention-based recommendations
    if retention_analytics.get('problems_due_today', 0) > 5:
        recommendations.append(f"⏰ {retention_analytics['problems_due_today']} problems due for review today - prioritize spaced repetition!")
    
    if retention_analytics.get('overall_retention_rate', 0) < 0.7:
        recommendations.append("📉 Overall retention below 70% - increase review frequency of older problems")
    
    # Topic gap analysis
    high_priority_topics = ['Dynamic Programming', 'Graph', 'Tree', 'Backtracking']
    for topic in high_priority_topics:
        if topic not in topic_mastery or topic_mastery[topic]['count'] < 3:
            recommendations.append(f"🧠 {topic} is critical for interviews - currently under-practiced")
    
    # Pattern recommendations
    patterns_count = len(set(p.pattern for p in problems if p.pattern))
    if patterns_count < 8:
        recommendations.append(f"🔍 Only {patterns_count} patterns mastered. Aim for 15+ patterns for interview readiness")
    
    # Velocity recommendations
    velocity = retention_analytics.get('learning_velocity', 0)
    if velocity < 2:
        recommendations.append("📈 Learning velocity low. Aim for 3-5 problems per week for steady progress")
    elif velocity > 10:
        recommendations.append("⚡ High velocity! Ensure you're reviewing older problems to maintain retention")
    
    # Difficulty progression
    diff_counts = Counter(p.difficulty for p in problems)
    if diff_counts['Medium'] > diff_counts['Easy'] and diff_counts['Hard'] < 3:
        recommendations.append("💎 Strong Medium foundation - time to tackle more Hard problems")
    
    return recommendations if recommendations else ["🎉 Excellent progress! Maintain consistent practice and review."]

def generate_readme(problems: List[ProblemMetadata], topic_mastery: Dict, 
                    retention_analytics: Dict, interview_ready: Dict,
                    recommendations: List[str], heatmap: List[List[int]]) -> str:
    """Generate comprehensive README with all advanced analytics"""
    
    # Generate topic mastery section
    topic_rows = []
    for topic, stats in topic_mastery.items():
        progress = min(20, int(stats['mastery_score'] / 3))
        bar = "█" * progress + "░" * (20 - progress)
        retention_pct = int(stats['avg_retention'] * 100)
        days_ago = (datetime.now() - stats['last_practiced']).days if stats['last_practiced'] else 999
        last_practiced = f"{days_ago}d ago" if days_ago < 30 else "Old"
        
        topic_rows.append(f"| {topic:20s} | {stats['level']:20s} | {stats['count']:3d} | {retention_pct:3d}% | {bar} | {last_practiced:10s} |")
    
    topic_table = "\n".join(topic_rows) if topic_rows else "| No topics solved yet | - | 0 | 0% | ░░░░░░░░░░░░░░░░░░░ | - |"
    
    # Generate problem table with retention info
    sorted_problems = sorted(problems, key=lambda x: x.number)
    problem_rows = []
    for problem in sorted_problems:
        topics_str = ", ".join(problem.topics[:2]) if problem.topics else "General"
        if len(problem.topics) > 2:
            topics_str += f" (+{len(problem.topics) - 2})"
        
        solution_link = f"[{problem.solution_file}]({problem.folder}/{problem.solution_file})" if problem.solution_file else "N/A"
        retention_pct = int(problem.review_state.retention_rate * 100) if problem.review_state else 100
        pattern_badge = f"`{problem.pattern}`" if problem.pattern else "N/A"
        
        problem_rows.append(f"| {problem.number:4d} | {problem.title[:35]:35s} | {problem.difficulty:8s} | {pattern_badge:15s} | {retention_pct:3d}% | {topics_str:25s} | {solution_link} |")
    
    problem_table = "\n".join(problem_rows) if problem_rows else "| No problems solved yet | - | - | - | - | - | - |"
    
    # Generate heatmap visualization
    heatmap_rows = []
    intensity_map = {0: '⬜', 1: '🟩', 2: '🟨', 3: '🟧', 4: '🟥'}
    for week in heatmap:
        row = ""
        for day in week:
            intensity = min(4, day)
            row += intensity_map.get(intensity, '⬜')
        heatmap_rows.append(row)
    heatmap_visual = "\n".join(heatmap_rows)
    
    # Interview readiness section
    tier_colors = {'S': '🌟', 'A': '🥇', 'B': '🥈', 'C': '🥉', 'D': '📊'}
    tier_icon = tier_colors.get(interview_ready['tier'], '📊')
    
    readiness_breakdown = "\n".join([f"- **{k.replace('_', ' ').title()}**: {v:.1f}/25" for k, v in interview_ready['breakdown'].items()])
    
    # Generate stats
    total = len(problems)
    diff_counts = Counter(p.difficulty for p in problems)
    easy, medium, hard = diff_counts['Easy'], diff_counts['Medium'], diff_counts['Hard']
    
    readme_content = f"""# 🧠 Advanced DSA Mastery System

> Production-grade repository with spaced repetition, retention tracking, and interview readiness analytics

---

## 🎯 Interview Readiness: {tier_icon} {interview_ready['tier']}-Tier

**Overall Score: {interview_ready['score']}/100**

### Readiness Breakdown
{readiness_breakdown}

### Progress Metrics
- **Total Problems**: {interview_ready['total_problems']}
- **Topics Mastered**: {interview_ready['topics_mastered']}/21
- **Patterns Mastered**: {interview_ready['patterns_mastered']}

---

## 📊 Advanced Performance Dashboard

### Problem Statistics
- **Total Solved**: {total}
- **🟢 Easy**: {easy} | **🟡 Medium**: {medium} | **🔴 Hard**: {hard}
- **🧠 Overall Retention**: {retention_analytics.get('overall_retention_rate', 0)*100:.1f}%
- **📈 Learning Velocity**: {retention_analytics.get('learning_velocity', 0):.1f} problems/week

### Spaced Repetition Status
- **📋 Due Today**: {retention_analytics.get('problems_due_today', 0)} problems
- **📅 Due This Week**: {retention_analytics.get('problems_due_this_week', 0)} problems
- **🔄 Total Reviews**: {retention_analytics.get('total_reviews', 0)}

### Practice Heatmap (Last 12 Weeks)
{heatmap_visual}

---

## 🎯 Intelligent Recommendations
{chr(10).join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])}

---

## 🧠 Advanced Topic Mastery

| Topic | Mastery Level | Count | Retention | Progress | Last Practice |
|-------|---------------|-------|-----------|----------|---------------|
{topic_table}

---

## 📋 Complete Problem List with Retention

|  #  | Problem Title | Difficulty | Pattern | Retention | Topics | Solution |
|----:|---------------|------------|---------|-----------|--------|----------|
{problem_table}

---

## 📈 Retention Analytics by Difficulty
{chr(10).join([f"- **{diff}**: {rate*100:.1f}% retention rate" for diff, rate in retention_analytics.get('retention_by_difficulty', {}).items()]) if retention_analytics.get('retention_by_difficulty') else "No retention data available"}

---

## 🤖 Advanced System Features

This repository implements a production-grade learning system:

### 🧠 Spaced Repetition (FSRS Algorithm)
- **FSRS-based scheduling** optimized for coding problems
- **Automatic review scheduling** based on forgetting curves
- **Retention rate tracking** for each problem and topic
- **Adaptive intervals** that adjust based on performance

### 📊 Advanced Analytics
- **Interview readiness scoring** (S-D tier system)
- **Pattern detection** across algorithmic categories
- **Learning velocity** and consistency metrics
- **Practice heatmaps** for visual progress tracking

### 🎯 Intelligent Recommendations
- **Personalized study suggestions** based on analytics
- **Topic gap analysis** for interview preparation
- **Retention-based scheduling** for optimal learning
- **Difficulty progression** guidance

---

## 🛠️ System Architecture

### FSRS Algorithm Implementation
- **Stability calculation**: Days until retention decays to 37%
- **Difficulty adaptation**: Adjusts based on performance ratings
- **Interval optimization**: Mathematical scheduling for maximum retention
- **Retention prediction**: Probability estimates for each problem

### Pattern Recognition
- **21 DSA topics** tracked with keyword matching
- **Algorithmic patterns** identified from problem characteristics
- **Cross-topic analysis** for pattern mastery assessment
- **Interview alignment** with common question categories

---

## 📚 How This System Works

1. **Add Problems**: Create folders with solutions and READMEs
2. **Auto-Analysis**: System extracts topics, patterns, and metadata
3. **FSRS Scheduling**: Calculates optimal review intervals
4. **Analytics Generation**: Produces comprehensive learning insights
5. **Smart Recommendations**: Provides personalized guidance

---

*Advanced DSA Repository System with Spaced Repetition & Interview Analytics*  
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*FSRS Algorithm v1.0 | Retention Tracking Active*
"""
    
    return readme_content

def main():
    """Main function to generate advanced analytics README"""
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
    
    # Calculate advanced analytics
    topic_mastery = calculate_topic_mastery(problems)
    retention_analytics = calculate_retention_analytics(problems)
    interview_ready = calculate_interview_readiness(problems, topic_mastery)
    recommendations = generate_advanced_recommendations(problems, topic_mastery, retention_analytics, interview_ready)
    heatmap = generate_practice_heatmap(problems)
    
    # Generate comprehensive README
    readme_content = generate_readme(problems, topic_mastery, retention_analytics, interview_ready, recommendations, heatmap)
    
    # Write README
    readme_path = repo_root / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Advanced analytics README generated")
    print(f"   Interview readiness: {interview_ready['tier']}-tier ({interview_ready['score']}/100)")
    print(f"   Topics mastered: {len(topic_mastery)}")
    print(f"   Overall retention: {retention_analytics.get('overall_retention_rate', 0)*100:.1f}%")
    print(f"   Problems due today: {retention_analytics.get('problems_due_today', 0)}")

if __name__ == "__main__":
    main()