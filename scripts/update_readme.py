#!/usr/bin/env python3
"""
AI-Powered DSA Mastery System with Knowledge Graph & Adaptive Learning
Features: Knowledge graph construction, similarity detection, personalized learning paths, AI recommendations
"""

import os
import re
import json
import math
import itertools
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import random

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

# Difficulty weights for algorithms
DIFFICULTY_WEIGHTS = {'Easy': 1.0, 'Medium': 2.0, 'Hard': 3.0}

# FSRS algorithm parameters
FSRS_PARAMS = {
    'request_retention': 0.9,
    'maximum_interval': 36500,
    'w': [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61]
}

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

@dataclass
class ReviewState:
    """Spaced repetition state for a problem"""
    stability: float = 0.0
    difficulty: float = 0.0
    last_review: Optional[datetime] = None
    next_review: Optional[datetime] = None
    reviews: int = 0
    total_reviews: int = 0
    retention_rate: float = 1.0

@dataclass
class ProblemNode:
    """Knowledge graph node for a problem"""
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
    confidence: int = 3
    notes: str = ""
    review_state: ReviewState = field(default_factory=ReviewState)
    embeddings: Dict[str, float] = field(default_factory=dict)
    similar_problems: List[int] = field(default_factory=list)
    learning_dependencies: List[int] = field(default_factory=list)

@dataclass
class KnowledgeGraph:
    """Knowledge graph connecting problems, topics, and patterns"""
    problem_nodes: Dict[int, ProblemNode] = field(default_factory=dict)
    topic_graph: Dict[str, Set[int]] = field(default_factory=dict)
    pattern_graph: Dict[str, Set[int]] = field(default_factory=dict)
    similarity_matrix: Dict[Tuple[int, int], float] = field(default_factory=dict)
    learning_paths: Dict[str, List[int]] = field(default_factory=dict)

def calculate_similarity(problem1: ProblemNode, problem2: ProblemNode) -> float:
    """Calculate similarity between two problems using multiple factors"""
    similarity = 0.0
    
    # Topic overlap (40% weight)
    topics1 = set(problem1.topics)
    topics2 = set(problem2.topics)
    if topics1 and topics2:
        topic_overlap = len(topics1 & topics2) / len(topics1 | topics2)
        similarity += topic_overlap * 0.4
    
    # Pattern match (30% weight)
    if problem1.pattern and problem2.pattern:
        pattern_match = 1.0 if problem1.pattern == problem2.pattern else 0.0
        similarity += pattern_match * 0.3
    
    # Difficulty proximity (20% weight)
    diff_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
    diff1 = diff_order.get(problem1.difficulty, 2)
    diff2 = diff_order.get(problem2.difficulty, 2)
    diff_similarity = 1.0 - abs(diff1 - diff2) / 2.0
    similarity += diff_similarity * 0.2
    
    # Language match (10% weight)
    if problem1.language and problem2.language:
        lang_match = 1.0 if problem1.language == problem2.language else 0.0
        similarity += lang_match * 0.1
    
    return round(similarity, 3)

def build_knowledge_graph(problems: List[ProblemNode]) -> KnowledgeGraph:
    """Build a comprehensive knowledge graph from problems"""
    kg = KnowledgeGraph()
    
    # Add problem nodes
    for problem in problems:
        kg.problem_nodes[problem.number] = problem
    
    # Build topic graph
    for problem in problems:
        for topic in problem.topics:
            if topic not in kg.topic_graph:
                kg.topic_graph[topic] = set()
            kg.topic_graph[topic].add(problem.number)
    
    # Build pattern graph
    for problem in problems:
        if problem.pattern:
            if problem.pattern not in kg.pattern_graph:
                kg.pattern_graph[problem.pattern] = set()
            kg.pattern_graph[problem.pattern].add(problem.number)
    
    # Calculate similarity matrix
    problem_numbers = list(kg.problem_nodes.keys())
    for i, j in itertools.combinations(problem_numbers, 2):
        similarity = calculate_similarity(kg.problem_nodes[i], kg.problem_nodes[j])
        kg.similarity_matrix[(i, j)] = similarity
        kg.similarity_matrix[(j, i)] = similarity
        
        # Add to similar problems if similarity > threshold
        if similarity > 0.5:
            kg.problem_nodes[i].similar_problems.append(j)
            kg.problem_nodes[j].similar_problems.append(i)
    
    # Generate learning dependencies based on difficulty and similarity
    for problem_num, problem in kg.problem_nodes.items():
        dependencies = []
        for other_num, other_problem in kg.problem_nodes.items():
            if problem_num != other_num:
                # Add easier similar problems as dependencies
                diff_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
                if diff_order.get(other_problem.difficulty, 2) < diff_order.get(problem.difficulty, 2):
                    sim = kg.similarity_matrix.get((problem_num, other_num), 0)
                    if sim > 0.3:
                        dependencies.append((other_num, sim))
        
        # Sort by similarity and take top 3
        dependencies.sort(key=lambda x: x[1], reverse=True)
        problem.learning_dependencies = [d[0] for d in dependencies[:3]]
    
    # Generate learning paths
    kg.learning_paths = generate_learning_paths(kg)
    
    return kg

def generate_learning_paths(kg: KnowledgeGraph) -> Dict[str, List[int]]:
    """Generate personalized learning paths using graph algorithms"""
    paths = {}
    
    # Topic-based learning path
    topic_path = []
    for topic in sorted(kg.topic_graph.keys()):
        problems_in_topic = sorted(list(kg.topic_graph[topic]))
        topic_path.extend(problems_in_topic[:5])  # Top 5 per topic
    paths['topic_coverage'] = topic_path
    
    # Difficulty progression path
    easy_problems = [p for p in kg.problem_nodes.values() if p.difficulty == 'Easy']
    medium_problems = [p for p in kg.problem_nodes.values() if p.difficulty == 'Medium']
    hard_problems = [p for p in kg.problem_nodes.values() if p.difficulty == 'Hard']
    
    difficulty_path = [p.number for p in sorted(easy_problems, key=lambda x: x.number)]
    difficulty_path.extend([p.number for p in sorted(medium_problems, key=lambda x: x.number)])
    difficulty_path.extend([p.number for p in sorted(hard_problems, key=lambda x: x.number)])
    paths['difficulty_progression'] = difficulty_path
    
    # Pattern mastery path
    pattern_path = []
    for pattern in sorted(kg.pattern_graph.keys()):
        problems_in_pattern = sorted(list(kg.pattern_graph[pattern]))
        pattern_path.extend(problems_in_pattern[:3])
    paths['pattern_mastery'] = pattern_path
    
    # Similarity-based path (find most connected problems)
    connectivity = {p_num: len(p.similar_problems) for p_num, p in kg.problem_nodes.items()}
    most_connected = sorted(connectivity.items(), key=lambda x: x[1], reverse=True)
    paths['high_impact'] = [p[0] for p in most_connected[:10]]
    
    return paths

def generate_ai_recommendations(kg: KnowledgeGraph, user_problems: Set[int], 
                               topic_mastery: Dict, interview_ready: Dict) -> List[str]:
    """Generate AI-powered recommendations using knowledge graph"""
    recommendations = []
    
    if not kg.problem_nodes:
        recommendations.append("🎯 Start building your knowledge graph by solving foundational problems")
        return recommendations
    
    # Knowledge graph-based recommendations
    unsolved_problems = set(kg.problem_nodes.keys()) - user_problems
    
    # Find high-impact unsolved problems (most similar to solved ones)
    high_impact_unsolved = []
    for unsolved_num in unsolved_problems:
        unsolved_node = kg.problem_nodes[unsolved_num]
        similarity_score = 0
        for solved_num in user_problems:
            if solved_num in kg.problem_nodes:
                sim = kg.similarity_matrix.get((unsolved_num, solved_num), 0)
                similarity_score += sim
        high_impact_unsolved.append((unsolved_num, similarity_score))
    
    high_impact_unsolved.sort(key=lambda x: x[1], reverse=True)
    if high_impact_unsolved:
        top_rec = kg.problem_nodes[high_impact_unsolved[0][0]]
        recommendations.append(f"🎯 High-impact problem: #{top_rec.number} {top_rec.title} - similar to your solved problems")
    
    # Learning path recommendations
    if 'pattern_mastery' in kg.learning_paths:
        pattern_path = kg.learning_paths['pattern_mastery']
        for problem_num in pattern_path:
            if problem_num not in user_problems:
                problem = kg.problem_nodes[problem_num]
                recommendations.append(f"📈 Learning path suggestion: #{problem.number} {problem.title} for pattern mastery")
                break
    
    # Knowledge gap analysis using graph
    topic_coverage = {topic: len(problems) for topic, problems in kg.topic_graph.items()}
    weak_topics = [topic for topic, count in topic_coverage.items() if count < 2]
    if weak_topics:
        recommendations.append(f"🧠 Knowledge graph gaps: {', '.join(weak_topics[:3])} - need more coverage")
    
    # Dependency-based recommendations
    for problem_num in user_problems:
        if problem_num in kg.problem_nodes:
            problem = kg.problem_nodes[problem_num]
            for dep_num in problem.learning_dependencies:
                if dep_num not in user_problems:
                    dep_problem = kg.problem_nodes[dep_num]
                    recommendations.append(f"🔗 Prerequisite recommendation: #{dep_problem.number} {dep_problem.title} (dependency for #{problem.number})")
                    break
    
    # Graph clustering recommendations
    if len(kg.topic_graph) > 5:
        recommendations.append(f"🕸️ Your knowledge graph has {len(kg.topic_graph)} topic clusters - focus on connecting concepts")
    
    return recommendations if recommendations else ["🎉 Excellent knowledge graph coverage! Continue building connections."]

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

def extract_problem_info(folder_path: Path) -> Optional[ProblemNode]:
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
        next_review=solve_date + timedelta(days=1),
        reviews=1
    )
    
    return ProblemNode(
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

def calculate_retention_analytics(problems: List[ProblemNode]) -> Dict[str, Any]:
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
    
    # Learning velocity
    if len(problems) > 1:
        date_range = (max(p.solve_date for p in problems) - min(p.solve_date for p in problems)).days
        learning_velocity = len(problems) / max(1, date_range / 7)
    else:
        learning_velocity = 0
    
    # Knowledge graph connectivity
    avg_connections = sum(len(p.similar_problems) for p in problems) / len(problems) if problems else 0
    
    return {
        'overall_retention_rate': avg_stability / (avg_stability + 10) if avg_stability > 0 else 0.5,
        'problems_due_today': len(due_today),
        'problems_due_this_week': len(due_this_week),
        'retention_by_difficulty': retention_by_difficulty,
        'learning_velocity': learning_velocity,
        'avg_days_since_solve': 0,
        'total_reviews': sum(p.review_state.total_reviews for p in problems if p.review_state),
        'knowledge_graph_connectivity': avg_connections
    }

def calculate_interview_readiness(problems: List[ProblemNode], topic_mastery: Dict, kg: KnowledgeGraph) -> Dict[str, Any]:
    """Calculate interview readiness score with knowledge graph factors"""
    if not problems:
        return {'score': 0, 'tier': 'D', 'breakdown': {}}
    
    scores = {}
    
    # Problem count score
    total_problems = len(problems)
    count_score = min(25, total_problems * 0.5)
    scores['problem_count'] = count_score
    
    # Difficulty balance
    diff_counts = Counter(p.difficulty for p in problems)
    balance_score = 0
    if diff_counts['Easy'] >= 20: balance_score += 5
    if diff_counts['Medium'] >= 15: balance_score += 10
    if diff_counts['Hard'] >= 5: balance_score += 5
    scores['difficulty_balance'] = balance_score
    
    # Topic coverage
    topic_count = len(topic_mastery)
    coverage_score = min(25, topic_count * 1.5)
    scores['topic_coverage'] = coverage_score
    
    # Knowledge graph connectivity
    connectivity_score = min(20, kg.similarity_matrix.__len__() * 0.1)
    scores['graph_connectivity'] = connectivity_score
    
    # Pattern mastery
    patterns = Counter(p.pattern for p in problems if p.pattern)
    pattern_score = min(10, len(patterns) * 0.8)
    scores['pattern_mastery'] = pattern_score
    
    # Learning path diversity
    path_diversity = len(kg.learning_paths)
    diversity_score = min(10, path_diversity * 2.5)
    scores['learning_diversity'] = diversity_score
    
    total_score = sum(scores.values())
    
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
        'patterns_mastered': len(patterns),
        'graph_connections': len(kg.similarity_matrix)
    }

def calculate_topic_mastery(problems: List[ProblemNode], kg: KnowledgeGraph) -> Dict[str, Dict[str, Any]]:
    """Calculate advanced topic mastery with knowledge graph insights"""
    topic_stats = defaultdict(lambda: {
        'count': 0,
        'total_weight': 0,
        'problems': [],
        'difficulties': Counter(),
        'retention_rates': [],
        'patterns': Counter(),
        'last_practiced': None,
        'graph_connections': 0
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
            topic_stats[topic]['graph_connections'] += len(problem.similar_problems)
    
    # Calculate mastery levels with graph connectivity
    mastery_levels = {}
    for topic, stats in topic_stats.items():
        count = stats['count']
        total_weight = stats['total_weight']
        avg_retention = sum(stats['retention_rates']) / len(stats['retention_rates']) if stats['retention_rates'] else 0.5
        graph_connections = stats['graph_connections']
        
        # Enhanced mastery score with graph connectivity
        mastery_score = (count * 2) + (total_weight * 3) + (avg_retention * 20) + (graph_connections * 0.5)
        
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
            'graph_connections': graph_connections,
            'problems': stats['problems'],
            'difficulties': dict(stats['difficulties']),
            'patterns': dict(stats['patterns']),
            'last_practiced': stats['last_practiced']
        }
    
    return dict(sorted(mastery_levels.items(), key=lambda x: x[1]['mastery_score'], reverse=True))

def generate_practice_heatmap(problems: List[ProblemNode]) -> List[List[int]]:
    """Generate a 3-month practice heatmap"""
    if not problems:
        return [[0] * 7 for _ in range(12)]
    
    now = datetime.now()
    heatmap = [[0] * 7 for _ in range(12)]
    
    for problem in problems:
        days_ago = (now - problem.solve_date).days
        if days_ago < 84:
            week = min(11, days_ago // 7)
            day = (now - timedelta(days=days_ago)).weekday()
            heatmap[11 - week][day] += 1
    
    return heatmap

def generate_knowledge_graph_visualization(kg: KnowledgeGraph) -> str:
    """Generate ASCII visualization of the knowledge graph"""
    if not kg.problem_nodes:
        return "Knowledge graph empty - solve problems to build connections"
    
    lines = []
    lines.append("🕸️ KNOWLEDGE GRAPH STRUCTURE")
    lines.append("=" * 40)
    
    # Show topic clusters
    lines.append("\n📚 Topic Clusters:")
    for topic, problems in sorted(kg.topic_graph.items(), key=lambda x: len(x[1]), reverse=True):
        problem_list = ", ".join(map(str, sorted(list(problems))[:5]))
        if len(problems) > 5:
            problem_list += f" (+{len(problems) - 5})"
        lines.append(f"  {topic}: [{problem_list}]")
    
    # Show pattern clusters
    lines.append("\n🔧 Pattern Clusters:")
    for pattern, problems in sorted(kg.pattern_graph.items(), key=lambda x: len(x[1]), reverse=True):
        problem_list = ", ".join(map(str, sorted(list(problems))[:3]))
        if len(problems) > 3:
            problem_list += f" (+{len(problems) - 3})"
        lines.append(f"  {pattern}: [{problem_list}]")
    
    # Show most connected problems
    lines.append("\n🔗 Most Connected Problems:")
    connectivity = {p_num: len(p.similar_problems) for p_num, p in kg.problem_nodes.items()}
    most_connected = sorted(connectivity.items(), key=lambda x: x[1], reverse=True)[:5]
    for p_num, connections in most_connected:
        problem = kg.problem_nodes[p_num]
        lines.append(f"  #{p_num} {problem.title[:30]}: {connections} connections")
    
    # Show learning paths
    lines.append("\n🛤️ Generated Learning Paths:")
    for path_name, path_problems in kg.learning_paths.items():
        path_preview = ", ".join(map(str, path_problems[:5]))
        if len(path_problems) > 5:
            path_preview += f" ({len(path_problems)} total)"
        lines.append(f"  {path_name}: [{path_preview}]")
    
    return "\n".join(lines)

def generate_readme(problems: List[ProblemNode], kg: KnowledgeGraph, topic_mastery: Dict, 
                    retention_analytics: Dict, interview_ready: Dict,
                    ai_recommendations: List[str], heatmap: List[List[int]]) -> str:
    """Generate comprehensive README with AI-powered analytics"""
    
    # Generate topic mastery section
    topic_rows = []
    for topic, stats in topic_mastery.items():
        progress = min(20, int(stats['mastery_score'] / 3))
        bar = "█" * progress + "░" * (20 - progress)
        retention_pct = int(stats['avg_retention'] * 100)
        days_ago = (datetime.now() - stats['last_practiced']).days if stats['last_practiced'] else 999
        last_practiced = f"{days_ago}d ago" if days_ago < 30 else "Old"
        connections = stats['graph_connections']
        
        topic_rows.append(f"| {topic:20s} | {stats['level']:20s} | {stats['count']:3d} | {retention_pct:3d}% | {connections:2d} | {bar} | {last_practiced:10s} |")
    
    topic_table = "\n".join(topic_rows) if topic_rows else "| No topics solved yet | - | 0 | 0% | 0 | ░░░░░░░░░░░░░░░░░░░ | - |"
    
    # Generate problem table with knowledge graph info
    sorted_problems = sorted(problems, key=lambda x: x.number)
    problem_rows = []
    for problem in sorted_problems:
        topics_str = ", ".join(problem.topics[:2]) if problem.topics else "General"
        if len(problem.topics) > 2:
            topics_str += f" (+{len(problem.topics) - 2})"
        
        solution_link = f"[{problem.solution_file}]({problem.folder}/{problem.solution_file})" if problem.solution_file else "N/A"
        retention_pct = int(problem.review_state.retention_rate * 100) if problem.review_state else 100
        pattern_badge = f"`{problem.pattern}`" if problem.pattern else "N/A"
        connections = len(problem.similar_problems)
        
        problem_rows.append(f"| {problem.number:4d} | {problem.title[:30]:30s} | {problem.difficulty:8s} | {pattern_badge:15s} | {retention_pct:3d}% | {connections:2d} | {topics_str:20s} | {solution_link} |")
    
    problem_table = "\n".join(problem_rows) if problem_rows else "| No problems solved yet | - | - | - | - | - | - | - |"
    
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
    
    # Generate knowledge graph visualization
    kg_visualization = generate_knowledge_graph_visualization(kg)
    
    # Interview readiness section
    tier_colors = {'S': '🌟', 'A': '🥇', 'B': '🥈', 'C': '🥉', 'D': '📊'}
    tier_icon = tier_colors.get(interview_ready['tier'], '📊')
    
    readiness_breakdown = "\n".join([f"- **{k.replace('_', ' ').title()}**: {v:.1f}/25" for k, v in interview_ready['breakdown'].items()])
    
    # Generate stats
    total = len(problems)
    diff_counts = Counter(p.difficulty for p in problems)
    easy, medium, hard = diff_counts['Easy'], diff_counts['Medium'], diff_counts['Hard']
    
    readme_content = f"""# 🧠 AI-Powered DSA Mastery System

> Next-generation repository with knowledge graphs, AI recommendations, and adaptive learning paths

---

## 🎯 Interview Readiness: {tier_icon} {interview_ready['tier']}-Tier

**Overall Score: {interview_ready['score']}/100**

### Readiness Breakdown
{readiness_breakdown}

### Knowledge Graph Metrics
- **Graph Connections**: {interview_ready['graph_connections']}
- **Learning Paths**: {len(kg.learning_paths)}
- **Topic Clusters**: {len(kg.topic_graph)}
- **Pattern Clusters**: {len(kg.pattern_graph)}

---

## 📊 AI-Enhanced Performance Dashboard

### Problem Statistics
- **Total Solved**: {total}
- **🟢 Easy**: {easy} | **🟡 Medium**: {medium} | **🔴 Hard**: {hard}
- **🧠 Overall Retention**: {retention_analytics.get('overall_retention_rate', 0)*100:.1f}%
- **📈 Learning Velocity**: {retention_analytics.get('learning_velocity', 0):.1f} problems/week
- **🕸️ Graph Connectivity**: {retention_analytics.get('knowledge_graph_connectivity', 0):.1f} avg connections

### Spaced Repetition Status
- **📋 Due Today**: {retention_analytics.get('problems_due_today', 0)} problems
- **📅 Due This Week**: {retention_analytics.get('problems_due_this_week', 0)} problems
- **🔄 Total Reviews**: {retention_analytics.get('total_reviews', 0)}

### Practice Heatmap (Last 12 Weeks)
{heatmap_visual}

---

## 🤖 AI-Powered Recommendations
{chr(10).join([f"{i+1}. {rec}" for i, rec in enumerate(ai_recommendations)])}

---

## 🕸️ Knowledge Graph Analysis
{kg_visualization}

---

## 🧠 Advanced Topic Mastery with Graph Insights

| Topic | Mastery Level | Count | Retention | Connections | Progress | Last Practice |
|-------|---------------|-------|-----------|-------------|----------|---------------|
{topic_table}

---

## 📋 Complete Problem List with Graph Metrics

|  #  | Problem Title | Difficulty | Pattern | Retention | Conn | Topics | Solution |
|----:|---------------|------------|---------|-----------|------|--------|----------|
{problem_table}

---

## 📈 Retention Analytics by Difficulty
{chr(10).join([f"- **{diff}**: {rate*100:.1f}% retention rate" for diff, rate in retention_analytics.get('retention_by_difficulty', {}).items()]) if retention_analytics.get('retention_by_difficulty') else "No retention data available"}

---

## 🤖 AI System Features

This repository implements a next-generation learning system:

### 🕸️ Knowledge Graph Technology
- **Automated graph construction** from problem metadata
- **Similarity detection** using multi-factor analysis
- **Learning dependency mapping** for optimal sequencing
- **Adaptive learning paths** using graph algorithms
- **Topic clustering** for knowledge organization

### 🧠 AI-Powered Analytics
- **Interview readiness scoring** with graph connectivity factors
- **Pattern recognition** across algorithmic categories
- **Knowledge gap analysis** using graph metrics
- **High-impact problem identification** via centrality measures
- **Personalized learning sequences** based on graph structure

### 🎯 Intelligent Recommendations
- **Knowledge graph-based suggestions** for optimal learning
- **Similarity-driven problem recommendations**
- **Learning path optimization** using graph traversal
- **Dependency-aware sequencing** for skill building
- **Adaptive difficulty progression** based on graph analysis

---

## 🛠️ AI System Architecture

### Knowledge Graph Engine
- **Multi-factor similarity calculation** (topics, patterns, difficulty, language)
- **Graph-based clustering** for topic and pattern groups
- **Learning path generation** using graph algorithms
- **Connectivity analysis** for problem importance
- **Dependency mapping** for skill prerequisites

### AI Recommendation Engine
- **Graph-based problem similarity** analysis
- **High-impact problem identification** via centrality
- **Learning gap detection** using graph metrics
- **Adaptive path generation** based on user progress
- **Knowledge graph visualization** for insights

---

## 📚 How the AI System Works

1. **Add Problems**: System extracts metadata and builds knowledge graph
2. **Graph Analysis**: Calculates similarities, dependencies, and clusters
3. **AI Processing**: Generates learning paths and identifies high-impact problems
4. **Smart Recommendations**: Provides graph-based personalized guidance
5. **Adaptive Learning**: Optimizes sequences based on knowledge graph structure

---

*AI-Powered DSA Repository System with Knowledge Graph & Adaptive Learning*  
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Knowledge Graph v2.0 | AI Recommendations Active | Adaptive Learning Paths*
"""
    
    return readme_content

def main():
    """Main function to generate AI-powered analytics README"""
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
    
    # Build knowledge graph
    kg = build_knowledge_graph(problems)
    
    # Calculate advanced analytics
    topic_mastery = calculate_topic_mastery(problems, kg)
    retention_analytics = calculate_retention_analytics(problems)
    interview_ready = calculate_interview_readiness(problems, topic_mastery, kg)
    
    # Generate AI recommendations
    user_problems = set(p.number for p in problems)
    ai_recommendations = generate_ai_recommendations(kg, user_problems, topic_mastery, interview_ready)
    
    # Generate visualizations
    heatmap = generate_practice_heatmap(problems)
    
    # Generate comprehensive README
    readme_content = generate_readme(problems, kg, topic_mastery, retention_analytics, interview_ready, ai_recommendations, heatmap)
    
    # Write README
    readme_path = repo_root / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"AI-powered analytics README generated")
    print(f"   Interview readiness: {interview_ready['tier']}-tier ({interview_ready['score']}/100)")
    print(f"   Knowledge graph: {len(kg.problem_nodes)} nodes, {len(kg.similarity_matrix)} edges")
    print(f"   Learning paths: {len(kg.learning_paths)} generated")
    print(f"   Topics mastered: {len(topic_mastery)}")

if __name__ == "__main__":
    main()