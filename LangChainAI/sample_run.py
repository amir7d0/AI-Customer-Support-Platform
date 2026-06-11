from __future__ import annotations

import json
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
if str(PACKAGE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR.parent))

from LangChainAI.schemas import TicketMetadata
from LangChainAI.sample_data import SAMPLE_EMAIL
from LangChainAI.service import create_support_service


def main() -> None:
    workflow, tools = create_support_service()
    ticket = TicketMetadata.from_email(SAMPLE_EMAIL)
    result = workflow.process_ticket(ticket)

    print("\n=== Processed Support Ticket ===\n")
    print(f"Response:\n{result.get('response')}\n")
    


if __name__ == "__main__":
    main()
