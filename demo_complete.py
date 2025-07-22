#!/usr/bin/env python3
"""
InkForge Complete Demo Script

This script demonstrates all the features of InkForge including:
- Content generation for different countries and platforms
- Auto-save functionality with multiple formats
- Session management and logging
- Quality control and retry mechanisms
"""

import os
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from inkforge.core.config import Config
from inkforge.core.generator import ContentGenerator
from inkforge.models.content import (
    ContentRequest, Country, Industry, Platform, Tone, Goal, OutputFormat
)

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


def main():
    """Main demo function."""
    console = Console() if RICH_AVAILABLE else None
    
    if console:
        console.print(Panel.fit(
            "[bold blue]🔥 InkForge Complete Demo[/bold blue]\n"
            "Showcasing AI-powered content generation with auto-save and session management",
            border_style="blue"
        ))
    else:
        print("🔥 InkForge Complete Demo")
        print("Showcasing AI-powered content generation with auto-save and session management")
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        if console:
            console.print("[red]❌ No OPENROUTER_API_KEY found in environment.[/red]")
            console.print("[yellow]Please set your API key: export OPENROUTER_API_KEY=your_key[/yellow]")
        else:
            print("❌ No OPENROUTER_API_KEY found in environment.")
            print("Please set your API key: export OPENROUTER_API_KEY=your_key")
        return
    
    # Initialize generator
    config = Config()
    generator = ContentGenerator(config)
    
    if console:
        console.print(f"[green]✅ Session started: {generator.session_id}[/green]")
        console.print(f"[dim]📁 Output directory: {generator.session_dir}[/dim]")
    else:
        print(f"✅ Session started: {generator.session_id}")
        print(f"📁 Output directory: {generator.session_dir}")
    
    # Demo scenarios
    scenarios = [
        {
            "name": "🇺🇸 English Tech Article for Medium",
            "request": ContentRequest(
                topic="The Future of AI-Powered Development Tools",
                country=Country.US,
                industry=Industry.TECHNOLOGY,
                platform=Platform.MEDIUM,
                tone=Tone.PROFESSIONAL,
                goal=Goal.ENGAGEMENT,
                keywords=["AI", "development", "tools", "productivity"],
                length=600
            ),
            "formats": [OutputFormat.MARKDOWN, OutputFormat.HTML, OutputFormat.JSON]
        },
        {
            "name": "🇨🇳 Chinese Finance Post for Zhihu",
            "request": ContentRequest(
                topic="2024年投资理财新趋势分析",
                country=Country.CN,
                industry=Industry.FINANCE,
                platform=Platform.ZHIHU,
                tone=Tone.ANALYTICAL,
                goal=Goal.COMMENTS,
                keywords=["投资", "理财", "趋势", "2024"],
                length=500
            ),
            "formats": [OutputFormat.MARKDOWN, OutputFormat.PLAIN]
        },
        {
            "name": "🐦 Twitter Thread about AI",
            "request": ContentRequest(
                topic="5 AI Tools That Will Change Your Workflow",
                country=Country.US,
                industry=Industry.TECHNOLOGY,
                platform=Platform.TWITTER,
                tone=Tone.CASUAL,
                goal=Goal.SHARES,
                length=300
            ),
            "formats": [OutputFormat.MARKDOWN, OutputFormat.PLAIN]
        }
    ]
    
    # Run scenarios
    for i, scenario in enumerate(scenarios, 1):
        if console:
            console.print(f"\n[bold cyan]Demo {i}/3: {scenario['name']}[/bold cyan]")
            
            # Show request details
            table = Table(title="Generation Parameters", show_header=False)
            table.add_column("Parameter", style="bold blue")
            table.add_column("Value", style="green")
            
            req = scenario["request"]
            table.add_row("Topic", req.topic)
            table.add_row("Country", req.country.value)
            table.add_row("Industry", req.industry.value)
            table.add_row("Platform", req.platform.value)
            table.add_row("Tone", req.tone.value)
            table.add_row("Goal", req.goal.value)
            table.add_row("Length", f"~{req.length} words")
            if req.keywords:
                table.add_row("Keywords", ", ".join(req.keywords))
            
            console.print(table)
            
            # Generate with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating content...", total=None)
                try:
                    response = generator.generate(
                        scenario["request"], 
                        auto_save=True, 
                        save_formats=scenario["formats"]
                    )
                    progress.update(task, completed=True)
                except Exception as e:
                    progress.update(task, description=f"❌ Failed: {str(e)}")
                    console.print(f"[red]Generation failed: {e}[/red]")
                    continue
        else:
            print(f"\nDemo {i}/3: {scenario['name']}")
            print(f"Topic: {scenario['request'].topic}")
            print("Generating content...")
            try:
                response = generator.generate(
                    scenario["request"], 
                    auto_save=True, 
                    save_formats=scenario["formats"]
                )
            except Exception as e:
                print(f"❌ Generation failed: {e}")
                continue
        
        # Display results
        if console:
            # Title
            console.print(Panel.fit(
                f"[bold green]{response.title}[/bold green]",
                border_style="green",
                title="Generated Title"
            ))
            
            # Content preview
            content_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
            console.print(Panel(
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
            stats_table.add_row("Quality Score", f"{response.metadata.get('quality_score', 'N/A')}")
            
            if response.tags:
                stats_table.add_row("Tags", ", ".join(response.tags))
            
            console.print(stats_table)
            
            # Show formats saved
            formats_str = ", ".join([f.value for f in scenario["formats"]])
            console.print(f"[dim]💾 Saved formats: {formats_str}[/dim]")
            
        else:
            print(f"📝 Title: {response.title}")
            print(f"📊 Word Count: {response.word_count}")
            print(f"⏱️  Read Time: {response.estimated_read_time} min")
            print(f"💾 Saved formats: {', '.join([f.value for f in scenario['formats']])}")
    
    # Show session summary
    session_summary = generator.get_session_summary()
    
    if console:
        console.print("\n[bold green]🎉 Demo completed![/bold green]")
        
        summary_table = Table(title="Session Summary")
        summary_table.add_column("Metric", style="bold blue")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Session ID", session_summary["session_id"])
        summary_table.add_row("Total Generations", str(session_summary["total_generations"]))
        summary_table.add_row("Successful", str(session_summary["successful_generations"]))
        summary_table.add_row("Failed", str(session_summary["failed_generations"]))
        summary_table.add_row("Output Directory", session_summary["session_dir"])
        
        console.print(summary_table)
        
        console.print("\n[bold blue]📁 Generated Files:[/bold blue]")
        for gen in session_summary["generations"]:
            status = "✅" if gen["success"] else "❌"
            console.print(f"  {status} {gen['topic'][:50]}... ({gen.get('word_count', 'N/A')} words)")
        
        console.print(f"\n[dim]💡 Use 'inkforge sessions --show {session_summary['session_id']}' to view details[/dim]")
        console.print(f"[dim]📂 Files are saved in: {session_summary['session_dir']}[/dim]")
        
    else:
        print("\n🎉 Demo completed!")
        print(f"Session ID: {session_summary['session_id']}")
        print(f"Total Generations: {session_summary['total_generations']}")
        print(f"Successful: {session_summary['successful_generations']}")
        print(f"Files saved in: {session_summary['session_dir']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
