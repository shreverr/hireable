from __future__ import annotations
from pydantic import BaseModel
from portia.builder import PlanBuilderV2, StepOutput, Input
from models.user import User
from typing import Optional

from config.portia import config
from portia import open_source_tool_registry, Portia


def scrapeSocials():
    """If the user's socials are already filled in DB, return them; otherwise continue later.

    Args:
            urls: A list of URL strings to process (not used when returning cached socials).
            userId: The user's document ID in the database.

    Returns:
            A dict with keys githubUrl, linkedInUrl, leetcodeUrl, xUrl if all are present; otherwise None.
    """

    # user = User.objects(id=userId).first()

    # socials, resume_url, portfolio_url = user.socials, user.resume_url, user.portfolio_url

    prompt = """
    Resume URl: https://res.cloudinary.com/dpf6c8boe/image/upload/v1750428758/mi6hnvneusqzav85tufz.pdf
    
    Your goal is to gather a specific set of social links for a given user. The required links are:

1. GitHub: Example format -> https://github.com/<username>
2. LinkedIn: Example format -> https://www.linkedin.com/in/<username>/
3. X (formerly Twitter): Example format -> https://x.com/<username>
4. LeetCode: Example format -> https://leetcode.com/u/<username>/

You will have access to the user's resume (typically as a PDF attachment) and, optionally, one or more portfolio links (as URLs). Follow this step-by-step process to extract the links:

1. **Start with the resume**: Use available tools to scan the entire resume for mentions of the social links. Look for explicit URLs, usernames, or icons/hyperlinks indicating these platforms. Extract any matching links directly.

2. **Check the portfolio (if provided)**: If a portfolio URL is available (e.g., from the resume or user input), use the available tool to visit the site. Scan the homepage, "About" section, footer, or contact page for the social links. Extract any matching ones.

3. **Handle missing links**: If any of the four required links are still missing after steps 1 and 2:
   - Use the links you've already found (e.g., GitHub or LinkedIn profile) as starting points.
   - Browse those profiles (via browse_page) and check the bio, header, "About" section, or linked websites for references to the missing platforms.
   - If needed, perform targeted web searches (via web_search) using the user's name combined with platform-specific queries (e.g., "John Doe LeetCode profile") to locate and verify missing links. Cross-reference with details from the resume to ensure accuracy.

Prioritize direct extraction from primary sources (resume and portfolio) for reliability. Only use secondary methods (profile bios or searches) if necessary, and validate any discovered links by browsing them briefly to confirm they belong to the user.

If a link cannot be found after exhaustive checks, note it as "Not found" with a brief explanation.
	"""
    portia = Portia(
        config=config,
        tools=open_source_tool_registry,
    )

    plan = portia.plan(prompt)
    print(plan.pretty_print())
    plan_run = portia.run_plan(plan)
    print(plan_run.model_dump_json(indent=2))


# Starting from Claude

# Define the structured output schema

class SocialLinksOutput(BaseModel):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter_x: Optional[str] = None
    leetcode: Optional[str] = None
    notes: str = ""


# Build the plan
plan = (
    PlanBuilderV2("Extract social media links from user resume and portfolio")
    .input(
        name="resume_content",
        description="The user's resume content (extracted from PDF or provided text)"
    )
    .input(
        name="portfolio_url",
        description="Optional portfolio URL to scan for additional links",
        default_value=None
    )

    # Step 1: Scan resume for social links
    .llm_step(
        task="Extract GitHub, LinkedIn, X/Twitter, and LeetCode links from the resume content. Look for explicit URLs, usernames, or any mentions of these platforms. Return found links in JSON format.",
        inputs=[Input("resume_content")],
        name="extract_from_resume"
    )

    # Step 2: If portfolio URL provided, scan it for additional links
    .if_(
        condition=lambda portfolio_url: portfolio_url is not None and portfolio_url.strip() != "",
        args={"portfolio_url": Input("portfolio_url")}
    )
    .single_tool_agent_step(
        tool="web_scraper",
        task="Visit the portfolio website and extract any GitHub, LinkedIn, X/Twitter, or LeetCode links. Check homepage, about section, footer, and contact pages.",
        inputs=[Input("portfolio_url")],
        name="extract_from_portfolio"
    )
    .endif()

    # Step 3: Combine results from resume and portfolio
    .llm_step(
        task="Combine the social links found from resume and portfolio. Create a consolidated list removing duplicates and prioritizing the most complete/accurate links.",
        inputs=[StepOutput("extract_from_resume"),
                StepOutput("extract_from_portfolio")],
        name="combine_initial_results"
    )

    # Step 4: Check if any links are still missing and search for them
    .llm_step(
        task="Identify which of the 4 required social links (GitHub, LinkedIn, X/Twitter, LeetCode) are still missing from the combined results.",
        inputs=[StepOutput("combine_initial_results")],
        name="identify_missing_links"
    )

    # Step 5: If links are missing, use found profiles to search for missing ones
    .if_(
        condition="There are missing social media links that need to be found",
        args={"missing_analysis": StepOutput("identify_missing_links")}
    )
    .single_tool_agent_step(
        tool="web_search",
        task="Search for missing social media profiles using the user's name and information from the resume combined with platform-specific queries (e.g., 'John Doe LeetCode profile')",
        inputs=[StepOutput("identify_missing_links"), Input("resume_content")],
        name="search_missing_links"
    )
    .endif()

    # Step 6: Validate found links by checking if they belong to the user
    .if_(
        condition="New links were found that need validation",
        args={"search_results": StepOutput("search_missing_links")}
    )
    .single_tool_agent_step(
        tool="web_scraper",
        task="Briefly visit the discovered social media profiles to validate they belong to the user by cross-referencing with details from the resume (name, skills, experience, etc.)",
        inputs=[StepOutput("search_missing_links"), Input("resume_content")],
        name="validate_found_links"
    )
    .endif()

    # Step 7: Generate final consolidated results
    .llm_step(
        task="Create the final consolidated list of social media links. For each platform (GitHub, LinkedIn, X/Twitter, LeetCode), provide the link if found or mark as 'Not found' with explanation. Include any relevant notes about the search process.",
        inputs=[
            StepOutput("combine_initial_results"),
            StepOutput("search_missing_links"),
            StepOutput("validate_found_links")
        ],
        name="final_consolidation"
    )

    # Configure final output with structured schema
    .final_output(
        output_schema=SocialLinksOutput,
        summarize=True
    )
    .build()
)
