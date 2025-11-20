"""
Syntax Roulette - English Word Roulette Text-to-Image Generator
A fun interactive application that generates sentences through spinning word wheels
and creates images from the generated text.

Usage:
    python main.py

Then open the displayed URL in your browser (typically http://localhost:7860)
"""

import gradio as gr
import random
import time
import platform
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from PIL import Image
import os

# Import word banks
from word_banks import WordBanks

# Import image generation utilities
from image_generator import ImageGenerator


@dataclass
class RouletteResult:
    """Data class to store roulette spin results"""
    subject: str = ""        # Subject
    predicate: str = ""      # Predicate/Verb
    attributive: str = ""    # Attributive/Adjective
    adverbial: str = ""      # Adverbial/Adverb
    complement: str = ""     # Complement/Object+Location


class SyntaxRouletteApp:
    """Main application class for Syntax Roulette"""
    
    def __init__(self):
        """Initialize the application"""
        self.word_banks = WordBanks()
        self.image_generator = ImageGenerator()
        self.current_result = RouletteResult()
        self.generation_history = []
        
        # Animation settings
        self.spin_duration = 2.0  # seconds
        self.spin_steps = 20
        
        print("✅ Syntax Roulette initialized successfully!")
    
    def shuffle_and_pick_card(self, category: str) -> tuple:
        """
        Shuffle deck and pick a card - with animation frames
        
        Args:
            category: Word category (subject/predicate/attributive/adverbial/complement)
            
        Returns:
            (shuffle_frames, final_word)
        """
        shuffle_frames, final_word = self.word_banks.shuffle_and_pick(category, show_shuffle=True)
        return shuffle_frames, final_word
    
    def spin_all_roulettes(self, progress=gr.Progress()) -> Tuple[str, str, str, str, str, str]:
        """
        Shuffle all decks and pick cards with animation
        
        Returns:
            Tuple of (subject, predicate, attributive, adverbial, complement, status_message)
        """
        progress(0, desc="🎴 Starting to shuffle decks...")
        time.sleep(0.2)
        
        # 5 categories based on syntax structure
        categories = [
            ("subject", "👤 Shuffling Subject deck..."),
            ("predicate", "⚡ Shuffling Predicate deck..."),
            ("attributive", "🎨 Shuffling Attributive deck..."),
            ("adverbial", "💫 Shuffling Adverbial deck..."),
            ("complement", "🎯 Shuffling Complement deck...")
        ]
        
        results = []
        total_categories = len(categories)
        
        for i, (category, desc) in enumerate(categories):
            # Update progress at start of category
            base_progress = (i / total_categories)
            progress(base_progress, desc=desc)
            time.sleep(0.15)
            
            # Get shuffle animation frames and final card
            shuffle_frames, final_word = self.shuffle_and_pick_card(category)
            
            # Show shuffle animation (reduced update frequency to prevent text overlap)
            # Only update every 5 frames instead of every frame
            for frame_idx, frame_word in enumerate(shuffle_frames):
                time.sleep(0.05)  # 50ms per frame
                # Only update progress every 5 frames to reduce UI flickering
                if frame_idx % 5 == 0 or frame_idx == len(shuffle_frames) - 1:
                    frame_progress = base_progress + ((frame_idx + 1) / len(shuffle_frames) / total_categories)
                    progress(frame_progress, desc=f"{desc.split()[0]} Shuffling...")
            
            # Pick the card (final selection) - simplified message
            results.append(final_word)
            pick_progress = (i + 0.9) / total_categories
            progress(pick_progress, desc=f"Picked: {final_word}")
            time.sleep(0.2)  # Slightly longer pause after picking
        
        # Store results
        self.current_result.subject = results[0]
        self.current_result.predicate = results[1]
        self.current_result.attributive = results[2]
        self.current_result.adverbial = results[3]
        self.current_result.complement = results[4]
        
        progress(1.0, desc="✅ Complete!")
        time.sleep(0.3)
        
        status = "✅ All cards picked! Click 'Generate Sentence' to create your prompt."
        
        return (
            results[0], results[1], results[2], 
            results[3], results[4], status
        )
    
    def generate_sentence(self, subject: str, predicate: str, attributive: str,
                         adverbial: str, complement: str) -> Tuple[str, str]:
        """
        Generate grammatically correct English sentence from syntax components
        
        Structure: [Article] [Attributive] [Subject] [Adverbial] [Predicate] [Complement]
        
        Args:
            subject: Subject (who/what)
            predicate: Predicate (action/verb)
            attributive: Attributive (describing adjective)
            adverbial: Adverbial (how the action is done)
            complement: Complement (object/place)
            
        Returns:
            Tuple of (enhanced_prompt, status_message)
        """
        if not subject or not predicate:
            return "", "❌ Error: Subject and predicate are required!"
        
        # Build sentence with proper grammar
        parts = []
        
        # Determine article
        first_word = attributive if attributive else subject
        article = self._get_article(first_word)
        
        # Build subject phrase: [Article] [Attributive] [Subject]
        subject_phrase = []
        if attributive:
            subject_phrase.append(attributive)
        subject_phrase.append(subject)
        
        parts.append(f"{article} {' '.join(subject_phrase)}")
        
        # Add predicate with adverbial: [Adverbial] [Predicate (gerund form)]
        if adverbial:
            parts.append(f"is {adverbial} {self._convert_verb_to_gerund(predicate)}")
        else:
            parts.append(f"is {self._convert_verb_to_gerund(predicate)}")
        
        # Add complement (already includes article/preposition)
        if complement:
            parts.append(complement)
        
        # Create sentence
        sentence = " ".join(parts)
        
        # Capitalize first letter and add period
        sentence = sentence[0].upper() + sentence[1:] + "."
        
        status = "✅ Sentence generated! Ready for image generation."
        
        return sentence, status
    
    def _get_article(self, word: str) -> str:
        """Determine appropriate article (a/an) for a word"""
        if not word:
            return "a"
        vowels = ['a', 'e', 'i', 'o', 'u']
        return "an" if word[0].lower() in vowels else "a"
    
    def _convert_verb_to_gerund(self, verb: str) -> str:
        """
        Convert base form verb to gerund (-ing form) for continuous tense
        
        Rules:
        1. Consonant-Vowel-Consonant (CVC) → double last consonant + ing (run→running)
        2. Ends with 'e' → drop 'e' + ing (dance→dancing)
        3. Ends with 'ie' → change 'ie' to 'y' + ing (die→dying)
        4. Regular → just add 'ing' (play→playing)
        """
        if not verb:
            return verb
        
        verb = verb.lower().strip()
        
        # Special irregular cases
        special_cases = {
            "be": "being",
            "see": "seeing",
            "agree": "agreeing",
            "free": "freeing"
        }
        
        if verb in special_cases:
            return special_cases[verb]
        
        # Rule 1: Ends with 'ie' → change to 'ying'
        if verb.endswith('ie'):
            return verb[:-2] + 'ying'  # die → dying, tie → tying
        
        # Rule 2: Ends with 'e' (but not 'ee', 'oe', 'ye') → drop 'e' + ing
        if verb.endswith('e') and len(verb) > 2:
            if not verb.endswith(('ee', 'oe', 'ye')):
                return verb[:-1] + 'ing'  # dance → dancing, write → writing
        
        # Rule 3: CVC pattern (Consonant-Vowel-Consonant) → double last + ing
        # Only for short verbs (3-4 letters) ending in single vowel + single consonant
        if len(verb) >= 3:
            vowels = set('aeiou')
            consonants = set('bcdfghjklmnpqrstvwxyz')
            
            # Check if it matches CVC pattern at the end
            if (len(verb) == 3 or 
                (len(verb) == 4 and verb[-3] not in vowels)):
                if (verb[-3] in consonants and 
                    verb[-2] in vowels and 
                    verb[-1] in consonants and
                    verb[-1] not in ('w', 'x', 'y')):  # Don't double w, x, y
                    return verb + verb[-1] + 'ing'  # run → running, swim → swimming
        
        # Rule 4: Regular verbs → just add 'ing'
        return verb + 'ing'  # play → playing, teach → teaching
    
    def generate_image_from_prompt(self, prompt: str, 
                                   negative_prompt: str,
                                   width: int, height: int,
                                   num_steps: int,
                                   guidance_scale: float,
                                   use_random_seed: bool,
                                   seed: int,
                                   progress=gr.Progress()) -> Tuple[Optional[Image.Image], str]:
        """
        Generate an image from the prompt using text-to-image AI
        
        Args:
            prompt: Text description for image generation
            negative_prompt: Things to avoid in the image
            width, height: Image dimensions
            num_steps: Number of inference steps
            guidance_scale: How closely to follow the prompt
            use_random_seed: Whether to use random seed
            seed: Fixed seed value
            
        Returns:
            Tuple of (generated_image, status_message)
        """
        if not prompt or prompt.strip() == "":
            return None, "❌ Error: Please provide a prompt!"
        
        try:
            # Generate seed
            if use_random_seed:
                seed = random.randint(0, 2**32 - 1)
            
            # Generate image (progress updates handled by image_generator)
            image = self.image_generator.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale,
                seed=seed,
                progress_callback=progress
            )
            
            if image is None:
                return None, "❌ Error: Image generation failed!"
            
            # Save to history
            self.generation_history.insert(0, {
                "image": image,
                "prompt": prompt,
                "seed": seed,
                "size": f"{width}x{height}"
            })
            
            # Limit history
            if len(self.generation_history) > 20:
                self.generation_history = self.generation_history[:20]
            
            status = f"✅ Image generated successfully! Seed: {seed}"
            return image, status
            
        except Exception as e:
            error_msg = f"❌ Error during image generation: {str(e)}"
            print(error_msg)
            return None, error_msg
    
    def get_history_gallery(self) -> List[Tuple[Image.Image, str]]:
        """Get history gallery for display"""
        if not self.generation_history:
            return []
        return [(item["image"], f"Seed: {item['seed']}") for item in self.generation_history]
    
    def clear_history(self) -> Tuple[List, str]:
        """Clear generation history"""
        self.generation_history = []
        return [], "✅ History cleared"
    
    def reset_all(self) -> Tuple[str, str, str, str, str, str, None, str]:
        """Reset all fields to empty state"""
        self.current_result = RouletteResult()
        return ("", "", "", "", "", "✅ All fields reset", None, "")


def create_gradio_interface() -> gr.Blocks:
    """
    Create the Gradio web interface
    
    Returns:
        Gradio Blocks application
    """
    
    app = SyntaxRouletteApp()
    
    # Custom CSS for better styling
    custom_css = """
    .roulette-box {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .roulette-result {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
        min-height: 60px;
    }
    """
    
    with gr.Blocks(title="Syntax Roulette - Word Wheel Image Generator", 
                   theme=gr.themes.Soft(primary_hue="purple", secondary_hue="pink"),
                   css=custom_css) as demo:
        
        # Header
        gr.Markdown(
            """
            # 🎴 Syntax Roulette - Card-Style Text-to-Image Generator
            
            ### Shuffle decks, pick cards, create sentences, generate amazing images!
            
            **How to use:**
            1. 🎴 Click "Spin All Wheels" to shuffle and pick cards from each syntax category
            2. ✏️ Edit any word if you want to customize
            3. 📝 Click "Generate Sentence" to create an enhanced prompt
            4. 🎨 Click "Generate Image" to create an AI image (watch real-time progress!)
            
            **5 Syntax Categories:** Subject | Predicate | Attributive | Adverbial | Complement
            """
        )
        
        with gr.Row():
            # Left panel - Card decks
            with gr.Column(scale=1):
                gr.Markdown("## 🎴 Card Decks (Syntax Categories)")
                
                status_message = gr.Markdown("🎯 Ready! Click 'Spin All Wheels' to shuffle and pick cards.")
                
                # Action buttons
                with gr.Group():
                    with gr.Row():
                        spin_all_btn = gr.Button("🎴 Shuffle & Pick Cards", variant="primary", size="lg")
                        reset_btn = gr.Button("🔄 Reset All", size="lg")
                
                # Word category outputs (5 syntax categories)
                with gr.Group():
                    gr.Markdown("### 🎴 Picked Cards (Selected Words)")
                    
                    with gr.Row():
                        subject_output = gr.Textbox(
                            label="Subject", 
                            placeholder="e.g., cat, boy, robot"
                        )
                        predicate_output = gr.Textbox(
                            label="Predicate", 
                            placeholder="e.g., eats, runs, plays"
                        )
                    
                    with gr.Row():
                        attributive_output = gr.Textbox(
                            label="Attributive", 
                            placeholder="e.g., big, happy, red"
                        )
                        adverbial_output = gr.Textbox(
                            label="Adverbial", 
                            placeholder="e.g., quickly, happily"
                        )
                    
                    with gr.Row():
                        complement_output = gr.Textbox(
                            label="Complement", 
                            placeholder="e.g., a pizza, in the kitchen",
                            show_copy_button=True
                        )
                
                # Sentence generation
                with gr.Group():
                    gr.Markdown("### 📝 Generated Sentence (Prompt)")
                    sentence_output = gr.Textbox(
                        label="Your Sentence",
                        placeholder="Your generated sentence will appear here...",
                        lines=3
                    )
                    generate_sentence_btn = gr.Button("📝 Generate Sentence", variant="secondary", size="lg")
                
                # Additional prompt controls
                with gr.Accordion("⚙️ Image Generation Settings", open=True):
                    negative_prompt = gr.Textbox(
                        label="Negative Prompt (things to avoid)",
                        placeholder="e.g., blurry, bad quality, distorted, ugly",
                        value="blurry, bad quality, distorted, ugly, deformed, extra limbs, mutated, disfigured",
                        lines=2
                    )
                    
                    with gr.Row():
                        width = gr.Slider(256, 768, value=512, step=64, label="Width")
                        height = gr.Slider(256, 768, value=512, step=64, label="Height")
                    
                    with gr.Row():
                        num_steps = gr.Slider(15, 50, value=25, step=5, label="Inference Steps", 
                                            info="More steps = better quality (25 = fast, 35 = high quality)")
                        guidance_scale = gr.Slider(5, 15, value=7.5, step=0.5, label="Guidance Scale",
                                                  info="How closely to follow prompt (7.5 recommended)")
                    
                with gr.Row():
                        use_random_seed = gr.Checkbox(label="Random Seed", value=True)
                        seed_value = gr.Number(label="Seed", value=42, precision=0)
            
            # Right panel - Image generation
            with gr.Column(scale=1):
                gr.Markdown("## 🎨 Generated Image")
                
                image_status = gr.Markdown("⏳ Waiting for image generation...")
                
                output_image = gr.Image(label="Generated Image", type="pil", height=450)
                
                generate_image_btn = gr.Button("🎨 Generate Image", variant="primary", size="lg")
                
                # System info
                with gr.Accordion("ℹ️ System Information", open=False):
                    system_info = f"""
                    **Platform:** {platform.system()} {platform.release()}
                    **Python:** {sys.version.split()[0]}
                    **Device:** {app.image_generator.get_device_info()}
                    """
                    gr.Markdown(system_info)
        
        # History section
        with gr.Accordion("📚 Generation History", open=False):
            with gr.Row():
                refresh_history_btn = gr.Button("🔄 Refresh History", size="sm")
                clear_history_btn = gr.Button("🗑️ Clear History", size="sm")
            
            history_gallery = gr.Gallery(
                label="Previous Generations",
                columns=4,
                rows=2,
                height=400
            )
            history_status = gr.Markdown("")
        
        # Help section
        with gr.Accordion("❓ Help & Tips", open=False):
            gr.Markdown(
                """
                ## 📖 User Guide
                
                ### Word Categories Explained:
                - **Subject**: The main noun (who/what is doing the action)
                - **Verb**: The action or state
                - **Object**: What receives the action
                - **Adjectives**: Descriptive words for nouns
                - **Adverb**: Describes how the action is performed
                - **Preposition + Location**: Where the action takes place
                
                ### Tips for Better Images:
                1. **Be Specific**: More descriptive words = better images
                2. **Use Style Keywords**: Add "photorealistic", "oil painting", "anime style", etc.
                3. **Negative Prompts**: List unwanted elements to improve quality
                4. **Inference Steps**: 20-30 steps is usually a good balance
                5. **Guidance Scale**: 7-8 follows prompt closely, 10+ very strictly
                
                ### Examples of Good Prompts:
                - "A majestic dragon gracefully flies over ancient mountains at sunset"
                - "The wise wizard carefully creates magical crystals in a mystical forest"
                - "A cute robot happily dances with colorful balloons in a futuristic city"
                
                ### Troubleshooting:
                - **Slow Generation?** Try reducing image size or inference steps
                - **Out of Memory?** Reduce image dimensions to 256x256 or 384x384
                - **macOS Issues?** The app automatically uses CPU mode if GPU is unavailable
                
                ### Keyboard Shortcuts:
                - Press Enter in text fields to quickly move to next step
                """
            )
        
        # Footer
        gr.Markdown(
            """
            ---
            <div style="text-align: center; color: #666;">
                <p>🎰 Syntax Roulette | Created with ❤️ using Gradio & Stable Diffusion</p>
                <p style="font-size: 0.9em;">Tip: Use Chrome or Firefox for best experience</p>
            </div>
            """
        )
        
        # ===== Event Handlers =====
        
        # Shuffle and pick cards
        spin_all_btn.click(
            fn=app.spin_all_roulettes,
            inputs=[],
            outputs=[
                subject_output, predicate_output, attributive_output,
                adverbial_output, complement_output, status_message
            ],
            show_progress="full"  # Enable progress bar with animation
        )
        
        # Generate sentence
        generate_sentence_btn.click(
            fn=app.generate_sentence,
            inputs=[
                subject_output, predicate_output, attributive_output,
                adverbial_output, complement_output
            ],
            outputs=[sentence_output, status_message],
            show_progress=False  # Quick operation
        )
        
        # Generate image - CRITICAL for progress display
        generate_image_btn.click(
            fn=app.generate_image_from_prompt,
            inputs=[
                sentence_output, negative_prompt,
                width, height, num_steps, guidance_scale,
                use_random_seed, seed_value
            ],
            outputs=[output_image, image_status],
            show_progress="full"  # Full progress with real-time updates
        )
        
        # Reset all
        reset_btn.click(
            fn=app.reset_all,
            inputs=[],
            outputs=[
                subject_output, predicate_output, attributive_output,
                adverbial_output, complement_output, sentence_output,
                output_image, image_status
            ]
        )
        
        # Random seed checkbox
        use_random_seed.change(
            fn=lambda x: gr.update(interactive=not x),
            inputs=use_random_seed,
            outputs=seed_value
        )
        
        # History buttons
        refresh_history_btn.click(
            fn=app.get_history_gallery,
            inputs=[],
            outputs=history_gallery
        )
        
        clear_history_btn.click(
            fn=app.clear_history,
            inputs=[],
            outputs=[history_gallery, history_status]
        )
    
    return demo


if __name__ == "__main__":
    print("=" * 70)
    print("🎰 Syntax Roulette - English Word Wheel Text-to-Image Generator")
    print("=" * 70)
    print("Initializing application...")
    print("Please wait while loading AI models (first run may take a few minutes)...")
    print("=" * 70)
    
    # Create and launch the application
    demo = create_gradio_interface()
    
    # Launch with appropriate settings
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True
    )
