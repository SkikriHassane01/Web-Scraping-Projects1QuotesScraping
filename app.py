import streamlit as st
import requests
from bs4 import BeautifulSoup
from random import choice
from time import sleep

BASE_URL = "https://quotes.toscrape.com"
TAGS = ['love', 'inspirational', 'life', 'humor', 'books']

@st.cache_data
def load_quotes():
    """
    Scrapes quotes for each tag and returns a list of quote dictionaries.
    Each dictionary contains 'tag', 'text', 'author', and 'bio_link'.
    """
    all_quotes = []
    for tag in TAGS:
        url = f"{BASE_URL}/tag/{tag}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            sleep(1)
        except Exception as e:
            st.warning(f"Error scraping {url}: {e}")
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all(class_="quote")
        for quote in quotes:
            all_quotes.append({
                "tag": tag,
                "text": quote.find(class_="text").get_text(),
                "author": quote.find(class_="author").get_text(),
                "bio_link": quote.find("a")["href"]
            })
        sleep(1)
    return all_quotes

def get_author_hint(quote):
    """
    Retrieves the author's birth details as a hint.
    """
    author_url = BASE_URL + quote['bio_link']
    try:
        res = requests.get(author_url, timeout=5)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        birth_date = soup.find(class_="author-born-date").get_text()
        birth_place = soup.find(class_="author-born-location").get_text()
        return f"Hint: The author was born on {birth_date} {birth_place}"
    except Exception as e:
        return "Hint: Unable to retrieve author's birth details."

def main():
    st.title("Quote Guessing Game")
    
    all_quotes = load_quotes()
    
    st.sidebar.header("Game Settings")
    selected_tag = st.sidebar.selectbox("Choose a tag", TAGS)
    
    # Filter quotes by the selected tag
    filtered_quotes = [q for q in all_quotes if q["tag"] == selected_tag]
    if not filtered_quotes:
        st.error("No quotes found for the selected tag.")
        return

   # Reset the quote when the tag changes
    if "previous_tag" not in st.session_state or st.session_state.previous_tag != selected_tag:
        st.session_state.random_quote = choice(filtered_quotes)
        st.session_state.remaining_guesses = 4
        st.session_state.guess = ""
        st.session_state.previous_tag = selected_tag  # Store current tag
    
    st.write(f"**Tag selected:** {selected_tag}")
    st.write("Guess the author of the following quote:")
    st.write(f"> {st.session_state.random_quote['text']}")
    
    guess_input = st.text_input("Your guess", st.session_state.guess)
    if guess_input:
        st.session_state.guess = guess_input

    if st.button("Submit Guess"):
        if st.session_state.guess.lower() == st.session_state.random_quote["author"].lower():
            st.success("CONGRATULATIONS!!! YOU GOT IT RIGHT")
            if st.button("Play Again"):
                st.session_state.random_quote = choice(filtered_quotes)
                st.session_state.remaining_guesses = 4
                st.session_state.guess = ""
        else:
            st.session_state.remaining_guesses -= 1
            if st.session_state.remaining_guesses > 0:
                hint = ""
                if st.session_state.remaining_guesses == 3:
                    hint = get_author_hint(st.session_state.random_quote)
                elif st.session_state.remaining_guesses == 2:
                    hint = f"Hint: The author's first two letters are: {st.session_state.random_quote['author'][:2]}"
                elif st.session_state.remaining_guesses == 1:
                    last_name = st.session_state.random_quote["author"].split(" ")[-1]
                    hint = f"Hint: The author's last name starts with: {last_name[0:2]}"
                st.info(f"Incorrect. Guesses remaining: {st.session_state.remaining_guesses}")
                st.info(hint)
            else:
                st.error(f"❌ Sorry, you ran out of guesses. The answer was: {st.session_state.random_quote['author']}")
                if st.button("Play Again"):
                    st.session_state.random_quote = choice(filtered_quotes)
                    st.session_state.remaining_guesses = 4
                    st.session_state.guess = ""

if __name__ == "__main__":
    main()
