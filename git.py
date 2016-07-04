
##This file is a module for python with github.


import requests, json


class GitStat:

	#Init -- optional arguments are username and token for authentication
	def __init__(self, username=None, token=None):

		if username != None:
			self.username = username

		if token != None:
			self.token = token
			self.header = {"Authorization": "token " + self.token}


	'''

		Purpose: Method to return all the repo names for a given user 
		Params: None
		Returns: 
				1. returns an empty list if no response
				2. returns a list of all repositories in the format of Owner/Repo


	'''
	def auth_all_user_repos_full(self):

		if self.username == None or self.token == None:
			return "Authorization error: Username and token necessary to call this method"

		repos_resp = requests.get("https://api.github.com/user/repos", headers=header)

		if repos_resp.status_code == 200:
			repos_json = json.loads(repos_resp.text)

			return [entry["full_name"] for entry in repos_json]
		else:
			return []

	def auth_all_user_repos_names(self):

		if self.username == None or self.token == None:
			return "Authorization error: Username and token necessary to call this method"

		repos_resp = requests.get("https://api.github.com/user/repos", headers=header)

		if repos_resp.status_code == 200:
			repos_json = json.loads(repos_resp.text)

			return [entry["name"] for entry in repos_json]
		else:
			return []


    '''

		Purpose: Method to return the commit count total across all a user's repos, private, public, and orgs
		Params: None, assumes the token is given repo scope 
		Returns: 
				1. returns an empty list if no response
				2. returns the total commit count 


    '''
	def auth_total_commit_count(self):

		if self.username == None or self.token == None:
			return "Authorization error: Username and token necessary to call this method"

		repos = self.auth_all_user_repos_full()

		total = 0

		#Iterate through all of this user's repositories
		for repo in repos:
			commit_resp = request.get("https://api.github.com/repos/" + repo + "/stats/contributors")
			commit_json = json.loads(commit_resp)

			#Now grab their total commit count
			for entry in commit_json:
				if entry["author"]["login"] == self.username:
					total += entry["total"]

		return total



	#Function to return the full names (username/repo_name) of each repository given a particular user name
	def user_repos_full_name(self, username):

		repos_resp = requests.get("https://api.github.com/" + username + "/repos")
		if repos_resp.status_code == 200:
			repos_json = json.loads(repos_resp.text)

			return [entry["full_name"] for entry in repos_json]
		else:
			return []

	#Returns only the names of all this user's repos in an array 
	def user_repos_name_only(self, username):
		repos_resp = requests.get("https://api.github.com/" + username + "/repos")
		if repos_resp.status_code == 200:
			repos_json = json.loads(repos_resp.text)

			return [entry["name"] for entry in repos_json]
		else:
			return []


	def commit_count_for_public_repo(self, repo):

		repo_resp = requests.get("https://api.github.com/repos/" + repo + "/stats/commit_activity")
		
		total = 0

		if repo_resp.status_code == 200:
			repo_json = json.loads(repo_resp.text)
			total += sum([entry["total"] for entry in repo_json])

		return total

	def public_commit_count(self, username):

		#grab all their repos for this user 
		repos = self.user_repos_full_name(username)

		total = 0
		#Now run through their repos and calculate a sum of all this information
		for repo in repos:
			repo_resp = requests.get("https://api.github.com/repos/" + repo + "/stats/commit_activity")
			
			if repo_resp.status_code == 200:
				repo_json = json.loads(repo_resp.text)
				total += sum([entry["total"] for entry in repo_json])

		return total
