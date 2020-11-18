"""
Author: Niall Coleman-Clarke
"""
from typing import Any, List
from datetime import datetime, timezone
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Calendar:
    creds: object = None

    def __init__(
        self,
        calendar_id: str,
        credentials_file: str = "credentials.json",
        token_file: str = "token.pickle",
    ):
        """A wrapper class for the google calendar library

        Args:
            calendar_id (str): Calendar id from google's API.
            credentials_file (str, optional): Path to your google credentials file. Defaults to "credentials.json".
            token_file (str, optional): Path to the google token file (generated from this class). Defaults to "token.pickle".
        """
        self.calendar_id = calendar_id
        self.token_file = token_file

        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, ["https://www.googleapis.com/auth/calendar.readonly"]
            )
            self.creds = flow.run_local_server(port=0)
            with open(token_file, "wb") as token:
                pickle.dump(self.creds, token)

    def __get_service(self) -> Any:
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            with open(self.token_file, "wb") as token:
                pickle.dump(self.creds, token)
        return build("calendar", "v3", credentials=self.creds)

    def get_events(
        self,
        min_dt: datetime = datetime.now(),
        max_dt: datetime = None,
        limit: int = 10,
    ) -> List[Any]:
        """Retrieves events from the calendar

        Args:
            min_dt (datetime, optional): Minimum datetime retrieved events have to start from. Defaults to datetime.now().
            max_dt (datetime, optional): Maximum datetime retrieved events have to start before. Defaults to None.
            limit (int, optional): Maximum number of events to retrieve. Defaults to 10.

        Returns:
            List[Any]: A list of the retrieved event data.
        """
        service = self.__get_service()
        to_utc = lambda dt: dt.astimezone(timezone.utc).isoformat()
        events = (
            service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=to_utc(min_dt),
                timeMax=to_utc(max_dt) if max_dt is not None else None,
                maxResults=limit,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events.get("items", [])
