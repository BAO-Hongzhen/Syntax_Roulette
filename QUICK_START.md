# 🚀 Quick Start Guide - Syntax Roulette

Quick reference for getting started with the Syntax Roulette text-to-image generator.

---

## 📦 Installation

### Windows
```bash
setup_windows.bat
```

### macOS / Linux
```bash
chmod +x setup_macos.sh run_macos.sh
./setup_macos.sh
```

**First time**: Downloads ~4GB model (5-15 minutes)

---

## ▶️ Running the App

### Windows
```bash
run_windows.bat
```

### macOS / Linux
```bash
./run_macos.sh
```

Opens at: `http://localhost:7860`

---

## 🎮 How to Use

### 1. Shuffle & Pick Cards 🎴
- Click **"Shuffle & Pick Cards"**
- Watch the shuffling animation
- 5 words selected (one from each category)
- Edit words if desired

### 2. Generate Sentence 📝
- Click **"Generate Sentence"**
- Gets grammatically correct English sentence
- Example: *"A little baby is carefully studying on a rooftop."*

### 3. Generate Image 🎨
- (Optional) Adjust settings
- Click **"Generate Image"**
- Wait ~30 seconds (Apple Silicon) or ~10 seconds (NVIDIA GPU)
- View your AI-generated image!

---

## ⚙️ Settings Quick Reference

### Default (Recommended)
```
Size: 512x512
Steps: 25
Guidance: 7.5
Time: ~30s (Apple Silicon), ~10s (NVIDIA)
```

### Faster
```
Steps: 15-20
Guidance: 7.0
Time: ~15-20s (Apple Silicon)
```

### Higher Quality
```
Steps: 35-40
Guidance: 8.5
Time: ~45-50s (Apple Silicon)
```

---

## 🎯 Word Categories

| Category | Count | Examples |
|----------|-------|----------|
| Subject | 30 | boy, cat, robot, wizard |
| Predicate | 30 | eat, play, fly, dance |
| Attributive | 30 | big, happy, red, silly |
| Adverbial | 30 | quickly, carefully, happily |
| Complement | 30 | a pizza, in the kitchen, on the moon |

**Total: 150 words**

---

## 🔧 Common Issues

### Black Images (macOS)
✅ Fixed automatically - uses float32 for MPS

### Out of Memory
- Reduce image size to 384x384 or 256x256
- Reduce steps to 15-20
- Restart app

### Slow Generation
- Reduce steps (15-25 is enough)
- Check GPU detection in terminal

### Model Won't Load
- Check internet connection
- Ensure 10GB free space
- Rerun setup script

---

## 💡 Tips

1. **Default settings work great** - no need to adjust for most uses
2. **Edit words** before generating sentence for custom combinations
3. **Use negative prompts** to avoid unwanted elements (e.g., "blurry, distorted")
4. **Try different seeds** for variations of the same prompt
5. **Start with 25 steps** - good balance of speed and quality

---

## 📚 More Info

- **Full Documentation**: See `README.md`
- **Custom Words**: Edit `word_banks.py`
- **Technical Details**: Check terminal output

---

## 🆘 Quick Commands

```bash
# Check Python version
python --version

# Check if venv is active
which python

# Reinstall dependencies
pip install -r requirements.txt

# Check GPU (macOS)
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"

# Check GPU (Windows/Linux)
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

---

## 🎴 Example Workflow

1. Run: `./run_macos.sh` (or `run_windows.bat`)
2. Click "Shuffle & Pick Cards"
3. Click "Generate Sentence"
4. Click "Generate Image"
5. Download and share your creation! 🎨

**That's it!** 🎉

---

*Need detailed help? See README.md*

