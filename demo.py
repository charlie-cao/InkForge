#!/usr/bin/env python3
"""
InkForge Demo Script

This script demonstrates the capabilities of InkForge by generating sample content
for different scenarios. It's designed to work with or without a real API key.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from inkforge.core.config import Config
from inkforge.core.generator import ContentGenerator
from inkforge.models.content import (
    ContentRequest, Country, Industry, Platform, Tone, Goal, OutputFormat
)
from inkforge.utils.formatters import format_content

# Rich for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    def rprint(*args, **kwargs):
        print(*args, **kwargs)


class InkForgeDemo:
    """InkForge demonstration class."""
    
    def __init__(self):
        """Initialize the demo."""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = None
        self.generator = None
        
    def setup(self):
        """Set up InkForge configuration."""
        if self.console:
            self.console.print(Panel.fit(
                "[bold blue]🔥 InkForge Demo[/bold blue]\n"
                "AI-powered high-quality blog content generator",
                border_style="blue"
            ))
        else:
            print("🔥 InkForge Demo")
            print("AI-powered high-quality blog content generator")
        
        # Check for API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            if self.console:
                self.console.print(
                    "[yellow]⚠️  No OPENROUTER_API_KEY found in environment.[/yellow]\n"
                    "[dim]This demo will run in mock mode.[/dim]\n"
                    "[dim]To use real AI generation, set your OpenRouter API key:[/dim]\n"
                    "[dim]export OPENROUTER_API_KEY=your_key_here[/dim]"
                )
            else:
                print("⚠️  No OPENROUTER_API_KEY found in environment.")
                print("This demo will run in mock mode.")
                print("To use real AI generation, set your OpenRouter API key:")
                print("export OPENROUTER_API_KEY=your_key_here")
            
            self.setup_mock_mode()
        else:
            self.setup_real_mode(api_key)
    
    def setup_mock_mode(self):
        """Set up mock mode for demonstration."""
        from unittest.mock import Mock, patch
        
        # Mock the AI service
        mock_response = Mock()
        mock_response.content = """# The Future of AI in Content Creation

Artificial Intelligence is revolutionizing how we create and consume content across the globe.

## The Current Landscape

Content creators today face unprecedented challenges:
- Information overload
- Platform-specific requirements
- Global audience expectations
- Quality vs. quantity balance

## AI-Powered Solutions

### Personalization at Scale
AI enables creators to tailor content for different:
- **Countries**: Adapting cultural nuances and preferences
- **Platforms**: Optimizing for Medium, Twitter, LinkedIn, etc.
- **Industries**: Finance, healthcare, technology, and more

### Quality Enhancement
Modern AI tools can:
1. Improve writing clarity and engagement
2. Suggest better headlines and hooks
3. Optimize content structure
4. Add platform-specific elements

## The InkForge Advantage

InkForge combines multiple AI capabilities:
- **Smart Prompting**: Context-aware prompt generation
- **Humanization**: Making AI content feel natural
- **Platform Optimization**: Tailored for each social platform
- **Global Localization**: Supporting 10+ countries and languages

## Looking Forward

The future of AI-powered content creation will focus on:
- Better understanding of cultural contexts
- More sophisticated engagement optimization
- Seamless integration with creator workflows
- Ethical AI practices and transparency

## Conclusion

As we move forward, tools like InkForge represent the next evolution in content creation - not replacing human creativity, but amplifying it.

What's your experience with AI content tools? Share your thoughts!

Tags: AI, content creation, blogging, technology
Engagement Tips: Ask readers about their AI tool experiences, Share specific use cases"""
        
        mock_response.model = "mistralai/mistral-small-3.2-24b-instruct:free"
        mock_response.usage = {"prompt_tokens": 150, "completion_tokens": 350, "total_tokens": 500}
        mock_response.finish_reason = "stop"
        mock_response.metadata = {"response_time": 2.3, "status_code": 200}
        
        # Patch the AI service
        patcher = patch('inkforge.core.ai_service.AIService')
        mock_service = patcher.start()
        mock_instance = Mock()
        mock_service.return_value.__aenter__.return_value = mock_instance
        mock_service.return_value.__aexit__.return_value = None
        mock_instance.generate_content.return_value = mock_response
        
        # Store patcher for cleanup
        self._patcher = patcher
        
        # Set up config
        self.config = Config()
        self.config.openrouter_api_key = "demo-mock-key"
        self.generator = ContentGenerator(self.config)
    
    def setup_real_mode(self, api_key: str):
        """Set up real mode with actual API."""
        self.config = Config()
        self.config.openrouter_api_key = api_key
        self.generator = ContentGenerator(self.config)
        
        if self.console:
            self.console.print("[green]✅ Real API mode enabled[/green]")
        else:
            print("✅ Real API mode enabled")
    
    def run_demo_scenarios(self):
        """Run various demo scenarios."""
        scenarios = [
            {
                "name": "🇺🇸 Medium Article (English)",
                "request": ContentRequest(
                    topic="The Future of Remote Work",
                    country=Country.US,
                    industry=Industry.BUSINESS,
                    platform=Platform.MEDIUM,
                    tone=Tone.PROFESSIONAL,
                    goal=Goal.ENGAGEMENT,
                    length=800
                )
            },
            {
                "name": "🇨🇳 Zhihu Post (Chinese)",
                "request": ContentRequest(
                    topic="人工智能在医疗领域的应用",
                    country=Country.CN,
                    industry=Industry.HEALTH,
                    platform=Platform.ZHIHU,
                    tone=Tone.ANALYTICAL,
                    goal=Goal.COMMENTS,
                    length=600
                )
            },
            {
                "name": "🐦 Twitter Thread",
                "request": ContentRequest(
                    topic="10 AI Tools Every Developer Should Know",
                    country=Country.US,
                    industry=Industry.TECHNOLOGY,
                    platform=Platform.TWITTER,
                    tone=Tone.CASUAL,
                    goal=Goal.SHARES,
                    length=400
                )
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            self.run_scenario(i, scenario["name"], scenario["request"])
    
    def run_scenario(self, number: int, name: str, request: ContentRequest):
        """Run a single demo scenario."""
        if self.console:
            self.console.print(f"\n[bold cyan]Demo {number}: {name}[/bold cyan]")
            
            # Show request details
            table = Table(title="Generation Parameters", show_header=False)
            table.add_column("Parameter", style="bold blue")
            table.add_column("Value", style="green")
            
            table.add_row("Topic", request.topic)
            table.add_row("Country", request.country.value)
            table.add_row("Industry", request.industry.value)
            table.add_row("Platform", request.platform.value)
            table.add_row("Tone", request.tone.value)
            table.add_row("Goal", request.goal.value)
            table.add_row("Length", f"~{request.length} words")
            
            self.console.print(table)
            
            # Generate with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Generating content...", total=None)
                response = self.generator.generate(request)
                progress.update(task, completed=True)
        else:
            print(f"\nDemo {number}: {name}")
            print(f"Topic: {request.topic}")
            print(f"Platform: {request.platform.value}")
            print("Generating content...")
            response = self.generator.generate(request)
        
        # Display results
        self.display_results(response)
        
        # Save to file
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)
        
        filename = f"demo_{number}_{request.platform.value}"
        
        # Save as Markdown
        md_file = output_dir / f"{filename}.md"
        format_content(response, OutputFormat.MARKDOWN, md_file)
        
        if self.console:
            self.console.print(f"[dim]💾 Saved to: {md_file}[/dim]")
        else:
            print(f"💾 Saved to: {md_file}")
    
    def display_results(self, response):
        """Display generation results."""
        if self.console:
            # Title
            self.console.print(Panel.fit(
                f"[bold green]{response.title}[/bold green]",
                border_style="green",
                title="Generated Title"
            ))
            
            # Content preview
            content_preview = response.content[:300] + "..." if len(response.content) > 300 else response.content
            self.console.print(Panel(
                content_preview,
                title="Content Preview",
                border_style="blue"
            ))
            
            # Stats
            stats_table = Table(show_header=False)
            stats_table.add_column("Metric", style="bold")
            stats_table.add_column("Value", style="cyan")
            
            stats_table.add_row("Word Count", str(response.word_count))
            stats_table.add_row("Read Time", f"{response.estimated_read_time} min")
            
            if response.tags:
                stats_table.add_row("Tags", ", ".join(response.tags))
            
            self.console.print(stats_table)
            
            # Tips
            if response.engagement_tips:
                self.console.print("\n[bold yellow]💡 Engagement Tips:[/bold yellow]")
                for tip in response.engagement_tips[:3]:  # Show first 3
                    self.console.print(f"  • {tip}")
        else:
            print(f"\n📝 Title: {response.title}")
            print(f"📊 Word Count: {response.word_count}")
            print(f"⏱️  Read Time: {response.estimated_read_time} min")
            print(f"\n📄 Content Preview:")
            print(response.content[:300] + "..." if len(response.content) > 300 else response.content)
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, '_patcher'):
            self._patcher.stop()


def main():
    """Main demo function."""
    demo = InkForgeDemo()
    
    try:
        demo.setup()
        demo.run_demo_scenarios()
        
        if demo.console:
            demo.console.print("\n[bold green]🎉 Demo completed successfully![/bold green]")
            demo.console.print("[dim]Check the 'demo_output' directory for generated files.[/dim]")
        else:
            print("\n🎉 Demo completed successfully!")
            print("Check the 'demo_output' directory for generated files.")
            
    except KeyboardInterrupt:
        if demo.console:
            demo.console.print("\n[yellow]Demo interrupted by user.[/yellow]")
        else:
            print("\nDemo interrupted by user.")
    except Exception as e:
        if demo.console:
            demo.console.print(f"\n[red]Error: {str(e)}[/red]")
        else:
            print(f"\nError: {str(e)}")
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()
