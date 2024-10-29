# TDS-PROJECT-1
# GitHub Users in Singapore with Over 100 Followers

### Key Insights

- I used the GitHub API to scrape users located in Singapore with over 100 followers, as well as their repositories.
- The most interesting insight was that **JavaScript** and **Python** were the most commonly used programming languages among these users, however **TypeScript** is having high trend.
- Developers looking to gain visibility should consider creating more public repositories in trending/common language to increase their followers.

### Process

1. Fetched GitHub users located in Singapore with over 100 followers using the GitHub API.
2. For each user, fetched up to 500 of their most recently pushed repositories.
3. Cleaned the data and saved it into two CSV files: `users.csv` (user details) and `repositories.csv` (repository details).

### Files in This Repository

- **fetch_data.py**: Contain python code to extract data while tracking progress of fetched data. 
- **users.csv**: Contains details of GitHub users in Singapore with over 100 followers.
- **repositories.csv**: Contains details of the public repositories of these users.
- **trend.png**: Contains trend chart of top 10 languages of these users.
- **trend.csv**: Contains trend table of top 10 languages of these users.
