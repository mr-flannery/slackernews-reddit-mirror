from bs4 import BeautifulSoup
import urllib.request
import json
import praw
import time


slackernews_url = "https://slackernews.de"
subreddit_name = "slackernewsmirror"


def read_credentials():
    credentials = None
    with open("credentials.json", "r") as file:
        credentials = json.load(open("credentials.json"))
    return credentials


def init():
    return read_credentials()


def crawl_frontpage():
    parsed_doc = None
    with urllib.request.urlopen(slackernews_url) as response:
        parsed_doc = BeautifulSoup(response.read(), "html.parser")

    return parsed_doc


def parse_posts(parsed_doc):
    posts = []

    for post in parsed_doc.find_all("div", class_="post"):
        post = {
            "post_link": post.find("a", class_="post-link")['href'],
            "post_title": post.find("a", class_="post-link").get_text(),
            "comments_link": post.find("a", class_="post-comments-link")['href']
        }

        posts.append(post)

    return posts


def get_submissions_from_slackernews():
    return parse_posts(crawl_frontpage())


def get_subreddit_submissions(reddit):
    posts = []
    for submission in reddit.subreddit(subreddit_name).new():
        if submission.is_self:
            continue
        post = {
            "post_link": submission.url,
            "post_title": submission.title
        }
        posts.append(post)
    return posts

def is_submission_in_subreddit_submissions(submission, subreddit_submissions):
    for sr_submission in subreddit_submissions:
        if submission["post_link"] == sr_submission["post_link"] and submission["post_title"] == sr_submission["post_title"]:
            return True
    return False

def start_bot(credentials):
    submissions = get_submissions_from_slackernews()
    reddit = praw.Reddit(client_id=credentials["client_id"],
                         client_secret=credentials["client_secret"],
                         password=credentials["password"],
                         user_agent=credentials["user_agent"],
                         username=credentials["username"])
    subreddit_submissions = get_subreddit_submissions(reddit)
    new_submissions = [x for x in submissions if not is_submission_in_subreddit_submissions(x, subreddit_submissions)]

    for new_submission in new_submissions:
        reddit.subreddit(subreddit_name).submit(new_submission["post_title"], url=new_submission["post_link"]).reply("Discussion on Slackernews: " + str(slackernews_url + new_submission["comments_link"]))
        time.sleep(2)

    print("")

if __name__ == "__main__":
    credentials = init()
    start_bot(credentials)