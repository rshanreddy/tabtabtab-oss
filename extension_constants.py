from tabtabtab_lib.extension_directory import BaseExtensionDependencies, BaseExtensionID
from enum import auto


class EXTENSION_DEPENDENCIES(BaseExtensionDependencies):
    """
    Enum containing all possible extension dependencies.
    """

    google_calendar_api_key = auto()
    notion_mcp_url = auto()
    calendar_mcp_url = auto()
    anthropic_api_key = auto()
    my_location = auto()
    daily_digest_prompt = auto()  # Customizable prompt for analysis
    daily_digest_storage_path = auto()  # Where to store collected content
    airtable_api_key = auto()
    airtable_base_id = auto()
    airtable_table_name = auto()


class EXTENSION_ID(BaseExtensionID):
    """
    Enum containing all possible extension IDs.
    """

    sample_extension = auto()
    notion_mcp_extension = auto()
    calendar_mcp_extension = auto()
    sample_context_extension = auto()
