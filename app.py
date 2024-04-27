import os
import streamlit as st
from tarot_deck import TarotDeck
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize tarot deck
tarot_deck = TarotDeck()

# Streamlit app
def main():
    st.title("Tarot Card Reading App")
    user_question = st.text_input("Enter your question:")

    if st.button("Get Tarot Reading"):
        tarot_deck.shuffle_cards()
        drawn_cards = tarot_deck.draw_cards()
        reading = get_tarot_reading_v1(user_question, drawn_cards)
        st.write("Your Tarot Reading:")
        st.write(reading)

def get_tarot_reading_v1(user_question,drawn_cards):

    prompt = tarot_deck.generate_prompt(user_question, drawn_cards)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        #response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a tarot reader. Please interpret the cards drawn for the user."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    main()
