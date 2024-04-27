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

    mode = st.radio("Choose Mode", ('Classic', 'Fun'))

    if mode == 'Classic':
        user_question = st.text_input("Enter your question:")
        if st.button("Get Tarot Reading"):
            tarot_deck.shuffle_cards()
            drawn_cards = tarot_deck.draw_cards()
            reading = get_tarot_reading_v1(user_question, drawn_cards)
            st.write("Your Tarot Reading:")
            st.write(reading)

    elif mode == 'Fun':
        if 'stage' not in st.session_state:
            st.session_state['stage'] = 'keyword_input'
        
        if st.session_state['stage'] == 'keyword_input':
            keyword = st.text_input("Type a keyword:")
            if st.button("Submit"):
                obj_set = FunMode.generate_object_sets(keyword)
                st.session_state['obj_set'] = obj_set
                image = FunMode.generate_set_image(obj_set)
                st.session_state['image'] = image
                st.session_state['stage'] = 'select_set'
                st.experimental_rerun()

        elif st.session_state['stage'] == 'select_set':
            st.image(st.session_state['image'], caption="Choose one of the following sets:")
            sets_list = st.session_state['obj_set'].split('\n')
            option = st.radio("Which set of objects would you like to pick?", sets_list)
            if st.button("Choose Set"):
                chosen_set = option.split('. ')[1]  # Removes the numbering like "1. "
                st.session_state['chosen_set'] = chosen_set
                st.session_state['stage'] = 'final_question'
        
        if st.session_state['stage'] == 'final_question':
            user_question = st.text_input("Now, type your question:")
            if st.button("Get Tarot Reading"):
                symbolism_list = FunMode.set_symbolism(st.session_state['chosen_set']).split(':')
                keywords = symbolism_list[0]
                st.write(symbolism_list[1])
                st.write("Your keywords are:", keywords)
                reading = FunMode.get_tarot_reading_fun(keywords, user_question)
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

class FunMode:
    def generate_object_sets(keyword):

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "Based on the keyword, give three sets of two whimsical objects. "
                                            + "The keyword and the object should be correlated but loosely."
                                            + "For each set, the objects come from two of the following categories:"
                                            + "mythological, jewerly, trivial and mundane, random medival thing, cuisine."
                                            + "Format: 1. object names separated with comma\n2. object names separated with comma\n3. object names separated with comma."
                                            + "Always omit the category names."},
                {"role": "user", "content": "The keyword is " + keyword}
            ]
        )
        return response.choices[0].message.content

    def generate_set_image(obj_set):
        response = client.images.generate(
          model="dall-e-3",
          prompt="Three set of objects, one set per card separated: "+ obj_set +
                "Resemble the art style of the PLAIN, MUNDANE OLD Waite Rider Tarot card."
                + "Each card must be same size.",
          size="1792x1024",
          quality="standard",
          n=1,
        )

        return response.data[0].url

    def set_symbolism(chosen_set):

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Give four keywords about the symbolism associated to a set of objects user chose"                                        + "Make sure to give two positive ones and two negative ones."
                                            + "Format: keywords_separated_by_commas:concise_explanation"},
                {"role": "user", "content": "The set of object is " + chosen_set}
            ]
        )
        return response.choices[0].message.content

    def get_tarot_reading_fun(keywords,user_question):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a tarot reader. Given four keywords and one user question, you draw out 1 card."
                                            + "This card should be correlated to the keywords but loosely."
                                            + "Detailed explain the face of this card. Explain each individuals and their meanings."
                                            + "Then answer user's question, with correspondence to symbolism of the card."
                                            + "The answer doesn't have to always be positive."
                                            + "Format: Card Name: [content]\n Individuals and their symbolisms: [content]\n Answer to your question: [content]"},
                {"role": "user", "content": "The keyword is " + keywords + "User question is " + user_question }
            ]
        )
        return response.choices[0].message.content
      



if __name__ == "__main__":
    main()
