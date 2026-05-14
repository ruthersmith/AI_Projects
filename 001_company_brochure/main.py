"""
    This claqss creates a brochure for a company to be used for prospective clients, investors and potential recruits
    This brochure is based on the company name and their primary website
"""
import requests
import json
from bs4 import BeautifulSoup
from openai import OpenAI


class Brochure:
    def __init__(self):
        self.model = "llama3.2"
        self.openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
      # Standard headers to fetch a website
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }

    def fetch_website_links(self, url):
        """
        Return the links on the webiste at the given url
        I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
        Feel free to use a class and optimize it!
        """
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        links = [link.get("href") for link in soup.find_all("a")]
        return [link for link in links if link]
    

    def _get_link_system_prompt(self):
        return """
            You are provided with a list of links found on a webpage.
            You are able to decide which of the links would be most relevant to include in a brochure about the company,
            such as links to an About page, or a Company page, or Careers/Jobs pages.
            You should respond in JSON as in this example:

            {
                "links": [
                    {"type": "about page", "url": "https://full.url/goes/here/about"},
                    {"type": "careers page", "url": "https://another.full.url/careers"}
                ]
            }
        """
    
    def _get_links_user_prompt(self, url):
        user_prompt = f"""
            Here is the list of links on the website {url} -
            Please decide which of these are relevant web links for a brochure about the company, 
            respond with the full https URL in JSON format.
            Do not include Terms of Service, Privacy, email links.

            Links (some might be relative links):

            """
        links = self.fetch_website_links(url)
        user_prompt += "\n".join(links)
        return user_prompt
    
    def select_relevant_links(self, url):
        print(f"Selecting relevant links for {url}")
        response = self.openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_link_system_prompt()},
                {"role": "user", "content": self._get_links_user_prompt(url)}
            ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        links = json.loads(result)
        print(f"Found {len(links['links'])} relevant links")
        return links
    
    def fetch_website_contents(self, url):
        """
        Return the title and contents of the website at the given url;
        truncate to 2,000 characters as a sensible limit
        """
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""
        return (title + "\n\n" + text)[:2_000]
    

    def fetch_page_and_all_relevant_links(self,url):

        contents = self.fetch_website_contents(url)
        relevant_links = self.select_relevant_links(url)

        result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"

        for link in relevant_links['links']:
            try:
                result += f"\n\n### Link: {link['type']}\n"
                result += self.fetch_website_contents(link["url"])
            except Exception as e:
                print(e)
        return result
    

    def _get_brochure_system_prompt(self):
        return """
            You are an assistant that analyzes the contents of several relevant pages from a company website
            and creates a short, humorous, entertaining, witty brochure about the company for prospective customers, investors and recruits.
            Respond in markdown without code blocks.
            Include details of company culture, customers and careers/jobs if you have the information.
        """
    
    def _get_brochure_user_prompt(self,company_name, url):
        user_prompt = f"""
        You are looking at a company called: {company_name}
        Here are the contents of its landing page and other relevant pages;
        use this information to build a short brochure of the company in markdown without code blocks.\n\n
        """
        user_prompt += self.fetch_page_and_all_relevant_links(url)
        user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
        return user_prompt

    def generate_brochure(self, company_name = "", website_url = ""):
        
        response = self.openai.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": self._get_brochure_system_prompt()},
            {"role": "user", "content": self._get_brochure_user_prompt(company_name, website_url)}
        ],
    )
        result = response.choices[0].message.content

        print(result)



if __name__ == "__main__":
    brochure = Brochure()
    brochure.generate_brochure("Nehemiah Hope Center", "https://www.nehemiahhc.com")
    

