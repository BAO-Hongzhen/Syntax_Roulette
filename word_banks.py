"""
Word Banks Module - Syntax Roulette
Organized by Chinese grammar structure: Subject, Predicate, Attributive, Adverbial, Complement
主语、谓语、定语、状语、补语

Each category contains exactly 30 carefully selected words.
"""

from typing import Dict, List
import random


class WordBanks:
    """
    Word bank manager with 5 categories based on syntax roles:
    - Subject (主语): Who/what performs the action
    - Predicate (谓语): The action/verb
    - Attributive (定语): Adjectives describing the subject
    - Adverbial (状语): Adverbs describing how the action is done
    - Complement (补语): Objects and places that complete the sentence
    """
    
    def __init__(self):
        """Initialize all word banks with exactly 30 words each"""
        self._initialize_word_banks()
    
    def _initialize_word_banks(self):
        """Set up 5 word categories with 30 words each"""
        
        # Subject (主语) - 30 nouns: people, animals, characters
        self.subject = [
            # People (14)
            "boy", "girl", "man", "woman", "baby", "child",
            "grandma", "grandpa", "teacher", "doctor",
            "chef", "artist", "dancer", "singer",
            
            # Animals (9)
            "cat", "dog", "bird", "fish", "elephant",
            "monkey", "rabbit", "penguin", "lion",
            
            # Characters (7)
            "robot", "alien", "ghost", "wizard",
            "princess", "pirate", "ninja"
        ]
        
        # Predicate (谓语) - 30 verbs: base form (原型动词)
        self.predicate = [
            # Basic actions
            "eat", "drink", "sleep", "walk", "run",
            "jump", "fly", "swim", "crawl", "climb",
            
            # Activities
            "play", "dance", "sing", "read", "write",
            "draw", "paint", "cook", "bake", "build",
            
            # Interactions
            "ride", "drive", "throw", "catch", "kick",
            "hug", "kiss", "teach", "study", "fight"
        ]
        
        # Attributive (定语) - 30 adjectives: describing words
        self.attributive = [
            # Size
            "big", "small", "tiny", "huge", "giant", "little",
            
            # Colors
            "red", "blue", "green", "yellow", "pink",
            "purple", "orange", "black", "white", "golden",
            
            # Qualities
            "happy", "sad", "angry", "silly", "funny",
            "crazy", "smart", "brave", "lazy", "shy",
            
            # Others
            "beautiful", "ugly", "old", "young"
        ]
        
        # Adverbial (状语) - 30 adverbs: manner of action
        self.adverbial = [
            # Speed (5)
            "quickly", "slowly", "fast", "rapidly", "gradually",
            
            # Manner (8)
            "carefully", "carelessly", "quietly", "loudly",
            "gently", "roughly", "smoothly", "awkwardly",
            
            # Emotion (7)
            "happily", "sadly", "angrily", "joyfully",
            "nervously", "calmly", "excitedly",
            
            # Style (10)
            "elegantly", "clumsily", "gracefully",
            "secretly", "openly", "suddenly", "continuously",
            "wildly", "softly", "proudly"
        ]
        
        # Complement (补语) - 30 words: objects and places (more specific for better AI generation)
        self.complement = [
            # Objects (11)
            "a pizza", "a cake", "a ball", "a guitar",
            "a phone", "a car", "a bicycle", "a book",
            "an umbrella", "a balloon", "a flower",
            
            # Places - Indoor (6)
            "in the kitchen", "in the bathroom", "in the bedroom",
            "at school", "in the bathtub", "at home",
            
            # Places - Outdoor (7)
            "in the park", "on the beach", "in the garden",
            "under a tree", "beside a river", "on the street",
            "at the zoo",
            
            # Places - Sky/Space (6) - More specific for better AI understanding
            "on a cloud in the sky", "on the moon", "in outer space",
            "on a rooftop", "flying in the sky", "in the forest"
        ]
    
    def get_category(self, category_name: str) -> List[str]:
        """
        Get words from a specific category
        
        Args:
            category_name: Name of the category (subject/predicate/attributive/adverbial/complement)
            
        Returns:
            List of 30 words in that category
        """
        category_map = {
            "subject": self.subject,
            "predicate": self.predicate,
            "attributive": self.attributive,
            "adverbial": self.adverbial,
            "complement": self.complement
        }
        
        return category_map.get(category_name, [])
    
    def shuffle_and_pick(self, category_name: str, show_shuffle: bool = True) -> tuple:
        """
        Shuffle the deck and pick a card (word)
        Returns shuffle animation frames if show_shuffle is True
        
        Args:
            category_name: Name of the category
            show_shuffle: Whether to return animation frames
            
        Returns:
            If show_shuffle: (animation_frames, final_word)
            Else: ([], final_word)
        """
        words = self.get_category(category_name)
        if not words:
            return ([], "")
        
        # Shuffle the deck
        shuffled = words.copy()
        random.shuffle(shuffled)
        
        if not show_shuffle:
            return ([], shuffled[0])
        
        # Create shuffle animation (show 15 random cards)
        shuffle_frames = []
        for i in range(15):
            shuffle_frames.append(random.choice(shuffled))
        
        # Final pick
        final_word = shuffled[0]
        
        return (shuffle_frames, final_word)
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """Get all word categories"""
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "attributive": self.attributive,
            "adverbial": self.adverbial,
            "complement": self.complement
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about all word banks"""
        categories = self.get_all_categories()
        return {name: len(words) for name, words in categories.items()}


# Test the word banks if run directly
if __name__ == "__main__":
    print("=" * 70)
    print("Word Banks Test - Syntax Structure")
    print("=" * 70)
    
    wb = WordBanks()
    stats = wb.get_stats()
    
    print("\nWord Bank Statistics:")
    print("-" * 70)
    print(f"{'Category':<20} {'Chinese':<15} {'Count':<10}")
    print("-" * 70)
    
    categories_cn = {
        "subject": "主语",
        "predicate": "谓语",
        "attributive": "定语",
        "adverbial": "状语",
        "complement": "补语"
    }
    
    total_words = 0
    for category, count in stats.items():
        cn_name = categories_cn.get(category, "")
        print(f"{category:<20} {cn_name:<15} {count:<10} words")
        total_words += count
    
    print("-" * 70)
    print(f"{'TOTAL':<20} {'总计':<15} {total_words:<10} words")
    print("\n" + "=" * 70)
    
    # Show sample from each category
    print("\nSample words from each category:")
    print("-" * 70)
    for category_name in stats.keys():
        words = wb.get_category(category_name)
        sample = ", ".join(words[:8])
        cn_name = categories_cn.get(category_name, "")
        print(f"{category_name:<15} ({cn_name}): {sample}...")
    
    print("\n" + "=" * 70)
    print("Example sentences:")
    print("-" * 70)
    for i in range(5):
        _, subj = wb.shuffle_and_pick("subject", False)
        _, pred = wb.shuffle_and_pick("predicate", False)
        _, attr = wb.shuffle_and_pick("attributive", False)
        _, adv = wb.shuffle_and_pick("adverbial", False)
        _, comp = wb.shuffle_and_pick("complement", False)
        
        sentence = f"A {attr} {subj} {adv} {pred} {comp}"
        print(f"{i+1}. {sentence}")
    
    print("=" * 70)
