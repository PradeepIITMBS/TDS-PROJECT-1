import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Prompt for GitHub token at runtime
GITHUB_TOKEN = 'Your_Github_personal_token'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Helper function for a text-based progress bar
def progress_bar(current, total, bar_length=40):
    fraction = current / total
    arrow = '=' * int(fraction * bar_length)
    padding = '-' * (bar_length - len(arrow))
    end = '\n' if current == total else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction * 100)}%', end=end)

# Fetch users based in Singapore with over 100 followers
def fetch_users():
    print("Fetching users in Singapore with more than 100 followers...")
    url = 'https://api.github.com/search/users'
    params = {'q': 'location:Singapore followers:>100', 'per_page': 100}
    users = []
    page = 1

    while True:
        params['page'] = page
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            user_batch = response.json().get('items', [])
            users.extend(user_batch)
            print(f"Fetched page {page}: {len(user_batch)} users.")
            if len(user_batch) < 100:  # No more users available
                break
            page += 1
            time.sleep(1)  # Avoid hitting rate limits
        else:
            print(f"Error {response.status_code}: {response.json()}")
            break

    print(f"Total users fetched: {len(users)}")
    return users

# Fetch user details with error handling
def fetch_user_details(username):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch details for {username}. Error {response.status_code}: {response.json()}")
        return None

# Fetch repositories for a user, limited to the 500 most recent pushed
def fetch_user_repositories(username):
    url = f'https://api.github.com/users/{username}/repos'
    params = {'per_page': 100, 'sort': 'pushed'}
    repos = []
    page = 1

    while len(repos) < 500:
        response = requests.get(url, headers=HEADERS, params={**params, 'page': page})
        if response.status_code == 200:
            repo_batch = response.json()
            repos.extend(repo_batch)
            # Track progress of fetched repositories
            print(f"Fetched {len(repo_batch)} repositories for {username}. Total: {len(repos)}")
            if len(repo_batch) < 100:  # No more repos available
                break
            page += 1
            time.sleep(1)  # Avoid hitting rate limits
        else:
            print(f"Failed to fetch repos for {username}. Error {response.status_code}: {response.json()}")
            break

    return repos[:500]  # Limit to 500 repositories

# Clean company names
def clean_company_name(company):
    if company:
        company = company.strip()
        if company.startswith('@'):
            company = company[1:]
        return company.upper()
    return ''

# Convert values according to requirements
def format_value(value):
    if value is None:
        return ''
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    return value

# Write user data to CSV
def write_users_csv(users):
    with open('users.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'login', 'name', 'company', 'location', 'email', 'hireable',
            'bio', 'public_repos', 'followers', 'following', 'created_at'
        ])
        for user in users:
            writer.writerow([
                format_value(user['login']),
                format_value(user.get('name')),
                clean_company_name(user.get('company')),
                format_value(user.get('location')),
                format_value(user.get('email')),
                format_value(user.get('hireable')),
                format_value(user.get('bio')),
                format_value(user.get('public_repos')),
                format_value(user.get('followers')),
                format_value(user.get('following')),
                format_value(user.get('created_at'))
            ])
    print("User data written to users.csv.")

# Write repository data to CSV
def write_repositories_csv(repositories):
    with open('repositories.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'login', 'full_name', 'created_at', 'stargazers_count', 'watchers_count',
            'language', 'has_projects', 'has_wiki', 'license_name'
        ])
        for repo in repositories:
            writer.writerow([
                format_value(repo['owner']['login']),
                format_value(repo['full_name']),
                format_value(repo.get('created_at')),
                format_value(repo.get('stargazers_count')),
                format_value(repo.get('watchers_count')),
                format_value(repo.get('language')),
                format_value(repo.get('has_projects')),
                format_value(repo.get('has_wiki')),
                format_value(repo['license']['key'] if repo.get('license') else '')
            ])
    print("Repository data written to repositories.csv.")

# Main function to execute the data fetching and writing process
def main():
    users = []
    repositories = []
    user_list = fetch_users()
    total_users = len(user_list)

    # Using ThreadPoolExecutor for concurrent fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_user_details, user_info['login']): user_info for user_info in user_list}

        for i, future in enumerate(as_completed(futures), start=1):
            user_info = futures[future]
            try:
                user = future.result()
                if user:
                    users.append(user)
                    repos = fetch_user_repositories(user['login'])
                    repositories.extend(repos)
            except Exception as e:
                print(f"Error fetching data for {user_info['login']}: {e}")
            progress_bar(i, total_users)  # Update progress bar for each user processed

    # Write to CSV files
    write_users_csv(users)
    write_repositories_csv(repositories)
    print("Data fetching and writing complete.")

if __name__ == "__main__":
    main()
