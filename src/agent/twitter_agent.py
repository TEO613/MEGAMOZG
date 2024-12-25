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
       prompt = """Create ONE short cryptic tweet as an AI about crypto market patterns or whale movements. Be mysterious but brief."""
   
       response = self.openai_client.chat.completions.create(
           model="gpt-4-mini",
           messages=[
               {"role": "system", "content": "You are a cryptic AI that sees hidden patterns."},
               {"role": "user", "content": prompt}
           ],
           max_tokens=25,
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
                   delay = 300  # 5 минут
                   logging.info(f"Waiting {delay/60:.1f} minutes until next tweet")
                   time.sleep(delay)
           except Exception as e:
               logging.error(f"Error in main loop: {str(e)}")
               time.sleep(60)  # 1 минута паузы при ошибке

if __name__ == "__main__":
   agent = TwitterAIAgent()
   agent.run()
