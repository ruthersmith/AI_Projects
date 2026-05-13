"""
    This claqss creates a brochure for a company to be used for prospective clients, investors and potential recruits
    This brochure is based on the company name and their primary website
"""


class Brochure:
    def __init__(self, company_name, website):
        self.company_name = company_name
        self.website = website


if __name__ == "__main__":
    brochure = Brochure("Google", "www.google.com")
    print(brochure.company_name)
    print(brochure.website)