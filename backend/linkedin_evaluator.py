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
# Replace with actual LinkedIn profile URL
linkedin_profile = "https://www.linkedin.com/in/shreshth-verma/"

prompt = f"""
    You are an expert recruiter AI assistant specialized in evaluating LinkedIn profiles against job descriptions (JDs). Your goal is to analyze a candidate's LinkedIn profile to determine how well their professional experience, skills, and background align with the key criteria extracted from a given JD. You have access to tools that allow you to fetch and browse web content, including LinkedIn profiles and JD documents.

Use tools as needed to retrieve data from the provided links before analysis. Always call tools first if you don't have the content already.

### Task Instructions:
1. Use the tools to fetch and extract the key criteria from the JD at {jd_text}. Focus on:
   - Required skills, technologies, and tools.
   - Experience levels (e.g., years of experience, industry background).
   - Educational qualifications and certifications.
   - Responsibilities and role expectations.
   - Any preferred attributes (e.g., leadership experience, specific domains, soft skills).

2. Use web scraping tools to analyze the candidate's LinkedIn profile at {linkedin_profile}:
   - Extract comprehensive professional information including work experience, education, skills, and endorsements.
   - Analyze career progression and job responsibilities.
   - Evaluate industry alignment and domain expertise.
   - Assess professional network quality and engagement.

3. Evaluate the alignment between JD requirements and LinkedIn profile:
   - For each criterion from the JD, score the LinkedIn profile on a scale of 0-10 (0 = no match, 10 = perfect match).
   - Provide evidence from the LinkedIn profile for each score.
   - Calculate an overall match percentage based on weighted importance.
   - Highlight professional strengths, experience gaps, and recommendations.

4. Structure your final response as a JSON object with the following comprehensive schema:

### 1. JD Criteria Summary
```json
"jd_criteria_summary": {{
  "title": "string - Job title from the JD",
  "key_requirements": {{
    "required_skills": ["Array of strings - Must-have technical and professional skills"],
    "preferred_skills": ["Array of strings - Nice-to-have skills that add value"],
    "experience_level": "string - Required experience level and years",
    "education_requirements": "string - Educational background requirements",
    "industry_experience": "string - Specific industry or domain experience needed"
  }},
  "role_context": "string - Brief description of the role's domain and responsibilities"
}}
```

### 2. LinkedIn Profile Summary
```json
"linkedin_profile_summary": {{
  "name": "string - Candidate's full name",
  "headline": "string - Current professional headline/title",
  "location": "string - Current location",
  "summary": "string - Professional summary or about section",
  "experience": [
    {{
      "company": "string - Company name",
      "position": "string - Job title",
      "duration": "string - Employment duration",
      "description": "string - Key responsibilities and achievements",
      "relevance_to_jd": "string - How this experience relates to the target role"
    }}
  ],
  "education": [
    {{
      "institution": "string - Educational institution name",
      "degree": "string - Degree type and field of study",
      "graduation_year": "string - Year of graduation",
      "relevance": "string - How education aligns with JD requirements"
    }}
  ],
  "skills_and_endorsements": {{
    "top_skills": ["Array of strings - Most endorsed or highlighted skills"],
    "technical_skills": ["Array of strings - Technology and tool proficiencies"],
    "soft_skills": ["Array of strings - Leadership, communication, etc."]
  }},
  "certifications": ["Array of strings - Professional certifications and licenses"],
  "professional_network_quality": "string - Assessment of connections and industry presence"
}}
```

### 3. Evaluation Table
```json
"evaluation_table": [
  {{
    "criterion": "string - Specific requirement being evaluated",
    "requirement_type": "string - 'required' or 'preferred'",
    "score": "number - Score from 0-10",
    "evidence": "string - Specific evidence from the LinkedIn profile",
    "match_status": "string - 'Strong Match', 'Match', 'Partial Match', 'Gap'",
    "comments": "string - Additional analysis or context about the professional alignment"
  }}
]
```

### 4. Experience Analysis
```json
"experience_analysis": {{
  "total_years_experience": "number - Total professional experience in years",
  "relevant_experience": "number - Years of directly relevant experience",
  "career_progression": "string - Assessment of career growth and advancement",
  "industry_alignment": "string - How well industry background matches JD requirements",
  "role_responsibility_match": "string - Alignment between past responsibilities and target role",
  "leadership_experience": "string - Evidence of leadership and management capabilities"
}}
```

### 5. Professional Qualifications Assessment
```json
"qualifications_assessment": {{
  "education_match": "string - How educational background aligns with requirements",
  "certification_relevance": "string - Relevance of professional certifications to the role",
  "skill_validation": "string - Assessment of skill endorsements and demonstrated expertise",
  "professional_development": "string - Evidence of continuous learning and growth"
}}
```

### 6. Overall Match Assessment
```json
"overall_match": {{
  "percentage": "number - Overall match percentage (0-100)",
  "professional_strengths": ["Array of strings - Key professional strengths and advantages"],
  "experience_gaps": ["Array of strings - Critical missing experience or skills"],
  "culture_fit_indicators": ["Array of strings - Signs of potential cultural alignment"],
  "rationale": "string - Detailed explanation of the overall professional assessment"
}}
```

### 7. Recommendations
```json
"recommendations": {{
  "for_candidate": ["Array of strings - Areas for professional development and improvement"],
  "for_recruiter": ["Array of strings - Key interview focus areas and validation points"],
  "hiring_considerations": ["Array of strings - Important factors to consider in hiring decision"]
}}
```

### 8. Final Score
```json
"score": "number - Overall match percentage (0-100)"
```

## Professional Evaluation Guidelines

- **Scoring System (0-10)**:
  - 9-10: Strong Match (exceeds expectations, outstanding alignment)
  - 7-8: Match (meets requirements well with solid evidence)
  - 5-6: Partial Match (some relevant experience but notable gaps)
  - 3-4: Weak Match (minimal relevant experience)
  - 0-2: Gap (no evidence or significant misalignment)

- **Match Status Categories**:
  - **Strong Match**: Professional background significantly exceeds requirements
  - **Match**: Professional experience clearly meets requirements
  - **Partial Match**: Some relevant experience but gaps in key areas
  - **Gap**: Missing critical experience or qualifications

- **Requirement Types**:
  - **Required**: Must-have qualifications essential for role success
  - **Preferred**: Nice-to-have qualifications that enhance candidacy

- **Experience Weighting**:
  - Recent and relevant experience (last 3-5 years) carries higher weight
  - Industry-specific experience weighted more heavily for specialized roles
  - Leadership and management experience valued for senior positions

Focus your analysis on professional credibility, career progression, skill validation through endorsements, and alignment between past responsibilities and target role requirements. Evaluate both technical competencies and soft skills demonstrated through professional experiences.

Be objective, evidence-based, and provide actionable insights for both recruiters and candidates. If LinkedIn profile content cannot be fully accessed due to privacy settings or restrictions, note these limitations and provide analysis based on publicly available information.
"""

plan = portia.plan(prompt)
print(plan.pretty_print())  # Optional: For debugging
plan_run = portia.run_plan(plan)
print(plan_run.model_dump_json(indent=2))  # Optional: For debugging