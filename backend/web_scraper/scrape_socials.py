from __future__ import annotations
from pydantic import BaseModel
# from portia.builder import PlanBuilderV2, StepOutput, Input
from typing import Optional, Dict, Any

from config.portia import config
from portia import Portia
# from portia.open_source_tools.pdf_reader_tool import PDFReaderTool
from portia.open_source_tools.crawl_tool import CrawlTool
from portia.open_source_tools.search_tool import SearchTool
from tools.pdf_reader import PdfToMarkdownTool


class SocialInput(BaseModel):
    """Optional inputs that can be supplied to the scraper/update flow.

    All fields are optional. Provide only what you have; missing ones may be
    discovered via scraping or left as-is depending on the caller logic.
    """
    githubUrl: Optional[str] = None
    linkedInUrl: Optional[str] = None
    leetcodeUrl: Optional[str] = None
    xUrl: Optional[str] = None
    resume_url: Optional[str] = None
    portfolio_url: Optional[str] = None


def scrapeSocials(userId: str, data: Optional[Dict[str, Any]] = None):
    """Collect or update a user's social/profile URLs.

    Args:
        userId: The user's document ID in the database.
        data: Optional dictionary that may include any of these keys (all optional):
              - githubUrl
              - linkedInUrl
              - leetcodeUrl
              - xUrl
              - resume_url
              - portfolio_url

              Extra keys are ignored. Missing keys are treated as None.

    Returns:
        A dict-like structure with the social/profile URLs discovered or provided, or None.
    """

    # Validate and normalize input dictionary so all expected fields are present or None
    social_input = SocialInput.model_validate(data or {})

    # user = User.objects(id=userId).first()

    # socials, resume_url, portfolio_url = user.socials, user.resume_url, user.portfolio_url

    # Build a dynamic prompt from provided optional data
    resume_line = (
        f"Resume URL: {social_input.resume_url}"
        if social_input.resume_url else "Resume URL: Not provided"
    )
    portfolio_line = (
        f"Portfolio URL: {social_input.portfolio_url}"
        if social_input.portfolio_url else "Portfolio URL: Not provided"
    )
    known_socials = []
    if social_input.githubUrl:
        known_socials.append(f"GitHub: {social_input.githubUrl}")
    if social_input.linkedInUrl:
        known_socials.append(f"LinkedIn: {social_input.linkedInUrl}")
    if social_input.leetcodeUrl:
        known_socials.append(f"LeetCode: {social_input.leetcodeUrl}")
    if social_input.xUrl:
        known_socials.append(f"X/Twitter: {social_input.xUrl}")
    known_block = ("\nKnown socials (may be partial):\n- " + "\n- ".join(known_socials)) if known_socials else ""


    prompt =f"""
    {resume_line}
    {portfolio_line}
    {known_block}""" + """

Social Link Extractor Tool
Your goal is to gather a specific set of links for a given user from provided URLs. The required links are:
Social Media Links:

GitHub: Example format → https://github.com/<username>
LinkedIn: Example format → https://www.linkedin.com/in/<username>/
X (formerly Twitter): Example format → https://x.com/<username>
LeetCode: Example format → https://leetcode.com/u/<username>/

Professional Links:
5. Portfolio: Personal website/portfolio (e.g., https://johndoe.dev, https://portfolio.johndoe.com)
6. Resume: Direct link to resume/CV (PDF, Google Docs, or other formats)
Process
You will be provided with one or more URLs (such as portfolio websites, personal pages, or other social profiles). Follow this step-by-step process to extract the target links:
Step 1: Analyze Provided URLs

Use the web_fetch tool to visit each provided URL
Scan the entire page content for:

Direct links to the target platforms
Social media icons/buttons
Footer sections with social links
"About" or "Contact" sections
Navigation menus
Bio sections



Step 2: Extract Links from Primary Sources

Look for explicit URLs matching the target formats
Check for usernames or handles that can be constructed into full URLs
Search for portfolio links (personal websites, custom domains)
Look for resume/CV links (PDF downloads, Google Docs, drive links)
Examine HTML anchor tags, social media widgets, and embedded links
Check download buttons or "View Resume" links
Verify any found links by briefly checking them

Step 3: Follow Connected Profiles (if needed)
If any of the six required links are missing after Step 1:

Use any discovered social profiles as starting points
Browse those profiles using web_fetch and check:

Bio sections
Header/banner areas
"About" sections
Linked websites or "Link in bio" references
Profile descriptions



Step 4: Targeted Web Search (last resort)
If links are still missing after Steps 1-3:

Perform targeted searches using web_search
Use queries like:

"[username/name]" site:github.com
"[username/name]" site:linkedin.com
"[username/name]" site:x.com
"[username/name]" site:leetcode.com
"[username/name]" portfolio
"[username/name]" resume filetype:pdf


Cross-reference search results with information from the provided URLs to ensure accuracy

Output Format
Provide results in JSON format:
{
  'source_urls': [
    'https://example1.com',
    'https://example2.com'
  ],
  'extracted_links': {
    'social_media': {
      'github': {
        'url': 'https://github.com/username',
        'status': 'found',
        'extraction_method': 'Direct link from portfolio homepage'
      },
      'linkedin': {
        'url': 'https://www.linkedin.com/in/username/',
        'status': 'found',
        'extraction_method': 'Footer social icons'
      },
      'twitter': {
        'url': null,
        'status': 'not_found',
        'extraction_method': 'Checked all provided URLs and linked profiles'
      },
      'leetcode': {
        'url': 'https://leetcode.com/u/username/',
        'status': 'found',
        'extraction_method': 'Found via GitHub profile bio'
      }
    },
    'professional': {
      'portfolio': {
        'url': 'https://johndoe.dev',
        'status': 'found',
        'extraction_method': 'Primary URL provided'
      },
      'resume': {
        'url': 'https://drive.google.com/file/d/.../resume.pdf',
        'status': 'found',
        'extraction_method': 'Download button on portfolio'
      }
    }
  },
  'summary': {
    'total_found': 5,
    'total_missing': 1,
    'success_rate': '83%'
  },
  'notes': [
    'Twitter/X profile could not be located after exhaustive search',
    'All other links verified and confirmed to belong to the correct person'
  ]
}

Important Guidelines

Prioritize accuracy: Only report links that you can verify belong to the correct person
Direct extraction first: Always check the provided URLs thoroughly before using secondary methods
Validate links: Briefly visit discovered links to confirm they're active and belong to the right person
Be thorough: Check multiple sections of each webpage (header, footer, about, contact, etc.)
Cross-reference: Use information from multiple sources to verify identity consistency
Don't use web_search tool before crawling first, if any links are not found then
resolve to web_search tool

If a link cannot be found after exhaustive analysis, mark it as "Not found" with a brief explanation of what was checked.
    """
    portia = Portia(
        config=config,
        tools=[CrawlTool(), PdfToMarkdownTool(), SearchTool()],
    )

    plan = portia.plan(prompt)
    print(plan.pretty_print())
    plan_run = portia.run_plan(plan)
    print(plan_run.model_dump_json(indent=2))
    # Return the structured result for downstream usage
    try:
        return plan_run.model_dump()
    except Exception:
        return None