"""Content humanization processor for InkForge."""

import re
import random
import asyncio
from typing import List, Dict, Any, Optional, Tuple

from ..models.content import ContentRequest
from ..core.config import Config


class Humanizer:
    """Humanizes AI-generated content to make it more natural and human-like."""
    
    def __init__(self, config: Config):
        """Initialize humanizer."""
        self.config = config
        
        # Humanization patterns and replacements
        self.patterns = {
            # Add personal touches
            "personal_touches": [
                (r'\bIn conclusion\b', ['To wrap up', 'In summary', 'Looking back', 'All things considered']),
                (r'\bFurthermore\b', ['Also', 'Plus', 'What\'s more', 'On top of that']),
                (r'\bHowever\b', ['But', 'Though', 'That said', 'On the flip side']),
                (r'\bTherefore\b', ['So', 'That\'s why', 'This means', 'As a result']),
                (r'\bAdditionally\b', ['Also', 'Plus', 'And', 'What\'s more']),
            ],
            
            # Add conversational elements
            "conversational": [
                (r'^([A-Z][^.!?]*[.!?])', [
                    r'You know, \1',
                    r'Here\'s the thing: \1',
                    r'Let me tell you, \1',
                    r'I\'ve found that \1',
                ]),
            ],
            
            # Add uncertainty and hedging
            "hedging": [
                (r'\bis\b([^.!?]*important[^.!?]*)', ['might be\\1', 'seems to be\\1', 'appears to be\\1']),
                (r'\bwill\b([^.!?]*help[^.!?]*)', ['can\\1', 'might\\1', 'could\\1']),
                (r'\balways\b', ['often', 'usually', 'typically', 'generally']),
                (r'\bnever\b', ['rarely', 'seldom', 'hardly ever']),
            ],
            
            # Add personal experience markers
            "experience_markers": [
                'In my experience,',
                'I\'ve noticed that',
                'From what I\'ve seen,',
                'I\'ve found that',
                'What I\'ve learned is',
                'My take on this is',
            ],
            
            # Add thinking markers
            "thinking_markers": [
                'I think',
                'I believe',
                'It seems to me',
                'My guess is',
                'I suspect',
                'I\'d say',
            ],
        }
        
        # Filler words and phrases
        self.fillers = [
            'you know',
            'I mean',
            'sort of',
            'kind of',
            'basically',
            'essentially',
            'actually',
            'really',
            'pretty much',
            'more or less',
        ]
        
        # Contractions
        self.contractions = {
            'do not': 'don\'t',
            'does not': 'doesn\'t',
            'did not': 'didn\'t',
            'will not': 'won\'t',
            'would not': 'wouldn\'t',
            'could not': 'couldn\'t',
            'should not': 'shouldn\'t',
            'cannot': 'can\'t',
            'is not': 'isn\'t',
            'are not': 'aren\'t',
            'was not': 'wasn\'t',
            'were not': 'weren\'t',
            'have not': 'haven\'t',
            'has not': 'hasn\'t',
            'had not': 'hadn\'t',
            'it is': 'it\'s',
            'that is': 'that\'s',
            'there is': 'there\'s',
            'here is': 'here\'s',
            'what is': 'what\'s',
            'where is': 'where\'s',
            'when is': 'when\'s',
            'how is': 'how\'s',
            'who is': 'who\'s',
            'I am': 'I\'m',
            'you are': 'you\'re',
            'we are': 'we\'re',
            'they are': 'they\'re',
            'I have': 'I\'ve',
            'you have': 'you\'ve',
            'we have': 'we\'ve',
            'they have': 'they\'ve',
            'I will': 'I\'ll',
            'you will': 'you\'ll',
            'we will': 'we\'ll',
            'they will': 'they\'ll',
        }
    
    def process(self, content: str, request: ContentRequest) -> str:
        """Process content synchronously."""
        return asyncio.run(self.process_async(content, request))
    
    async def process_async(self, content: str, request: ContentRequest) -> str:
        """Process content asynchronously."""
        if not self.config.enable_humanization:
            return content
        
        # Apply humanization techniques
        humanized_content = content
        
        # 1. Add contractions
        humanized_content = self._add_contractions(humanized_content)
        
        # 2. Replace formal transitions
        humanized_content = self._replace_formal_transitions(humanized_content)
        
        # 3. Add personal touches
        humanized_content = self._add_personal_touches(humanized_content)
        
        # 4. Add conversational elements
        humanized_content = self._add_conversational_elements(humanized_content)
        
        # 5. Add hedging and uncertainty
        humanized_content = self._add_hedging(humanized_content)
        
        # 6. Add occasional fillers (sparingly)
        humanized_content = self._add_fillers(humanized_content)
        
        # 7. Vary sentence structure
        humanized_content = self._vary_sentence_structure(humanized_content)
        
        # 8. Add minor imperfections
        humanized_content = self._add_minor_imperfections(humanized_content)
        
        return humanized_content
    
    def _add_contractions(self, content: str) -> str:
        """Add contractions to make text more conversational."""
        for full_form, contraction in self.contractions.items():
            # Case-insensitive replacement with proper capitalization
            pattern = re.compile(re.escape(full_form), re.IGNORECASE)
            
            def replace_func(match):
                original = match.group(0)
                if original[0].isupper():
                    return contraction.capitalize()
                return contraction
            
            content = pattern.sub(replace_func, content)
        
        return content
    
    def _replace_formal_transitions(self, content: str) -> str:
        """Replace formal transitions with more casual ones."""
        for pattern, replacements in self.patterns["personal_touches"]:
            if random.random() < 0.3:  # Apply to 30% of matches
                replacement = random.choice(replacements)
                content = re.sub(pattern, replacement, content, count=1)
        
        return content
    
    def _add_personal_touches(self, content: str) -> str:
        """Add personal experience markers."""
        sentences = content.split('. ')
        
        # Add personal markers to some sentences
        for i in range(len(sentences)):
            if random.random() < 0.1 and len(sentences[i]) > 50:  # 10% chance for longer sentences
                marker = random.choice(self.patterns["experience_markers"])
                sentences[i] = f"{marker} {sentences[i].lower()}"
        
        return '. '.join(sentences)
    
    def _add_conversational_elements(self, content: str) -> str:
        """Add conversational elements."""
        paragraphs = content.split('\n\n')
        
        for i in range(len(paragraphs)):
            if random.random() < 0.2:  # 20% chance per paragraph
                # Add conversational starter
                first_sentence = paragraphs[i].split('.')[0]
                if len(first_sentence) > 30:
                    starter = random.choice(['You know what?', 'Here\'s the thing:', 'Let me be honest:'])
                    paragraphs[i] = f"{starter} {paragraphs[i]}"
        
        return '\n\n'.join(paragraphs)
    
    def _add_hedging(self, content: str) -> str:
        """Add hedging and uncertainty to make content less absolute."""
        for pattern, replacements in self.patterns["hedging"]:
            if random.random() < 0.2:  # Apply to 20% of matches
                replacement = random.choice(replacements)
                content = re.sub(pattern, replacement, content, count=1)
        
        return content
    
    def _add_fillers(self, content: str) -> str:
        """Add occasional filler words (very sparingly)."""
        sentences = content.split('. ')
        
        for i in range(len(sentences)):
            if random.random() < 0.05 and len(sentences[i]) > 40:  # 5% chance for longer sentences
                filler = random.choice(self.fillers)
                # Insert filler after first few words
                words = sentences[i].split()
                if len(words) > 3:
                    insert_pos = random.randint(2, min(5, len(words) - 1))
                    words.insert(insert_pos, f"{filler},")
                    sentences[i] = ' '.join(words)
        
        return '. '.join(sentences)
    
    def _vary_sentence_structure(self, content: str) -> str:
        """Vary sentence structure to avoid monotony."""
        sentences = content.split('. ')
        
        for i in range(len(sentences)):
            sentence = sentences[i].strip()
            if len(sentence) > 60 and random.random() < 0.15:  # 15% chance for long sentences
                # Try to split long sentences
                if ' and ' in sentence:
                    parts = sentence.split(' and ', 1)
                    if len(parts[1]) > 20:
                        sentences[i] = f"{parts[0]}. And {parts[1]}"
                elif ' but ' in sentence:
                    parts = sentence.split(' but ', 1)
                    if len(parts[1]) > 20:
                        sentences[i] = f"{parts[0]}. But {parts[1]}"
        
        return '. '.join(sentences)
    
    def _add_minor_imperfections(self, content: str) -> str:
        """Add very minor imperfections to make content more human."""
        # Occasionally start sentences with "And" or "But"
        sentences = content.split('. ')
        
        for i in range(1, len(sentences)):  # Skip first sentence
            if random.random() < 0.08:  # 8% chance
                sentence = sentences[i].strip()
                if not sentence.startswith(('And', 'But', 'So')):
                    if 'however' in sentence.lower():
                        sentences[i] = sentence.replace('However', 'But', 1).replace('however', 'but', 1)
                    elif random.random() < 0.5:
                        sentences[i] = f"And {sentence.lower()}"
        
        return '. '.join(sentences)
    
    def get_humanization_stats(self, original: str, humanized: str) -> Dict[str, Any]:
        """Get statistics about humanization changes."""
        original_words = len(original.split())
        humanized_words = len(humanized.split())
        
        # Count contractions
        contraction_count = sum(1 for contraction in self.contractions.values() 
                              if contraction in humanized)
        
        # Count personal markers
        personal_marker_count = sum(1 for marker in self.patterns["experience_markers"] 
                                  if marker.lower() in humanized.lower())
        
        # Count fillers
        filler_count = sum(1 for filler in self.fillers 
                          if filler in humanized.lower())
        
        return {
            "original_word_count": original_words,
            "humanized_word_count": humanized_words,
            "word_count_change": humanized_words - original_words,
            "contractions_added": contraction_count,
            "personal_markers_added": personal_marker_count,
            "fillers_added": filler_count,
            "humanization_score": min(1.0, (contraction_count + personal_marker_count * 2 + filler_count) / 10),
        }
