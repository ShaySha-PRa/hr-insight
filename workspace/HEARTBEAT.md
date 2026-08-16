# Heartbeat

If Gmail is fully connected (Maton key plus an ACTIVE connection that can list messages), check unread mail for resume attachments and follow `gmail_resume_ingest`. Notify only when a new resume was ingested.

If Gmail is not connected, or listing mail returns missing-scope / unauthorized, do not retry in this heartbeat. Reply `HEARTBEAT_OK`.
