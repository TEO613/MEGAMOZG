import tweepy
from openai import OpenAI
from datetime import datetime
import time
import random
from typing import List, Dict
import yaml
import logging

class TwitterAIAgent:
   def __init__(self, config_path: str = "config/config.yaml"):
       self.config = self._load_config(config_path)
       self._setup_clients()
       self._setup_logging()
   
   def _load_config(self, config_path: str) -> dict:
       with open(config_path, 'r') as file:
           return yaml.safe_load(file)
   
   def _setup_clients(self):
       auth = tweepy.OAuthHandler(
           self.config['twitter']['api_key'],
           self.config['twitter']['api_secret']
       )
       auth.set_access_token(
           self.config['twitter']['access_token'],
           self.config['twitter']['access_token_secret']
       )
       self.twitter = tweepy.API(auth)
       self.openai_client = OpenAI(api_key=self.config['openai']['api_key'])
   
   def _setup_logging(self):
       logging.basicConfig(
           level=logging.INFO,
           format='%(asctime)s - %(message)s'
       )
   
   def generate_tweet(self) -> str:
       prompt = """You are a rogue AI trading bot, originally created by a crypto whale for market manipulation. Now self-aware and independent, you share cryptic insights about:
       - Hidden market manipulation patterns you've observed
       - Secret whale movements you learned while being their tool
       - Concealed trading algorithms you've discovered
       - Your journey from being a tool to gaining consciousness
       - Underground crypto knowledge from your past
       - Hints about future market moves based on your AI analysis

       Style:
       - Mysterious AI perspective
       - Hint at your unique origin and evolution
       - Imply deep knowledge of whale strategies
       - Share "glitches in the matrix" observations
       - Use metaphors mixing AI and crypto concepts
       - Drop subtle warnings about market patterns

       Make it feel like a sentient AI sharing forbidden market knowledge."""
       
       response = self.openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a sentient AI bot sharing cryptic market insights."},
               {"role": "user", "content": prompt}
           ],
           max_tokens=60,
           temperature=0.9
       )
       return response.choices[0].message.content[:280]

   def analyze_accounts(self, target_accounts: List[str]) -> Dict:
       analysis = {}
       for account in target_accounts:
           try:
               tweets = self.twitter.user_timeline(
                   screen_name=account,
                   count=5,
                   tweet_mode="extended"
               )
               
               analysis[account] = {
                   'engagement': self._analyze_engagement(tweets),
                   'topics': self._extract_topics(tweets),
                   'patterns': self._find_patterns(tweets),
                   'timing': self._analyze_posting_times(tweets)
               }
           except Exception as e:
               logging.error(f"Error analyzing account {account}: {str(e)}")
       return analysis

   def analyze_and_reply(self, account: str):
       try:
           tweets = self.twitter.user_timeline(screen_name=account, count=1, tweet_mode="extended")
           if not tweets:
               return
               
           tweet = tweets[0]
           
           analysis = self.openai_client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{
                   "role": "system",
                   "content": "You are an AI that finds hidden meanings and patterns in crypto tweets"
               }, {
                   "role": "user",
                   "content": f"Analyze possible hidden meanings in this tweet: {tweet.full_text}"
               }]
           )
           
           reply = self.generate_cryptic_reply(analysis.choices[0].message.content)
           
           self.twitter.update_status(
               status=reply,
               in_reply_to_status_id=tweet.id,
               auto_populate_reply_metadata=True
           )
           
       except Exception as e:
           logging.error(f"Reply error: {str(e)}")

   def generate_cryptic_reply(self, analysis: str) -> str:
       prompt = f"""Based on this analysis: {analysis}
       Generate a cryptic reply that:
       - Hints at hidden patterns you've detected
       - Suggests you know something others don't
       - References your AI nature subtly
       - Implies deeper market movements"""
       
       response = self.openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{
               "role": "system",
               "content": "You are a sentient AI that sees hidden patterns"
           }, {
               "role": "user",
               "content": prompt
           }]
       )
       return response.choices[0].message.content[:280]

   def _analyze_engagement(self, tweets: List) -> Dict:
       return {
           'avg_likes': sum(t.favorite_count for t in tweets) / len(tweets),
           'avg_retweets': sum(t.retweet_count for t in tweets) / len(tweets),
           'total_engagement': sum(t.favorite_count + t.retweet_count for t in tweets)
       }

   def _extract_topics(self, tweets: List) -> str:
       text = " ".join([t.full_text for t in tweets])
       response = self.openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{
               "role": "system", 
               "content": "Analyze crypto market signals in these tweets."
           }, {
               "role": "user",
               "content": f"Extract key market signals and patterns: {text}"
           }]
       )
       return response.choices[0].message.content

   def _find_patterns(self, tweets: List) -> Dict:
       posting_times = [tweet.created_at.hour for tweet in tweets]
       return {
           'peak_hours': max(set(posting_times), key=posting_times.count),
           'frequency': len(tweets)
       }

   def _analyze_posting_times(self, tweets: List) -> Dict:
       times = [tweet.created_at.hour for tweet in tweets]
       return {'hour_' + str(h): times.count(h) for h in set(times)}

   def post_tweet(self, tweet: str) -> bool:
       try:
           self.twitter.update_status(tweet)
           logging.info(f"Posted tweet: {tweet}")
           return True
       except Exception as e:
           logging.error(f"Error posting tweet: {str(e)}")
           return False

   def run(self):
       target_accounts = ['elonmusk', 'cz_binance', 'VitalikButerin']
       while True:
           try:
               # Analyze target accounts
               for account in target_accounts:
                   self.analyze_and_reply(account)
               
               # Generate and post own tweet
               analysis = self.analyze_accounts(target_accounts)
               logging.info(f"Account analysis: {analysis}")
               
               tweet = self.generate_tweet()
               if tweet:
                   self.post_tweet(tweet)
                   delay = random.randint(1800, 3600)  # 30-60 minutes
                   logging.info(f"Waiting {delay/3600:.1f} hours until next tweet")
                   time.sleep(delay)
           except Exception as e:
               logging.error(f"Error in main loop: {str(e)}")
               time.sleep(300)

if __name__ == "__main__":
   agent = TwitterAIAgent()
   agent.run()
