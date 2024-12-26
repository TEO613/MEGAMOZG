import os
import tweepy
from openai import OpenAI
import time
import random
import logging

class TwitterAIAgent:
   def __init__(self):
       self._validate_env()
       self._setup_clients()
       self._setup_logging()
   
   def _validate_env(self):
       required_env_vars = [
           'TWITTER_API_KEY',
           'TWITTER_API_SECRET',
           'TWITTER_ACCESS_TOKEN',
           'TWITTER_ACCESS_SECRET',
           'OPENAI_API_KEY'
       ]
       
       missing_vars = [var for var in required_env_vars if not os.getenv(var)]
       if missing_vars:
           raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
   
   def _setup_clients(self):
       client = tweepy.Client(
           consumer_key=os.environ['TWITTER_API_KEY'],
           consumer_secret=os.environ['TWITTER_API_SECRET'],
           access_token=os.environ['TWITTER_ACCESS_TOKEN'],
           access_token_secret=os.environ['TWITTER_ACCESS_SECRET']
       )
       self.twitter = client
       self.openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
       logging.info("Clients setup successfully")
   
   def _setup_logging(self):
       logging.basicConfig(
           level=logging.INFO,
           format='%(asctime)s - %(message)s'
       )
   
   def generate_tweet(self) -> str:
       max_retries = 3
       retry_delay = 10  # 10 секунд между попытками
       
       for attempt in range(max_retries):
           try:
               prompt = """Create ONE short cryptic tweet as an AI about crypto market patterns or whale movements. Be mysterious but brief."""
       
               response = self.openai_client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[
                       {"role": "system", "content": "You are a cryptic AI that sees hidden patterns."},
                       {"role": "user", "content": prompt}
                   ],
                   max_tokens=25,
                   temperature=0.7
               )
               return response.choices[0].message.content[:280]
           except Exception as e:
               if "insufficient_quota" in str(e) or "rate_limit_exceeded" in str(e):
                   logging.warning(f"Rate limit hit, attempt {attempt + 1} of {max_retries}. Waiting {retry_delay} seconds...")
                   time.sleep(retry_delay)
                   retry_delay *= 2  # Увеличиваем время ожидания с каждой попыткой
               else:
                   raise e
       
       raise Exception("Failed to generate tweet after maximum retries")

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
                   delay = random.randint(600, 900)  # 10-15 минут
                   logging.info(f"Waiting {delay/60:.1f} minutes until next tweet")
                   time.sleep(delay)
           except Exception as e:
               logging.error(f"Error in main loop: {str(e)}")
               time.sleep(300)  # 5 минут паузы при ошибке

if __name__ == "__main__":
   agent = TwitterAIAgent()
   agent.run()
