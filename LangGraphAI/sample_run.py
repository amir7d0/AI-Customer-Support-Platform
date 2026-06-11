from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from deep_agent.nodes import SupportTicketWorkflow
from deep_agent.schemas import TicketMetadata

SAMPLE_EMAIL = """From: jane.doe@example.com
Subject: Cannot access account after password reset
Date: 2026-06-06
Body:
Hello team,

I recently reset my password, but I still cannot log into my account. I get an error message telling me the password is invalid. I have already tried clearing my cache and using a different browser.

Please help as soon as possible because I need access to my billing information.

Thanks,
Jane
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true", help="Persist the ticket and create internal actions.")
    args = parser.parse_args()

    workflow = SupportTicketWorkflow()
    ticket = TicketMetadata.from_email(SAMPLE_EMAIL)
    print("Processing ticket:", args.commit)
    result = workflow.process_ticket(ticket, commit=args.commit)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
