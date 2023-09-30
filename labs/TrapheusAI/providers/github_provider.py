import os
import requests
import constants

"""
Searches csv data sets from github
"""
def search_code(query):
    github_params = {
        "q": f"{query} .csv in:path",
        "per_page": 5,
    }
    request_headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer " + os.environ.get("GITHUB_ACCESS_TOKEN"),
    }
    response = requests.get(constants.GITHUB_END_POINT + constants.GITHUB_SEARCH_PATH, params=github_params,
                            headers=request_headers)
    response.raise_for_status()
    data = response.json()
    return data

"""
Returns the formatted repository name, path and url
"""
def format_results(results):
    formatted_results = []
    for result in results:
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