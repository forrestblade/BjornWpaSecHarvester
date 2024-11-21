from typing import Dict, Any
from pathlib import Path
import random
import json
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from ..config.comments import DISPLAY_COMMENTS

class DisplayManager:
    """
    Manages Bjorn's e-Paper display updates for WPA-SEC Harvester.
    Integrates with Bjorn's character and Viking theme.
    """
    
    def __init__(self, shared_data: Dict[str, Any]):
        self.shared_data = shared_data
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.current_theme = "info"
        self.current_status = "idle"
        
        # Viking-themed icons for different states
        self.icons = {
            'startup': '⚔️',
            'search': '🔍',
            'process': '⚡',
            'download': '📥',
            'victory': '🏆',
            'error': '🛡️'
        }
        
        # Initialize progress display
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold]{task.percentage:>3.0f}%"),
        )

    def update_display(self, status: Dict[str, Any]) -> None:
        """Update Bjorn's e-Paper display with current status."""
        try:
            # Update internal state
            self.current_theme = status.get('style', 'info')
            self.current_status = status.get('status', 'idle')

            # Prepare display data
            display_data = {
                'module': 'WPA-SEC Harvester',
                'icon': self._get_icon(status.get('icon', 'search')),
                'status': self._format_status(status),
                'comment': self._get_comment(),
                'stats': self._get_stats(),
                'progress': status.get('progress', {}),
                'theme': self.current_theme
            }

            # Update Bjorn's display through shared data
            self.shared_data.update_display(display_data)
            
            # Update console display
            self._update_console_display(display_data)

        except Exception as e:
            self.logger.error(f"Display update failed: {e}")

    def _get_icon(self, icon_key: str) -> str:
        """Get Viking-themed icon for current status."""
        return self.icons.get(icon_key, self.icons['search'])

    def _format_status(self, status: Dict[str, Any]) -> str:
        """Format status message with Viking theme."""
        icon = self._get_icon(status.get('icon', 'search'))
        message = status.get('message', 'No status message')
        return f"{icon} {message}"

    def _get_comment(self) -> str:
        """Get themed Viking comment for current status."""
        comments = DISPLAY_COMMENTS.get(self.current_theme, [])
        if not comments:
            comments = DISPLAY_COMMENTS.get('info', ['The hunt continues...'])
        return random.choice(comments)

    def _get_stats(self) -> Dict[str, Any]:
        """Get current statistics for display."""
        return {
            'networks_found': self.shared_data.get('stats', {}).get('total_networks_found', 0),
            'successful_cracks': self.shared_data.get('stats', {}).get('successful_harvests', 0),
            'failed_attempts': self.shared_data.get('stats', {}).get('failed_attempts', 0),
            'current_operation': self.current_status
        }

    def _update_console_display(self, display_data: Dict[str, Any]) -> None:
        """Update rich console display."""
        self.console.clear()
        self.console.print("\n[bold blue]Bjorn WPA-SEC Harvester[/bold blue]")
        self.console.print(f"[cyan]Status:[/cyan] {display_data['status']}")
        self.console.print(f"[cyan]Comment:[/cyan] {display_data['comment']}")
        
        # Display progress if available
        if display_data.get('progress'):
            with self.progress:
                task_id = self.progress.add_task(
                    description="Processing",
                    total=display_data['progress'].get('total', 100)
                )
                self.progress.update(
                    task_id,
                    completed=display_data['progress'].get('current', 0)
                )

        # Display stats
        self.console.print("\n[cyan]Stats:[/cyan]")
        for key, value in display_data['stats'].items():
            self.console.print(f"  {key}: {value}")
