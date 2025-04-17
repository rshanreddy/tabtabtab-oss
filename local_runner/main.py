import asyncio
import logging
from typing import Any, Dict, Optional, Type
import argparse
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tabtabtab_lib.extension_interface import (
    Notification,
    ExtensionInterface,
    OnContextResponse,
)
from tabtabtab_lib.llm_interface import LLMContext, LLMProcessorInterface
from tabtabtab_lib.sse_interface import SSESenderInterface
from tabtabtab_lib.llm import LLMModel
from dotenv import load_dotenv
from extension_constants import EXTENSION_DEPENDENCIES


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("local_runner")

load_dotenv()


class MockSSESender(SSESenderInterface):
    """Mocks the SSE sender to log events instead of sending them."""

    async def send_event(
        self, device_id: str, event_name: str, data: Dict[str, Any]
    ) -> None:
        log.info(
            f"[Mock SSE Send] To Device: {device_id}, Event Name: {event_name}, Data: {data}"
        )

    # Add the send_push_notification method required by the ExtensionInterface base
    async def send_push_notification(
        self, device_id: str, notification: Notification
    ) -> None:
        log.info(
            f"[Mock Send Push] To Device: {device_id}, Request ID: {notification.request_id}, "
            f"Status: {notification.status}, Title: {notification.title}, "
            f"Detail: {notification.detail}, Content: '{notification.content[:50]}...'"
        )


class MockLLMProcessor(LLMProcessorInterface):
    """Mocks the LLM Processor Interface."""

    async def process(
        self,
        system_prompt: str,
        message: str,
        contexts: list[LLMContext],
        model: LLMModel,
        stream: bool = False,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> Optional[str]:
        log.warning("[Mock LLM Process] Generating analysis...")
        
        return """
Key Themes:
- Major AI Infrastructure Advancements
- Record-Breaking Financial Performance
- Technical Performance Improvements

Important Insights:
1. AI Hardware Market
   - NVIDIA dominates with 409% YoY growth in Data Center revenue ($18.4B)
   - Demand still exceeds supply, indicating continued growth potential
   - New superchips promise 2x performance improvement

2. AI Model Capabilities
   - Claude 3 shows significant improvements across all metrics
   - 25% reduction in hallucinations indicates more reliable AI systems
   - 200K token context window enables more complex applications

Connections & Patterns:
- Hardware-Software Co-evolution: NVIDIA's chip improvements align with Claude's increased capabilities
- Market Validation: Strong financial performance (76.4% margins) suggests AI infrastructure investments are paying off
- Competitive Dynamics: Both companies pushing boundaries in their respective domains

Action Items:
1. Technical Investigation
   - Analyze implications of 200K token context for enterprise applications
   - Evaluate new NVIDIA superchips for AI infrastructure planning

2. Market Strategy
   - Monitor AI chip supply constraints and pricing trends
   - Track real-world performance of Claude 3 vs. benchmarks
   - Consider implications of improved hallucination rates for critical applications

3. Investment Considerations
   - NVIDIA's margins suggest room for new market entrants
   - Infrastructure scaling will be critical for AI deployment
   - Multi-modal AI capabilities may open new market segments
"""


# a complete mock context for on_copy
def get_mock_copy_context():
    return {
        "device_id": "test_device_123",
        "request_id": "req_copy_abc",
        "session_id": "session-test-123",
        "timestamp": "2025-04-16T05:39:26.128251",
        "window_info": {
            "bundleIdentifier": "com.google.Chrome",
            "appName": "Google Chrome",
            "windowTitle": "Anthropic releases Claude 3 Opus",
            "windowOwner": "Google Chrome",
            "accessibilityData": {"browser_url": "https://www.anthropic.com/news/claude-3"},
        },
        "screenshot_provided": True,
        "screenshot_data": b"simulated_screenshot_bytes",
        "selected_text": """Claude 3 Opus achieves state-of-the-art performance across key benchmarks:
- 99th percentile on AP Biology exam
- 95% accuracy on mathematical reasoning
- 94% success rate on coding challenges
- Processes 200K tokens of context
- Reduced hallucination rate by 25% compared to previous version
- New multimodal capabilities with advanced vision understanding""",
        "dependencies": {},
    }


def get_mock_copy_context2():
    return {
        "device_id": "test_device_123",
        "request_id": "req_copy_def",
        "session_id": "session-test-123",
        "timestamp": "2025-04-16T06:15:26.128251",
        "window_info": {
            "bundleIdentifier": "com.google.Chrome",
            "appName": "Google Chrome",
            "windowTitle": "NVIDIA Q4 2024 Earnings",
            "windowOwner": "Google Chrome",
            "accessibilityData": {"browser_url": "https://investor.nvidia.com/news"},
        },
        "screenshot_provided": True,
        "screenshot_data": b"simulated_screenshot_bytes",
        "selected_text": """NVIDIA announces record Q4 results:
- Revenue: $22.1B (up 265% YoY)
- Data Center revenue: $18.4B (up 409%)
- Gaming revenue: $2.9B (up 56%)
- Gross margin increased to 76.4%
- AI chip demand continues to outstrip supply
- Announced new AI superchips with 2x performance""",
        "dependencies": {},
    }


def get_mock_paste_context():
    return {
        "device_id": "test_device_456",
        "request_id": "req_paste_xyz",
        "session_id": "session-test-123",
        "window_info": {
            "bundleIdentifier": "com.google.Chrome",
            "windowOwner": "Google Chrome",
            "appName": "Google Chrome",
            "windowTitle": "TabTabTab - Manage Extensions",
            "accessibilityData": {
                "browser_url": "http://localhost:8000/extensions",
                "url": "http://localhost:8000/extensions",
            },
        },
        "screenshot_provided": True,
        "screenshot_data": b"",
        "content_type": "text",
        "metadata": {
            "window_info": '{"bundleIdentifier":"com.google.Chrome","appName":"Google Chrome"}'
        },
        "hint": f"Sample hint text for paste",
        "extensions_context": {
            "another_extension_id": {  # Example context from another extension
                "contexts": [
                    {
                        "description": "some_context_key",
                        "context": "some_context_value_async",
                    },
                    {
                        "description": "some_other_context_key",
                        "context": '{"some_nested_key": "some_nested_value_async"}',
                    },
                ]
            }
        },
    }


async def main(
    extension_class: Type[ExtensionInterface],
    action: str,
    dependencies: Dict[str, Any],
    wait_time_seconds: int = 20,
):
    """Main function to instantiate and test the specified Extension."""
    extension_name = extension_class.__name__
    log.info(f"--- Starting Local Extension Runner for {extension_name} ---")
    log.info(f"Action requested: {action}")
    log.info(f"Dependencies provided: {list(dependencies.keys())}")

    extension = extension_class(
        sse_sender=MockSSESender(),
        llm_processor=MockLLMProcessor(),
        extension_id=f"{extension_name}_local_test",
    )

    # --- Call Extension Methods based on action ---
    if action in ["copy", "all"]:
        log.info(f"\n--- Testing {extension_name}.on_copy ---")
        
        # First copy
        copy_context = get_mock_copy_context()
        copy_context["dependencies"] = dependencies
        try:
            copy_response = await extension.on_copy(copy_context)
            log.info(f"on_copy response 1: {copy_response}")
            await asyncio.sleep(2)  # Short wait between copies
        except Exception as e:
            log.error(f"Error during first copy: {e}", exc_info=True)

        # Second copy
        copy_context2 = get_mock_copy_context2()
        copy_context2["dependencies"] = dependencies
        try:
            copy_response2 = await extension.on_copy(copy_context2)
            log.info(f"on_copy response 2: {copy_response2}")
            log.info("Waiting for background tasks (may involve network calls)...")
            await asyncio.sleep(wait_time_seconds)
        except Exception as e:
            log.error(f"Error during second copy: {e}", exc_info=True)

    if action in ["paste", "all"]:
        log.info(f"\n--- Testing {extension_name}.on_paste ---")
        paste_context = get_mock_paste_context()
        paste_context["dependencies"] = dependencies
        try:
            paste_response = await extension.on_paste(paste_context)
            log.info(f"on_paste response: {paste_response}")
            log.info("Waiting for background tasks (if any from paste)...")
            await asyncio.sleep(wait_time_seconds)
        except Exception as e:
            log.error(
                f"Error calling on_paste or its background task: {e}", exc_info=True
            )

    # --- Add test for on_context_request ---
    if action in ["context", "all"]:
        log.info(f"\n--- Testing {extension_name}.on_context_request ---")
        context_request_context = {
            "source_extension_id": "source_of_the_request",
            "context_query": {
                "query_type": "sample_query",
                "details": "Requesting general context information.",
                "dependencies": dependencies,
            },
        }
        try:
            context_response: Optional[OnContextResponse] = (
                await extension.on_context_request(
                    source_extension_id=context_request_context["source_extension_id"],
                    context_query=context_request_context["context_query"],
                )
            )
            log.info(f"on_context_request response: {context_response}")
            # No background task wait needed typically for context requests
        except Exception as e:
            log.error(f"Error calling on_context_request: {e}", exc_info=True)

    log.info(f"\n--- Local Extension Runner Finished for {extension_name} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run local tests for NotionMCPExtension."
    )
    parser.add_argument(
        "action",
        choices=["copy", "paste", "context", "all"],
        help="Specify which action to test: 'copy', 'paste', 'context', or 'all'.",
    )
    args = parser.parse_args()
    # Using the hardcoded values from the previous version for now:
    dependencies = {
        EXTENSION_DEPENDENCIES.notion_mcp_url.name: os.getenv("NOTION_MCP_URL"),
        EXTENSION_DEPENDENCIES.anthropic_api_key.name: os.getenv("ANTHROPIC_API_KEY"),
    }

    # Check if required dependencies are present
    if not dependencies.get(
        EXTENSION_DEPENDENCIES.notion_mcp_url.name
    ) or not dependencies.get(EXTENSION_DEPENDENCIES.anthropic_api_key.name):
        log.error("Missing required dependencies: mcp_url or anthropic_api_key")
        sys.exit(1)

    # Run the main async function
    # Pass the action and loaded dependencies
    from extensions.notion_mcp_extension.notion_mcp_extension import NotionMCPExtension

    asyncio.run(
        main(
            NotionMCPExtension,
            args.action,
            dependencies=dependencies,
            wait_time_seconds=20,
        )
    )
