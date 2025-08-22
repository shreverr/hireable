from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Dict, Any

from config.portia import config
from portia import Portia
from portia.open_source_tools.crawl_tool import CrawlTool
from portia.open_source_tools.search_tool import SearchTool
from tools.pdf_reader import PdfToMarkdownTool

class EvalInput(BaseModel):
    """Input for platform evaluation. Currently requires the platform-specific URL."""
    url: str


def evaluate_platform(userId: str, platform: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Evaluate a user's profile on a specific platform based on common criteria.
    
    This function serves as a template for evaluating different platforms.
    It uses Portia to plan and execute the evaluation based on a platform-specific prompt.
    
    Args:
        userId: The user's document ID (for potential DB integration).
        platform: The platform to evaluate (e.g., 'github', 'leetcode', 'x', 'linkedin').
        data: Optional dict containing 'url' for the platform profile.
    
    Returns:
        A dict with evaluation results in JSON-like structure, or None on error.
    
    To add a new platform:
    1. Add a case in the if-elif chain for the platform.
    2. Define a tailored prompt with steps for data extraction and scoring.
    3. Specify tools relevant to the platform (e.g., CrawlTool for web scraping, SearchTool for supplementary searches).
    4. Ensure the output JSON format is consistent across platforms for easy aggregation.
    """
    if not data or 'url' not in data:
        raise ValueError("Data must include 'url' for the platform.")

    input_data = EvalInput.model_validate(data)
    url = input_data.url

    # Platform-specific prompts and tools
    if platform == 'github':
        prompt = f"""
        GitHub Profile Evaluator Tool

        Your goal is to evaluate the GitHub profile at {url} based on these criteria:
        - Commits: Total number and volume of commits across repositories.
        - Code Quality: Based on stars, forks, issue resolution, code organization (if accessible).
        - Recent Work Consistency: Frequency and recency of commits/contributions in the last 12 months.

        Process:
        Step 1: Use the crawl_tool to fetch the main profile page (e.g., overview, repositories tab).
        Extract: Username, total repositories, followers, total stars, contribution graph (e.g., commit streaks).

        Step 2: Crawl the repositories list. Select top 5-10 repositories by stars or activity.
        For each:
        - Crawl the repo page.
        - Extract: Commit count, last commit date, stars, forks, open/closed issues.

        Step 3: If needed, use search_tool for targeted queries like "site:github.com [username] commits" or "site:github.com [username] repositories" to supplement data.

        Step 4: Assign scores (0-10) for each criterion based on extracted data.
        Examples:
        - Commits: >1000 total commits → 10; 500-1000 → 8; <100 → 0.
        - Code Quality: High average stars/forks (>50 per repo) and low open issues ratio → 10.
        - Recent Work Consistency: Commits in >80% of weeks in last year → 10; sporadic → low score.

        Step 5: Compute overall platform score as weighted average.
        Weights: Commits=1, Code Quality=0.2, Recent Work Consistency=0.4.
        Formula: (commits_score * 1 + code_quality_score * 0.2 + recent_consistency_score * 0.4) / (1 + 0.2 + 0.4)

        Output Format (JSON):
        {{
          "platform": "github",
          "url": "{url}",
          "criteria": {{
            "commits": {{
              "score": <float>,
              "explanation": "<brief explanation with key metrics>"
            }},
            "code_quality": {{
              "score": <float>,
              "explanation": "<brief explanation with key metrics>"
            }},
            "recent_work_consistency": {{
              "score": <float>,
              "explanation": "<brief explanation with key metrics>"
            }}
          }},
          "overall_score": <float>,
          "notes": ["<any additional notes or limitations>"]
        }}

        Important Guidelines:
        - Prioritize direct crawling over search.
        - Handle private repos or limited access gracefully (note if data is incomplete).
        - Verify all data belongs to the correct user.
        - Do not fabricate metrics; base scores on evidence.
        """
        tools = [CrawlTool(), SearchTool()]

    elif platform == 'leetcode':
        # Template for LeetCode - customize prompt similarly
        prompt = f"""
        LeetCode Profile Evaluator Tool

        Your goal is to evaluate the LeetCode profile at {url} based on these criteria:
        - Commits: N/A or map to problems solved.
        - Code Quality: Based on acceptance rate, difficulty of problems, contest ratings.
        - Recent Work Consistency: Frequency of submissions in the last 12 months.

        # ... (Add steps similar to GitHub: crawl profile, extract solved problems, rating, submission history)
        # Use similar scoring and output format.
        """
        tools = [CrawlTool(), SearchTool()]
        # Note: Implement full prompt as needed.

    elif platform == 'x':
        # Template for X (Twitter)
        prompt = f"""
        X Profile Evaluator Tool

        Your goal is to evaluate the X profile at {url} based on these criteria:
        - Commits: N/A or map to post volume on tech topics.
        - Code Quality: Based on engagement (likes, retweets) on code-related posts.
        - Recent Work Consistency: Posting frequency in the last 12 months.

        # ... (Add steps: crawl profile, extract posts, engagement metrics)
        # Note: May need X-specific tools if available, but use CrawlTool/SearchTool.
        """
        tools = [CrawlTool(), SearchTool()]

    elif platform == 'linkedin':
        # Template for LinkedIn
        prompt = f"""
        LinkedIn Profile Evaluator Tool

        Your goal is to evaluate the LinkedIn profile at {url} based on these criteria:
        - Commits: N/A or map to project updates.
        - Code Quality: Based on endorsements, skills, project descriptions.
        - Recent Work Consistency: Activity like posts, job changes in last 12 months.

        # ... (Add steps: crawl profile sections - experience, skills, activity)
        """
        tools = [CrawlTool(), SearchTool(), PdfToMarkdownTool()]  

    else:
        raise ValueError(f"Unsupported platform: {platform}")

    # Initialize and run Portia
    portia = Portia(
        config=config,
        tools=tools,
    )

    plan = portia.plan(prompt)
    print(plan.pretty_print())  # Optional: For debugging
    plan_run = portia.run_plan(plan)
    print(plan_run.model_dump_json(indent=2))  # Optional: For debugging

    try:
        return plan_run.model_dump()
    except Exception:
        return None