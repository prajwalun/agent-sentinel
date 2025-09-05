from agent_sentinel import monitor
import requests
import json
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from exa_py import Exa

class CompetitorDataSchema(BaseModel):
    company_name: str = Field(description="Name of the company")
    pricing: str = Field(description="Pricing details, tiers, and plans")
    key_features: List[str] = Field(description="Main features and capabilities of the product/service")
    tech_stack: List[str] = Field(description="Technologies, frameworks, and tools used")
    marketing_focus: str = Field(description="Main marketing angles and target audience")
    customer_feedback: str = Field(description="Customer testimonials, reviews, and feedback")

@monitor
def run_competitor_analysis(url, description, api_keys, search_engine):
    """
    Run the competitor analysis workflow using the provided parameters.
    Args:
        url (str): The company URL.
        description (str): The company description.
        api_keys (dict): Dictionary of required API keys.
        search_engine (str): 'Perplexity AI - Sonar Pro' or 'Exa AI'.
    Returns:
        dict: Results including competitor URLs, comparison table, and analysis report.
    """
    # Setup agents and tools
    firecrawl_tools = FirecrawlTools(
        api_key=api_keys['firecrawl_api_key'],
        scrape=False,
        crawl=True,
        limit=5
    )
    firecrawl_agent = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=api_keys['openai_api_key']),
        tools=[firecrawl_tools, DuckDuckGoTools()],
        show_tool_calls=True,
        markdown=True
    )
    analysis_agent = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=api_keys['openai_api_key']),
        show_tool_calls=True,
        markdown=True
    )
    comparison_agent = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=api_keys['openai_api_key']),
        show_tool_calls=True,
        markdown=True
    )
    # Get competitor URLs
    competitor_urls = []
    if search_engine == "Perplexity AI - Sonar Pro":
        perplexity_url = "https://api.perplexity.ai/chat/completions"
        content = "Find me 3 competitor company URLs similar to the company with "
        if url and description:
            content += f"URL: {url} and description: {description}"
        elif url:
            content += f"URL: {url}"
        else:
            content += f"description: {description}"
        content += ". ONLY RESPOND WITH THE URLS, NO OTHER TEXT."
        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "Be precise and only return 3 company URLs ONLY."},
                {"role": "user", "content": content}
            ],
            "max_tokens": 1000,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {api_keys['perplexity_api_key']}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(perplexity_url, json=payload, headers=headers)
            response.raise_for_status()
            urls = response.json()['choices'][0]['message']['content'].strip().split('\n')
            competitor_urls = [u.strip() for u in urls if u.strip()]
        except Exception as e:
            competitor_urls = []
    else:  # Exa AI
        try:
            exa = Exa(api_key=api_keys['exa_api_key'])
            if url:
                result = exa.find_similar(
                    url=url,
                    num_results=3,
                    exclude_source_domain=True,
                    category="company"
                )
            else:
                result = exa.search(
                    description,
                    type="neural",
                    category="company",
                    use_autoprompt=True,
                    num_results=3
                )
            competitor_urls = [item.url for item in result.results]
        except Exception as e:
            competitor_urls = []
    # Extract competitor info
    competitor_data = []
    for comp_url in competitor_urls:
        try:
            app = FirecrawlApp(api_key=api_keys['firecrawl_api_key'])
            url_pattern = f"{comp_url}/*"
            extraction_prompt = """
            Extract detailed information about the company's offerings, including:
            - Company name and basic information
            - Pricing details, plans, and tiers
            - Key features and main capabilities
            - Technology stack and technical details
            - Marketing focus and target audience
            - Customer feedback and testimonials
            Analyze the entire website content to provide comprehensive information for each field.
            """
            response = app.extract(
                [url_pattern],
                {
                    'prompt': extraction_prompt,
                    'schema': CompetitorDataSchema.model_json_schema(),
                }
            )
            if response.get('success') and response.get('data'):
                extracted_info = response['data']
                competitor_json = {
                    "competitor_url": comp_url,
                    "company_name": extracted_info.get('company_name', 'N/A'),
                    "pricing": extracted_info.get('pricing', 'N/A'),
                    "key_features": extracted_info.get('key_features', [])[:5],
                    "tech_stack": extracted_info.get('tech_stack', [])[:5],
                    "marketing_focus": extracted_info.get('marketing_focus', 'N/A'),
                    "customer_feedback": extracted_info.get('customer_feedback', 'N/A')
                }
                competitor_data.append(competitor_json)
        except Exception as e:
            continue
    # Generate comparison table
    comparison_table = None
    if competitor_data:
        formatted_data = json.dumps(competitor_data, indent=2)
        system_prompt = f"""
        As an expert business analyst, analyze the following competitor data in JSON format and create a structured comparison.
        Extract and summarize the key information into concise points.
        {formatted_data}
        Return the data in a structured format with EXACTLY these columns:
        Company, Pricing, Key Features, Tech Stack, Marketing Focus, Customer Feedback
        Rules:
        1. For Company: Include company name and URL
        2. For Key Features: List top 3 most important features only
        3. For Tech Stack: List top 3 most relevant technologies only
        4. Keep all entries clear and concise
        5. Format feedback as brief quotes
        6. Return ONLY the structured data, no additional text
        """
        comparison_response = comparison_agent.run(system_prompt)
        try:
            table_lines = [
                line.strip()
                for line in comparison_response.content.split('\n')
                if line.strip() and '|' in line
            ]
            headers = [col.strip() for col in table_lines[0].split('|') if col.strip()]
            data_rows = []
            for line in table_lines[2:]:
                row_data = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(row_data) == len(headers):
                    data_rows.append(row_data)
            comparison_table = pd.DataFrame(data_rows, columns=headers)
        except Exception as e:
            comparison_table = comparison_response.content
    # Generate analysis report
    analysis_report = None
    if competitor_data:
        formatted_data = json.dumps(competitor_data, indent=2)
        report = analysis_agent.run(
            f"""Analyze the following competitor data in JSON format and identify market opportunities to improve my own company:
            {formatted_data}
            Tasks:
            1. Identify market gaps and opportunities based on competitor offerings
            2. Analyze competitor weaknesses that we can capitalize on
            3. Recommend unique features or capabilities we should develop
            4. Suggest pricing and positioning strategies to gain competitive advantage
            5. Outline specific growth opportunities in underserved market segments
            6. Provide actionable recommendations for product development and go-to-market strategy
            Focus on finding opportunities where we can differentiate and do better than competitors.
            Highlight any unmet customer needs or pain points we can address.
            """
        )
        analysis_report = report.content
    return {
        'competitor_urls': competitor_urls,
        'competitor_data': competitor_data,
        'comparison_table': comparison_table,
        'analysis_report': analysis_report
    } 