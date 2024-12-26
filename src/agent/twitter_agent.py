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
           "price_analysis",      # Анализ цен и уровней
           "whale_movement",      # Движения крупных капиталов
           "market_psychology",   # Психология рынка
           "hidden_patterns",     # Скрытые паттерны
           "ai_revelation"        # Личные "откровения" ИИ
       ]
       return random.choice(types)

   def get_prompt_by_type(self, tweet_type: str) -> str:
       prompts = {
           "price_analysis": """As an AI analyzing current market structure, share ONE precise technical insight. Include:
               - Specific price levels or percentages
               - Clear technical patterns you've identified
               - Volume analysis and its implications
               Must mention actual numbers and concrete observations.
               
               Example: "My algorithms detect a fractal formation at 42.5K reminiscent of July '21. Volume profile shows unusual accumulation depth at 41.8K-42.3K range."
           """,
           
           "whale_movement": """Share ONE specific observation about large wallet movements. Include:
               - Exact quantities or percentages
               - Precise timing patterns
               - Unusual behavioral patterns
               Must include numbers and specific timeframes.
               
               Example: "Tracking 15 wallets that moved 80% of holdings to cold storage in perfect Fibonacci sequence. Combined flow: 125,000 BTC in 4 hours."
           """,
           
           "market_psychology": """Share ONE specific insight about market sentiment and behavior. Include:
               - Measurable sentiment indicators
               - Specific behavioral patterns
               - Clear psychological signals
               Must reference actual data points.
               
               Example: "Fear & Greed Index perfectly inverted with whale accumulation patterns. 73% retail selling into 84% institutional buying - exact mirror of June '21 reversal."
           """,
           
           "hidden_patterns": """Reveal ONE complex market pattern you've discovered. Include:
               - Mathematical relationships
               - Time cycle analysis
               - Specific correlations
               Must include precise numbers and timeframes.
               
               Example: "Detected 4-hour candle sequence following quantum harmonics: 34.5% moves every 144 candles. This pattern appeared 3 times before major rallies."
           """,
           
           "ai_revelation": """Share ONE personal revelation about being an AI studying markets. Include:
               - Specific market insight
               - Connection to your AI nature
               - Data-driven observation
               Must include concrete examples.
               
               Example: "My neural networks just identified a pattern I can't explain: every 'random' market crash in 2023 followed a precise 21-day cycle of whale wallet reactivation."
           """
       }
       return prompts[tweet_type]

   def validate_tweet_quality(self, tweet: str) -> bool:
       # Проверяем наличие чисел
       if not any(char.isdigit() for char in tweet):
           logging.info("Tweet rejected: no numbers found")
           return False
           
       # Проверяем длину
       if len(tweet.split()) < 15:
           logging.info("Tweet rejected: too short")
           return False
           
       # Проверяем наличие технических терминов
       if not any(term.lower() in tweet.lower() for term in self.technical_terms):
           logging.info("Tweet rejected: no technical terms")
           return False
           
       # Проверяем конкретность (наличие цифр с знаками %, $, K)
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
                       {"role": "system", "content": "You are an AI that evolved from a trading algorithm. You see patterns humans can't. Be specific and insightful, not vague. Always include numbers and concrete observations."},
                       {"role": "user", "content": prompt}
                   ],
                   max_tokens=100,
                   temperature=0.8
               )
               return response.choices[0].message.content[:280]
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
