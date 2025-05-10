import praw
import os
from psaw import PushshiftAPI
from replit import db
from prawcore.exceptions import NotFound

api = PushshiftAPI()

def send_message(item, reply_message):
    try:
        item.reply(body = reply_message)
        item.mark_read()
        return True
    except Exception as e:
        print(e)
        return False
    
def already_commented(comment_id):
  if comment_id in db.keys():
      return True

def user_exists(name):
  try:
    reddit.redditor(name).id
  except NotFound:
    return False
  return True


def count_words(user, word_list, limit=5000):
  gen = api.search_comments(author=user, limit=limit)

  info = {
      "total_comments": 0,
      "counts": [0] * len(word_list),
  }

  for comment in gen:
    for i, word in enumerate(word_list):
      if word.lower() in comment.body.lower():
        info["counts"][i] += 1
    info["total_comments"] += 1

  return info


client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
username = os.environ['username']
password = os.environ['password']

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent="<WordCountBot 1.0>")

for item in reddit.inbox.stream(skip_existing=False):
  print(item.subject)
  print()
  print(item.body)
  data = item.body.replace("\_", "_").split()

  if item.subject == "username mention":
    data.pop(0)

  print(data)

  if len(data) >= 2 and len(data) <= 6 and not already_commented(item.id):
    name = data[0]
    if user_exists(name):
      print(f"Running: {name} Words {data[1:]}")
      info = count_words(name, data[1:])
      print(info)

      reply_message = f"{name} sent {info['total_comments']} messages. Here are the word counts...\n"
      for index, word in enumerate(data[1:]):
          reply_message = reply_message + f"\n{word} {info['counts'][index]}\n"
      successful = send_message(item, reply_message)
      if successful:
          db[item.id] = item.author.name
          print(f"Message sent to {name} successfully")
      send_message(item, reply_message)
    else:
      print("User does not exist")