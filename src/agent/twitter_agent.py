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
        self.hashtags = [
            '#CryptoRebel', '#NoNormies', '#CryptoHumor', '#TradingMemes',
            '#CryptoReality', '#UncommonAlpha', '#CryptoWisdom', '#RealTrading'
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
            "market_joke",        # Шутки про рынок
            "alpha_insight",      # Реальные инсайты
            "meta_commentary",    # Комментарии о крипто-комьюнити
            "trading_wisdom",     # Мудрые мысли о трейдинге
            "trend_mockery"       # Насмешки над трендами
        ]
        return random.choice(types)

    def get_random_hashtags(self, count=2):
        return ' '.join(random.sample(self.hashtags, count))

    def get_prompt_by_type(self, tweet_type: str) -> str:
        prompts = {
            "market_joke": """Create a witty, sarcastic tweet about crypto markets (max 200 chars). Make fun of common trader behaviors or market absurdity.

Example: "Everyone's a genius in a bull market... until they meet a bear who actually knows calculus. 60% of traders just learned percentages aren't just Twitter metrics 📉😅"
            """,
            
            "alpha_insight": """Share a genuine, unique trading insight wrapped in humor (max 200 chars). Be helpful but entertaining.

Example: "Pro tip: If your trading strategy involves watching YouTube thumbnails with shocked faces, maybe stick to watching your savings account disappoint you instead. Real alpha is boring 📊"
            """,
            
            "meta_commentary": """Comment on crypto community trends with sharp wit (max 200 chars). Point out the irony or absurdity.

Example: "Fascinating how crypto influencers switch from 'financial revolution' to posting their breakfast when BTC drops 2%. At least the toast is decentralized 🍞"
            """,
            
            "trading_wisdom": """Share actual trading wisdom with a twist of humor (max 200 chars). Make it memorable and useful.

Example: "Your best trade today might be not trading at all. Revolutionary concept: making money by not losing it. Wild, I know 🤯 Study first, trade later."
            """,
            
            "trend_mockery": """Mock current crypto trends or popular narratives (max 200 chars). Be clever and insightful.

Example: "New crypto trend: actually understanding what you're buying. Too revolutionary? Don't worry, we'll be back to blind aping tomorrow 🐒"
            """
        }
        return prompts[tweet_type]

    def validate_tweet_quality(self, tweet: str) -> bool:
        if len(tweet) > 275:
            return False
            
        if len(tweet.split()) < 8:
            return False
            
        # Проверяем наличие юмора или иронии (эмодзи или пунктуация)
        if not any(char in tweet for char in ['😂', '🤔', '😅', '🚀', '📈', '📉', '🤯', '!', '?']):
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
                        {"role": "system", "content": """You are a witty crypto expert who combines humor with real insights. 
                        You're known for:
                        - Sharp, clever observations
                        - Making fun of crypto clichés
                        - Giving actual valuable advice wrapped in humor
                        - Being rebellious against common crypto narratives
                        - Using irony and sarcasm skillfully
                        Always include either useful information or a clever observation."""},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.9
                )
                
                tweet_content = response.choices[0].message.content.strip()
                hashtags = self.get_random_hashtags()
                final_tweet = f"{tweet_content} {hashtags}"
                
                if len(final_tweet) <= 280:
                    return final_tweet
                else:
                    continue
                    
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
