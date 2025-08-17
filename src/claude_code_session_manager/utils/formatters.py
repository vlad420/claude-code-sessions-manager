from datetime import datetime, timedelta

try:
    from claude_code_session_manager.domain.models import Session
except ImportError:
    from src.claude_code_session_manager.domain.models import Session

from io import StringIO


def format_date(date: datetime) -> str:
    """Format a datetime object to a readable string."""
    return date.strftime("%d-%m-%Y %H:%M:%S")


def format_duration(duration: timedelta) -> str:
    """Format a timedelta object to a readable string."""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours} ore, {minutes} minute"


def format_session_info(session: Session) -> str:
    return format_session_info_rich_text(session)


def format_session_info_rich_text(
    session: Session, width: int = 60, with_color: bool = True
) -> str:
    """
    Returnează un string formatat frumos (cu/sau fără culori) folosind Rich,
    dar ca text render-uit, nu obiect Rich. Păstrează semnătura "return str".
    """
    try:
        from rich.panel import Panel
        from rich.table import Table
        from rich.console import Console
    except ImportError:
        # Dacă Rich nu e instalat, întoarce fallback-ul tău clasic
        return "\n".join(
            [
                "Sesiune:",
                f"Started: {format_date(session.created_at)}",
                f"Expiră: {format_date(session.expires_at)}",
                f"Status: {getattr(session.status, 'name', str(session.status))}",
            ]
        )

    def _status_name(s: object) -> str:
        return getattr(s, "name", str(s))

    def _status_color(name: str) -> str:
        name_u = name.upper()
        if "ACTIVE" in name_u:
            return "green"
        if "EXPIRED" in name_u:
            return "red"
        if "PAUSED" in name_u or "PENDING" in name_u:
            return "yellow"
        return "blue"

    # --- calc timp/progres (robust la lipsa expires_at) ---
    created: datetime | None = getattr(session, "created_at", None)
    expires: datetime | None = getattr(session, "expires_at", None)
    tz = getattr(expires, "tzinfo", None) if expires else None
    now = datetime.now(tz=tz) if tz else datetime.now()

    total_seconds: float = (
        (expires - created).total_seconds() if (expires and created) else 0
    )
    remaining: float = (expires - now).total_seconds() if (expires) else 0
    remaining = max(remaining, 0)
    pct = (
        int(round(100 * (1 - (remaining / total_seconds))))
        if total_seconds > 0
        else (0 if remaining > 0 else 100)
    )
    # bară de progres (30 caractere)
    bar_len = 30
    filled = int(round(pct * bar_len / 100))
    bar = "█" * filled + "░" * (bar_len - filled)

    # --- build tabel + panel ---
    table = Table.grid(padding=(0, 1))
    table.add_column(justify="right", style="bold")
    table.add_column()

    table.add_row("Pornită:", format_date(created) if created else "-")
    table.add_row("Expiră:", format_date(expires) if expires else "-")

    status_name = _status_name(session.status)
    color = _status_color(status_name)
    status_render = f"[{color}]●[/] {status_name}" if with_color else f"● {status_name}"
    table.add_row("Stare:", status_render)

    if total_seconds > 0:
        prog = f"[{color}]{bar}[/] {pct:>3}%" if with_color else f"{bar} {pct:>3}%"
        table.add_row("Progres:", prog)
    if (
        total_seconds > 0
        and remaining > 0
        and "ACTIVE" in status_name.upper()
        and expires
    ):
        table.add_row("Timp rămas:", format_duration(expires - now))

    panel = Panel(
        table, title="Sesiune", border_style="cyan" if with_color else "white"
    )

    # --- render în string ---
    if with_color:
        buf = StringIO()
        # force_terminal=True => scrie cu secvențe ANSI în buffer
        console = Console(file=buf, force_terminal=True, width=width)
        console.print(panel)
        return buf.getvalue()
    else:
        # record=True + export_text() => text curat, fără coduri ANSI
        console = Console(record=True, width=width)
        console.print(panel)
        return console.export_text()


def format_success_message(message: str) -> str:
    """Format a success message."""
    return f"✓ {message}"


def format_error_message(message: str) -> str:
    """Format an error message."""
    return f"✗ {message}"
