# import modules
import requests
from csv import writer
from bs4 import BeautifulSoup
from random import choice
from time import sleep

Quotes = {} # list to store scraped data(all the tags)
all_quotes = [] # this will hold all the information about the quote(tag, text, author) in a dict
base_url = "https://quotes.toscrape.com"

# list of tags that the user can chose + /tag/
tags = ['love','inspirational','life','humor','books']

for i, tag in enumerate(tags):
    url = f"{base_url}/tag/{tag}"
    try:
        print(f"[{i+1}/{len(tags)}] Scraping: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        print(f"Successfully scraped: {url}\n")
        sleep(1)
    except Exception as e:
        print(f"the url that you add is not valid \nraise this exception:{e}")
        exit()
    soup = BeautifulSoup(response.text,"html.parser")
    Quotes = soup.find_all(class_="quote")
    for quote in Quotes:
        all_quotes.append(
            
            {
                "tag": tag,
                "text": quote.find(class_="text").get_text(),
                "author": quote.find(class_="author").get_text(),
                "bio-link": quote.find("a")["href"]
            }
        )
    sleep(1)
    

print(f"{'_' * 30}")
for tag in tags:
    print(f"{'_' * 12}{tag}{'_' * 12}")
print(f"{'_' * 30}")

c = input("chose a tag from the list above\n").strip().lower()

# Filter quotes by the selected tag
filtered_quotes = [q for q in all_quotes if q["tag"] == c]

remaining_guesses = 4
# Display a random quote from the selected tag

random_quote = choice(filtered_quotes)
print(f"\n📝 Quote: {random_quote['text']}")
guess = ''
while guess.lower() != random_quote["author"].lower() and remaining_guesses > 0:
    guess = input(f"Who said this quote? Guesses remaining {remaining_guesses}")
    
    if guess == random_quote["author"]:
        print("CONGRATULATIONS!!! YOU GOT IT RIGHT")
        break
    remaining_guesses -= 1
    
    if remaining_guesses == 3:
        url = f"{base_url}/author/{random_quote['author']}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        birth_date = soup.find(class_="author-born-date").get_text()
        birth_place = soup.find(class_="author-born-location").get_text()
        print(f"Here's a hint: The author was born on {birth_date}{birth_place}")
     
    elif remaining_guesses == 2:
        print(
            f"Here's a hint: 👤The author's first name starts with: {random_quote['author'][0:2]}")
     
    elif remaining_guesses == 1:
        last_initial = random_quote["author"].split(" ")[1][0:2]
        print(
            f"Here's a hint: 👤The author's last name starts with: {last_initial}")
     
    else:
        print(
            f"❌Sorry, you ran out of guesses. The answer was {random_quote['author']}")


