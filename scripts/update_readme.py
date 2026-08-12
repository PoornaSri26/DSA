#!/usr/bin/env python3
"""
Simple DSA Repository README Generator
Auto-updates README with problem list and basic stats
"""

import os
import re
from pathlib import Path
from collections import Counter

def extract_problem_info(folder_path):
    """Extract basic problem information from folder."""
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
    
    # Extract problem number from folder name
    folder_name = folder_path.name
    number_match = re.match(r'(\d+)-', folder_name)
    problem_number = int(number_match.group(1)) if number_match else 0
    
    # Find solution file
    solution_files = list(folder_path.glob("*.cpp")) + list(folder_path.glob("*.py")) + \
                     list(folder_path.glob("*.java")) + list(folder_path.glob("*.js"))
    solution_file = solution_files[0] if solution_files else None
    
    return {
        'number': problem_number,
        'title': title,
        'difficulty': difficulty,
        'url': url,
        'folder': folder_name,
        'solution_file': solution_file.name if solution_file else None
    }

def generate_readme(problems):
    """Generate simple, clean README with visual elements."""
    
    # Count by difficulty
    diff_counts = Counter(p['difficulty'] for p in problems)
    total = len(problems)
    easy = diff_counts.get('Easy', 0)
    medium = diff_counts.get('Medium', 0)
    hard = diff_counts.get('Hard', 0)
    
    # Simple progress bar
    progress = "█" * min(20, total) + "░" * max(0, 20 - total)
    
    # Sort by problem number
    sorted_problems = sorted(problems, key=lambda x: x['number'])
    
    # Generate table rows with emoji
    table_rows = []
    for problem in sorted_problems:
        solution_link = f"[{problem['solution_file']}]({problem['folder']}/{problem['solution_file']})" if problem['solution_file'] else "N/A"
        emoji = "🟢" if problem['difficulty'] == 'Easy' else "🟡" if problem['difficulty'] == 'Medium' else "🔴"
        table_rows.append(f"| {problem['number']:4d} | {emoji} {problem['title'][:40]:40s} | {solution_link} |")
    
    table_content = "\n".join(table_rows)
    
    readme_content = f"""# 🧩 LeetCode Solutions

![Progress](https://img.shields.io/badge/Progress-{total}-20-green) ![Easy](https://img.shields.io/badge/Easy-{easy}-brightgreen) ![Medium](https://img.shields.io/badge/Medium-{medium}-yellow) ![Hard](https://img.shields.io/badge/Hard-{hard}-red)

{progress} **{total}/20** problems

---

## 📋 Problems

|  #  | Problem | Solution |
|----:|---------|----------|
{table_content}

---

## ➕ Add Problem

`{{number}}-problem-name/` → solution file + README → push ✨

---

*Auto-updated by GitHub Actions*
"""
    
    return readme_content

def main():
    """Main function."""
    repo_root = Path(__file__).parent.parent
    
    # Find problem folders
    problem_folders = []
    for item in repo_root.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name not in ['scripts', '.github']:
            if re.match(r'^\d+', item.name):
                problem_folders.append(item)
    
    # Extract problem info
    problems = []
    for folder in problem_folders:
        problem_info = extract_problem_info(folder)
        if problem_info:
            problems.append(problem_info)
    
    if not problems:
        print("No problems found!")
        return
    
    # Generate README
    readme_content = generate_readme(problems)
    
    # Write README
    readme_path = repo_root / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"README updated with {len(problems)} problems")

if __name__ == "__main__":
    main()