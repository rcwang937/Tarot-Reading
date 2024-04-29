import os
import streamlit as st
from tarot_deck import TarotDeck
from openai import OpenAI
from dotenv import load_dotenv

import base64
import time
from PIL import Image

load_dotenv()


with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

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
        if user_question:
            tarot_deck = TarotDeck()
            tarot_deck.shuffle_cards()

            # st.button("Shuffle Cards")

            # # Simulate card shuffling animation
            # if st.button("Stop Shuffling"):
            #     pass

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Shuffle Cards"):
                    st.session_state['shuffling'] = True
            
            with col2:
                if st.session_state.get('shuffling', False):
                    if st.button("Stop Shuffling"):
                        st.session_state['shuffling'] = False

            if st.session_state.get('shuffling', False):
                st.write("Card shuffling...")

            # selected_indices = st.multiselect("Choose your cards:", options=range(78), format_func=lambda x: "Card " + str(x+1))


            # if len(selected_indices) == 3:
            #     drawn_cards = [tarot_deck.shuffled_deck[i] for i in selected_indices]
            #     images = []
            #     captions = []
            #     for card in drawn_cards:
            #         image_path = os.path.join( card[2])
            #         img = Image.open(image_path)
            #         if card[1] == 'downward':
            #             img = img.rotate(180)
            #         images.append(img)
            #         captions.append(card[0])

            #     st.image(images, width=200, caption=captions)
                
            selected_indices = st.multiselect("Choose your cards:", options=range(78), format_func=lambda x: "Card " + str(x+1))

            if len(selected_indices) == 3:
                drawn_cards = [tarot_deck.shuffled_deck[i] for i in selected_indices]
                images = []
                captions = []
                for card in drawn_cards:
                    image_path = os.path.join(card[2])
                    img = Image.open(image_path)
                    if card[1] == 'downward':
                        img = img.rotate(180)
                    images.append(img)
                    captions.append(f"<span style='color:darkred;'>{card[0]}</span>")

                cols = st.columns(3)
                for i, image in enumerate(images):
                    with cols[i]:
                        st.markdown(f"<div style='width: 210px;text-align: center;background-color:rgba(251, 248, 196,1); padding: 8px;  border-radius:4%;'>{captions[i]}</div>", unsafe_allow_html=True)
                        st.image(image, width=210)


                # Call reading function
                reading = get_tarot_reading_v1(user_question, drawn_cards)
                HeaderWrite("Your Tarot Reading:")
                ReadingWrite(reading)

    elif mode == 'Fun':
        if 'stage' not in st.session_state:
            st.session_state['stage'] = 'keyword_input'

        if st.session_state['stage'] == 'keyword_input':
            keyword = st.text_input("Type a keyword:")
            if st.button("Submit"):
                obj_set = FunMode.generate_object_sets(keyword)
                st.session_state['obj_set'] = obj_set
                # image = FunMode.generate_set_image(obj_set)
                # st.session_state['image'] = image
                st.session_state['stage'] = 'select_set'
                st.experimental_rerun()

        elif st.session_state['stage'] == 'select_set':
            # st.image(st.session_state['image'], caption="Choose one of the following sets:")
            sets_list = st.session_state['obj_set'].split('\n')
            option = st.radio("Which set of objects would you like to pick?", sets_list)
            if st.button("Choose Set"):
                chosen_set = option.split('. ')[1]  
                st.session_state['chosen_set'] = chosen_set
                st.session_state['stage'] = 'final_question'

        if st.session_state['stage'] == 'final_question':
            user_question = st.text_input("Now, type your question:")
            if st.button("Get Tarot Reading"):
                st.session_state['user_question'] = user_question  

                keywords = FunMode.set_symbolism(st.session_state['chosen_set'])
                ReadingWrite("Keywords: "+keywords)
                reading = FunMode.get_tarot_reading_fun(keywords, st.session_state['user_question'])
                ReadingWrite(reading)





# def get_tarot_reading_v1(user_question,drawn_cards):

#     prompt = tarot_deck.generate_prompt(user_question, drawn_cards)

#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo-0125",
#         #response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a tarot reader. Please interpret the cards drawn for the user. 1. Provide the card info and the upward or downward status of each card. 2. Give an explaination of each individual card, and then a overall analysis based on these three cards."},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response.choices[0].message.content
                
def get_tarot_reading_v1(user_question,drawn_cards):

    prompt = tarot_deck.generate_prompt(user_question, drawn_cards)

    response = client.chat.completions.create(
        model="gpt-4",
        #response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a tarot reader. Please interpret the cards drawn for the user."
                                        + " Provide the card info and the upward or downward status of each card."
                                        + " Give an explaination of each individual card, and then a overall analysis based on these three cards."
                                        + " Please feel free to use the elments in the cards as sysmbols for the user's situation if necessary"
                                        + " Your answer don't always have to be positive."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def load_and_rotate_image(image_path, orientation):
    img = Image.open(image_path)
    if orientation == 'downward':
        img = img.rotate(180)  # Rotate the image by 180 degrees
    return img


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
                + "Each card must be same size. Major colors: Ivory yellow, dark red, dark blue.",
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
                                            + "Format: ONLY keywords separated by commas. NO other explanation."},
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
                                            + "Explain the card face, its symbolism and find a storyline for the image if any."
                                            + "Then answer user's question, with correspondence to symbolism of the card."
                                            + "The answer doesn't have to always be positive."
                                            + "Format: Your Card: [content]\n\n Symbolism: [content]\n\n Answer: [content]"},
                {"role": "user", "content": "The keyword is " + keywords + "User question is " + user_question }
            ]
        )
        return response.choices[0].message.content


def ReadingWrite(url):
    #  st.markdown(f'< style="background-color:rgba(255, 255, 240, 0.7);font-size:24px;border-radius:4%;">{url}</>', unsafe_allow_html=True)
    st.markdown(f'<div style="background-color:rgba(251, 248, 196,1); padding: 8px; ">{url}</div>', unsafe_allow_html=True)

def HeaderWrite(url):
    st.markdown(f'<div style="background-color:rgba(251, 248, 196,1); padding: 8px; font-size:24px; font-weight:bold;">{url}</div>', unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()
