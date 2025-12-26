import openai
from dotenv import load_dotenv, find_dotenv
import yfinance as yf

_ = load_dotenv(find_dotenv())

cliente = openai.Client()
