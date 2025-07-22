"""Engagement optimization processor for InkForge."""

import re
import random
import asyncio
from typing import List, Dict, Any, Optional

from ..models.content import ContentRequest, Goal
from ..core.config import Config


class EngagementOptimizer:
    """Optimizes content for better engagement and interaction."""
    
    def __init__(self, config: Config):
        """Initialize engagement optimizer."""
        self.config = config
        
        # Engagement patterns by goal
        self.engagement_patterns = {
            Goal.ENGAGEMENT: {
                "questions": [
                    "What do you think about this?",
                    "Have you experienced something similar?",
                    "What's your take on this?",
                    "How do you handle this situation?",
                    "What would you add to this list?",
                ],
                "call_to_action": [
                    "Share your thoughts in the comments below!",
                    "Let me know what you think!",
                    "I'd love to hear your perspective!",
                    "Drop a comment and let's discuss!",
                ],
                "hooks": [
                    "Here's something that might surprise you:",
                    "You won't believe what happened next:",
                    "This changed everything:",
                    "The results were shocking:",
                ],
            },
            Goal.SHARES: {
                "shareable_quotes": [
                    "💡 Key insight:",
                    "🔥 Remember this:",
                    "✨ Pro tip:",
                    "🎯 Bottom line:",
                ],
                "share_prompts": [
                    "Found this helpful? Share it with someone who needs to see this!",
                    "If this resonates with you, pass it along!",
                    "Think others would benefit? Hit that share button!",
                ],
            },
            Goal.COMMENTS: {
                "discussion_starters": [
                    "What's your experience with this?",
                    "Am I missing something here?",
                    "What would you do differently?",
                    "Which approach works best for you?",
                ],
                "controversial_takes": [
                    "Here's an unpopular opinion:",
                    "This might be controversial, but:",
                    "Not everyone will agree with this:",
                ],
            },
            Goal.FOLLOWERS: {
                "value_propositions": [
                    "Follow for more insights like this!",
                    "Want more content like this? Hit follow!",
                    "Join me for regular updates on this topic!",
                ],
                "expertise_signals": [
                    "In my years of experience,",
                    "Having worked in this field,",
                    "After studying this extensively,",
                ],
            },
            Goal.CONVERSION: {
                "urgency_creators": [
                    "Don't wait on this:",
                    "Time-sensitive opportunity:",
                    "Limited availability:",
                    "Act now:",
                ],
                "benefit_highlighters": [
                    "Here's what you'll gain:",
                    "The benefits are clear:",
                    "This will help you:",
                ],
            },
            Goal.AWARENESS: {
                "educational_hooks": [
                    "Did you know that:",
                    "Here's something most people don't realize:",
                    "The surprising truth is:",
                    "What many don't understand:",
                ],
                "myth_busters": [
                    "Let's debunk this myth:",
                    "Contrary to popular belief:",
                    "The reality is different:",
                ],
            },
        }
        
        # Emotional triggers
        self.emotional_triggers = {
            "curiosity": ["surprising", "secret", "hidden", "revealed", "discovered"],
            "urgency": ["now", "today", "immediately", "quickly", "before it's too late"],
            "exclusivity": ["exclusive", "insider", "private", "members only", "VIP"],
            "social_proof": ["thousands", "millions", "everyone", "most people", "experts"],
            "fear": ["mistake", "danger", "risk", "warning", "avoid"],
            "desire": ["want", "need", "crave", "dream", "wish"],
        }
    
    def process(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Process content synchronously."""
        return asyncio.run(self.process_async(content, request))
    
    async def process_async(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Process content asynchronously."""
        if not self.config.enable_engagement_optimization:
            return {"content": content, "tips": []}
        
        optimized_content = content
        engagement_tips = []
        
        # Apply goal-specific optimizations
        if request.goal in self.engagement_patterns:
            result = self._apply_goal_optimization(optimized_content, request.goal)
            optimized_content = result["content"]
            engagement_tips.extend(result["tips"])
        
        # Add emotional triggers
        optimized_content = self._add_emotional_triggers(optimized_content, request)
        
        # Optimize structure for engagement
        optimized_content = self._optimize_structure(optimized_content)
        
        # Add platform-specific engagement elements
        platform_result = self._add_platform_engagement(optimized_content, request)
        optimized_content = platform_result["content"]
        engagement_tips.extend(platform_result["tips"])
        
        # Generate additional engagement tips
        additional_tips = self._generate_engagement_tips(request)
        engagement_tips.extend(additional_tips)
        
        return {
            "content": optimized_content,
            "tips": engagement_tips,
        }
    
    def _apply_goal_optimization(self, content: str, goal: Goal) -> Dict[str, Any]:
        """Apply goal-specific optimizations."""
        patterns = self.engagement_patterns.get(goal, {})
        tips = []
        optimized_content = content
        
        if goal == Goal.ENGAGEMENT:
            # Add questions throughout the content
            optimized_content = self._add_questions(optimized_content, patterns.get("questions", []))
            
            # Add call-to-action at the end
            cta = random.choice(patterns.get("call_to_action", [""]))
            if cta:
                optimized_content += f"\n\n{cta}"
                tips.append("Added call-to-action to encourage comments")
        
        elif goal == Goal.SHARES:
            # Add shareable quotes
            optimized_content = self._add_shareable_quotes(optimized_content, patterns.get("shareable_quotes", []))
            
            # Add share prompt
            share_prompt = random.choice(patterns.get("share_prompts", [""]))
            if share_prompt:
                optimized_content += f"\n\n{share_prompt}"
                tips.append("Added share prompt to encourage sharing")
        
        elif goal == Goal.COMMENTS:
            # Add discussion starters
            discussion_starter = random.choice(patterns.get("discussion_starters", [""]))
            if discussion_starter:
                optimized_content += f"\n\n{discussion_starter}"
                tips.append("Added discussion starter to encourage comments")
        
        elif goal == Goal.FOLLOWERS:
            # Add follow prompt
            follow_prompt = random.choice(patterns.get("value_propositions", [""]))
            if follow_prompt:
                optimized_content += f"\n\n{follow_prompt}"
                tips.append("Added follow prompt to encourage subscriptions")
        
        elif goal == Goal.CONVERSION:
            # Add urgency and benefits
            optimized_content = self._add_conversion_elements(optimized_content, patterns)
            tips.append("Added conversion-focused elements")
        
        elif goal == Goal.AWARENESS:
            # Add educational hooks
            optimized_content = self._add_educational_hooks(optimized_content, patterns)
            tips.append("Added educational hooks for awareness")
        
        return {"content": optimized_content, "tips": tips}
    
    def _add_questions(self, content: str, questions: List[str]) -> str:
        """Add engaging questions throughout the content."""
        paragraphs = content.split('\n\n')
        
        # Add questions to some paragraphs
        for i in range(1, len(paragraphs), 3):  # Every third paragraph
            if i < len(paragraphs) and random.random() < 0.4:
                question = random.choice(questions)
                paragraphs[i] += f"\n\n{question}"
        
        return '\n\n'.join(paragraphs)
    
    def _add_shareable_quotes(self, content: str, quote_markers: List[str]) -> str:
        """Add shareable quotes with visual markers."""
        sentences = content.split('. ')
        
        # Find impactful sentences to highlight
        for i, sentence in enumerate(sentences):
            if (len(sentence) > 30 and len(sentence) < 120 and 
                random.random() < 0.1 and quote_markers):
                marker = random.choice(quote_markers)
                sentences[i] = f"\n\n{marker} {sentence}\n\n"
        
        return '. '.join(sentences)
    
    def _add_emotional_triggers(self, content: str, request: ContentRequest) -> str:
        """Add emotional triggers based on content and goal."""
        # Select appropriate emotional triggers based on goal
        trigger_types = []
        
        if request.goal == Goal.ENGAGEMENT:
            trigger_types = ["curiosity", "social_proof"]
        elif request.goal == Goal.SHARES:
            trigger_types = ["curiosity", "exclusivity"]
        elif request.goal == Goal.CONVERSION:
            trigger_types = ["urgency", "desire", "fear"]
        elif request.goal == Goal.AWARENESS:
            trigger_types = ["curiosity", "social_proof"]
        else:
            trigger_types = ["curiosity"]
        
        # Apply triggers sparingly
        for trigger_type in trigger_types:
            if random.random() < 0.3:  # 30% chance
                triggers = self.emotional_triggers.get(trigger_type, [])
                if triggers:
                    trigger_word = random.choice(triggers)
                    # Try to incorporate the trigger naturally
                    content = self._incorporate_trigger(content, trigger_word)
        
        return content
    
    def _incorporate_trigger(self, content: str, trigger_word: str) -> str:
        """Incorporate emotional trigger naturally into content."""
        # Simple implementation - could be more sophisticated
        if trigger_word in ["surprising", "secret", "hidden"]:
            # Add to beginning of a paragraph
            paragraphs = content.split('\n\n')
            if len(paragraphs) > 1:
                target_para = random.randint(1, len(paragraphs) - 1)
                paragraphs[target_para] = f"Here's something {trigger_word}: {paragraphs[target_para]}"
                content = '\n\n'.join(paragraphs)
        
        return content
    
    def _optimize_structure(self, content: str) -> str:
        """Optimize content structure for engagement."""
        # Ensure good paragraph breaks
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Add emphasis to key points
        content = self._add_emphasis(content)
        
        return content
    
    def _add_emphasis(self, content: str) -> str:
        """Add emphasis to key points."""
        # Look for sentences with key phrases and emphasize them
        key_phrases = [
            r'\b(important|crucial|essential|key|vital)\b',
            r'\b(remember|note|keep in mind)\b',
            r'\b(tip|advice|suggestion)\b',
        ]
        
        for pattern in key_phrases:
            if random.random() < 0.3:  # 30% chance
                content = re.sub(
                    f'([^.!?]*{pattern}[^.!?]*[.!?])',
                    r'**\1**',
                    content,
                    count=1,
                    flags=re.IGNORECASE
                )
        
        return content
    
    def _add_platform_engagement(self, content: str, request: ContentRequest) -> Dict[str, Any]:
        """Add platform-specific engagement elements."""
        tips = []
        
        if request.platform.value == "twitter":
            # Add thread indicators
            content = self._optimize_for_twitter(content)
            tips.append("Optimized for Twitter thread format")
        
        elif request.platform.value == "linkedin":
            # Add professional networking elements
            content += "\n\nWhat's your experience with this? Let's connect and discuss!"
            tips.append("Added LinkedIn networking prompt")
        
        elif request.platform.value == "zhihu":
            # Add question-answer format
            content = self._optimize_for_zhihu(content)
            tips.append("Optimized for Zhihu Q&A format")
        
        return {"content": content, "tips": tips}
    
    def _optimize_for_twitter(self, content: str) -> str:
        """Optimize content for Twitter threads."""
        # Add thread numbering hints
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 3:
            paragraphs[0] = f"🧵 Thread: {paragraphs[0]}"
            for i in range(1, min(len(paragraphs), 10)):
                paragraphs[i] = f"{i+1}/ {paragraphs[i]}"
        
        return '\n\n'.join(paragraphs)
    
    def _optimize_for_zhihu(self, content: str) -> str:
        """Optimize content for Zhihu format."""
        # Add question format at the beginning
        if not content.startswith("问题："):
            content = f"问题：关于{content.split('.')[0]}的思考\n\n答案：\n\n{content}"
        
        return content
    
    def _add_conversion_elements(self, content: str, patterns: Dict[str, List[str]]) -> str:
        """Add conversion-focused elements."""
        # Add urgency
        urgency = random.choice(patterns.get("urgency_creators", [""]))
        if urgency:
            content += f"\n\n{urgency}"
        
        # Add benefits
        benefits = random.choice(patterns.get("benefit_highlighters", [""]))
        if benefits:
            # Insert benefits section
            content += f"\n\n{benefits}\n- Save time and effort\n- Get better results\n- Avoid common mistakes"
        
        return content
    
    def _add_educational_hooks(self, content: str, patterns: Dict[str, List[str]]) -> str:
        """Add educational hooks for awareness content."""
        hook = random.choice(patterns.get("educational_hooks", [""]))
        if hook:
            # Add hook at the beginning
            content = f"{hook} {content}"
        
        return content
    
    def _generate_engagement_tips(self, request: ContentRequest) -> List[str]:
        """Generate additional engagement tips based on request."""
        tips = []
        
        # Goal-specific tips
        if request.goal == Goal.ENGAGEMENT:
            tips.append("Ask follow-up questions in comments to keep conversations going")
            tips.append("Respond to comments quickly to boost engagement")
        
        elif request.goal == Goal.SHARES:
            tips.append("Create visually appealing quote cards from key insights")
            tips.append("Share behind-the-scenes content related to this topic")
        
        elif request.goal == Goal.COMMENTS:
            tips.append("Share a personal story related to this topic")
            tips.append("Ask for specific examples from your audience")
        
        # Platform-specific tips
        if request.platform.value == "linkedin":
            tips.append("Tag relevant industry professionals in your post")
            tips.append("Share in relevant LinkedIn groups")
        
        elif request.platform.value == "twitter":
            tips.append("Use relevant hashtags to increase discoverability")
            tips.append("Engage with replies to boost thread visibility")
        
        return tips
