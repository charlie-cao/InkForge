"""Platform-specific optimization processor for InkForge."""

import re
import asyncio
from typing import Dict, List, Any, Optional

from ..models.content import ContentRequest, Platform
from ..core.config import Config


class PlatformOptimizer:
    """Optimizes content for specific platforms."""
    
    def __init__(self, config: Config):
        """Initialize platform optimizer."""
        self.config = config
        
        # Platform-specific optimization rules
        self.platform_rules = {
            Platform.MEDIUM: {
                "max_title_length": 100,
                "preferred_structure": ["subtitle", "headings", "bullet_points"],
                "formatting": {
                    "use_subheadings": True,
                    "use_bullet_points": True,
                    "use_quotes": True,
                    "use_emphasis": True,
                },
                "engagement": ["claps", "responses", "highlights"],
            },
            Platform.ZHIHU: {
                "max_title_length": 50,
                "preferred_structure": ["question_format", "data_support", "personal_experience"],
                "formatting": {
                    "use_numbers": True,
                    "use_data": True,
                    "use_examples": True,
                    "chinese_punctuation": True,
                },
                "engagement": ["upvotes", "comments", "follows"],
            },
            Platform.TWITTER: {
                "max_title_length": 280,
                "preferred_structure": ["thread", "hooks", "short_paragraphs"],
                "formatting": {
                    "use_emojis": True,
                    "use_hashtags": True,
                    "thread_numbering": True,
                    "character_limit": 280,
                },
                "engagement": ["retweets", "likes", "replies"],
            },
            Platform.XIAOHONGSHU: {
                "max_title_length": 20,
                "preferred_structure": ["visual_appeal", "lifestyle_focus", "personal_story"],
                "formatting": {
                    "use_emojis": True,
                    "use_tags": True,
                    "visual_breaks": True,
                    "casual_tone": True,
                },
                "engagement": ["likes", "saves", "shares"],
            },
            Platform.LINKEDIN: {
                "max_title_length": 150,
                "preferred_structure": ["professional_insight", "industry_relevance", "networking"],
                "formatting": {
                    "professional_tone": True,
                    "use_statistics": True,
                    "industry_keywords": True,
                    "call_to_connect": True,
                },
                "engagement": ["likes", "comments", "shares", "connections"],
            },
            Platform.SUBSTACK: {
                "max_title_length": 120,
                "preferred_structure": ["newsletter_format", "sections", "personal_voice"],
                "formatting": {
                    "use_sections": True,
                    "personal_anecdotes": True,
                    "subscriber_focus": True,
                    "email_friendly": True,
                },
                "engagement": ["subscriptions", "comments", "shares"],
            },
        }
    
    def process(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Process content synchronously."""
        return asyncio.run(self.process_async(content, request))
    
    async def process_async(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Process content asynchronously."""
        if not self.config.enable_platform_optimization:
            return {"content": content, "notes": []}
        
        platform = request.platform
        if platform not in self.platform_rules:
            return {"content": content, "notes": [f"No specific optimization rules for {platform.value}"]}
        
        rules = self.platform_rules[platform]
        optimized_content = content
        notes = []
        
        # Apply platform-specific optimizations
        if platform == Platform.MEDIUM:
            result = self._optimize_for_medium(optimized_content, rules)
        elif platform == Platform.ZHIHU:
            result = self._optimize_for_zhihu(optimized_content, rules)
        elif platform == Platform.TWITTER:
            result = self._optimize_for_twitter(optimized_content, rules)
        elif platform == Platform.XIAOHONGSHU:
            result = self._optimize_for_xiaohongshu(optimized_content, rules)
        elif platform == Platform.LINKEDIN:
            result = self._optimize_for_linkedin(optimized_content, rules)
        elif platform == Platform.SUBSTACK:
            result = self._optimize_for_substack(optimized_content, rules)
        else:
            result = {"content": optimized_content, "notes": []}
        
        return result
    
    def _optimize_for_medium(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Medium."""
        notes = []
        
        # Add subtitle if not present
        if not re.search(r'^.+\n\n.+$', content[:200]):
            lines = content.split('\n')
            if len(lines) > 0:
                # Add a subtitle after the first line (title)
                subtitle = "A comprehensive guide to understanding this important topic."
                content = f"{lines[0]}\n\n{subtitle}\n\n" + '\n'.join(lines[1:])
                notes.append("Added subtitle for Medium format")
        
        # Ensure proper heading structure
        content = self._add_medium_headings(content)
        notes.append("Optimized heading structure for Medium")
        
        # Add bullet points where appropriate
        content = self._add_bullet_points(content)
        
        # Add pull quotes
        content = self._add_pull_quotes(content)
        notes.append("Added formatting elements for better Medium readability")
        
        return {"content": content, "notes": notes}
    
    def _optimize_for_zhihu(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Zhihu."""
        notes = []
        
        # Convert to Q&A format if not already
        if not content.startswith(("问题：", "题主问：")):
            first_sentence = content.split('.')[0] if '.' in content else content[:50]
            content = f"问题：{first_sentence}？\n\n我的回答：\n\n{content}"
            notes.append("Converted to Zhihu Q&A format")
        
        # Add data and examples
        content = self._add_zhihu_data_support(content)
        notes.append("Added data support and examples for Zhihu audience")
        
        # Use Chinese punctuation
        content = self._convert_to_chinese_punctuation(content)
        
        # Add personal experience markers
        content = self._add_personal_experience_markers(content)
        notes.append("Added personal experience elements")
        
        return {"content": content, "notes": notes}
    
    def _optimize_for_twitter(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Twitter threads."""
        notes = []
        
        # Convert to thread format
        content = self._convert_to_twitter_thread(content)
        notes.append("Converted to Twitter thread format")
        
        # Add emojis
        content = self._add_twitter_emojis(content)
        
        # Add hashtags
        content = self._add_twitter_hashtags(content)
        notes.append("Added emojis and hashtags for Twitter")
        
        return {"content": content, "notes": notes}
    
    def _optimize_for_xiaohongshu(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Xiaohongshu (Little Red Book)."""
        notes = []
        
        # Add visual breaks with emojis
        content = self._add_xiaohongshu_visual_breaks(content)
        
        # Make tone more casual and personal
        content = self._make_casual_tone(content)
        notes.append("Adjusted tone for Xiaohongshu audience")
        
        # Add lifestyle elements
        content = self._add_lifestyle_elements(content)
        notes.append("Added lifestyle-focused elements")
        
        return {"content": content, "notes": notes}
    
    def _optimize_for_linkedin(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for LinkedIn."""
        notes = []
        
        # Add professional context
        content = self._add_professional_context(content)
        notes.append("Added professional context for LinkedIn")
        
        # Add industry statistics
        content = self._add_industry_statistics(content)
        
        # Add networking call-to-action
        content += "\n\n💼 What's your experience with this? Let's connect and share insights!"
        notes.append("Added professional networking elements")
        
        return {"content": content, "notes": notes}
    
    def _optimize_for_substack(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for Substack newsletter."""
        notes = []
        
        # Add newsletter greeting
        content = f"Hello subscribers! 👋\n\n{content}"
        
        # Add sections
        content = self._add_newsletter_sections(content)
        notes.append("Added newsletter-style sections")
        
        # Add subscription prompt
        content += "\n\n📧 If you found this valuable, please share it with others who might benefit. And don't forget to subscribe for more insights!"
        notes.append("Added subscription call-to-action")
        
        return {"content": content, "notes": notes}
    
    def _add_medium_headings(self, content: str) -> str:
        """Add proper heading structure for Medium."""
        paragraphs = content.split('\n\n')
        
        # Add headings to longer paragraphs
        for i in range(1, len(paragraphs)):
            if len(paragraphs[i]) > 200 and not paragraphs[i].startswith('#'):
                # Try to extract a heading from the first sentence
                first_sentence = paragraphs[i].split('.')[0]
                if len(first_sentence) < 80:
                    paragraphs[i] = f"## {first_sentence}\n\n{paragraphs[i][len(first_sentence)+1:]}"
        
        return '\n\n'.join(paragraphs)
    
    def _add_bullet_points(self, content: str) -> str:
        """Add bullet points where appropriate."""
        # Look for lists in the content
        content = re.sub(
            r'(\d+\.\s+[^\n]+(?:\n\d+\.\s+[^\n]+)*)',
            lambda m: '\n'.join(f"• {line[3:]}" for line in m.group(1).split('\n')),
            content
        )
        return content
    
    def _add_pull_quotes(self, content: str) -> str:
        """Add pull quotes for emphasis."""
        sentences = content.split('. ')
        
        for i, sentence in enumerate(sentences):
            if (50 < len(sentence) < 120 and 
                any(word in sentence.lower() for word in ['important', 'key', 'crucial', 'remember'])):
                sentences[i] = f"\n\n> {sentence}\n\n"
                break  # Only add one pull quote
        
        return '. '.join(sentences)
    
    def _add_zhihu_data_support(self, content: str) -> str:
        """Add data support for Zhihu content."""
        # Add some example data points
        data_examples = [
            "根据最新研究显示，",
            "数据表明，",
            "调查发现，",
            "统计显示，",
        ]
        
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 2:
            data_intro = f"{data_examples[0]}这个现象在实际应用中非常常见。"
            paragraphs.insert(2, data_intro)
        
        return '\n\n'.join(paragraphs)
    
    def _convert_to_chinese_punctuation(self, content: str) -> str:
        """Convert to Chinese punctuation."""
        # Basic punctuation conversion
        content = content.replace('?', '？')
        content = content.replace('!', '！')
        content = content.replace(',', '，')
        content = content.replace(';', '；')
        content = content.replace(':', '：')
        
        return content
    
    def _add_personal_experience_markers(self, content: str) -> str:
        """Add personal experience markers for Zhihu."""
        markers = [
            "在我的经验中，",
            "我发现，",
            "从我的观察来看，",
            "根据我的实践，",
        ]
        
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            marker = markers[0]
            paragraphs[1] = f"{marker}{paragraphs[1]}"
        
        return '\n\n'.join(paragraphs)
    
    def _convert_to_twitter_thread(self, content: str) -> str:
        """Convert content to Twitter thread format."""
        paragraphs = content.split('\n\n')
        
        # Limit each tweet to ~250 characters
        tweets = []
        current_tweet = ""
        
        for para in paragraphs:
            if len(current_tweet + para) < 250:
                current_tweet += para + " "
            else:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = para + " "
        
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Number the tweets
        numbered_tweets = []
        for i, tweet in enumerate(tweets):
            if i == 0:
                numbered_tweets.append(f"🧵 {tweet}")
            else:
                numbered_tweets.append(f"{i+1}/ {tweet}")
        
        return '\n\n'.join(numbered_tweets)
    
    def _add_twitter_emojis(self, content: str) -> str:
        """Add relevant emojis for Twitter."""
        emoji_map = {
            'important': '⚠️',
            'tip': '💡',
            'key': '🔑',
            'success': '✅',
            'warning': '⚠️',
            'money': '💰',
            'time': '⏰',
            'growth': '📈',
        }
        
        for word, emoji in emoji_map.items():
            if word in content.lower():
                content = content.replace(word, f"{emoji} {word}", 1)
                break
        
        return content
    
    def _add_twitter_hashtags(self, content: str) -> str:
        """Add relevant hashtags for Twitter."""
        # Add hashtags at the end
        hashtags = ["#ContentCreation", "#BloggingTips", "#WritingCommunity"]
        content += f"\n\n{' '.join(hashtags)}"
        
        return content
    
    def _add_xiaohongshu_visual_breaks(self, content: str) -> str:
        """Add visual breaks with emojis for Xiaohongshu."""
        visual_breaks = ["✨", "🌟", "💫", "🔥", "💖", "🎯"]
        
        paragraphs = content.split('\n\n')
        for i in range(1, len(paragraphs), 2):
            if i < len(paragraphs):
                break_emoji = visual_breaks[i % len(visual_breaks)]
                paragraphs[i] = f"{break_emoji} {paragraphs[i]}"
        
        return '\n\n'.join(paragraphs)
    
    def _make_casual_tone(self, content: str) -> str:
        """Make tone more casual for Xiaohongshu."""
        # Replace formal words with casual ones
        casual_replacements = {
            'Furthermore': '还有',
            'However': '不过',
            'Therefore': '所以',
            'Additionally': '另外',
        }
        
        for formal, casual in casual_replacements.items():
            content = content.replace(formal, casual)
        
        return content
    
    def _add_lifestyle_elements(self, content: str) -> str:
        """Add lifestyle-focused elements."""
        lifestyle_phrases = [
            "在日常生活中，",
            "我的个人体验是，",
            "分享一个小技巧：",
            "生活中我发现，",
        ]
        
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            phrase = lifestyle_phrases[0]
            paragraphs[1] = f"{phrase}{paragraphs[1]}"
        
        return '\n\n'.join(paragraphs)
    
    def _add_professional_context(self, content: str) -> str:
        """Add professional context for LinkedIn."""
        professional_intros = [
            "In today's business environment,",
            "From a professional standpoint,",
            "In my industry experience,",
            "As professionals, we often encounter",
        ]
        
        intro = professional_intros[0]
        content = f"{intro} {content}"
        
        return content
    
    def _add_industry_statistics(self, content: str) -> str:
        """Add industry statistics for LinkedIn."""
        # Add a statistics section
        stats_section = "\n\n📊 Key Statistics:\n• 85% of professionals report this challenge\n• Industry growth rate: 15% annually\n• ROI improvement: up to 40%"
        
        # Insert after first paragraph
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            paragraphs.insert(2, stats_section.strip())
        
        return '\n\n'.join(paragraphs)
    
    def _add_newsletter_sections(self, content: str) -> str:
        """Add newsletter-style sections."""
        sections = [
            "📖 Today's Topic",
            "💡 Key Insights",
            "🎯 Action Items",
            "🤔 Final Thoughts",
        ]
        
        paragraphs = content.split('\n\n')
        
        # Add section headers
        if len(paragraphs) >= 4:
            for i, section in enumerate(sections):
                if i * 2 < len(paragraphs):
                    paragraphs[i * 2] = f"## {section}\n\n{paragraphs[i * 2]}"
        
        return '\n\n'.join(paragraphs)
