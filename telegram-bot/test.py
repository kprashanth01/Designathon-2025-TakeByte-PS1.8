# Add to imports section
import wikipediaapi
import re

# Initialize Wikipedia API with proper user agent
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='FactCheckerBot/1.0 (your-email@example.com)'  # Replace with your email
)

# Modify the DuckDuckGo search function to find Wikipedia articles
async def search_duckduckgo_wiki(query):
    """Search for Wikipedia articles using DuckDuckGo"""
    try:
        print(f"Searching DuckDuckGo for Wikipedia articles about: {query}")
        search_query = urllib.parse.quote_plus(f"{query} site:wikipedia.org")
        
        url = f"https://html.duckduckgo.com/html/?q={search_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"DuckDuckGo search failed: {response.status_code}")
            return None
            
        # Parse HTML response
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract Wikipedia URLs
        results = soup.select('.result__a')
        wiki_urls = []
        
        for result in results[:5]:  # Check top 5 results
            href = result.get('href', '')
            if 'wikipedia.org/wiki/' in href:
                # Extract the article title from URL
                title = href.split('/wiki/')[-1]
                wiki_urls.append(title)
                
        if wiki_urls:
            # Get the first matching Wikipedia article
            for title in wiki_urls:
                page = wiki_wiki.page(title)
                if page.exists():
                    return page.url
        
        return None
    except Exception as e:
        print(f"Error in DuckDuckGo Wikipedia search: {str(e)}")
        traceback.print_exc()
        return None

# Modify the scrape_articles function to handle Wikipedia articles
async def scrape_wiki_article(url):
    """Scrape Wikipedia article using Firecrawl"""
    try:
        if not FIRECRAWL_API_KEY:
            print("Firecrawl API key is not set. Skipping web scraping.")
            return None
            
        print(f"Scraping Wikipedia article: {url}")
        
        scrape_result = firecrawl_client.scrape_url(
            url,
            params={
                'formats': ['markdown', 'html'],
                'timeout': 20000
            }
        )
        
        if scrape_result and "data" in scrape_result:
            # Try to get content from markdown first
            if scrape_result["data"].get("markdown"):
                content = scrape_result["data"]["markdown"]
            # Fall back to HTML if markdown not available
            elif scrape_result["data"].get("html"):
                soup = BeautifulSoup(scrape_result["data"]["html"], 'html.parser')
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                    element.extract()
                content = soup.get_text(separator='\n')
            else:
                return None
                
            # Clean up the content
            content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
            content = content[:5000]  # Limit length
            
            return f"Wikipedia Article:\n\nSource: {url}\n\n{content}"
            
        return None
    except Exception as e:
        print(f"Error scraping Wikipedia article: {str(e)}")
        traceback.print_exc()
        return None

# Modify the handle_message function's else block