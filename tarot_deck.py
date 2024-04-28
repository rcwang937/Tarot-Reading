import random
import os

class TarotDeck:
    def __init__(self):
        self.base_path = 'STATIC/cards/'
        self.cards = [
            ('The Fool', 'm00.jpg'), ('The Magician', 'm01.jpg'), ('The High Priestess', 'm02.jpg'),
            ('The Empress', 'm03.jpg'), ('The Emperor', 'm04.jpg'), ('The Hierophant', 'm05.jpg'),
            ('The Lovers', 'm06.jpg'), ('The Chariot', 'm07.jpg'), ('Strength', 'm08.jpg'),
            ('The Hermit', 'm09.jpg'), ('Wheel of Fortune', 'm10.jpg'), ('Justice', 'm11.jpg'),
            ('The Hanged Man', 'm12.jpg'), ('Death', 'm13.jpg'), ('Temperance', 'm14.jpg'),
            ('The Devil', 'm15.jpg'), ('The Tower', 'm16.jpg'), ('The Star', 'm17.jpg'),
            ('The Moon', 'm18.jpg'), ('The Sun', 'm19.jpg'), ('Judgement', 'm20.jpg'),
            ('The World', 'm21.jpg')
        ] + [
            (f'{rank} of Wands', f'w{idx+1:02d}.jpg') for idx, rank in enumerate([
                'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
                'Nine', 'Ten', 'Page', 'Knight', 'Queen', 'King'
            ])
        ] + [
            (f'{rank} of Cups', f'c{idx+1:02d}.jpg') for idx, rank in enumerate([
                'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
                'Nine', 'Ten', 'Page', 'Knight', 'Queen', 'King'
            ])
        ] + [
            (f'{rank} of Swords', f's{idx+1:02d}.jpg') for idx, rank in enumerate([
                'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
                'Nine', 'Ten', 'Page', 'Knight', 'Queen', 'King'
            ])
        ] + [
            (f'{rank} of Pentacles', f'p{idx+1:02d}.jpg') for idx, rank in enumerate([
                'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
                'Nine', 'Ten', 'Page', 'Knight', 'Queen', 'King'
            ])
        ]
        self.shuffled_deck = []

    def shuffle_cards(self):
        deck_with_orientation = [(card, random.choice(['upward', 'downward']), os.path.join(self.base_path, img)) for card, img in self.cards]
        random.shuffle(deck_with_orientation)
        self.shuffled_deck = deck_with_orientation

    def draw_cards(self, num_cards=3):
        return self.shuffled_deck[:num_cards]

    def generate_prompt(self, user_question, drawn_cards):
        prompt = f"User asked: {user_question}\n\n"
        for card, orientation, img in drawn_cards:  # Add img to unpack the third element
            prompt += f"The card drawn is {card} facing {orientation}.\n"
        prompt += "What is the meaning of these cards and how do they address the user's question?"
        return prompt

