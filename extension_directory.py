from tabtabtab_lib.extension_directory import (
    ExtensionDescriptor,
)
from extensions.sample_extension.sample_extension import SampleExtension
from extensions.sample_context_extension.sample_context_extension import (
    SampleContextExtension,
)
from extensions.notion_mcp_extension.notion_mcp_extension import NotionMCPExtension
from extensions.calendar_mcp_extension.calendar_mcp_extension import (
    CalendarMCPExtension,
)
from extensions.text_formatter_extension.text_formatter_extension import TextFormatterExtension
from extensions.daily_digest_extension.daily_digest_extension import DailyDigestExtension
from extension_constants import EXTENSION_DEPENDENCIES, EXTENSION_ID


EXTENSION_DIRECTORY = [
    ExtensionDescriptor(
        extension_id=EXTENSION_ID.sample_extension,
        description="Sample extension to show how to use the extension interface. It takes a copy of a web browser page (public only) and summarizes it.",
        dependencies=[],
        extension_class=SampleExtension,
    ),
    ExtensionDescriptor(
        extension_id=EXTENSION_ID.sample_context_extension,
        description="Sample context extension to show how to use the extension as context provider.",
        dependencies=[],
        extension_class=SampleContextExtension,
    ),
    ExtensionDescriptor(
        extension_id=EXTENSION_ID.notion_mcp_extension,
        description="Notion extension, pushes any text that is copied to the right place in Notion",
        dependencies=[
            EXTENSION_DEPENDENCIES.notion_mcp_url,
            EXTENSION_DEPENDENCIES.anthropic_api_key,
        ],
        extension_class=NotionMCPExtension,
    ),
    ExtensionDescriptor(
        extension_id=EXTENSION_ID.calendar_mcp_extension,
        description="Calendar extension, copy a text and add it to your calender, paste a text and get calendar aware responses.",
        dependencies=[
            EXTENSION_DEPENDENCIES.calendar_mcp_url,
            EXTENSION_DEPENDENCIES.anthropic_api_key,
            EXTENSION_DEPENDENCIES.my_location,
        ],
        extension_class=CalendarMCPExtension,
    ),
    ExtensionDescriptor(
        extension_id=EXTENSION_ID.text_formatter_extension,
        description="Text formatter extension that cleans and formats text during copy/paste operations.",
        dependencies=[],
        extension_class=TextFormatterExtension,
    ),
    ExtensionDescriptor(
        extension_id=EXTENSION_ID.daily_digest_extension,
        description="Collects and analyzes content you copy throughout the day, generating AI-powered insights and summaries.",
        dependencies=[
            EXTENSION_DEPENDENCIES.anthropic_api_key,
            EXTENSION_DEPENDENCIES.daily_digest_prompt,
            EXTENSION_DEPENDENCIES.daily_digest_storage_path,
        ],
        extension_class=DailyDigestExtension,
    ),
]
