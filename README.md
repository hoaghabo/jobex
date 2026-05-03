## Backend Messaging Structure

The backend messaging module is organized using a modular, channel-based architecture.

The main `messaging` app contains shared messaging logic such as common models, services, selectors, tasks, constants, serializers, views, and URLs.

Each messaging channel is implemented as a separate Django app under `apps/messaging/channels/`. This keeps channel-specific logic isolated and makes the system easier to extend in the future.

Current supported channels:

- SMS
- Email/Mail
- Telegram

Each channel contains its own:

- models
- admin configuration
- views
- serializers
- URLs
- services
- Celery tasks
- providers
- constants
- migrations

This structure allows each channel to evolve independently while sharing common messaging functionality from the parent `messaging` app.
