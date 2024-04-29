import os
import streamlit as st
from tarot_deck import TarotDeck
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import base64
import time
from PIL import Image

load_dotenv()


with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


# Connect to MongoDB
def get_db():
    client = MongoClient(os.getenv("MONGODB_URI"), tls=True, tlsAllowInvalidCertificates=True)
    db = client.tarot_app
    return db


# Function to save user data to MongoDB
def save_user_data(question, cards, reading_type, reading_content):
    db = get_db()
    user_data = {
        "question": question,
        "cards": cards,
        "reading_type": reading_type,
        "reading_content": reading_content,
        "timestamp": time.time()
    }
    db.user_readings.insert_one(user_data)

def save_fun_data(keywords, question, reading_type, reading_content):
    db = get_db()
    user_data = {
        "keywords": keywords,
        "question": question,
        "reading_type": reading_type,
        "reading_content": reading_content,
        "timestamp": time.time()
    }
    db.funmode_readings.insert_one(user_data)

#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize tarot deck
tarot_deck = TarotDeck()

# Streamlit app
def main():
    st.title("Tarot Card Reading App")
    i=1

    mode = st.radio("Choose Mode", ('Classic', 'Fun'))

    if mode == 'Classic':
        user_question = st.text_input("Enter your question:")
        if user_question:

            # shuffle card
            tarot_deck = TarotDeck()
            tarot_deck.shuffle_cards()

            # display card shuffling options
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

            selected_indices = st.multiselect("The order of your selection matters.\n\nChoose your 3 cards:", options=range(78), format_func=lambda x: "Card " + str(x+1))

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
                reading_ft= get_tarot_reading_finetune(user_question, drawn_cards)
                reading_normal= get_tarot_reading_normal(user_question, drawn_cards)

                HeaderWrite("Finetune Model Reading...")
                ReadingWrite(reading_ft)
                HeaderWrite("Normal Model Reading...")
                ReadingWrite(reading_normal)

                # Allow user to choose which reading they prefer
                reading_choice = st.radio("Choose the reading you prefer:", ('Finetuned Model', 'Normal Model'))
                if st.button("Confirm Choice"):
                    # Determine the content of the chosen reading
                    if reading_choice == 'Finetuned Model':
                        chosen_reading_content = reading_ft
                    else:
                        chosen_reading_content = reading_normal

                    # Save user data including their choice and the reading content
                    card_names = [card[0] for card in drawn_cards]  # Extract card names for storage
                    save_user_data(user_question, card_names, reading_choice, chosen_reading_content)
                    st.success("Your choice and session details have been saved.")


    # elif mode == 'Fun':
    #     if 'stage' not in st.session_state:
    #         st.session_state['stage'] = 'keyword_input'

    #     if st.session_state['stage'] == 'keyword_input':
    #         keyword = st.text_input("Type a keyword:")
    #         if st.button("Submit"):
    #             obj_set = FunMode.generate_object_sets(keyword)
    #             st.session_state['obj_set'] = obj_set
    #             st.session_state['stage'] = 'select_set'
    #             st.experimental_rerun()

    #     elif st.session_state['stage'] == 'select_set':
    #         sets_list = st.session_state['obj_set'].split('\n')
    #         option = st.radio("Which set of objects would you like to pick?", sets_list)
    #         if st.button("Choose Set"):
    #             chosen_set = option.split('. ')[1]
    #             st.session_state['chosen_set'] = chosen_set
    #             st.session_state['stage'] = 'final_question'
    #             st.experimental_rerun()


    #     elif st.session_state['stage'] == 'final_question':
    #         user_question = st.text_input("Now, type your question:")
    #         st.session_state['User_question'] = user_question
    #         # if 'Keywords' in st.session_state:
    #         #     HeaderWrite("Keywords:")
    #         #     ReadingWrite(st.session_state['Keywords'])
    #         # if 'ft_reading' in st.session_state:
    #         #     HeaderWrite("Finetuned model reading...")
    #         #     ReadingWrite(st.session_state['ft_reading'].replace("\\n", "\n"))
    #         # if 'reading' in st.session_state:                
    #         #     HeaderWrite("Normal model reading...")
    #         #     ReadingWrite(st.session_state['reading'])               

    #         if st.button("Get Tarot Reading"):
    #             keywords = FunMode.set_symbolism(st.session_state['chosen_set'])

    #             st.session_state['Keywords'] = keywords
    #             HeaderWrite("Keywords:")
    #             ReadingWrite(keywords)

    #             ft_reading = FunMode.get_tarot_reading_fun_finetuned(keywords, user_question)
    #             st.session_state['ft_reading'] = ft_reading
    #             HeaderWrite("Finetuned model reading...")
    #             ReadingWrite(ft_reading.replace("\\n", "\n"))
    #             reading = FunMode.get_tarot_reading_fun(keywords, user_question)
    #             st.session_state['reading'] = reading
    #             HeaderWrite("Normal model reading...")
    #             ReadingWrite(reading)
                
    #             reading_choice = st.radio("Choose the reading you prefer:", ('Finetuned Model', 'Normal Model'))

    #             if st.button("Confirm Choice"):
    #                 st.session_state['choice'] = reading_choice
    #                 if reading_choice == 'Finetuned Model':
    #                     st.session_state['chosen_content'] = reading_ft
    #                 else:
    #                     st.session_state['chosen_content'] = reading_normal
    #                 st.session_state['stage'] = 'saving'

    #     elif st.session_state['stage'] == 'saving':
 
    #             save_fun_data(st.session_state['Keywords'], st.session_state['User_question'], st.session_state['choice'], st.session_state['chosen_content'])
    #             st.success("Your choice and session details have been saved.")
                



    elif mode == 'Fun':
        if 'stage' not in st.session_state:
            st.session_state['stage'] = 'keyword_input'

        if st.session_state['stage'] == 'keyword_input':
            keyword = st.text_input("Type a keyword:")
            if st.button("Submit"):
                obj_set = FunMode.generate_object_sets(keyword)
                st.session_state['obj_set'] = obj_set
                st.session_state['stage'] = 'select_set'
                st.experimental_rerun()

        elif st.session_state['stage'] == 'select_set':
            sets_list = st.session_state['obj_set'].split('\n')
            option = st.radio("Which set of objects would you like to pick?", sets_list)
            if st.button("Choose Set"):
                chosen_set = option.split('. ')[1]
                st.session_state['chosen_set'] = chosen_set
                st.session_state['stage'] = 'final_question'

        elif st.session_state['stage'] == 'final_question':
            user_question = st.text_input("Now, type your question:")
            if user_question:
                keywords = FunMode.set_symbolism(st.session_state['chosen_set'])
                HeaderWrite("Keywords:")
                ReadingWrite(keywords)

                ft_reading = FunMode.get_tarot_reading_fun_finetuned(keywords, user_question)
                HeaderWrite("Finetuned model reading...")
                ReadingWrite(ft_reading.replace("\\n", "\n"))
                reading = FunMode.get_tarot_reading_fun(keywords, user_question)
                HeaderWrite("Normal model reading...")
                ReadingWrite(reading)
                 
                reading_choice = st.radio("Choose the reading you prefer:", ('Finetuned Model', 'Normal Model'))
                
                if st.button("Confirm Choice"):
                    if reading_choice == 'Finetuned Model':
                        chosen_reading_content = ft_reading
                    else:
                        chosen_reading_content = reading
 
                    save_fun_data(keywords, user_question, reading_choice, chosen_reading_content)
                    st.success("Your choice and session details have been saved.")


                

def get_tarot_reading_normal(user_question,drawn_cards):
    prompt = tarot_deck.generate_prompt(user_question, drawn_cards)

    response = client.chat.completions.create(
        model="gpt-4",
        #response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": " You are a tarot reader. Please interpret the cards drawn for the user."
                                        + " Provide the card info and the upward or downward status of each card."
                                        + " Give an explaination of each individual card, and then a overall analysis based on these three cards."
                                        + " Please feel free to use the elments in the cards as sysmbols for the user's situation if necessary"
                                        + " Your answer don't always have to be positive."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_tarot_reading_finetune(user_question,drawn_cards):

    prompt = tarot_deck.generate_prompt(user_question, drawn_cards)

    response = client.chat.completions.create(
        #####model="gpt-4",
        model='ft:gpt-3.5-turbo-0125:personal::9J7eW2F9',
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

    # def generate_set_image(obj_set):
    #     response = client.images.generate(
    #       model="dall-e-3",
    #       prompt="Three set of objects, one set per card separated: "+ obj_set +
    #             "Resemble the art style of the PLAIN, MUNDANE OLD Waite Rider Tarot card."
    #             + "Each card must be same size. Major colors: Ivory yellow, dark red, dark blue.",
    #       size="1792x1024",
    #       quality="standard",
    #       n=1,
    #     )

    #     return response.data[0].url

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
                                            + "Explain the card face, its symbolism, finding a storyline for the image if any."
                                            + "Then answer user's question, with correspondence to symbolism of the card."
                                            + "The answer doesn't have to always be positive."
                                            + "Format: Your Card: [content]\n\n Symbolism: [content]\n\n Answer: [content]"},
                {"role": "user", "content": "The keyword is " + keywords + "User question is " + user_question }
            ]
        )
        return response.choices[0].message.content


    def get_tarot_reading_fun_finetuned(keywords,user_question):
        response = client.chat.completions.create(
            model='ft:gpt-3.5-turbo-0125:personal::9JAroEX6',
            messages=[
                {"role": "system", "content": "You are a tarot reader. Given four keywords and one user question, you draw out 1 card."
                                            + "This card should be correlated to the keywords but loosely."
                                            + "Explain the card face, its symbolism, finding a storyline for the image if any."
                                            + "Then answer user's question, with correspondence to symbolism of the card."
                                            + "The answer doesn't have to always be positive."
                                            + "Format: Your Card: [content]\n\n Symbolism: [content]\n\n Answer: [content]"},
                {"role": "user", "content": "Keywords: " + keywords + "User question: " + user_question }
            ]
        )
        return response.choices[0].message.content


def ReadingWrite(url):
    url = url.replace("\n", "<br>")
    #  st.markdown(f'< style="background-color:rgba(255, 255, 240, 0.7);font-size:24px;border-radius:4%;">{url}</>', unsafe_allow_html=True)
    st.markdown(f'<div style="background-color:rgba(251, 248, 196,1); padding: 8px; ">{url}</div>', unsafe_allow_html=True)

def HeaderWrite(url):
    st.markdown(f'<div style="background-color:rgba(251, 248, 196,1); padding: 8px; font-size:24px; font-weight:bold;">{url}</div>', unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()
