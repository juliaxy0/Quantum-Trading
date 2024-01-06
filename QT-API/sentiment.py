# 1. Install and Import Baseline Dependencies
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
from bs4 import BeautifulSoup
import requests
from transformers import pipeline
import pandas as pd
import os

class sentimentAnalysisClass:

    def __init__(self,crypto):
        # Setup Model
        self.model_name = "human-centered-summarization/financial-summarization-pegasus"
        self.tokenizer = PegasusTokenizer.from_pretrained(self.model_name)
        self.model = PegasusForConditionalGeneration.from_pretrained(self.model_name)
        self.crypto = crypto
        
    def search_for_stock_news_links(self,ticker):
        search_url = 'https://cryptonews.net/?q={}&rubricId=-1&location=title&type=any&time=past_day'.format(ticker) 
        r = requests.get(search_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        atags = soup.find_all('a', attrs ={'class': 'title'})
        hrefs = [link['href'] for link in atags]
        return hrefs

    def scrape_and_process(self,URLs):
        ARTICLES = []
        for url in URLs:
            full_url = 'https://cryptonews.net'+ url
            r = requests.get(full_url)
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.find_all('p')
            text = [res.text for res in results]
            words = ' '.join(text).split(' ')[:350]
            ARTICLE = ' '.join(words)
            ARTICLES.append(ARTICLE)
        return ARTICLES

    def summarize(self,articles):
        summaries = []
        for article in articles:
            # Split the article into chunks of maximum sequence length
            chunk_size = 512
            chunks = [article[i:i+chunk_size] for i in range(0, len(article), chunk_size)]

            # Generate summaries for each chunk
            chunk_summaries = []
            for chunk in chunks:
                # Tokenize the chunk
                input_ids = self.tokenizer.encode(chunk, return_tensors="pt")

                # Generate summary
                output = self.model.generate(input_ids, max_length=55, num_beams=5, early_stopping=True)
                summary = self.tokenizer.decode(output[0], skip_special_tokens=True)
                chunk_summaries.append(summary)

            # Concatenate the summaries for all chunks
            summaries.append(" ".join(chunk_summaries))

        return summaries

    def create_output_array(self, crypto, summaries, scores, urls):
        output = []
        for counter in range(len(summaries)):
            output_this = [
                            crypto, 
                            summaries[counter], 
                            scores[counter]['label'], 
                            scores[counter]['score'], 
                            'https://cryptonews.net'+ urls[counter]
                        ]
            output.append(output_this)
        return output

    def analyse(self):

        # Search for Stock News using Google and Yahoo Finance
        urls = self.search_for_stock_news_links(self.crypto)

        # Search and Scrape Cleaned URLs
        articles = self.scrape_and_process(urls)

        # Summarise all Articles
        summaries = self.summarize(articles)

        # Create the sentiment analysis pipeline
        sentiment = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
        scores = sentiment(summaries)
        
        # Exporting Results
        final_output = self.create_output_array(self.crypto, summaries, scores, urls)

        # Create DataFrame without the first row
        df = pd.DataFrame(final_output[1:], columns=final_output[0])

        csv_file_path = 'E:/QuantumTrading/QT-API/sentimentData/{}.csv'.format(self.crypto)

        # Check if the file exists
        if not os.path.isfile(csv_file_path):
            # If the file doesn't exist, create it with the specified header
            df.to_csv(csv_file_path, index=False, header=['Ticker', 'Summary', 'Sentiment', 'Sentiment Score', 'URL'])
        else:
            # If the file exists, replace its content with the new DataFrame
            df.to_csv(csv_file_path, mode='w', index=False, header=['Ticker', 'Summary', 'Sentiment', 'Sentiment Score', 'URL'])