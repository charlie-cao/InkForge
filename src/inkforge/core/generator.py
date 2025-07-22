"""Content generator for InkForge."""

import re
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .config import Config
from .ai_service import AIService, AIServiceManager, GenerationConfig
from ..models.content import ContentRequest, ContentResponse, OutputFormat
from ..templates.prompt_manager import PromptManager
from ..processors.humanizer import Humanizer
from ..processors.engagement_optimizer import EngagementOptimizer
from ..processors.platform_optimizer import PlatformOptimizer
from ..utils.formatters import format_content


class ContentGenerator:
    """Main content generator class."""

    def __init__(self, config: Config):
        """Initialize content generator."""
        self.config = config
        self.ai_manager = AIServiceManager(config)
        self.prompt_manager = PromptManager()

        # Initialize processors
        self.humanizer = Humanizer(config) if config.enable_humanization else None
        self.engagement_optimizer = EngagementOptimizer(config) if config.enable_engagement_optimization else None
        self.platform_optimizer = PlatformOptimizer(config) if config.enable_platform_optimization else None

        # Session management
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path(config.default_output_dir) / "sessions" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Session data
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "config": config.dict(exclude={'_config_file', '_config_dir'}),
            "generations": []
        }
    
    def _setup_logging(self):
        """Setup session logging."""
        log_file = self.session_dir / "session.log"

        # Create logger
        self.logger = logging.getLogger(f"inkforge_session_{self.session_id}")
        self.logger.setLevel(logging.DEBUG if self.config.debug else logging.INFO)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Session {self.session_id} started")

    def generate(self, request: ContentRequest, auto_save: bool = True, save_formats: Optional[List[OutputFormat]] = None) -> ContentResponse:
        """Generate content synchronously."""
        return asyncio.run(self.generate_async(request, auto_save, save_formats))
    
    async def generate_async(self, request: ContentRequest, auto_save: bool = True, save_formats: Optional[List[OutputFormat]] = None) -> ContentResponse:
        """Generate content asynchronously."""
        generation_start = datetime.now()
        generation_id = f"gen_{generation_start.strftime('%H%M%S')}"

        self.logger.info(f"Starting generation {generation_id}")
        self.logger.info(f"Request: {request.dict()}")

        # Default save formats
        if save_formats is None:
            save_formats = [OutputFormat.MARKDOWN, OutputFormat.HTML, OutputFormat.JSON]

        # Validate configuration
        if not self.ai_manager.validate_configuration():
            error_msg = "AI service configuration is invalid. Please check your API key and settings."
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate prompt
        self.logger.info("Generating prompt...")
        prompt = self.prompt_manager.generate_prompt(request)
        self.logger.debug(f"Generated prompt ({len(prompt)} chars): {prompt[:200]}...")

        # Create generation config
        generation_config = GenerationConfig(
            model=self.config.default_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            enable_humanization=self.config.enable_humanization,
            enable_engagement_optimization=self.config.enable_engagement_optimization,
            enable_platform_optimization=self.config.enable_platform_optimization,
            min_quality_score=self.config.min_quality_score,
            max_retries=self.config.max_retries,
        )
        self.logger.info(f"Generation config: {generation_config.dict()}")
        
        # Generate content with retries
        generation_data = {
            "generation_id": generation_id,
            "request": request.dict(),
            "prompt": prompt,
            "config": generation_config.dict(),
            "attempts": [],
            "start_time": generation_start.isoformat()
        }

        for attempt in range(generation_config.max_retries):
            attempt_start = datetime.now()
            self.logger.info(f"Generation attempt {attempt + 1}/{generation_config.max_retries}")

            attempt_data = {
                "attempt": attempt + 1,
                "start_time": attempt_start.isoformat(),
                "prompt_length": len(prompt)
            }

            try:
                # Debug: Check config before creating AI service
                self.logger.debug(f"Config API key present: {bool(self.config.openrouter_api_key)}")
                self.logger.debug(f"Config validation: {self.config.validate_api_key()}")

                async with AIService(self.config) as ai_service:
                    self.logger.info("Calling AI service...")
                    ai_response = await ai_service.generate_content(prompt, generation_config)

                    attempt_data.update({
                        "ai_response": {
                            "model": ai_response.model,
                            "usage": ai_response.usage,
                            "finish_reason": ai_response.finish_reason,
                            "response_time": ai_response.metadata.get("response_time", 0),
                            "content_length": len(ai_response.content)
                        }
                    })

                    self.logger.info(f"AI response received: {ai_response.usage}")

                # Parse AI response
                self.logger.info("Parsing AI response...")
                parsed_content = self._parse_ai_response(ai_response.content)

                # Quality check
                quality_score = self._calculate_quality_score(parsed_content, request)
                attempt_data["quality_score"] = quality_score

                self.logger.info(f"Quality score: {quality_score:.2f} (threshold: {generation_config.min_quality_score})")

                if quality_score >= generation_config.min_quality_score:
                    # Process content
                    self.logger.info("Processing content...")
                    processed_content = await self._process_content(parsed_content, request)

                    # Create response
                    response = self._create_response(processed_content, request, ai_response)

                    # Mark attempt as successful
                    attempt_data.update({
                        "success": True,
                        "end_time": datetime.now().isoformat(),
                        "final_word_count": response.word_count
                    })
                    generation_data["attempts"].append(attempt_data)
                    generation_data["success"] = True
                    generation_data["end_time"] = datetime.now().isoformat()

                    # Auto-save if enabled
                    if auto_save:
                        self._save_generation(generation_id, request, response, generation_data, save_formats)

                    self.logger.info(f"Generation {generation_id} completed successfully")
                    return response
                else:
                    attempt_data["success"] = False
                    attempt_data["reason"] = f"Quality score {quality_score:.2f} below threshold {generation_config.min_quality_score}"

                    if attempt < generation_config.max_retries - 1:
                        # Adjust prompt for retry
                        self.logger.warning(f"Quality score too low, retrying... (attempt {attempt + 1})")
                        prompt = self._adjust_prompt_for_retry(prompt, quality_score, attempt)
                        attempt_data["retry_prompt_adjustment"] = True
                    else:
                        # Use the content anyway but warn about quality
                        self.logger.warning("Using low-quality content after max retries")
                        processed_content = await self._process_content(parsed_content, request)
                        response = self._create_response(processed_content, request, ai_response)
                        response.metadata["quality_warning"] = f"Content quality score ({quality_score:.2f}) below threshold ({generation_config.min_quality_score})"

                        attempt_data.update({
                            "success": True,
                            "quality_warning": True,
                            "end_time": datetime.now().isoformat(),
                            "final_word_count": response.word_count
                        })
                        generation_data["attempts"].append(attempt_data)
                        generation_data["success"] = True
                        generation_data["quality_warning"] = True
                        generation_data["end_time"] = datetime.now().isoformat()

                        # Auto-save if enabled
                        if auto_save:
                            self._save_generation(generation_id, request, response, generation_data, save_formats)

                        return response

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Generation attempt {attempt + 1} failed: {error_msg}")

                attempt_data.update({
                    "success": False,
                    "error": error_msg,
                    "error_type": type(e).__name__,
                    "end_time": datetime.now().isoformat()
                })

                if attempt < generation_config.max_retries - 1:
                    self.logger.info("Retrying after error...")
                else:
                    generation_data["attempts"].append(attempt_data)
                    generation_data["success"] = False
                    generation_data["final_error"] = error_msg
                    generation_data["end_time"] = datetime.now().isoformat()

                    # Save failed generation data
                    if auto_save:
                        self._save_failed_generation(generation_id, request, generation_data)

                    raise e

            generation_data["attempts"].append(attempt_data)

        error_msg = "Failed to generate content after maximum retries"
        self.logger.error(error_msg)
        generation_data["success"] = False
        generation_data["final_error"] = error_msg
        generation_data["end_time"] = datetime.now().isoformat()

        if auto_save:
            self._save_failed_generation(generation_id, request, generation_data)

        raise RuntimeError(error_msg)
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response to extract title, content, and metadata."""
        lines = content.strip().split('\n')
        
        # Try to extract structured response
        title = ""
        main_content = ""
        tags = []
        engagement_tips = []
        
        # Look for title patterns
        title_patterns = [
            r'^#\s+(.+)$',  # Markdown H1
            r'^Title:\s*(.+)$',  # Explicit title
            r'^\*\*Title:\*\*\s*(.+)$',  # Bold title
        ]
        
        content_started = False
        current_section = "content"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for title
            if not title:
                for pattern in title_patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        continue
            
            # Check for sections
            if re.match(r'^(tags?|suggested tags?):', line, re.IGNORECASE):
                current_section = "tags"
                continue
            elif re.match(r'^(engagement tips?|tips?):', line, re.IGNORECASE):
                current_section = "tips"
                continue
            elif line.startswith('#') and title:
                current_section = "content"
                content_started = True
            
            # Process based on current section
            if current_section == "tags":
                # Extract tags
                tag_line = re.sub(r'^(tags?|suggested tags?):\s*', '', line, flags=re.IGNORECASE)
                extracted_tags = [tag.strip() for tag in re.split(r'[,;]', tag_line) if tag.strip()]
                tags.extend(extracted_tags)
            elif current_section == "tips":
                # Extract engagement tips
                tip_line = re.sub(r'^(engagement tips?|tips?):\s*', '', line, flags=re.IGNORECASE)
                if tip_line:
                    engagement_tips.append(tip_line)
            else:
                # Main content
                if title and (content_started or not line.startswith('#')):
                    main_content += line + '\n'
                elif not title:
                    # If no title found yet, treat first substantial line as title
                    if len(line) > 10 and not line.startswith('-') and not line.startswith('*'):
                        title = line
                    else:
                        main_content += line + '\n'
        
        # Fallback: if no title extracted, use first line or generate one
        if not title:
            first_line = content.split('\n')[0].strip()
            if len(first_line) < 100:
                title = first_line
            else:
                title = "Generated Content"
        
        # Clean up content
        main_content = main_content.strip()
        if not main_content:
            main_content = content
        
        return {
            "title": title,
            "content": main_content,
            "tags": tags,
            "engagement_tips": engagement_tips,
        }
    
    def _calculate_quality_score(self, parsed_content: Dict[str, Any], request: ContentRequest) -> float:
        """Calculate content quality score."""
        score = 0.0
        max_score = 1.0
        
        # Check if title exists and is reasonable
        title = parsed_content.get("title", "")
        if title and len(title.strip()) > 5:
            score += 0.2
        
        # Check content length
        content = parsed_content.get("content", "")
        word_count = len(content.split())
        
        if word_count >= request.length * 0.7:  # At least 70% of requested length
            score += 0.3
        elif word_count >= request.length * 0.5:  # At least 50% of requested length
            score += 0.15
        
        # Check for structure (headings, paragraphs)
        if re.search(r'^#+\s', content, re.MULTILINE):  # Has headings
            score += 0.1
        
        if content.count('\n\n') >= 2:  # Has multiple paragraphs
            score += 0.1
        
        # Check for keywords inclusion
        if request.keywords:
            keywords_found = sum(1 for keyword in request.keywords 
                               if keyword.lower() in content.lower())
            keyword_score = min(keywords_found / len(request.keywords), 1.0) * 0.2
            score += keyword_score
        else:
            score += 0.2  # Full score if no keywords specified
        
        # Check for engagement elements
        engagement_indicators = [
            r'\?',  # Questions
            r'!',   # Exclamations
            r'\b(you|your)\b',  # Direct address
            r'\b(how|why|what|when|where)\b',  # Question words
        ]
        
        engagement_count = sum(1 for pattern in engagement_indicators 
                             if re.search(pattern, content, re.IGNORECASE))
        
        if engagement_count >= 3:
            score += 0.1
        
        return min(score, max_score)

    def _save_generation(self, generation_id: str, request: ContentRequest, response: ContentResponse, generation_data: Dict[str, Any], save_formats: List[OutputFormat]):
        """Save successful generation with all formats and metadata."""
        try:
            # Create generation directory
            gen_dir = self.session_dir / generation_id
            gen_dir.mkdir(exist_ok=True)

            # Save metadata
            metadata_file = gen_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(generation_data, f, indent=2, ensure_ascii=False, default=str)

            # Generate safe filename from topic
            safe_topic = "".join(c for c in request.topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length

            # Save in requested formats
            for format_type in save_formats:
                try:
                    formatted_content = format_content(response, format_type)

                    # Determine file extension
                    extensions = {
                        OutputFormat.MARKDOWN: '.md',
                        OutputFormat.HTML: '.html',
                        OutputFormat.JSON: '.json',
                        OutputFormat.PLAIN: '.txt'
                    }

                    ext = extensions.get(format_type, '.txt')
                    filename = f"{safe_topic}_{generation_id}{ext}"
                    file_path = gen_dir / filename

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)

                    self.logger.info(f"Saved {format_type.value} format: {file_path}")

                except Exception as e:
                    self.logger.error(f"Failed to save {format_type.value} format: {e}")

            # Save raw AI response
            raw_file = gen_dir / "raw_response.txt"
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(generation_data["attempts"][-1]["ai_response"].get("content", ""))

            # Save prompt used
            prompt_file = gen_dir / "prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(generation_data["prompt"])

            # Update session data
            self.session_data["generations"].append({
                "generation_id": generation_id,
                "topic": request.topic,
                "success": True,
                "word_count": response.word_count,
                "formats_saved": [f.value for f in save_formats],
                "directory": str(gen_dir.relative_to(self.session_dir))
            })

            # Save updated session data
            self._save_session_data()

            self.logger.info(f"Generation {generation_id} saved successfully to {gen_dir}")

        except Exception as e:
            self.logger.error(f"Failed to save generation {generation_id}: {e}")

    def _save_failed_generation(self, generation_id: str, request: ContentRequest, generation_data: Dict[str, Any]):
        """Save failed generation data for debugging."""
        try:
            # Create generation directory
            gen_dir = self.session_dir / f"{generation_id}_FAILED"
            gen_dir.mkdir(exist_ok=True)

            # Save metadata
            metadata_file = gen_dir / "failed_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(generation_data, f, indent=2, ensure_ascii=False, default=str)

            # Save prompt used
            prompt_file = gen_dir / "prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(generation_data["prompt"])

            # Update session data
            self.session_data["generations"].append({
                "generation_id": generation_id,
                "topic": request.topic,
                "success": False,
                "error": generation_data.get("final_error", "Unknown error"),
                "directory": str(gen_dir.relative_to(self.session_dir))
            })

            # Save updated session data
            self._save_session_data()

            self.logger.info(f"Failed generation {generation_id} data saved to {gen_dir}")

        except Exception as e:
            self.logger.error(f"Failed to save failed generation data: {e}")

    def _save_session_data(self):
        """Save session data to file."""
        try:
            session_file = self.session_dir / "session_data.json"
            self.session_data["last_updated"] = datetime.now().isoformat()

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        total_generations = len(self.session_data["generations"])
        successful_generations = sum(1 for g in self.session_data["generations"] if g["success"])

        return {
            "session_id": self.session_id,
            "session_dir": str(self.session_dir),
            "start_time": self.session_data["start_time"],
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "failed_generations": total_generations - successful_generations,
            "generations": self.session_data["generations"]
        }
    
    def _adjust_prompt_for_retry(self, original_prompt: str, quality_score: float, attempt: int) -> str:
        """Adjust prompt for retry based on quality issues."""
        adjustments = [
            "\n\nIMPORTANT: Please ensure the content is well-structured with clear headings and paragraphs.",
            "\n\nIMPORTANT: Make sure to include engaging elements like questions and direct reader address.",
            "\n\nIMPORTANT: Focus on creating valuable, in-depth content that meets the requested word count.",
        ]
        
        if attempt < len(adjustments):
            return original_prompt + adjustments[attempt]
        else:
            return original_prompt + "\n\nIMPORTANT: Please create high-quality, engaging content that fully addresses the topic."
    
    async def _process_content(self, parsed_content: Dict[str, Any], request: ContentRequest) -> Dict[str, Any]:
        """Process content through various processors."""
        content = parsed_content["content"]
        
        # Apply humanization
        if self.humanizer:
            content = await self.humanizer.process_async(content, request)
        
        # Apply engagement optimization
        if self.engagement_optimizer:
            engagement_result = await self.engagement_optimizer.process_async(content, request)
            content = engagement_result.get("content", content)
            parsed_content["engagement_tips"].extend(engagement_result.get("tips", []))
        
        # Apply platform optimization
        if self.platform_optimizer:
            platform_result = await self.platform_optimizer.process_async(content, request)
            content = platform_result.get("content", content)
            parsed_content["platform_specific_notes"] = platform_result.get("notes", [])
        
        parsed_content["content"] = content
        return parsed_content
    
    def _create_response(self, processed_content: Dict[str, Any], request: ContentRequest, ai_response) -> ContentResponse:
        """Create final content response."""
        content = processed_content["content"]
        word_count = len(content.split())
        
        return ContentResponse(
            title=processed_content["title"],
            content=content,
            metadata={
                "generation_model": ai_response.model,
                "generation_time": datetime.now().isoformat(),
                "usage": ai_response.usage,
                "request_params": request.dict(),
                "response_time": ai_response.metadata.get("response_time", 0),
            },
            engagement_tips=processed_content.get("engagement_tips", []),
            platform_specific_notes=processed_content.get("platform_specific_notes", []),
            word_count=word_count,
            estimated_read_time=max(1, round(word_count / 200)),
            tags=processed_content.get("tags", []),
        )
