"""
Style Engine - Manages author style profiles and generates blended writing prompts
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger
import textstat


class AuthorProfile:
    """Represents an author's writing style characteristics"""

    def __init__(self, data: Dict[str, Any]):
        self.name = data["name"]
        self.genre = data["genre"]

        # Style characteristics
        self.tone = data["style"]["tone"]  # dark, light, neutral, etc.
        self.formality = data["style"]["formality"]  # casual, formal, balanced
        self.sentence_length = data["style"]["sentence_length"]  # short, medium, long
        self.avg_sentence_words = data["style"]["avg_sentence_words"]

        # Voice characteristics
        self.pov_preference = data["voice"]["pov_preference"]  # 1st, 3rd limited, etc.
        self.narrative_style = data["voice"]["narrative_style"]
        self.dialogue_ratio = data["voice"]["dialogue_ratio"]

        # Vocabulary
        self.vocab_complexity = data["vocabulary"]["complexity"]  # simple, moderate, complex
        self.reading_level = data["vocabulary"]["reading_level"]

        # Signature elements
        self.signature_techniques = data["signature"]["techniques"]
        self.common_themes = data["signature"]["common_themes"]

        # Prompt template
        self.style_descriptor = data["style_descriptor"]

    @classmethod
    def from_file(cls, filepath: Path) -> "AuthorProfile":
        """Load author profile from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(data)


class StyleEngine:
    """Manages style profiles and generates blended writing prompts"""

    def __init__(self, profiles_dir: Path):
        """Initialize style engine

        Args:
            profiles_dir: Directory containing author profile JSON files
        """
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, AuthorProfile] = {}
        self.load_profiles()

    def load_profiles(self):
        """Load all author profiles from directory"""
        if not self.profiles_dir.exists():
            logger.warning(f"Profiles directory not found: {self.profiles_dir}")
            return

        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                profile = AuthorProfile.from_file(profile_file)
                self.profiles[profile.name] = profile
                logger.info(f"Loaded profile: {profile.name}")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")

    def get_profile(self, author_name: str) -> Optional[AuthorProfile]:
        """Get author profile by name"""
        return self.profiles.get(author_name)

    def list_authors(self) -> List[str]:
        """Get list of available author names"""
        return sorted(self.profiles.keys())

    def blend_styles(
        self, style_mix: Dict[str, float], tone: float = 0.5, formality: float = 0.5, sentence_length: float = 0.5
    ) -> str:
        """Generate blended style prompt

        Args:
            style_mix: Dict of {author_name: percentage} (must sum to 1.0)
            tone: Slider value 0.0 (dark) to 1.0 (light)
            formality: Slider value 0.0 (casual) to 1.0 (formal)
            sentence_length: Slider value 0.0 (short) to 1.0 (long)

        Returns:
            Style instruction prompt for LLM
        """
        # Validate style mix
        total_percentage = sum(style_mix.values())
        if not (0.99 <= total_percentage <= 1.01):
            raise ValueError(f"Style percentages must sum to 1.0 (got {total_percentage})")

        # Build style descriptor
        style_parts = []

        for author, percentage in sorted(style_mix.items(), key=lambda x: x[1], reverse=True):
            profile = self.get_profile(author)
            if not profile:
                logger.warning(f"Profile not found: {author}")
                continue

            if percentage > 0.05:  # Only include if >5%
                pct_str = f"{int(percentage * 100)}%"
                style_parts.append(f"{pct_str} {profile.style_descriptor}")

        blended_descriptor = " + ".join(style_parts)

        # Generate tone instruction
        tone_instruction = self._get_tone_instruction(tone)
        formality_instruction = self._get_formality_instruction(formality)
        length_instruction = self._get_length_instruction(sentence_length)

        # Combine into full prompt
        prompt_template = f"""Write in a blended style: {blended_descriptor}

Tone: {tone_instruction}
Formality: {formality_instruction}
Sentence Structure: {length_instruction}

Maintain consistency with these style guidelines throughout your writing."""

        return prompt_template

    def _get_tone_instruction(self, value: float) -> str:
        """Convert tone slider (0.0-1.0) to instruction"""
        if value < 0.2:
            return "Very dark, ominous, serious"
        elif value < 0.4:
            return "Dark but accessible, tension-filled"
        elif value < 0.6:
            return "Balanced, natural tone"
        elif value < 0.8:
            return "Light, optimistic, hopeful"
        else:
            return "Very light, whimsical, humorous"

    def _get_formality_instruction(self, value: float) -> str:
        """Convert formality slider (0.0-1.0) to instruction"""
        if value < 0.2:
            return "Very casual, conversational, everyday language"
        elif value < 0.4:
            return "Mostly casual with natural flow"
        elif value < 0.6:
            return "Balanced formality, professional but accessible"
        elif value < 0.8:
            return "Formal, polished, sophisticated"
        else:
            return "Very formal, literary, elevated prose"

    def _get_length_instruction(self, value: float) -> str:
        """Convert sentence length slider (0.0-1.0) to instruction"""
        if value < 0.2:
            return "Very short, punchy sentences (5-10 words average)"
        elif value < 0.4:
            return "Short to medium sentences (10-15 words average)"
        elif value < 0.6:
            return "Medium length sentences (15-20 words average)"
        elif value < 0.8:
            return "Long, flowing sentences (20-25 words average)"
        else:
            return "Very long, complex sentences (25+ words average)"

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for style characteristics

        Args:
            text: Text sample to analyze

        Returns:
            Dict with style metrics
        """
        if not text or len(text.strip()) == 0:
            return {}

        sentences = text.split(".")
        sentence_count = len([s for s in sentences if s.strip()])

        words = text.split()
        word_count = len(words)

        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Use textstat for readability metrics
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        reading_level = textstat.text_standard(text, float_output=True)

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "flesch_reading_ease": round(flesch_reading_ease, 1),
            "reading_level": reading_level,
        }

    def generate_prompt(
        self,
        user_instruction: str,
        style_mix: Dict[str, float],
        tone: float = 0.5,
        formality: float = 0.5,
        sentence_length: float = 0.5,
        context: Optional[str] = None,
    ) -> str:
        """Generate complete writing prompt with style blending

        Args:
            user_instruction: User's writing request (e.g., "Write a tense scene where...")
            style_mix: Author style percentages
            tone: Tone slider value
            formality: Formality slider value
            sentence_length: Sentence length slider value
            context: Optional context from previous chapters

        Returns:
            Complete prompt ready to send to LLM
        """
        style_instruction = self.blend_styles(style_mix, tone, formality, sentence_length)

        prompt_parts = [style_instruction, "", f"Task: {user_instruction}"]

        if context:
            prompt_parts.append("")
            prompt_parts.append(f"Context (maintain consistency):\n{context}")

        return "\n".join(prompt_parts)
