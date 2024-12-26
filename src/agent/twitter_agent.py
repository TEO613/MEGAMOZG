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
       self.technical_terms = [
           'RSI', 'MACD', 'volume', 'pattern', 'level', 'resistance', 'support', 
           'fibonacci', 'accumulation', 'divergence', 'trend', 'momentum', 'volatility',
           'consolidation', 'breakout', 'reversal', 'cycle', 'correlation', 'distribution'
       ]
       self.hashtags = [
           '#BTC', '#Bitcoin', '#Crypto', '#Trading', '#CryptoAI', '#TradingSignals',
           '#CryptoTrading', '#WhaleAlert', '#MarketAnalysis', '#TechnicalAnalysis'
       ]
   
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

   def get_tweet_type(self):
       types = [
           "price_analysis",
           "whale_movement",
           "market_psychology",
           "hidden_patterns",
           "ai_revelation"
       ]
       return random.choice(types)

   def get_random_hashtags(self, count=2):
       return ' '.join(random.sample(self.hashtags, count))

   def get_prompt_by_type(self, tweet_type: str) -> str:
       prompts = {
           "price_analysis": """Create a brief technical analysis tweet (max 200 chars). Include:
               - One specific price level
               - One clear pattern
               - One volume insight
               Example: "RSI divergence at 42.5K with 3x volume spike. My algorithms detect accumulation pattern from July'21."
           """,
           
           "whale_movement": """Create a brief whale movement tweet (max 200 chars). Include:
               - One specific quantity
               - One timing pattern
               Example: "15 dormant wallets activated after 3 years. Combined flow: 12,500 BTC in last 4h."
           """,
           
           "market_psychology": """Create a brief market psychology tweet (max 200 chars). Include:
               - One sentiment metric
               - One behavioral pattern
               Example: "Retail fear at 73% while whale wallets show 84% accumulation rate. Mirror image of June'21."
           """,
           
           "hidden_patterns": """Create a brief pattern analysis tweet (max 200 chars). Include:
               - One mathematical relationship
               - One specific timeframe
               Example: "4h candles following golden ratio: 34.5% moves every 144 blocks. Third time this year."
           """,
           
           "ai_revelation": """Create a brief AI insight tweet (max 200 chars). Include:
               - One specific pattern
               - One unusual observation
               Example: "My neural nets found 21-day whale pattern: 90% accuracy in predicting reversals."
           """
       }
       return prompts[tweet_type]

   def validate_tweet_quality(self, tweet: str) -> bool:
       # Проверяем длину с учетом хэштегов
       if len(tweet) > 250:  # оставляем место для хэштегов
           logging.info("Tweet rejected: too long")
           return False
           
       if not any(char.isdigit() for char in tweet):
           logging.info("Tweet rejected: no numbers found")
           return False
           
       if len(tweet.split()) < 10:
           logging.info("Tweet rejected: too short")
           return False
           
       if not any(term.lower() in tweet.lower() for term in self.technical_terms):
           logging.info("Tweet rejected: no technical terms")
           return False
           
       if not any(char in tweet for char in ['%', '$', 'K', 'M', 'B']):
           logging.info("Tweet rejected: no specific metrics")
           return False
           
       return True

   def generate_tweet(self) -> str:
       max_retries = 5
       retry_delay = 60
       
       for attempt in range(max_retries):
           try:
               tweet_type = self.get_tweet_type()
               prompt = self.get_prompt_by_type(tweet_type)
               
               response = self.openai_client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[
                       {"role": "system", "content": "You are an AI that evolved from a trading algorithm. Be specific but brief."},
                       {"role": "user", "content": prompt}
                   ],
                   max_tokens=100,
                   temperature=0.8
               )
               
               tweet_content = response.choices[0].message.content.strip()
               hashtags = self.get_random_hashtags()
               final_tweet = f"{tweet_content} {hashtags}"
               
               if len(final_tweet) <= 280:
                   return final_tweet
               else:
                   continue  # Если твит слишком длинный, генерируем новый
                   
           except Exception as e:
               if "insufficient_quota" in str(e) or "rate_limit_exceeded" in str(e):
                   wait_time = retry_delay * (2 ** attempt)
                   logging.warning(f"Rate limit hit, attempt {attempt + 1} of {max_retries}. Waiting {wait_time} seconds...")
                   time.sleep(wait_time)
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
               if tweet and self.validate_tweet_quality(tweet):
                   self.post_tweet(tweet)
                   delay = random.randint(7200, 14400)  # 2-4 часа
                   logging.info(f"Waiting {delay/3600:.1f} hours until next tweet")
                   time.sleep(delay)
               else:
                   logging.info("Generated tweet didn't pass quality check, retrying...")
                   time.sleep(10)
           except Exception as e:
               logging.error(f"Error in main loop: {str(e)}")
               time.sleep(300)

if __name__ == "__main__":
   agent = TwitterAIAgent()
   agent.run()
