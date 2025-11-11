"""
Image Generator Module
Handles text-to-image generation with cross-platform GPU support
Supports CUDA (Windows/Linux), MPS (macOS Apple Silicon), and CPU fallback
"""

import torch
import platform
import time
from PIL import Image
from typing import Optional, Callable
import os


class ImageGenerator:
    """
    Cross-platform text-to-image generator using Stable Diffusion
    Automatically detects and uses the best available hardware
    """
    
    def __init__(self):
        """Initialize the image generator with appropriate device"""
        self.device = self._detect_device()
        self.model = None
        self.model_loaded = False
        self.model_id = "runwayml/stable-diffusion-v1-5"  # Using SD 1.5 for compatibility
        
        print(f"🖥️  Device detected: {self.device}")
        print(f"📦 Model: {self.model_id}")
        
        # Load model lazily (on first generation)
        self._load_model()
    
    def _detect_device(self) -> str:
        """
        Detect the best available device for image generation
        
        Returns:
            Device string: 'cuda', 'mps', or 'cpu'
        """
        system = platform.system()
        
        # Check for CUDA (NVIDIA GPUs on Windows/Linux)
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA GPU detected: {gpu_name}")
            return device
        
        # Check for MPS (Apple Silicon on macOS)
        if system == "Darwin" and hasattr(torch.backends, "mps"):
            if torch.backends.mps.is_available():
                device = "mps"
                print(f"✅ Apple Silicon MPS detected")
                return device
        
        # Fallback to CPU
        print(f"⚠️  No GPU detected, using CPU (this will be slower)")
        print(f"   Platform: {system} {platform.machine()}")
        return "cpu"
    
    def _load_model(self):
        """Load the Stable Diffusion model"""
        if self.model_loaded:
            return
        
        try:
            print("📦 Loading Stable Diffusion model...")
            print("   (First time may take several minutes to download)")
            
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            
            # Load the model with optimizations
            # Note: MPS requires float32 to avoid black images bug
            if self.device == "mps":
                torch_dtype = torch.float32  # MPS must use float32
            elif self.device == "cuda":
                torch_dtype = torch.float16  # CUDA can use float16
            else:
                torch_dtype = torch.float32  # CPU uses float32
            
            self.model = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch_dtype,
                safety_checker=None,  # Disable safety checker for speed
                requires_safety_checker=False
            )
            
            # Set model to evaluation mode for inference
            self.model.unet.eval()
            self.model.vae.eval()
            
            # Use faster scheduler
            self.model.scheduler = DPMSolverMultistepScheduler.from_config(
                self.model.scheduler.config
            )
            
            # Move to device
            if self.device == "mps":
                # Special handling for MPS to avoid black images
                self.model = self.model.to(self.device)
                # Enable attention slicing for memory efficiency on MPS
                self.model.enable_attention_slicing()
                print("   ⚠️  Using float32 for MPS (prevents black images)")
            elif self.device == "cuda":
                self.model = self.model.to(self.device)
                # Enable memory efficient attention for CUDA
                try:
                    self.model.enable_xformers_memory_efficient_attention()
                except:
                    self.model.enable_attention_slicing()
            else:  # CPU
                self.model = self.model.to(self.device)
                self.model.enable_attention_slicing()
            
            self.model_loaded = True
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("   Falling back to demo mode (placeholder images)")
            self.model_loaded = False
            self.model = None
    
    def generate(self,
                prompt: str,
                negative_prompt: str = "",
                width: int = 512,
                height: int = 512,
                num_inference_steps: int = 25,
                guidance_scale: float = 7.5,
                seed: int = None,
                progress_callback: Optional[Callable] = None) -> Optional[Image.Image]:
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of desired image
            negative_prompt: Things to avoid in the image
            width: Image width (must be divisible by 8)
            height: Image height (must be divisible by 8)
            num_inference_steps: Number of denoising steps (more = better quality)
            guidance_scale: How closely to follow the prompt (7-8 recommended)
            seed: Random seed for reproducibility
            progress_callback: Optional callback for progress updates
            
        Returns:
            Generated PIL Image or None if generation failed
        """
        # Validate dimensions
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        # If model not loaded, try to load it
        if not self.model_loaded:
            if progress_callback:
                progress_callback(0.05, desc="📦 Loading model...")
            self._load_model()
            if progress_callback and self.model_loaded:
                progress_callback(0.15, desc="✅ Model ready")
                time.sleep(0.3)  # Brief pause to show completion
        
        # If still not loaded, use fallback
        if not self.model_loaded or self.model is None:
            return self._generate_placeholder(prompt, width, height, seed)
        
        try:
            # Set random seed
            generator = None
            if seed is not None:
                # MPS generator must use CPU device
                if self.device == "mps":
                    generator = torch.Generator(device="cpu").manual_seed(seed)
                else:
                    generator = torch.Generator(device=self.device).manual_seed(seed)
            
            if progress_callback:
                progress_callback(0.2, desc="🎨 Starting generation...")
                time.sleep(0.2)  # Brief pause before starting
            
            # Generate image with progress tracking
            with torch.inference_mode():
                # Custom progress callback for diffusers
                # Update less frequently to prevent UI text overlap
                def diffusers_callback(step, timestep, latents):
                    if progress_callback:
                        # Only update every 3 steps or on last step to reduce UI flickering
                        if step % 3 == 0 or step == num_inference_steps - 1:
                            # Calculate progress: 20% start + 75% for generation + 5% for finalization
                            current_progress = 0.2 + ((step + 1) / num_inference_steps) * 0.75
                            percentage = int(current_progress * 100)
                            progress_callback(
                                current_progress, 
                                desc=f"🎨 Generating... {percentage}%"
                            )
                
                result = self.model(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    callback=diffusers_callback,
                    callback_steps=1
                )
            
            if progress_callback:
                progress_callback(0.98, desc="✨ Finalizing...")
                time.sleep(0.2)
            
            image = result.images[0]
            
            if progress_callback:
                progress_callback(1.0, desc="✅ Complete!")
                time.sleep(0.3)
            
            return image
            
        except RuntimeError as e:
            error_msg = str(e)
            if "out of memory" in error_msg.lower():
                print("❌ Out of memory error!")
                print("   Try: 1) Reduce image size, 2) Reduce inference steps, 3) Restart the app")
                if progress_callback:
                    progress_callback(1.0, desc="❌ Out of memory")
            else:
                print(f"❌ Runtime error: {error_msg}")
                if progress_callback:
                    progress_callback(1.0, desc="❌ Failed")
            
            # Return placeholder on error
            return self._generate_placeholder(prompt, width, height, seed)
            
        except Exception as e:
            print(f"❌ Unexpected error during generation: {e}")
            if progress_callback:
                progress_callback(1.0, desc="❌ Error")
            return self._generate_placeholder(prompt, width, height, seed)
    
    def _generate_placeholder(self, prompt: str, width: int, height: int, seed: int = None) -> Image.Image:
        """
        Generate a placeholder image when model is not available
        
        Args:
            prompt: Text prompt (used for variation)
            width, height: Image dimensions
            seed: Random seed
            
        Returns:
            Placeholder PIL Image
        """
        import random
        from PIL import ImageDraw, ImageFont
        
        if seed is not None:
            random.seed(seed)
        
        # Create gradient background
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Generate colors based on prompt hash
        prompt_hash = hash(prompt) % 1000000
        random.seed(prompt_hash)
        
        color1 = tuple([random.randint(100, 255) for _ in range(3)])
        color2 = tuple([random.randint(50, 200) for _ in range(3)])
        
        # Draw gradient
        for y in range(height):
            ratio = y / height
            color = tuple([
                int(color1[i] * (1 - ratio) + color2[i] * ratio)
                for i in range(3)
            ])
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add decorative elements
        for _ in range(random.randint(5, 15)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(10, 50)
            color = tuple([random.randint(50, 255) for _ in range(3)])
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
        
        # Add prompt text
        if width >= 300 and height >= 200:
            text = prompt[:40] + "..." if len(prompt) > 40 else prompt
            # Draw text background
            try:
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                padding = 15
                text_x = (width - text_width) // 2
                text_y = height - text_height - 20
                
                # Semi-transparent background
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle(
                    [text_x - padding, text_y - padding,
                     text_x + text_width + padding, text_y + text_height + padding],
                    fill=(0, 0, 0, 160)
                )
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                draw.text((text_x, text_y), text, fill='white')
            except:
                pass
        
        # Add watermark
        watermark = "Demo Mode - Model Not Loaded"
        try:
            draw.text((10, 10), watermark, fill='white')
        except:
            pass
        
        return img
    
    def get_device_info(self) -> str:
        """
        Get detailed device information
        
        Returns:
            String describing the current device setup
        """
        info_parts = []
        
        if self.device == "cuda":
            info_parts.append(f"NVIDIA GPU ({torch.cuda.get_device_name(0)})")
            memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            info_parts.append(f"{memory_gb:.1f}GB VRAM")
        elif self.device == "mps":
            info_parts.append("Apple Silicon GPU (MPS)")
        else:
            info_parts.append("CPU")
            info_parts.append(f"{platform.processor()}")
        
        return " | ".join(info_parts) if info_parts else self.device
    
    def clear_memory(self):
        """Clear GPU memory cache"""
        if self.device == "cuda":
            torch.cuda.empty_cache()
        elif self.device == "mps":
            torch.mps.empty_cache()
    
    def unload_model(self):
        """Unload the model from memory"""
        if self.model is not None:
            del self.model
            self.model = None
            self.model_loaded = False
            self.clear_memory()
            print("✅ Model unloaded from memory")


# Test the image generator if run directly
if __name__ == "__main__":
    print("=" * 70)
    print("Image Generator Test")
    print("=" * 70)
    
    generator = ImageGenerator()
    
    print("\n" + "=" * 70)
    print("Testing image generation...")
    print("=" * 70)
    
    test_prompt = "a beautiful sunset over mountains, highly detailed, 8k"
    print(f"\nPrompt: {test_prompt}")
    print("Generating image...")
    
    image = generator.generate(
        prompt=test_prompt,
        negative_prompt="blurry, bad quality",
        width=512,
        height=512,
        num_inference_steps=20,
        seed=42
    )
    
    if image:
        output_path = "test_output.png"
        image.save(output_path)
        print(f"✅ Image saved to: {output_path}")
    else:
        print("❌ Image generation failed")
    
    print("\n" + "=" * 70)
    print("Device info:", generator.get_device_info())
    print("=" * 70)

