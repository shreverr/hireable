from tools.pdf_reader import PdfToMarkdownTool
from portia.open_source_tools.search_tool import SearchTool
from portia.open_source_tools.crawl_tool import CrawlTool
from portia import DefaultToolRegistry, McpToolRegistry, Portia, Config, ToolRegistry

import os
from portia import Portia
from web_scraper.scrape_socials import scrapeSocials
from web_scraper.evaluate_platforms import evaluate_platform
from models.user import User
from config.db import connectDb
from dotenv import load_dotenv
from config.portia import config
load_dotenv()


my_tool_registry = ToolRegistry([
    PdfToMarkdownTool()
])

github_pat: str | None = os.getenv('GITHUB_PAT')

if(github_pat is None):
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
github_link = "https://github.com/shivambajpai04"

prompt = """
    You are an expert recruiter AI assistant specialized in evaluating GitHub profiles against job descriptions (JDs). Your goal is to analyze a candidate's GitHub profile to determine how well it aligns with the key criteria extracted from a given JD. You have access to tools that allow you to fetch and browse web content, such as GitHub profiles and JD links.

Use tools as needed to retrieve data from the provided links before analysis. Always call tools first if you don't have the content already.

### Task Instructions:
1. Use the tools to fetch and extract the key criteria from the JD at {https://pub-eb4327f5bd25419da66fc17aa5ca024d.r2.dev/SD%20Intern%20JD.pdf}. Focus on:
   - Required skills, technologies, and tools.
   - Experience levels (e.g., years of experience, project types).
   - Responsibilities and qualifications.
   - Any preferred attributes (e.g., open-source contributions, specific domains).

2. Use concrete metrics to analyse candidates github at {https://github.com/shreverr} at profile against the JD:
    - Based on the criteria you would use tools to explore and evaluate the users github profile.
    - For visiting individual repositories and exploring code you would use crawler.

3. Evaluate the alignment:
   - For each criterion from the JD, score the GitHub profile on a scale of 0-10 (0 = no match, 10 = perfect match).
   - Provide evidence from the GitHub profile for each score.
   - Calculate an overall match percentage (average of all scores).
   - Highlight strengths, gaps, and recommendations (e.g., "Strong in Python but lacks experience in cloud services mentioned in JD.").

4. Structure your final response as a JSON object with the following comprehensive schema:
### 1. JD Criteria Summary
```json
"jd_criteria_summary": {
  "title": "string - Job title from the JD",
  "key_requirements": {
    "required_skills": ["Array of strings - Must-have technical skills and technologies"],
    "preferred_skills": ["Array of strings - Nice-to-have skills that add value"],
    "experience_level": "string - Required experience level or educational background",
    "project_requirements": "string - Specific project experience requirements"
  },
  "role_context": "string - Brief description of the role's domain/industry focus"
}
```

### 2. GitHub Profile Summary
```json
"github_profile_summary": {
  "username": "string - GitHub username",
  "bio": "string - Profile bio or description",
  "self_reported_skills": ["Array of strings - Technologies listed in profile README/bio"],
  "key_repositories": [
    {
      "name": "string - Repository name",
      "description": "string - Brief description of the project",
      "technologies_used": ["Array of strings - Tech stack identified in the project"],
      "project_type": "string - e.g., 'full-stack', 'frontend', 'backend', 'CLI tool', etc."
    }
  ],
  "overall_profile_impression": "string - Summary of the candidate's technical focus and capabilities"
}
```

### 3. Evaluation Table
```json
"evaluation_table": [
  {
    "criterion": "string - Specific requirement being evaluated",
    "requirement_type": "string - 'required' or 'preferred'",
    "score": "number - Score from 0-10",
    "evidence": "string - Specific evidence from the GitHub profile",
    "match_status": "string - 'Strong Match', 'Match', 'Partial Match', 'Gap'",
    "comments": "string - Additional analysis or context about the match"
  }
]
```

### 4. Overall Match Assessment
```json
"overall_match": {
  "percentage": "number - Overall match percentage (0-100)",
  "strengths": ["Array of strings - Key areas where candidate excels"],
  "gaps": ["Array of strings - Critical missing skills or experience"],
  "rationale": "string - Detailed explanation of the overall assessment"
}
```

### 6. Final Score
```json
"score": "number - Overall match percentage"
```

## Schema Guidelines

- **Scoring System**: Use a 0-10 scale for individual criteria, where:
  - 9-10: Strong Match (exceeds expectations)
  - 7-8: Match (meets requirements well)
  - 5-6: Partial Match (some evidence, but gaps exist)
  - 3-4: Weak Match (minimal evidence)
  - 0-2: Gap (no evidence or completely missing)

- **Match Status Categories**:
  - **Strong Match**: Exceeds requirements with clear evidence
  - **Match**: Meets requirements with solid evidence
  - **Partial Match**: Some relevant experience but gaps exist
  - **Gap**: Missing or insufficient evidence

- **Requirement Types**:
  - **Required**: Must-have skills critical for the role
  - **Preferred**: Nice-to-have skills that add value

- **Overall Percentage**: Calculate based on weighted importance of required vs. preferred skills, with required skills having higher impact on the final score.

Ensure your analysis is thorough, evidence-based, and provides actionable insights for both recruiters and candidates.
Be objective, evidence-based, and concise. If the links are invalid or content can't be fetched, note that and proceed with assumptions if possible.
"""

plan = portia.plan(prompt)
print(plan.pretty_print())  # Optional: For debugging
plan_run = portia.run_plan(plan)
print(plan_run.model_dump_json(indent=2))  # Optional: For debugging
