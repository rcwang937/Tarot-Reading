import random

class TarotDeck:
    def __init__(self):
        self.cards = [
            'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor',
            'The Hierophant', 'The Lovers', 'The Chariot', 'Strength', 'The Hermit',
            'Wheel of Fortune', 'Justice', 'The Hanged Man', 'Death', 'Temperance',
            'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun',
            'Judgement', 'The World'
        ] + [
            f'{rank} of {suit}' for suit in ['Wands', 'Cups', 'Swords', 'Pentacles']
            for rank in ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Page', 'Knight', 'Queen', 'King']
        ]
        self.shuffled_deck = []

    def shuffle_cards(self):
        deck_with_orientation = [(card, random.choice(['upward', 'downward'])) for card in self.cards]
        random.shuffle(deck_with_orientation)
        self.shuffled_deck = deck_with_orientation

    def draw_cards(self, num_cards=3):
        return self.shuffled_deck[:num_cards]

    def generate_prompt(self, user_question, drawn_cards):
        prompt = f"User asked: {user_question}\n\n"
        for card, orientation in drawn_cards:
            prompt += f"The card drawn is {card} facing {orientation}.\n"
        prompt += "What is the meaning of these card and how to address them to the user's question?"
        return prompt

