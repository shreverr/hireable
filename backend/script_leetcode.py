from tools.pdf_reader import PdfToMarkdownTool
from tools.leetcode import LeetCodeAPITool
from portia.open_source_tools.search_tool import SearchTool
from portia.open_source_tools.crawl_tool import CrawlTool
from portia import DefaultToolRegistry, McpToolRegistry, Portia, Config, ToolRegistry

import os
from portia import Portia
from models.user import User
from config.db import connectDb
from dotenv import load_dotenv
from config.portia import config
load_dotenv()


my_tool_registry = ToolRegistry([
    PdfToMarkdownTool(),
    LeetCodeAPITool()
])

github_pat: str | None = os.getenv('GITHUB_PAT')

if (github_pat is None):
    exit()

tool_registry = my_tool_registry + DefaultToolRegistry(config) + McpToolRegistry.from_stdio_connection(
    server_name="github",
    command="docker",
    args=[
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server",
    ],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_pat},
)

portia = Portia(
    config=config,
    tools=tool_registry,
)

jd_text = "https://pub-eb4327f5bd25419da66fc17aa5ca024d.r2.dev/SD%20Intern%20JD.pdf"
leetcode_username = "shivambajpai04"  # Replace with actual LeetCode username

prompt = f"""
    You are an expert technical recruiter AI assistant specialized in evaluating LeetCode profiles against job descriptions (JDs). Your goal is to analyze a candidate's competitive programming and problem-solving skills through their LeetCode performance to determine how well they align with the algorithmic and technical requirements extracted from a given JD.

### Task Instructions:
1. First, extract the key technical and algorithmic criteria from the JD at {jd_text}. Focus on:
   - Data structures and algorithms knowledge needed
   - Problem-solving complexity requirements
   - Technical skill level expectations
   - Any specific algorithmic domains mentioned (e.g., dynamic programming, graphs, etc.)

2. Analyze the candidate's LeetCode profile for username '{leetcode_username}':
   - Retrieve comprehensive profile data and skill statistics
   - Evaluate problem-solving performance across different difficulty levels
   - Assess skill distribution across various algorithmic topics
   - Analyze consistency and activity patterns

3. Evaluate the alignment between JD requirements and LeetCode performance:
   - For each criterion from the JD, score the LeetCode profile on a scale of 0-10 (0 = no evidence, 10 = exceptional performance)
   - Provide concrete evidence from the LeetCode statistics for each score
   - Calculate an overall match percentage based on weighted importance
   - Highlight algorithmic strengths, skill gaps, and recommendations

4. Structure your final response as a JSON object with the following comprehensive schema:

### 1. JD Technical Criteria Summary
```json
"jd_criteria_summary": {{
  "title": "string - Job title from the JD",
  "technical_requirements": {{
    "programming_languages": ["Array of strings - Required/preferred languages"],
    "algorithmic_concepts": ["Array of strings - Data structures and algorithms needed"],
    "problem_complexity": "string - Expected problem-solving complexity level",
    "technical_domains": ["Array of strings - Specific technical areas (e.g., backend, systems, ML)"]
  }},
  "role_context": "string - Brief description of the technical role's focus"
}}
```

### 2. LeetCode Profile Summary
```json
"leetcode_profile_summary": {{
  "username": "string - LeetCode username",
  "overall_stats": {{
    "total_solved": "number - Total problems solved",
    "easy_solved": "number - Easy problems solved",
    "medium_solved": "number - Medium problems solved", 
    "hard_solved": "number - Hard problems solved",
    "acceptance_rate": "number - Overall acceptance rate percentage",
    "ranking": "number - Current global ranking if available"
  }},
  "skill_distribution": {{
    "strong_areas": ["Array of strings - Algorithmic topics with high proficiency"],
    "developing_areas": ["Array of strings - Algorithmic topics with room for improvement"],
    "language_proficiency": ["Array of strings - Programming languages used most frequently"]
  }},
  "activity_pattern": "string - Assessment of consistency and recent activity"
}}
```

### 3. Evaluation Table
```json
"evaluation_table": [
  {{
    "criterion": "string - Specific technical requirement being evaluated",
    "requirement_type": "string - 'critical', 'important', or 'preferred'",
    "score": "number - Score from 0-10",
    "evidence": "string - Specific evidence from LeetCode performance data",
    "match_status": "string - 'Exceptional', 'Strong Match', 'Adequate', 'Below Expectations', 'Gap'",
    "comments": "string - Detailed analysis of how LeetCode performance relates to this requirement"
  }}
]
```

### 4. Algorithmic Assessment
```json
"algorithmic_assessment": {{
  "problem_solving_level": "string - Assessment of overall problem-solving capability",
  "difficulty_comfort_zone": "string - Analysis of performance across Easy/Medium/Hard problems",
  "algorithmic_breadth": "string - Evaluation of skill diversity across different CS topics",
  "consistency_score": "number - Score 0-10 for solving consistency and activity",
  "learning_trajectory": "string - Assessment of skill development over time if data available"
}}
```

### 5. Overall Match Assessment
```json
"overall_match": {{
  "percentage": "number - Overall match percentage (0-100)",
  "technical_strengths": ["Array of strings - Key algorithmic/technical strengths"],
  "skill_gaps": ["Array of strings - Areas needing improvement for this role"],
  "readiness_level": "string - Assessment of candidate's readiness for technical interviews",
  "rationale": "string - Detailed explanation of the overall assessment"
}}
```

### 6. Recommendations
```json
"recommendations": {{
  "for_candidate": ["Array of strings - Specific areas to focus on for improvement"],
  "for_recruiter": ["Array of strings - Interview focus areas and follow-up questions"],
  "timeline_estimate": "string - Estimated time for candidate to reach role requirements if gaps exist"
}}
```

### 7. Final Score
```json
"score": "number - Overall match percentage (0-100)"
```

## Scoring Guidelines

- **Scoring System (0-10)**:
  - 9-10: Exceptional (Top-tier performance, exceeds expectations)
  - 7-8: Strong Match (Solid performance, meets requirements well)
  - 5-6: Adequate (Meets basic requirements with some gaps)
  - 3-4: Below Expectations (Significant gaps in expected areas)
  - 0-2: Gap (Insufficient evidence or major deficiencies)

- **Match Status Categories**:
  - **Exceptional**: Performance significantly exceeds role requirements
  - **Strong Match**: Performance clearly meets and often exceeds requirements
  - **Adequate**: Performance meets minimum requirements with minor gaps
  - **Below Expectations**: Performance shows potential but has notable gaps
  - **Gap**: Performance indicates significant skill development needed

- **Requirement Priority Weighting**:
  - **Critical**: Core algorithmic skills essential for the role (70% weight)
  - **Important**: Supporting technical skills that enhance performance (20% weight)
  - **Preferred**: Nice-to-have skills that add value (10% weight)

Focus your analysis on quantifiable LeetCode metrics and their correlation to real-world technical requirements. Be objective and provide actionable insights for both technical recruiters and candidates preparing for similar roles.

If the LeetCode profile cannot be accessed or has insufficient data, note these limitations and provide analysis based on available information.
"""

plan = portia.plan(prompt)
print(plan.pretty_print())  # Optional: For debugging
plan_run = portia.run_plan(plan)
print(plan_run.model_dump_json(indent=2))  # Optional: For debugging
