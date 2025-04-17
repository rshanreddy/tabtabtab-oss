"""Airtable client for the Daily Digest Extension."""

import requests
from datetime import datetime
from typing import Dict, Any, Optional

from . import config

class AirtableClient:
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None):
        """Initialize the Airtable client.
        
        Args:
            api_key: Optional Airtable API key. If not provided, uses the one from config.
            base_id: Optional Airtable base ID. If not provided, uses the one from config.
        """
        self.api_key = api_key or config.AIRTABLE_API_KEY
        self.base_id = base_id or config.AIRTABLE_BASE_ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def _get_table_url(self) -> str:
        """Get the full URL for the Airtable table."""
        return f"{config.AIRTABLE_API_URL}/{self.base_id}/{config.AIRTABLE_TABLE_NAME}"
    
    def create_entry(self, title: str, content: str, source_url: str, summary: str) -> Dict[str, Any]:
        """Create a new entry in the Airtable table.
        
        Args:
            title: The title of the digest entry
            content: The content of the digest entry
            source_url: The source URL of the content
            summary: A summary of the content
            
        Returns:
            The created record from Airtable
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        data = {
            "fields": {
                config.FIELD_DATE: datetime.now().isoformat(),
                config.FIELD_TITLE: title,
                config.FIELD_CONTENT: content,
                config.FIELD_SOURCE_URL: source_url,
                config.FIELD_SUMMARY: summary
            }
        }
        
        response = requests.post(
            self._get_table_url(),
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_entries(self, max_records: int = 100) -> Dict[str, Any]:
        """Retrieve entries from the Airtable table.
        
        Args:
            max_records: Maximum number of records to retrieve
            
        Returns:
            Dictionary containing the retrieved records
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        params = {"maxRecords": max_records}
        response = requests.get(
            self._get_table_url(),
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json() 