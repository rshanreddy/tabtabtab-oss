import logging
from typing import Any, Dict, Optional, List
import json
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

from tabtabtab_lib.extension_interface import (
    ExtensionInterface,
    CopyResponse,
    PasteResponse,
    OnContextResponse,
    Notification,
    NotificationStatus,
    ImmediatePaste,
)
from tabtabtab_lib.llm import LLMModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class DigestEntry:
    """Represents a single entry in the daily digest."""
    def __init__(self, url: str, title: str, content: str, timestamp: str):
        self.url = url
        self.title = title
        self.content = content
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: dict) -> 'DigestEntry':
        return DigestEntry(
            url=data.get("url", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", "")
        )

class DailyDigestExtension(ExtensionInterface):
    """
    An extension that collects and analyzes content you copy throughout the day.
    Stores content in Airtable and generates AI analysis.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.airtable_api_key = None
        self.airtable_base_id = None
        self.airtable_table_name = None
        self.custom_prompt = None
        self.today_entries: List[DigestEntry] = []

    async def _save_to_airtable(self, entry: DigestEntry) -> bool:
        """Save an entry to Airtable."""
        if not all([self.airtable_api_key, self.airtable_base_id, self.airtable_table_name]):
            log.error("Airtable credentials not configured")
            return False

        url = f"https://api.airtable.com/v0/{self.airtable_base_id}/{self.airtable_table_name}"
        headers = {
            "Authorization": f"Bearer {self.airtable_api_key}",
            "Content-Type": "application/json"
        }
        
        # Format data for Airtable
        data = {
            "records": [{
                "fields": {
                    "URL": entry.url,
                    "Title": entry.title,
                    "Content": entry.content,
                    "Timestamp": entry.timestamp,
                    "Date": entry.timestamp.split('T')[0]  # Extract date for easier filtering
                }
            }]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        log.info(f"Successfully saved entry to Airtable")
                        return True
                    else:
                        log.error(f"Failed to save to Airtable: {response.status}")
                        return False
        except Exception as e:
            log.error(f"Error saving to Airtable: {e}")
            return False

    async def _load_todays_entries(self) -> List[DigestEntry]:
        """Load today's entries from Airtable."""
        if not all([self.airtable_api_key, self.airtable_base_id, self.airtable_table_name]):
            log.error("Airtable credentials not configured")
            return []

        today = datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.airtable.com/v0/{self.airtable_base_id}/{self.airtable_table_name}"
        headers = {
            "Authorization": f"Bearer {self.airtable_api_key}",
        }
        params = {
            "filterByFormula": f"Date = '{today}'"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        entries = []
                        for record in data.get("records", []):
                            fields = record.get("fields", {})
                            entry = DigestEntry(
                                url=fields.get("URL", ""),
                                title=fields.get("Title", ""),
                                content=fields.get("Content", ""),
                                timestamp=fields.get("Timestamp", "")
                            )
                            entries.append(entry)
                        return entries
                    else:
                        log.error(f"Failed to load from Airtable: {response.status}")
                        return []
        except Exception as e:
            log.error(f"Error loading from Airtable: {e}")
            return []

    async def _extract_webpage_info(self, url: str) -> tuple[str, str]:
        """Extract title and main content from a webpage."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Get title
                        title = soup.title.string if soup.title else url
                        
                        # Try to get main content
                        content = ""
                        for p in soup.find_all('p'):
                            content += p.get_text() + "\n"
                        
                        return title, content
        except Exception as e:
            log.error(f"Error extracting webpage info: {e}")
        
        return url, ""

    async def on_copy(self, context: Dict[str, Any]) -> CopyResponse:
        """
        When content is copied, store it in Airtable.
        """
        log.info(f"[{self.extension_id}] on_copy called")

        device_id = context.get("device_id")
        request_id = context.get("request_id")
        window_info = context.get("window_info", {})
        selected_text = context.get("selected_text", "")
        
        # Get Airtable credentials from dependencies
        dependencies = context.get("dependencies", {})
        self.airtable_api_key = dependencies.get("airtable_api_key")
        self.airtable_base_id = dependencies.get("airtable_base_id")
        self.airtable_table_name = dependencies.get("airtable_table_name")
        
        if not selected_text:
            return CopyResponse(
                notification=Notification(
                    request_id=request_id,
                    title="Daily Digest",
                    detail="No text selected to add to digest",
                    content="",
                    status=NotificationStatus.ERROR,
                )
            )

        # Get URL and extract webpage info if available
        url = window_info.get("accessibilityData", {}).get("browser_url", "")
        title = ""
        content = selected_text

        if url:
            title, webpage_content = await self._extract_webpage_info(url)
            if webpage_content:
                content = f"{selected_text}\n\nContext from article:\n{webpage_content}"

        # Create new entry
        entry = DigestEntry(
            url=url,
            title=title,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to Airtable
        success = await self._save_to_airtable(entry)

        if not success:
            return CopyResponse(
                notification=Notification(
                    request_id=request_id,
                    title="Daily Digest",
                    detail="Failed to save to Airtable",
                    content="",
                    status=NotificationStatus.ERROR,
                )
            )

        return CopyResponse(
            notification=Notification(
                request_id=request_id,
                title="Daily Digest",
                detail=f"Added to digest: {title or 'New entry'}",
                content="",
                status=NotificationStatus.READY,
            )
        )

    async def on_paste(self, context: Dict[str, Any]) -> PasteResponse:
        """
        Generate an AI analysis of today's collected content.
        """
        log.info(f"[{self.extension_id}] on_paste called")

        device_id = context.get("device_id")
        request_id = context.get("request_id")
        hint = context.get("hint", "").lower()

        # Get dependencies
        dependencies = context.get("dependencies", {})
        self.airtable_api_key = dependencies.get("airtable_api_key")
        self.airtable_base_id = dependencies.get("airtable_base_id")
        self.airtable_table_name = dependencies.get("airtable_table_name")
        self.custom_prompt = dependencies.get("daily_digest_prompt")

        # Load today's entries from Airtable
        entries = await self._load_todays_entries()

        if not entries:
            return PasteResponse(
                paste=Notification(
                    request_id=request_id,
                    title="Daily Digest",
                    detail="No entries collected today",
                    content="",
                    status=NotificationStatus.ERROR,
                )
            )

        # Prepare content for analysis
        content_for_analysis = "\n\n---\n\n".join([
            f"Title: {entry.title}\nURL: {entry.url}\nTime: {entry.timestamp}\n\nContent:\n{entry.content}"
            for entry in entries
        ])

        # Default prompt if none provided
        if not self.custom_prompt:
            self.custom_prompt = """
            You are an intelligent content analyzer. Review the collected content and:
            1. Identify key themes and insights
            2. Highlight the most important points
            3. Suggest connections between different pieces
            4. Note any action items or follow-ups
            
            Format your response in a clear, organized way.
            """

        try:
            # Use LLM to analyze content
            analysis = await self.llm_processor.process(
                system_prompt=self.custom_prompt,
                message=f"Analyze the following collected content:\n\n{content_for_analysis}",
                contexts=[],
                model=LLMModel.GEMINI_FLASH,
            )

            return PasteResponse(
                paste=Notification(
                    request_id=request_id,
                    title="Daily Digest",
                    detail="Generated digest analysis",
                    content=analysis or "Error generating analysis",
                    status=NotificationStatus.READY if analysis else NotificationStatus.ERROR,
                )
            )

        except Exception as e:
            log.error(f"Error generating analysis: {e}")
            return PasteResponse(
                paste=Notification(
                    request_id=request_id,
                    title="Daily Digest",
                    detail=f"Error generating analysis: {str(e)}",
                    content="",
                    status=NotificationStatus.ERROR,
                )
            )

    async def on_context_request(
        self, source_extension_id: str, context_query: Dict[str, Any]
    ) -> OnContextResponse:
        """
        Provide information about today's collected content.
        """
        log.info(f"[{self.extension_id}] Received context request from '{source_extension_id}'")

        # Load today's entries from Airtable
        entries = await self._load_todays_entries()

        digest_info = {
            "entry_count": len(entries),
            "urls": [entry.url for entry in entries if entry.url],
            "timestamps": [entry.timestamp for entry in entries]
        }

        return OnContextResponse(
            contexts=[
                OnContextResponse.ExtensionContext(
                    description="daily_digest_info",
                    context=json.dumps(digest_info)
                )
            ]
        ) 