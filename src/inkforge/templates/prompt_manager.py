"""Prompt template management for InkForge."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, Template

from ..models.content import ContentRequest, Country, Industry, Platform, Tone, Goal


class PromptManager:
    """Manages prompt templates for different countries, platforms, and industries."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize prompt manager."""
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "prompts"
        
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Load template mappings
        self.mappings = self._load_mappings()
        
        # Ensure default templates exist
        self._ensure_default_templates()
    
    def _load_mappings(self) -> Dict[str, Any]:
        """Load template mappings configuration."""
        mappings_file = self.templates_dir / "mappings.json"
        
        if mappings_file.exists():
            try:
                with open(mappings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Return default mappings
        return self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict[str, Any]:
        """Get default template mappings."""
        return {
            "country_templates": {
                "US": "base_english.j2",
                "UK": "base_english.j2",
                "CN": "base_chinese.j2",
                "JP": "base_japanese.j2",
                "FR": "base_french.j2",
                "DE": "base_german.j2",
                "KR": "base_korean.j2",
                "IN": "base_english.j2",
                "BR": "base_portuguese.j2",
                "ES": "base_spanish.j2",
            },
            "platform_modifiers": {
                "medium": "platform_medium.j2",
                "zhihu": "platform_zhihu.j2",
                "twitter": "platform_twitter.j2",
                "xiaohongshu": "platform_xiaohongshu.j2",
                "wechat": "platform_wechat.j2",
                "linkedin": "platform_linkedin.j2",
                "substack": "platform_substack.j2",
                "note": "platform_note.j2",
                "blog": "platform_blog.j2",
            },
            "industry_modifiers": {
                "finance": "industry_finance.j2",
                "health": "industry_health.j2",
                "education": "industry_education.j2",
                "gaming": "industry_gaming.j2",
                "technology": "industry_technology.j2",
                "lifestyle": "industry_lifestyle.j2",
                "business": "industry_business.j2",
                "travel": "industry_travel.j2",
                "food": "industry_food.j2",
                "general": "industry_general.j2",
            },
            "tone_modifiers": {
                "professional": "tone_professional.j2",
                "casual": "tone_casual.j2",
                "entertaining": "tone_entertaining.j2",
                "analytical": "tone_analytical.j2",
                "inspirational": "tone_inspirational.j2",
                "neutral": "tone_neutral.j2",
            },
            "goal_modifiers": {
                "engagement": "goal_engagement.j2",
                "conversion": "goal_conversion.j2",
                "shares": "goal_shares.j2",
                "comments": "goal_comments.j2",
                "followers": "goal_followers.j2",
                "awareness": "goal_awareness.j2",
            }
        }
    
    def _ensure_default_templates(self):
        """Ensure default templates exist."""
        templates_to_create = [
            ("base_english.j2", self._get_base_english_template()),
            ("base_chinese.j2", self._get_base_chinese_template()),
            ("platform_medium.j2", self._get_platform_medium_template()),
            ("platform_zhihu.j2", self._get_platform_zhihu_template()),
            ("industry_general.j2", self._get_industry_general_template()),
            ("industry_finance.j2", self._get_industry_finance_template()),
            ("tone_professional.j2", self._get_tone_professional_template()),
            ("tone_casual.j2", self._get_tone_casual_template()),
            ("goal_engagement.j2", self._get_goal_engagement_template()),
        ]
        
        for template_name, template_content in templates_to_create:
            template_file = self.templates_dir / template_name
            if not template_file.exists():
                template_file.write_text(template_content, encoding='utf-8')
    
    def generate_prompt(self, request: ContentRequest) -> str:
        """Generate a complete prompt based on the request."""
        # Get base template
        base_template_name = self.mappings["country_templates"].get(
            request.country.value, "base_english.j2"
        )
        
        # Get modifier templates
        platform_modifier = self.mappings["platform_modifiers"].get(
            request.platform.value, "platform_blog.j2"
        )
        industry_modifier = self.mappings["industry_modifiers"].get(
            request.industry.value, "industry_general.j2"
        )
        tone_modifier = self.mappings["tone_modifiers"].get(
            request.tone.value, "tone_professional.j2"
        )
        goal_modifier = self.mappings["goal_modifiers"].get(
            request.goal.value, "goal_engagement.j2"
        )
        
        # Load and render templates
        context = {
            "request": request,
            "topic": request.topic,
            "country": request.country.value,
            "industry": request.industry.value,
            "platform": request.platform.value,
            "tone": request.tone.value,
            "goal": request.goal.value,
            "language": request.language,
            "keywords": request.keywords or [],
            "length": request.length,
            "custom_instructions": request.custom_instructions,
        }
        
        # Render base template
        base_template = self.env.get_template(base_template_name)
        base_prompt = base_template.render(**context)
        
        # Render and combine modifiers
        modifiers = []
        
        for modifier_name in [platform_modifier, industry_modifier, tone_modifier, goal_modifier]:
            try:
                modifier_template = self.env.get_template(modifier_name)
                modifier_content = modifier_template.render(**context)
                if modifier_content.strip():
                    modifiers.append(modifier_content.strip())
            except Exception:
                continue
        
        # Combine all parts
        full_prompt = base_prompt
        if modifiers:
            full_prompt += "\n\nAdditional Requirements:\n" + "\n".join(f"- {mod}" for mod in modifiers)
        
        return full_prompt
    
    def _get_base_english_template(self) -> str:
        """Get base English template."""
        return """You are an expert content creator specializing in high-quality blog posts for global audiences.

Create an engaging, well-structured blog post about "{{ topic }}" with the following specifications:

**Target Audience:** {{ country }} readers
**Industry Focus:** {{ industry }}
**Platform:** {{ platform }}
**Tone:** {{ tone }}
**Goal:** {{ goal }}
**Language:** {{ language }}
**Target Length:** Approximately {{ length }} words

{% if keywords %}
**Keywords to Include:** {{ keywords | join(', ') }}
{% endif %}

**Content Structure Requirements:**
1. Compelling headline that grabs attention
2. Engaging introduction with a hook
3. Well-organized main content with clear sections
4. Practical insights and actionable advice
5. Strong conclusion with call-to-action

**Quality Standards:**
- Write in a natural, human-like style
- Include specific examples and data when relevant
- Ensure content is valuable and not just filler
- Make it engaging and shareable
- Optimize for the target platform's audience preferences

{% if custom_instructions %}
**Additional Instructions:** {{ custom_instructions }}
{% endif %}

Please provide:
1. A compelling title
2. The complete blog post content
3. Suggested tags (3-5 tags)
4. Brief engagement tips for this specific content"""
    
    def _get_base_chinese_template(self) -> str:
        """Get base Chinese template."""
        return """你是一位专业的内容创作专家，专门为全球受众创作高质量的博客文章。

请创作一篇关于"{{ topic }}"的引人入胜、结构良好的博客文章，具体要求如下：

**目标受众：** {{ country }} 读者
**行业重点：** {{ industry }}
**平台：** {{ platform }}
**语调：** {{ tone }}
**目标：** {{ goal }}
**语言：** {{ language }}
**目标长度：** 大约 {{ length }} 字

{% if keywords %}
**需要包含的关键词：** {{ keywords | join('、') }}
{% endif %}

**内容结构要求：**
1. 吸引人的标题
2. 有钩子的引人入胜的开头
3. 组织良好的主要内容，分段清晰
4. 实用见解和可操作的建议
5. 有行动号召的强有力结论

**质量标准：**
- 用自然、人性化的风格写作
- 在相关时包含具体例子和数据
- 确保内容有价值，不只是填充
- 让内容引人入胜且易于分享
- 针对目标平台的受众偏好进行优化

{% if custom_instructions %}
**额外说明：** {{ custom_instructions }}
{% endif %}

请提供：
1. 一个引人注目的标题
2. 完整的博客文章内容
3. 建议的标签（3-5个标签）
4. 针对此特定内容的简要互动提示"""
    
    def _get_platform_medium_template(self) -> str:
        """Get Medium platform modifier."""
        return """Optimize for Medium's audience: Use subheadings, bullet points, and readable paragraphs. Include a compelling subtitle."""
    
    def _get_platform_zhihu_template(self) -> str:
        """Get Zhihu platform modifier."""
        return """针对知乎优化：使用问答式开头，包含数据支持，添加个人经验分享，使用中文互联网用户熟悉的表达方式。"""
    
    def _get_industry_general_template(self) -> str:
        """Get general industry modifier."""
        return """Keep content accessible to general audiences while maintaining depth and value."""
    
    def _get_industry_finance_template(self) -> str:
        """Get finance industry modifier."""
        return """Include relevant financial data, market trends, and practical investment advice. Cite credible financial sources."""
    
    def _get_tone_professional_template(self) -> str:
        """Get professional tone modifier."""
        return """Maintain a professional, authoritative tone while remaining approachable and clear."""
    
    def _get_tone_casual_template(self) -> str:
        """Get casual tone modifier."""
        return """Use a conversational, friendly tone with personal anecdotes and relatable examples."""
    
    def _get_goal_engagement_template(self) -> str:
        """Get engagement goal modifier."""
        return """Include thought-provoking questions, encourage comments, and add shareable quotes or insights."""
