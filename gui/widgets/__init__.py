"""GUI widget primitives.

Currently exports the page-chrome helpers from ``chrome`` (Card, PageHeader,
Section, StatusPill). New reusable widgets go here.
"""

from .chrome import Card, PageHeader, Section, StatusPill

__all__ = ["Card", "PageHeader", "Section", "StatusPill"]
