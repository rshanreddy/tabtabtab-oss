"""Google Docs client for the Daily Digest Extension."""

import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

from . import config

class GoogleDocsClient:
    def __init__(self, mcp_url: Optional[str] = None):
        """Initialize the Google Docs client.
        
        Args:
            mcp_url: Optional MCP URL. If not provided, uses the one from config.
        """
        self.mcp_url = mcp_url or config.GDOCS_MCP_URL
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def create_entry(self, title: str, content: str, source_url: str, summary: str) -> Dict[str, Any]:
        """Create a new entry in the Google Doc.
        
        Args:
            title: The title of the digest entry
            content: The content of the digest entry
            source_url: The source URL of the content
            summary: A summary of the content
            
        Returns:
            The response from the MCP
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        timestamp = datetime.now().strftime(config.TIMESTAMP_FORMAT)
        date = datetime.now().strftime(config.DATE_FORMAT)
        
        data = {
            "content": [
                {
                    "type": "heading",
                    "content": f"{config.SECTION_TITLE}: {title}"
                },
                {
                    "type": "paragraph",
                    "content": f"{config.SECTION_DATE}: {date}"
                },
                {
                    "type": "paragraph",
                    "content": f"{config.SECTION_SOURCE_URL}: {source_url}"
                },
                {
                    "type": "paragraph",
                    "content": f"{config.SECTION_SUMMARY}: {summary}"
                },
                {
                    "type": "paragraph",
                    "content": f"{config.SECTION_CONTENT}:\n{content}"
                },
                {
                    "type": "paragraph",
                    "content": f"Timestamp: {timestamp}"
                },
                {
                    "type": "paragraph",
                    "content": "---"
                }
            ]
        }
        
        response = requests.post(
            self.mcp_url,
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_entries(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve entries from the Google Doc.
        
        Args:
            date: Optional date to filter entries by (YYYY-MM-DD format)
            
        Returns:
            List of entries from the document
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        params = {}
        if date:
            params["date"] = date
            
        response = requests.get(
            self.mcp_url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json() 