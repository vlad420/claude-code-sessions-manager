from dataclasses import asdict, dataclass
import json
import datetime
import subprocess
from enum import StrEnum, unique

SESSION_DURATION = 5  # Durata sesiunii în ore


@unique
class SessionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Session:
    created_at: datetime.datetime
    expires_at: datetime.datetime
    status: SessionStatus


# Activator sesiune.
def activate_session() -> None:
    try:
        send_claude_message(message="Hello, Claude!")
    except Exception as e:
        print(f"Nu s-a putut activa sesiunea: {e}")
        return None

    created_at = datetime.datetime.now()
    expires_at = created_at + datetime.timedelta(hours=SESSION_DURATION)
    session = Session(
        created_at=created_at, expires_at=expires_at, status=SessionStatus.ACTIVE
    )
    save_session(session)
    print("Sesiune activată cu succes!")


def send_claude_message(message: str) -> None:
    cmd = ["claude", "-p", message, "--max-turns", "1", "--output-format", "json"]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            timeout=10,
        )

    except subprocess.TimeoutExpired as e:
        raise Exception(f"Timpul de execuție a expirat: {e}")

    raw_output = result.stdout.strip()

    response = json.loads(raw_output)

    verify_claude_response(response)


def verify_claude_response(response: dict) -> None:
    # Veridica daca raspunsul este o eroare
    if response["is_error"]:
        raise Exception(f"EROARE: {response['result']}")


def save_session(session: Session) -> None:
    with open("session.json", "w") as file:
        json.dump(asdict(session), file, ensure_ascii=False, indent=4, default=str)


# Get sesiune.
def get_session():
    try:
        with open("session.json", "r") as file:
            session_data = json.load(file)
            created_at = datetime.datetime.fromisoformat(session_data["created_at"])
            expires_at = datetime.datetime.fromisoformat(session_data["expires_at"])
            status = (
                expires_at > datetime.datetime.now()
                and SessionStatus.ACTIVE
                or SessionStatus.EXPIRED
            )
            return Session(
                created_at=created_at,
                expires_at=expires_at,
                status=status,
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def print_session_info(session: Session) -> None:
    duration = session.expires_at - datetime.datetime.now()
    print(
        f"Sesiune:\nStarted: {format_date(session.created_at)}\nExpiră: {format_date(session.expires_at)}\nStatus: {session.status}{f'\nTimp rămas: {format_duration(duration)}' if session.status == SessionStatus.ACTIVE else ''}"
    )


def format_date(date: datetime.datetime) -> str:
    return date.strftime("%d-%m-%Y %H:%M:%S")


def format_duration(duration: datetime.timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours} ore, {minutes} minute"


def check_session():
    current_session = get_session()
    if not current_session:
        print("Nu există o sesiune activă.")
    else:
        print_session_info(current_session)
        save_session(current_session)


if __name__ == "__main__":
    activate_session()
    check_session()
