"""Tool module registry and collection helpers."""

from kaiten_mcp.tools import (
    audit_and_analytics,
    automations,
    blockers,
    boards,
    card_relations,
    card_types,
    cards,
    charts,
    checklists,
    columns,
    comments,
    custom_properties,
    documents,
    external_links,
    files,
    lanes,
    members,
    projects,
    roles_and_groups,
    service_desk,
    spaces,
    subscribers,
    tags,
    time_logs,
    tree,
    utilities,
    webhooks,
)

TOOL_MODULES = [
    audit_and_analytics,
    automations,
    blockers,
    boards,
    card_relations,
    card_types,
    cards,
    charts,
    checklists,
    columns,
    comments,
    custom_properties,
    documents,
    external_links,
    files,
    lanes,
    members,
    projects,
    roles_and_groups,
    service_desk,
    spaces,
    subscribers,
    tags,
    time_logs,
    tree,
    utilities,
    webhooks,
]


def collect_tools(allowed_names: frozenset[str] | None = None) -> dict[str, dict]:
    """Collect tool definitions from modules, optionally filtered by name."""
    tools: dict[str, dict] = {}
    for module in TOOL_MODULES:
        if not hasattr(module, "TOOLS"):
            continue
        for name, definition in module.TOOLS.items():
            if allowed_names is not None and name not in allowed_names:
                continue
            tools[name] = definition
    return tools
