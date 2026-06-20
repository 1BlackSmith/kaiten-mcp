"""Operator profile: tool whitelist and exclusion of admin/destructive tools."""

from kaiten_mcp.profiles.operator import OPERATOR_TOOL_NAMES
from kaiten_mcp.registry import collect_tools
from kaiten_mcp.server import ALL_TOOLS as FULL_TOOLS
from kaiten_mcp.server_operator import ALL_TOOLS as OPERATOR_TOOLS


class TestOperatorProfile:
    def test_operator_tool_count(self):
        assert len(OPERATOR_TOOLS) == len(OPERATOR_TOOL_NAMES)
        assert len(OPERATOR_TOOLS) == 104

    def test_operator_subset_of_full(self):
        assert OPERATOR_TOOL_NAMES <= FULL_TOOLS.keys()
        for name in OPERATOR_TOOLS:
            assert OPERATOR_TOOLS[name] is FULL_TOOLS[name]

    def test_no_card_delete(self):
        assert "kaiten_delete_card" not in OPERATOR_TOOLS

    def test_no_space_delete(self):
        assert "kaiten_delete_space" not in OPERATOR_TOOLS

    def test_no_document_delete(self):
        assert "kaiten_delete_document" not in OPERATOR_TOOLS
        assert "kaiten_delete_document_group" not in OPERATOR_TOOLS

    def test_documents_read_write_without_delete(self):
        for name in (
            "kaiten_list_documents",
            "kaiten_create_document",
            "kaiten_get_document",
            "kaiten_update_document",
            "kaiten_list_document_groups",
            "kaiten_create_document_group",
            "kaiten_get_document_group",
            "kaiten_update_document_group",
        ):
            assert name in OPERATOR_TOOLS

    def test_no_admin_modules(self):
        admin_prefixes = (
            "kaiten_create_api_key",
            "kaiten_delete_api_key",
            "kaiten_list_api_keys",
            "kaiten_delete_space",
            "kaiten_create_webhook",
            "kaiten_list_audit_logs",
            "kaiten_create_automation",
            "kaiten_add_space_user",
            "kaiten_set_sd_user_temp_password",
            "kaiten_remove_project_card",
            "kaiten_delete_project",
            "kaiten_add_planned_relation",
        )
        for name in admin_prefixes:
            assert name not in OPERATOR_TOOLS

    def test_project_add_only_no_remove(self):
        assert "kaiten_add_project_card" in OPERATOR_TOOLS
        assert "kaiten_remove_project_card" not in OPERATOR_TOOLS

    def test_saved_filters_included(self):
        for name in (
            "kaiten_list_saved_filters",
            "kaiten_create_saved_filter",
            "kaiten_get_saved_filter",
            "kaiten_update_saved_filter",
            "kaiten_delete_saved_filter",
        ):
            assert name in OPERATOR_TOOLS

    def test_collect_tools_filter_matches_operator(self):
        filtered = collect_tools(OPERATOR_TOOL_NAMES)
        assert set(filtered.keys()) == OPERATOR_TOOL_NAMES
