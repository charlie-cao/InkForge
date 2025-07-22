"""
InkForge CLI - Interactive command-line interface for AI-powered blog content generation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import print as rprint

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()

from .models.content import (
    Country, Industry, Platform, Tone, Goal, OutputFormat,
    ContentRequest, GenerationConfig
)
from .core.config import Config
from .core.generator import ContentGenerator

# Initialize Typer app and Rich console
app = typer.Typer(
    name="inkforge",
    help="🔥 InkForge - AI-powered high-quality blog content generator for global creators",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()

# Global config instance
config: Optional[Config] = None
config_file_path: Optional[Path] = None
debug_mode: bool = False


def get_config() -> Config:
    """Get or initialize global config."""
    global config
    if config is None:
        config = Config(config_file=config_file_path, debug=debug_mode)
    return config


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """
    🔥 InkForge - AI-powered high-quality blog content generator for global creators.
    
    Generate engaging, platform-optimized blog content tailored for different countries,
    industries, and audiences using advanced AI technology.
    """
    if version:
        from . import __version__
        rprint(f"InkForge version {__version__}")
        raise typer.Exit()
    
    # Set global config parameters
    global config_file_path, debug_mode
    config_file_path = config_file
    debug_mode = debug

    # Initialize config
    global config
    config = Config(config_file=config_file, debug=debug)

    if debug:
        console.print("[dim]Debug mode enabled[/dim]")


@app.command()
def generate(
    topic: str = typer.Argument(..., help="The main topic or title for your blog post"),
    country: Country = typer.Option(Country.US, "--country", "-co", help="Target country"),
    industry: Industry = typer.Option(Industry.GENERAL, "--industry", "-i", help="Target industry"),
    platform: Platform = typer.Option(Platform.MEDIUM, "--platform", "-p", help="Target platform"),
    tone: Tone = typer.Option(Tone.PROFESSIONAL, "--tone", "-t", help="Content tone"),
    goal: Goal = typer.Option(Goal.ENGAGEMENT, "--goal", "-g", help="Content goal"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Target language"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Comma-separated keywords"),
    length: int = typer.Option(1000, "--length", "-len", help="Approximate word count", min=100, max=5000),
    output_format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, "--format", "-f", help="Output format"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    save_formats: Optional[str] = typer.Option("md,html,json", "--save-formats", help="Comma-separated formats to auto-save (md,html,json,txt)"),
    auto_save: bool = typer.Option(True, "--auto-save/--no-auto-save", help="Enable/disable auto-save"),
    interactive: bool = typer.Option(False, "--interactive", "-int", help="Interactive mode"),
    custom_instructions: Optional[str] = typer.Option(None, "--instructions", help="Custom instructions"),
):
    """
    Generate high-quality blog content using AI.
    
    Examples:
    
        # Basic usage
        inkforge generate "The Future of AI in Healthcare"
        
        # Specify target audience and platform
        inkforge generate "投资理财入门指南" --country CN --platform zhihu --industry finance
        
        # Interactive mode
        inkforge generate "Tech Trends 2024" --interactive
        
        # Custom output with specific formats
        inkforge generate "Travel Tips" --format html --output travel-post.html

        # Auto-save in multiple formats
        inkforge generate "Tech Guide" --save-formats "md,html,txt"

        # Disable auto-save
        inkforge generate "Quick Note" --no-auto-save
    """
    try:
        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

        # Parse save formats
        save_format_list = []
        if save_formats and auto_save:
            format_mapping = {
                'md': OutputFormat.MARKDOWN,
                'markdown': OutputFormat.MARKDOWN,
                'html': OutputFormat.HTML,
                'json': OutputFormat.JSON,
                'txt': OutputFormat.PLAIN,
                'plain': OutputFormat.PLAIN
            }

            for fmt in save_formats.split(","):
                fmt = fmt.strip().lower()
                if fmt in format_mapping:
                    save_format_list.append(format_mapping[fmt])
                else:
                    console.print(f"[yellow]Warning: Unknown format '{fmt}' ignored[/yellow]")

        # Interactive mode
        if interactive:
            topic, country, industry, platform, tone, goal, language, keyword_list, length, custom_instructions = run_interactive_mode(
                topic, country, industry, platform, tone, goal, language, keyword_list, length, custom_instructions
            )
        
        # Create content request
        request = ContentRequest(
            topic=topic,
            country=country,
            industry=industry,
            platform=platform,
            tone=tone,
            goal=goal,
            language=language,
            keywords=keyword_list,
            length=length,
            custom_instructions=custom_instructions,
        )
        
        # Show generation info
        show_generation_info(request)
        
        # Generate content
        with console.status("[bold green]Generating content...", spinner="dots"):
            # Ensure config is properly loaded
            cfg = get_config()
            if not cfg.validate_api_key():
                console.print("[red]❌ API key not configured or invalid[/red]")
                console.print("[yellow]Please set OPENROUTER_API_KEY environment variable or use 'inkforge config --set openrouter_api_key --value YOUR_KEY'[/yellow]")
                raise typer.Exit(1)

            generator = ContentGenerator(cfg)
            response = generator.generate(request, auto_save=auto_save, save_formats=save_format_list)

        # Display results
        display_results(response, output_format, output_file)

        # Show session info if auto-save is enabled
        if auto_save:
            session_summary = generator.get_session_summary()
            console.print(f"\n[dim]📁 Session: {session_summary['session_id']}[/dim]")
            console.print(f"[dim]💾 Files saved to: {session_summary['session_dir']}[/dim]")
            if save_format_list:
                formats_str = ", ".join([f.value for f in save_format_list])
                console.print(f"[dim]📄 Formats: {formats_str}[/dim]")

        console.print("\n[bold green]✨ Content generated successfully![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation cancelled by user.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        if get_config().debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command("config")
def config_cmd(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Set configuration key"),
    value: Optional[str] = typer.Option(None, "--value", help="Configuration value"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration"),
):
    """
    Manage InkForge configuration.
    
    Examples:
    
        # Show current config
        inkforge config --show
        
        # Set API key
        inkforge config --set openrouter_api_key --value your_key_here
        
        # Reset configuration
        inkforge config --reset
    """
    cfg = get_config()
    
    if reset:
        if Confirm.ask("Are you sure you want to reset configuration to defaults?"):
            cfg.reset_to_defaults()
            console.print("[green]Configuration reset to defaults.[/green]")
        return
    
    if set_key and value:
        cfg.set(set_key, value)
        console.print(f"[green]Set {set_key} = {value}[/green]")
        return
    
    if show or (not set_key and not value):
        show_config(cfg)


@app.command()
def sessions(
    list_sessions: bool = typer.Option(False, "--list", "-l", help="List recent sessions"),
    show_session: Optional[str] = typer.Option(None, "--show", "-s", help="Show session details"),
    clean_old: bool = typer.Option(False, "--clean", help="Clean old sessions (>7 days)"),
):
    """
    Manage generation sessions.

    Examples:

        # List recent sessions
        inkforge sessions --list

        # Show specific session
        inkforge sessions --show 20241201_143022

        # Clean old sessions
        inkforge sessions --clean
    """
    try:
        cfg = get_config()
        output_dir = Path(cfg.default_output_dir) / "sessions"

        if not output_dir.exists():
            console.print("[yellow]No sessions found.[/yellow]")
            return

        if clean_old:
            clean_old_sessions(output_dir)
            return

        if show_session:
            show_session_details(output_dir, show_session)
            return

        if list_sessions or (not show_session and not clean_old):
            list_recent_sessions(output_dir)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.command()
def templates(
    list_templates: bool = typer.Option(False, "--list", "-l", help="List available templates"),
    show_template: Optional[str] = typer.Option(None, "--show", "-s", help="Show specific template"),
    create_template: Optional[str] = typer.Option(None, "--create", "-c", help="Create new template"),
):
    """
    Manage content templates.

    Examples:

        # List all templates
        inkforge templates --list

        # Show specific template
        inkforge templates --show finance_analysis

        # Create new template
        inkforge templates --create my_template
    """
    # TODO: Implement template management
    console.print("[yellow]Template management coming soon![/yellow]")


def run_interactive_mode(topic, country, industry, platform, tone, goal, language, keywords, length, custom_instructions):
    """Run interactive configuration mode."""
    console.print(Panel.fit(
        "[bold blue]🔥 InkForge Interactive Mode[/bold blue]\n"
        "Let's configure your content generation step by step.",
        border_style="blue"
    ))
    
    # Topic (already provided)
    console.print(f"\n[bold]Topic:[/bold] {topic}")
    
    # Country selection
    if Confirm.ask("Would you like to change the target country?", default=False):
        country_options = [c.value for c in Country]
        country = Country(Prompt.ask("Select country", choices=country_options, default=country.value))
    
    # Industry selection
    if Confirm.ask("Would you like to change the industry?", default=False):
        industry_options = [i.value for i in Industry]
        industry = Industry(Prompt.ask("Select industry", choices=industry_options, default=industry.value))
    
    # Platform selection
    if Confirm.ask("Would you like to change the platform?", default=False):
        platform_options = [p.value for p in Platform]
        platform = Platform(Prompt.ask("Select platform", choices=platform_options, default=platform.value))
    
    # Additional options
    if Confirm.ask("Would you like to customize tone, goal, or other settings?", default=False):
        tone_options = [t.value for t in Tone]
        tone = Tone(Prompt.ask("Select tone", choices=tone_options, default=tone.value))
        
        goal_options = [g.value for g in Goal]
        goal = Goal(Prompt.ask("Select goal", choices=goal_options, default=goal.value))
        
        new_length = Prompt.ask("Word count", default=str(length))
        try:
            length = int(new_length)
        except ValueError:
            pass
        
        new_keywords = Prompt.ask("Keywords (comma-separated)", default="")
        if new_keywords:
            keywords = [k.strip() for k in new_keywords.split(",") if k.strip()]
        
        custom_instructions = Prompt.ask("Custom instructions", default=custom_instructions or "")
    
    return topic, country, industry, platform, tone, goal, language, keywords, length, custom_instructions


def show_generation_info(request: ContentRequest):
    """Display generation information."""
    table = Table(title="Content Generation Settings", show_header=False)
    table.add_column("Setting", style="bold blue")
    table.add_column("Value", style="green")
    
    table.add_row("Topic", request.topic)
    table.add_row("Country", request.country.value)
    table.add_row("Industry", request.industry.value)
    table.add_row("Platform", request.platform.value)
    table.add_row("Tone", request.tone.value)
    table.add_row("Goal", request.goal.value)
    table.add_row("Language", request.language or "auto")
    table.add_row("Length", f"~{request.length} words")
    
    if request.keywords:
        table.add_row("Keywords", ", ".join(request.keywords))
    
    console.print(table)
    console.print()


def display_results(response, output_format: OutputFormat, output_file: Optional[Path]):
    """Display generation results."""
    # Show title
    console.print(Panel.fit(
        f"[bold blue]{response.title}[/bold blue]",
        border_style="blue",
        title="Generated Title"
    ))
    
    # Show content preview
    content_preview = response.content[:500] + "..." if len(response.content) > 500 else response.content
    console.print(Panel(
        content_preview,
        title="Content Preview",
        border_style="green"
    ))
    
    # Show metadata
    console.print(f"\n[bold]Word Count:[/bold] {response.word_count}")
    console.print(f"[bold]Estimated Read Time:[/bold] {response.estimated_read_time} minutes")
    
    if response.tags:
        console.print(f"[bold]Suggested Tags:[/bold] {', '.join(response.tags)}")
    
    # Save to file if specified
    if output_file:
        save_content(response, output_format, output_file)
        console.print(f"\n[green]Content saved to: {output_file}[/green]")


def save_content(response, output_format: OutputFormat, output_file: Path):
    """Save content to file."""
    content = response.content
    
    if output_format == OutputFormat.HTML:
        content = f"<h1>{response.title}</h1>\n\n{content.replace(chr(10), '<br>')}"
    elif output_format == OutputFormat.JSON:
        import json
        content = json.dumps(response.dict(), indent=2, ensure_ascii=False)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding='utf-8')


def list_recent_sessions(output_dir: Path):
    """List recent sessions."""
    sessions = []

    for session_dir in output_dir.iterdir():
        if session_dir.is_dir():
            session_file = session_dir / "session_data.json"
            if session_file.exists():
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    sessions.append((session_dir.name, session_data))
                except:
                    continue

    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    # Sort by start time (newest first)
    sessions.sort(key=lambda x: x[1].get("start_time", ""), reverse=True)

    table = Table(title="Recent Sessions")
    table.add_column("Session ID", style="bold blue")
    table.add_column("Start Time", style="green")
    table.add_column("Generations", style="cyan")
    table.add_column("Success Rate", style="yellow")

    for session_id, data in sessions[:10]:  # Show last 10 sessions
        total = len(data.get("generations", []))
        successful = sum(1 for g in data.get("generations", []) if g.get("success", False))
        success_rate = f"{successful}/{total}" if total > 0 else "0/0"

        start_time = data.get("start_time", "Unknown")
        if start_time != "Unknown":
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                start_time = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass

        table.add_row(session_id, start_time, str(total), success_rate)

    console.print(table)


def show_session_details(output_dir: Path, session_id: str):
    """Show details of a specific session."""
    session_dir = output_dir / session_id
    session_file = session_dir / "session_data.json"

    if not session_file.exists():
        console.print(f"[red]Session {session_id} not found.[/red]")
        return

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error reading session data: {e}[/red]")
        return

    # Session info
    console.print(Panel.fit(
        f"[bold blue]Session: {session_id}[/bold blue]\n"
        f"Start Time: {session_data.get('start_time', 'Unknown')}\n"
        f"Directory: {session_dir}",
        border_style="blue"
    ))

    # Generations
    generations = session_data.get("generations", [])
    if generations:
        table = Table(title="Generations")
        table.add_column("ID", style="bold")
        table.add_column("Topic", style="green")
        table.add_column("Status", style="cyan")
        table.add_column("Word Count", style="yellow")
        table.add_column("Formats", style="dim")

        for gen in generations:
            status = "✅ Success" if gen.get("success", False) else "❌ Failed"
            word_count = str(gen.get("word_count", "N/A"))
            formats = ", ".join(gen.get("formats_saved", []))

            table.add_row(
                gen.get("generation_id", "Unknown"),
                gen.get("topic", "Unknown")[:50],
                status,
                word_count,
                formats
            )

        console.print(table)
    else:
        console.print("[yellow]No generations in this session.[/yellow]")


def clean_old_sessions(output_dir: Path):
    """Clean sessions older than 7 days."""
    import shutil
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=7)
    cleaned_count = 0

    for session_dir in output_dir.iterdir():
        if session_dir.is_dir():
            try:
                # Parse session ID to get date
                session_id = session_dir.name
                if len(session_id) >= 8:
                    date_part = session_id[:8]  # YYYYMMDD
                    session_date = datetime.strptime(date_part, "%Y%m%d")

                    if session_date < cutoff_date:
                        shutil.rmtree(session_dir)
                        cleaned_count += 1
                        console.print(f"[dim]Cleaned session: {session_id}[/dim]")
            except:
                continue

    console.print(f"[green]Cleaned {cleaned_count} old sessions.[/green]")


def show_config(cfg: Config):
    """Display current configuration."""
    table = Table(title="InkForge Configuration")
    table.add_column("Setting", style="bold blue")
    table.add_column("Value", style="green")
    table.add_column("Description", style="dim")

    # Add configuration rows
    table.add_row("API Key", "***" if cfg.openrouter_api_key else "Not set", "OpenRouter API key")
    table.add_row("Default Model", cfg.default_model, "Default AI model")
    table.add_row("Default Country", cfg.default_country, "Default target country")
    table.add_row("Default Industry", cfg.default_industry, "Default industry")
    table.add_row("Default Platform", cfg.default_platform, "Default platform")
    table.add_row("Output Directory", cfg.default_output_dir, "Default output directory")

    console.print(table)


if __name__ == "__main__":
    app()
