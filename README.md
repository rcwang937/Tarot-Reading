# Tarot Card AI Reading WebApp

## Introduction
Tarot Card AI Reading is a web application that provides insightful tarot card readings in two modes: Classic and Fun. Utilizing OpenAI, Streamlit, MongoDB, and the application offers users a personalized tarot experience.

### Classic Mode
In Classic Mode, users submit a question and select three cards from a shuffled deck.
### Fun Mode
Fun Mode provides light-hearted and quick tarot readings for entertainment.

Both modes provide readings from a fine-tuned OpenAI model, based on tarot case studies, and GPT-4 model. The two model provides detailed analysis addressing users' specific questions.  Users can choose their preferred analysis, which is saved to MongoDB for future model enhancement.


## Setup and Running the Application

### 1. Clone the Repository
Start by cloning the repository to your local machine. Open your terminal and run the following command:
```
git clone https://github.com/rcwang937/Tarot-Reading
```

### 2. Install Dependencies

This project uses Pipenv to manage dependencies. Ensure you have Pipenv installed; if not, you can install it using pip:
```
pip install pipenv
```
Once Pipenv is installed, you can install all dependencies specified in the Pipfile:
```
pipenv install
```

### 3. Run the Application
With the dependencies in place, you can run the application using Streamlit. Make sure you are still in the project's root directory and run:
```
streamlit run app.py
```
OR
```
pipenv run streamlit run app.py
```

## Configuration
Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY='YOUR API KEY'
MONGODB_URI='Please ask contributor for more info'
```
Replace `YOUR API KEY` with the actual API key from OpenAI. If you want your results to be saved to the database, please contact the project contributor for the MongoDB URI.

## Sample Usage Video

To see the app in action, watch the sample usage video below:

[![Watch the video](STATIC/face_image.jpg)](STATIC/PrettyMuchEverything.mp4)


## License

This project is licensed under the GNU General Public License (GPL). See the `LICENSE` file for more details.
