import random
import time
from typing import Optional, Tuple, Dict

class FalseNewsChecker:
    """
    A simulated statistical machine learning model for checking false news.

    It analyzes text (URL/Content) using keyword frequency and domain patterns,
    and analyzes image data using simulated statistical feature scoring.
    """

    def __init__(self):
        # A statistical feature set based on sensationalism keywords (Weights)
        self.sensational_keywords: Dict[str, float] = {
            "shocking": 0.25, "exclusive": 0.15, "must see": 0.20,
            "disaster": 0.10, "scam": 0.30, "fake news": -0.5, # Negative weight for fact-checking sites
            "truth": 0.05, "exposed": 0.22, "viral": 0.18,
        }
        # Thresholds for decision making
        self.MISINFO_THRESHOLD: float = 0.55
        self.MANIPULATION_THRESHOLD: float = 0.70

    def _analyze_text_for_bias(self, url: str, content: str = "") -> float:
        """
        Simulates statistical text classification (Keyword Frequency + Domain Heuristics).

        A higher score means higher likelihood of sensationalism or misinformation.
        """
        text = (url + " " + content).lower()
        bias_score = 0.0

        # Feature 1: Keyword Frequency Analysis (Statistical Score)
        for keyword, weight in self.sensational_keywords.items():
            count = text.count(keyword)
            bias_score += count * weight

        # Feature 2: Domain Heuristics (Pattern Matching)
        if "blogspot" in url or "wordpress" in url or url.endswith(".co"):
            bias_score += 0.3 # Low authority domain penalty
        if any(bad_pattern in url for bad_pattern in ["hoax", "conspiracy", "rumor"]):
            bias_score += 0.4 # Misinformation pattern penalty

        # Normalize the score (preventing runaway scores while keeping it statistical)
        final_score = min(bias_score / 2.5, 1.0)
        return final_score

    def _analyze_image_for_manipulation(self, file_size_kb: int, noise_factor: float) -> float:
        """
        Simulates statistical image forensic analysis (Deepfake/Manipulation Detection).

        Real forensic tools use features like Noise Residue, ELA (Error Level Analysis),
        and Metadata. We approximate this statistically.

        A higher score means higher likelihood of digital manipulation.
        """
        manipulation_score = 0.0

        # Feature 1: Noise Factor (Simulated Noise Residue Analysis)
        # Deepfakes often have statistically anomalous noise patterns.
        manipulation_score += noise_factor * 0.45

        # Feature 2: File Size vs. Quality (Simulated Compression/Resaving Heuristics)
        # Highly manipulated or over-compressed images might show a low size relative to expected quality.
        if file_size_kb < 100 and noise_factor > 0.5:
            manipulation_score += 0.35 # Small, noisy file implies multiple saves/loss of fidelity

        # Feature 3: Metadata Presence (Simulated Metadata Analysis)
        # Manipulation tools often strip metadata; this is simulated via a random chance
        # weighted by high noise (if noise is high, assume metadata is stripped more often)
        if random.random() < noise_factor:
            manipulation_score += 0.20

        # Clamp the final score
        return min(manipulation_score, 1.0)

    def check(self, url: str, image_features: Optional[Tuple[int, float]] = None, content: str = "") -> str:
        """
        Runs both text and image analysis to determine a verdict.

        Args:
            url (str): The link to the news source.
            image_features (tuple, optional): (file_size_kb, noise_factor) for the image.

        Returns:
            str: The final verdict (e.g., "VERIFIED", "CAUTION", "MISINFORMATION").
        """
        print(f"\n--- Checking URL: {url} ---")

        text_score = self._analyze_text_for_bias(url, content)
        image_score = 0.0

        if image_features:
            file_size_kb, noise_factor = image_features
            image_score = self._analyze_image_for_manipulation(file_size_kb, noise_factor)
            print(f"Image Analysis (Size: {file_size_kb}KB, Noise: {noise_factor:.2f}): {image_score:.2f}")

        print(f"Text Bias Score: {text_score:.2f}")

        # Final Verdict Logic (Bayesian approach simulated via weighted average)
        # Weights: Text carries 60% weight, Image 40% (if present)
        final_misinfo_score = (text_score * 0.6) + (image_score * 0.4 if image_features else text_score)

        verdict = "VERIFIED (Low Risk)"

        if final_misinfo_score > self.MANIPULATION_THRESHOLD:
            verdict = "HIGH MISINFORMATION RISK 🚨"
        elif final_misinfo_score > self.MISINFO_THRESHOLD:
            verdict = "CAUTION ADVISED (High Bias/Uncertainty) ⚠️"

        return f"Final Misinformation Score: {final_misinfo_score:.2f} | VERDICT: {verdict}"

# --- Example Usage with User Input ---

if __name__ == '__main__':
    checker = FalseNewsChecker()

    print("\n--- False News Checker (Simulated Input) ---")

    # 1. Get Text Input
    user_url = input("Enter the URL to check (e.g., https://conspiracyblog.co/shocking-news): ")
    user_content = input("Enter the article content (or leave blank): ")

    # 2. Get Simulated Image Feature Input
    print("\n--- Simulated Image Features (For testing Deepfake/Manipulation) ---")
    print("> NOTE: These are *simulated* features, not actual file analysis.")
    image_check = input("Do you want to include image analysis? (yes/no): ").lower()

    user_image_features: Optional[Tuple[int, float]] = None

    if image_check == 'yes':
        try:
            # Simulated File Size (e.g., 50KB for a small/compressed image, 500KB for a large one)
            file_size_kb = int(input("Enter simulated File Size in KB (e.g., 100): "))
            
            # Simulated Noise/Anomaly Factor (0.0 to 1.0. Higher means more manipulation risk. e.g., 0.1 for clean, 0.9 for suspicious)
            noise_factor = float(input("Enter simulated Noise Factor (0.0 to 1.0, e.g., 0.85): "))
            
            user_image_features = (file_size_kb, noise_factor)
        except ValueError:
            print("Invalid input for image features. Proceeding with Text-Only analysis.")

    # 3. Run Check
    print("\n" + "="*50)
    print("ANALYSIS INITIATED")
    print("="*50)
    
    time.sleep(1) # Simulate processing time

    final_result = checker.check(
        url=user_url,
        content=user_content,
        image_features=user_image_features
    )

    print("\n" + "*"*50)
    print(final_result)
    print("*"*50)