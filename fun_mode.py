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
      