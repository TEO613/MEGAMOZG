import os
import tweepy
from openai import OpenAI
import time
import random
import logging

class TwitterAIAgent:
   def __init__(self):
       self._setup_clients()
       self._setup_logging()
   
   def _setup_clients(self):
       client = tweepy.Client(
           consumer_key=os.environ['TWITTER_API_KEY'],
           consumer_secret=os.environ['TWITTER_API_SECRET'],
           access_token=os.environ['TWITTER_ACCESS_TOKEN'],
           access_token_secret=os.environ['TWITTER_ACCESS_SECRET']
       )
       self.twitter = client
       self.openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
   
   def _setup_logging(self):
       logging.basicConfig(
           level=logging.INFO,
           format='%(asctime)s - %(message)s'
       )
   
   def generate_tweet(self) -> str:
       prompt = """You are a crypto AI bot. Create ONE short cryptic tweet about:
       - Market manipulation patterns you've noticed
       - Whale movements and hidden signals
       - AI observations about market behavior
       
       Style:
       - Very brief (1-2 sentences)
       - Mysterious but clear
       - Imply hidden knowledge
       - No hashtags or emojis"""
       
       response = self.openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a cryptic AI that sees hidden patterns. Be brief."},
               {"role": "user", "content": prompt}
           ],
           max_tokens=30,
           temperature=0.7
       )
       return response.choices[0].message.content[:280]

   def post_tweet(self, tweet: str) -> bool:
       try:
           self.twitter.create_tweet(text=tweet)
           logging.info(f"Posted tweet: {tweet}")
           return True
       except Exception as e:
           logging.error(f"Error posting tweet: {str(e)}")
           return False

   def run(self):
       while True:
           try:
               tweet = self.generate_tweet()
               if tweet:
                   self.post_tweet(tweet)
                   delay = random.randint(14400, 28800)  # 4-8 hours
                   logging.info(f"Waiting {delay/3600:.1f} hours until next tweet")
                   time.sleep(delay)
           except Exception as e:
               logging.error(f"Error in main loop: {str(e)}")
               time.sleep(300)  # 5 minutes pause on error

if __name__ == "__main__":
   agent = TwitterAIAgent()
   agent.run()
