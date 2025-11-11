# 🎴 Syntax Roulette - Card-Style Text-to-Image Generator

An interactive application that generates creative English sentences through card-style word selection and creates AI-generated images using Stable Diffusion.

![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 🎴 **5 Card Decks** - 150 carefully selected words across 5 syntax categories
- 🎲 **Shuffle & Pick Animation** - Visual card shuffling with real-time progress
- 📝 **Smart Grammar** - Automatically generates grammatically correct English sentences
- 🎨 **AI Image Generation** - Powered by Stable Diffusion 1.5
- 🖥️ **Cross-Platform** - Windows, macOS (Intel & Apple Silicon), and Linux
- ⚡ **GPU Acceleration** - Auto-detection of NVIDIA CUDA, Apple MPS, or CPU fallback
- 🌐 **User-Friendly Web UI** - Clean Gradio interface
- 📊 **Real-time Progress** - Clear status updates during generation

---

## 🚀 Quick Start

### Windows

```bash
# Setup (first time only)
setup_windows.bat

# Run application
run_windows.bat
```

### macOS / Linux

```bash
# Setup (first time only)
chmod +x setup_macos.sh run_macos.sh
./setup_macos.sh

# Run application
./run_macos.sh
```

The web interface will open automatically at `http://localhost:7860`

**First run**: Downloads the Stable Diffusion model (~4GB, 5-15 minutes). Subsequent runs start instantly.

---

## 📋 Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 10GB disk space (for AI model)
- Internet connection (first-time setup only)

### Recommended
- Python 3.10+
- 16GB RAM
- GPU: NVIDIA (6GB+ VRAM) or Apple Silicon (M1/M2/M3)

---

## 🎮 How to Use

### Step 1: Shuffle & Pick Cards 🎴

Click **"Shuffle & Pick Cards"** to randomly select words from 5 syntax categories:

| Category | Role | Examples |
|----------|------|----------|
| **Subject** (主语) | Who/what does the action | boy, girl, cat, dog, robot, wizard |
| **Predicate** (谓语) | The action/verb | eat, drink, play, dance, fly, swim |
| **Attributive** (定语) | Describes the subject | big, small, happy, silly, red, blue |
| **Adverbial** (状语) | How the action is done | quickly, carefully, happily, slowly |
| **Complement** (补语) | Objects/places | a pizza, in the kitchen, on the moon |

Each deck contains **30 words** - total **150 words**.

Watch the shuffling animation as cards are picked!

### Step 2: Generate Sentence 📝

Click **"Generate Sentence"** to combine words into a grammatically correct English sentence.

**Sentence Structure:**
```
[Article] [Attributive] [Subject] is [Adverbial] [Predicate-ing] [Complement]
```

**Example outputs:**
```
"A little baby is carefully studying on a rooftop."
"A crazy dog is slowly swimming in the bathtub."
"A tiny bird is quickly flying on a cloud in the sky."
```

You can edit any word before generating the sentence!

### Step 3: Create Image 🎨

1. **(Optional) Adjust settings:**
   - **Image Size**: 256x256 to 768x768
   - **Inference Steps**: 15-50 (default: 25)
   - **Guidance Scale**: 5-15 (default: 7.5)
   - **Negative Prompt**: Things to avoid

2. Click **"Generate Image"**

3. Watch real-time progress bar

4. View and download your AI-generated image!

---

## ⚙️ Image Generation Settings

### Default Settings (Optimized for Speed & Quality)

```
Size: 512x512
Steps: 25
Guidance: 7.5
Negative: blurry, bad quality, distorted, ugly, deformed
```

**Performance:**
- NVIDIA GPU: ~10 seconds
- Apple Silicon: ~30 seconds  
- CPU: ~2-3 minutes

### Preset Configurations

#### ⚡ Fastest (15-20 seconds on Apple Silicon)
```
Steps: 15-20
Guidance: 7.0
Size: 512x512
```

#### 💎 High Quality (45-50 seconds on Apple Silicon)
```
Steps: 35-40
Guidance: 8.5
Size: 512x512
```

#### 🎨 Maximum Quality (80-100 seconds on Apple Silicon)
```
Steps: 50
Guidance: 9.0
Size: 768x768
```

---

## 🔧 Troubleshooting

### Black Images on macOS
✅ **Fixed automatically** - The app uses `float32` precision for MPS devices.

### Out of Memory
- Reduce image size (try 384x384 or 256x256)
- Reduce inference steps (try 15-20)
- Restart the application

### Slow Generation
- Use fewer steps (15-25 is usually sufficient)
- Reduce image size if needed
- Check if GPU is being detected (see terminal output)

### Model Not Loading
- Ensure stable internet connection for first download
- Check available disk space (need ~10GB)
- Try rerunning setup script

### Dependencies Issue
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🎯 Word Banks

Each category contains **30 everyday words** designed to create amusing and creative combinations!

### Subject (30 words)
People, animals, and characters:
```
boy, girl, man, woman, baby, child, grandma, grandpa, teacher, doctor,
chef, artist, dancer, singer, cat, dog, bird, fish, elephant, monkey,
rabbit, penguin, lion, robot, alien, ghost, wizard, princess, pirate, ninja
```

### Predicate (30 words)
Base form verbs (actions):
```
eat, drink, sleep, walk, run, jump, fly, swim, crawl, climb,
play, dance, sing, read, write, draw, paint, cook, bake, build,
ride, drive, throw, catch, kick, hug, kiss, teach, study, fight
```

### Attributive (30 words)
Descriptive adjectives:
```
big, small, tiny, huge, giant, little, red, blue, green, yellow,
pink, purple, orange, black, white, happy, sad, angry, silly, funny,
crazy, smart, brave, lazy, shy, beautiful, ugly, old, young, golden
```

### Adverbial (30 words)
Manner adverbs:
```
quickly, slowly, fast, rapidly, gradually, carefully, carelessly, quietly,
loudly, gently, roughly, smoothly, awkwardly, happily, sadly, angrily,
joyfully, nervously, calmly, excitedly, elegantly, clumsily, gracefully,
secretly, openly, suddenly, continuously, wildly, softly, proudly
```

### Complement (30 words)
Objects and places:
```
a pizza, a cake, a ball, a guitar, a phone, a car, a bicycle, a book,
an umbrella, a balloon, a flower, in the kitchen, in the bathroom,
in the bedroom, at school, in the bathtub, at home, in the park,
on the beach, in the garden, under a tree, beside a river, on the street,
at the zoo, on a cloud in the sky, on the moon, in outer space,
on a rooftop, flying in the sky, in the forest
```

**Example Combinations:**
- 🏀🛁 "A small boy is quickly playing a ball in the bathtub"
- 🍕🌙 "A silly cat is happily eating a pizza on the moon"
- 🚀☁️ "A brave pirate is wildly riding flying in the sky"

---

## 💻 Project Structure

```
Syntax_Roulette/
├── main.py                 # Main application and Gradio UI
├── word_banks.py          # Word categories and selection logic
├── image_generator.py     # Stable Diffusion integration
├── requirements.txt       # Python dependencies
├── setup_windows.bat      # Windows setup script
├── setup_macos.sh         # macOS/Linux setup script
├── run_windows.bat        # Windows run script
├── run_macos.sh           # macOS/Linux run script
├── README.md              # Main documentation (this file)
└── QUICK_START_GUIDE.md   # Quick reference guide
```

---

## ❓ FAQ

**Q: Do I need an internet connection?**  
A: Yes for first-time setup (model download ~4GB). Afterwards, works completely offline.

**Q: How long does image generation take?**  
A: Depends on hardware:
- NVIDIA GPU: 5-15 seconds
- Apple Silicon: 20-40 seconds
- CPU: 2-5 minutes

**Q: Can I add my own words?**  
A: Yes! Edit `word_banks.py` and add words to any category list. Each list should remain around 30 words for best variety.

**Q: Why does the first run take so long?**  
A: The Stable Diffusion model (~4GB) needs to be downloaded once. It's cached locally for future use.

**Q: Can I use a different AI model?**  
A: Yes! Edit `image_generator.py` and change `self.model_id` to any compatible Stable Diffusion model from Hugging Face.

**Q: Does this work without a GPU?**  
A: Yes, it automatically falls back to CPU mode. Image generation will be slower but fully functional.

**Q: Why are some generated images not perfect?**  
A: AI image generation is probabilistic. Try:
- Adjusting guidance scale (7-9 works best)
- Increasing inference steps (30-40 for better quality)
- Adding specific negative prompts
- Regenerating with a different seed

---

## 🛠️ Advanced Usage

### Custom Words
Edit `word_banks.py` to customize word banks:
```python
self.subject = [
    "your", "custom", "words", "here"
]
```

### Check GPU Status
```bash
# macOS - Check MPS availability
python -c "import torch; print('MPS Available:', torch.backends.mps.is_available())"

# Windows/Linux - Check CUDA availability  
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

### Manual Setup (Alternative)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

---

## 🎓 Technical Details

### Technologies Used
- **Python 3.8+** - Programming language
- **Gradio** - Web UI framework
- **PyTorch** - Deep learning framework
- **Diffusers** - Hugging Face Stable Diffusion library
- **Pillow** - Image processing

### GPU Support
- **NVIDIA CUDA** - Windows/Linux with NVIDIA GPUs
- **Apple MPS** - macOS with Apple Silicon (M1/M2/M3)
- **CPU Fallback** - Works on any system (slower)

### Grammar Rules
The app implements proper English grammar rules:
- **Article selection**: "a" vs "an" based on vowel sounds
- **Gerund formation**: Converts verbs to -ing form (e.g., study→studying, run→running)
- **Continuous tense**: "is [adverb] [verb-ing]" structure
- **Sentence capitalization**: First letter uppercase, ends with period

---

## 🤝 Contributing

Contributions welcome! You can:
- Add more words to word banks
- Improve UI/UX design
- Add new features (e.g., save/load presets)
- Optimize performance
- Fix bugs
- Improve documentation

---

## 📄 License

**MIT License** - Free to use, modify, and distribute.

**Note:** Stable Diffusion model has its own license (CreativeML Open RAIL-M). See [Hugging Face](https://huggingface.co/runwayml/stable-diffusion-v1-5) for details.

---

## 🆘 Support

**Getting Help:**
1. Check this README
2. Review `QUICK_START_GUIDE.md`
3. Check terminal output for error messages
4. Ensure virtual environment is activated
5. Verify all dependencies are installed

**Useful Commands:**
```bash
# Check Python version
python --version

# Check if virtual environment is active
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Check PyTorch installation
python -c "import torch; print(torch.__version__)"
```

---

<div align="center">

## 🎉 Ready to Create!

**Shuffle cards, craft sentences, generate art!**

```bash
# Windows
run_windows.bat

# macOS/Linux
./run_macos.sh
```

🎴 **Happy Creating!** 🎨

---

*Made with ❤️ using Python, Gradio & Stable Diffusion*

</div>
