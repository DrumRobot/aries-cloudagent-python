"""Revocation utilities."""

import re

REVOCATION_EVENT_PREFIX = "acapy::REVOCATION::"
EVENT_LISTENER_PATTERN = re.compile(f"^{REVOCATION_EVENT_PREFIX}(.*)?$")
REVOCATION_REG_EVENT = "REGISTRY"
REVOCATION_ENTRY_EVENT = "ENTRY"
