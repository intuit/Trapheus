import os
import requests
import constants
import streamlit as streamlit
from providers.baseProvider import IBaseProvider

"""
Searches csv data sets from github
"""

class Github(IBaseProvider):

    def connect(self, input: str):
        request_params = {
            "q": f"{input} .csv in:path",
            "per_page": 5,
        }
        request_headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "Bearer " +  streamlit.secrets["GITHUB_ACCESS_TOKEN"],
        }
        return request_headers, request_params


    @streamlit.cache_data(ttl=constants.TTL)
    def query(_self, input: str):
        request_headers, request_params = _self.connect(input)
        response = requests.get(constants.GITHUB_END_POINT + constants.GITHUB_SEARCH_PATH, params=request_params,
                                headers=request_headers)
        response.raise_for_status()
        response_body = response.json()
        return response_body

    @streamlit.cache_data(ttl=constants.TTL)
    def extract_data(_self, input: str):
        formatted_results = []
        data = _self.query(input).get("items", [])
        for item in data:
            repo = item["repository"]["full_name"]
            repo_path = item["path"]
            repo_url = item["html_url"].replace("/blob/", "/raw/")

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

