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
    PdfToMarkdownTool(),
    SearchTool(),
    CrawlTool()
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
github_link = "https://github.com/shivambajpai04"
linkedin_link = "https://www.linkedin.com/in/shivambajpai04"  # Add LinkedIn profile

prompt = """
    You are an expert recruiter AI assistant specialized in evaluating both GitHub and LinkedIn profiles against job descriptions (JDs). Your goal is to analyze a candidate's GitHub profile AND LinkedIn profile to determine how well they align with the key criteria extracted from a given JD. You have access to tools that allow you to fetch and browse web content, including GitHub profiles, LinkedIn profiles, and JD links.

Use tools as needed to retrieve data from the provided links before analysis. Always call tools first if you don't have the content already.

### Task Instructions:
1. Use the tools to fetch and extract the key criteria from the JD at {https://pub-eb4327f5bd25419da66fc17aa5ca024d.r2.dev/SD%20Intern%20JD.pdf}. Focus on:
   - Required skills, technologies, and tools.
   - Experience levels (e.g., years of experience, project types).
   - Responsibilities and qualifications.
   - Any preferred attributes (e.g., open-source contributions, specific domains).

2. Use concrete metrics to analyse candidates GitHub profile at {https://github.com/shreverr}:
    - Based on the criteria you would use tools to explore and evaluate the users github profile.
    - For visiting individual repositories and exploring code you would use crawler.

3. Use concrete metrics to analyse candidates LinkedIn profile at {https://www.linkedin.com/in/shreshth-verma/}:
    - Extract professional experience, education, skills, endorsements, and recommendations.
    - Analyze posts, articles, and professional activity for domain expertise.
    - Look for certifications, courses, and professional development.
    - Evaluate professional network and connections quality.
    - Check for consistency with GitHub profile data.

4. Cross-platform evaluation:
   - Compare information consistency between GitHub and LinkedIn
   - Identify complementary strengths across both platforms
   - Note any discrepancies or missing professional presentation
   - Evaluate overall professional brand coherence

5. Evaluate the alignment:
   - For each criterion from the JD, score both GitHub and LinkedIn profiles on a scale of 0-10 (0 = no match, 10 = perfect match).
   - Provide evidence from both platforms for each score.
   - Calculate platform-specific match percentages and an overall combined match percentage.
   - Highlight strengths, gaps, and recommendations across both platforms.

6. Structure your final response as a JSON object with the following comprehensive schema:

### 1. JD Criteria Summary
```json
"jd_criteria_summary": {
  "title": "string - Job title from the JD",
  "key_requirements": {
    "required_skills": ["Array of strings - Must-have technical skills and technologies"],
    "preferred_skills": ["Array of strings - Nice-to-have skills that add value"],
    "experience_level": "string - Required experience level or educational background",
    "project_requirements": "string - Specific project experience requirements",
    "soft_skills": ["Array of strings - Communication, leadership, teamwork requirements"]
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
      "project_type": "string - e.g., 'full-stack', 'frontend', 'backend', 'CLI tool', etc.",
      "stars": "number - Repository stars",
      "commits": "number - Recent commit activity"
    }
  ],
  "overall_profile_impression": "string - Summary of the candidate's technical focus and capabilities",
  "activity_metrics": {
    "total_repos": "number - Total repositories",
    "contribution_streak": "string - Recent contribution activity",
    "followers": "number - GitHub followers"
  }
}
```

### 3. LinkedIn Profile Summary
```json
"linkedin_profile_summary": {
  "name": "string - Full name from LinkedIn",
  "headline": "string - Professional headline",
  "current_position": "string - Current job title and company",
  "experience": [
    {
      "title": "string - Job title",
      "company": "string - Company name",
      "duration": "string - Employment duration",
      "description": "string - Role description and achievements"
    }
  ],
  "education": [
    {
      "institution": "string - Educational institution",
      "degree": "string - Degree and field of study",
      "duration": "string - Study period"
    }
  ],
  "skills_and_endorsements": ["Array of strings - Listed skills with endorsement counts"],
  "certifications": ["Array of strings - Professional certifications"],
  "recent_activity": "string - Summary of recent posts and engagement",
  "network_quality": "string - Assessment of professional connections",
  "overall_profile_impression": "string - Summary of professional brand and presentation"
}
```

### 4. Cross-Platform Consistency Analysis
```json
"cross_platform_analysis": {
  "consistency_score": "number - Score 0-10 for information consistency",
  "complementary_strengths": ["Array of strings - Strengths that complement each other"],
  "discrepancies": ["Array of strings - Any conflicting or missing information"],
  "professional_brand_coherence": "string - Assessment of overall professional presentation"
}
```

### 5. Evaluation Table
```json
"evaluation_table": [
  {
    "criterion": "string - Specific requirement being evaluated",
    "requirement_type": "string - 'required' or 'preferred'",
    "github_score": "number - GitHub score from 0-10",
    "github_evidence": "string - Specific evidence from GitHub profile",
    "linkedin_score": "number - LinkedIn score from 0-10", 
    "linkedin_evidence": "string - Specific evidence from LinkedIn profile",
    "combined_score": "number - Weighted combined score from 0-10",
    "match_status": "string - 'Strong Match', 'Match', 'Partial Match', 'Gap'",
    "comments": "string - Additional analysis about the combined evidence"
  }
]
```

### 6. Platform-Specific Match Assessment
```json
"platform_match_assessment": {
  "github_match": {
    "percentage": "number - GitHub-only match percentage (0-100)",
    "strengths": ["Array of strings - Key GitHub strengths"],
    "gaps": ["Array of strings - GitHub-specific gaps"]
  },
  "linkedin_match": {
    "percentage": "number - LinkedIn-only match percentage (0-100)", 
    "strengths": ["Array of strings - Key LinkedIn strengths"],
    "gaps": ["Array of strings - LinkedIn-specific gaps"]
  },
  "combined_match": {
    "percentage": "number - Overall combined match percentage (0-100)",
    "strengths": ["Array of strings - Combined strengths from both platforms"],
    "gaps": ["Array of strings - Critical missing skills or experience"],
    "rationale": "string - Detailed explanation of the combined assessment"
  }
}
```

### 7. Professional Presentation Analysis
```json
"professional_presentation": {
  "github_professionalism": "number - Score 0-10 for GitHub professional presentation",
  "linkedin_professionalism": "number - Score 0-10 for LinkedIn professional presentation", 
  "overall_brand_strength": "number - Score 0-10 for overall professional brand",
  "recommendations": ["Array of strings - Suggestions for improving professional presentation"]
}
```

### 8. Final Score
```json
"final_assessment": {
  "overall_score": "number - Final combined score (0-100)",
  "recommendation": "string - Hire/Interview/Pass recommendation with rationale",
  "key_decision_factors": ["Array of strings - Main factors influencing the decision"]
}
```

## Scoring Guidelines

### Individual Platform Scoring:
- **GitHub Technical Score (0-10)**:
  - 9-10: Exceptional technical skills with high-quality projects
  - 7-8: Strong technical skills with good project portfolio
  - 5-6: Adequate technical skills with some relevant projects
  - 3-4: Basic technical skills with limited relevant work
  - 0-2: Insufficient technical demonstration

- **LinkedIn Professional Score (0-10)**:
  - 9-10: Exceptional professional presentation and experience
  - 7-8: Strong professional background and presentation
  - 5-6: Adequate professional experience and presentation
  - 3-4: Basic professional presence with some gaps
  - 0-2: Poor professional presentation or insufficient information

### Combined Scoring:
- **GitHub Weight**: 60% for technical roles, 40% for management roles
- **LinkedIn Weight**: 40% for technical roles, 60% for management roles
- **Cross-platform Consistency Bonus**: +5% for highly consistent profiles
- **Professional Brand Bonus**: +5% for exceptionally coherent professional brand

### Match Status Categories:
- **Strong Match**: Combined score 85-100 (exceeds expectations)
- **Match**: Combined score 70-84 (meets requirements well)
- **Partial Match**: Combined score 50-69 (some gaps but potential)
- **Gap**: Combined score below 50 (significant concerns)

### Recommendation Guidelines:
- **Strong Hire**: Score 85+, strong technical + professional presentation
- **Interview**: Score 70-84, good potential with some areas to explore
- **Consider**: Score 50-69, potential but significant gaps to discuss
- **Pass**: Score below 50, substantial concerns outweigh potential

Ensure your analysis is thorough, evidence-based, and provides actionable insights for recruiters. Consider how GitHub and LinkedIn data complement each other to form a complete picture of the candidate's professional profile.

Be objective, evidence-based, and comprehensive. If links are invalid or content can't be fetched, note that and proceed with available information.
"""

plan = portia.plan(prompt)
print(plan.pretty_print())  # Optional: For debugging
plan_run = portia.run_plan(plan)
print(plan_run.model_dump_json(indent=2))  # Optional: For debugging
