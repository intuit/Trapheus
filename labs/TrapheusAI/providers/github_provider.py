import os
import requests
import constants
from baseProvider import IBaseProvider

"""
Searches csv data sets from github
"""

class Github(IBaseProvider):

    def __init__(self, query: str):
        self.query = query

    def query(self):
        request_params = {
            "q": f"{query} .csv in:path",
            "per_page": 5,
        }
        request_headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "Bearer " + os.environ.get("GITHUB_ACCESS_TOKEN"),
        }
        return request_headers, request_params

    def query(self):
        request_headers, request_params = self.query()
        response = requests.get(constants.GITHUB_END_POINT + constants.GITHUB_SEARCH_PATH, params=request_params,
                                headers=request_headers)
        response.raise_for_status()
        response_body = response.json()
        return response_body

    def extract_data(self):
        formatted_results = []
        data = self.query()
        for result in data:
            repo = result["repository"]["full_name"]
            repo_path = result["path"]
            repo_url = result["html_url"].replace("/blob/", "/raw/")

        #defer the response body using streamand inspect only headers
        response = requests.get(repo_url, stream=True)
        if response.status_code == 200:
            lines_count = 0
            content = ''
            # Retreive the first three items
            for line in response.iter_lines():
                if lines_count >= 3:
                    break
                content += line.decode('utf-8', errors="ignore") + "\n"
                lines_count += 1
        else:
            content = ""

        result = {
            "repo": repo,
            "subpath": repo_path,
            "fullurl": repo_url,
            "text": content,
        }
        formatted_results.append(result)
        return formatted_results

