import json
import sqlite3
from pathlib import Path

import pytest

from tools import knowledge_search, ticket_creation, ticket_lookup


@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    """Create isolated local data files so tests never modify the project DB."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    employees = [
        {"employee_id": "EMP1001", "name": "Arun Kumar", "department": "Finance"},
        {"employee_id": "EMP1002", "name": "Priya Sharma", "department": "HR"},
        {"employee_id": "EMP1024", "name": "Rahul Verma", "department": "Engineering"},
    ]

    knowledge_base = [
        {
            "id": "KB001",
            "title": "VPN Password Reset",
            "category": "VPN",
            "content": (
                "Open the corporate password portal. Choose 'Reset Password'. "
                "Verify your identity using Multi-Factor Authentication (MFA). "
                "Create a new password."
            ),
        },
        {
            "id": "KB002",
            "title": "VPN Connection Troubleshooting",
            "category": "VPN",
            "content": "Check network connectivity and retry the VPN connection.",
        },
        {
            "id": "KB003",
            "title": "Wi-Fi Troubleshooting",
            "category": "Network",
            "content": "Restart Wi-Fi and reconnect to the corporate network.",
        },
        {
            "id": "KB004",
            "title": "Laptop Restart",
            "category": "Laptop",
            "content": "Restart the laptop and check for the issue again.",
        },
        {
            "id": "KB005",
            "title": "MFA Setup",
            "category": "Security",
            "content": "Register the authenticator application for MFA.",
        },
    ]

    employee_file = data_dir / "employees.json"
    knowledge_file = data_dir / "knowledge_base.json"
    db_file = data_dir / "tickets.db"

    employee_file.write_text(json.dumps(employees), encoding="utf-8")
    knowledge_file.write_text(json.dumps(knowledge_base), encoding="utf-8")

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE tickets (
            ticket_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_team TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    seed_tickets = [
        (
            "INC-1001",
            "EMP1024",
            "VPN",
            "Unable to connect to corporate VPN.",
            "High",
            "In Progress",
            "Network Support",
            "2026-09-10 09:30:00",
        ),
        (
            "INC-1002",
            "EMP1001",
            "Laptop",
            "Laptop is restarting unexpectedly.",
            "Medium",
            "Open",
            "Desktop Support",
            "2026-09-11 11:15:00",
        ),
        (
            "INC-1003",
            "EMP1002",
            "Email",
            "Unable to send emails.",
            "Medium",
            "Resolved",
            "Messaging Support",
            "2026-09-12 14:20:00",
        ),
        (
            "INC-1004",
            "EMP1024",
            "Email",
            "The email application is not sending messages.",
            "Medium",
            "Open",
            "IT Support",
            "2026-09-14 12:37:00",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO tickets (
            ticket_id, employee_id, category, description,
            priority, status, assigned_team, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        seed_tickets,
    )

    connection.commit()
    connection.close()

    monkeypatch.setattr(knowledge_search, "KNOWLEDGE_FILE", knowledge_file)
    monkeypatch.setattr(ticket_lookup, "DATABASE_FILE", db_file)
    monkeypatch.setattr(ticket_creation, "DATABASE_FILE", db_file)
    monkeypatch.setattr(ticket_creation, "EMPLOYEE_FILE", employee_file)

    return {
        "db": db_file,
        "employees": employee_file,
        "knowledge": knowledge_file,
    }


@pytest.fixture
def empty_ticket_environment(tmp_path, monkeypatch):
    """Create an isolated environment with employees and an empty ticket table."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    employee_file = data_dir / "employees.json"
    db_file = data_dir / "tickets.db"

    employees = [
        {"employee_id": "EMP1001", "name": "Arun Kumar", "department": "Finance"},
        {"employee_id": "EMP1002", "name": "Priya Sharma", "department": "HR"},
        {"employee_id": "EMP1024", "name": "Rahul Verma", "department": "Engineering"},
    ]

    employee_file.write_text(json.dumps(employees), encoding="utf-8")

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE tickets (
            ticket_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_team TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()

    monkeypatch.setattr(ticket_creation, "DATABASE_FILE", db_file)
    monkeypatch.setattr(ticket_creation, "EMPLOYEE_FILE", employee_file)

    return {"db": db_file}
