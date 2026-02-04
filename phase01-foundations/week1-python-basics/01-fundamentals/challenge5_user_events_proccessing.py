# Raw data received from a source system (e.g. APIs or logs)
events = [
    {"event_id": 1, "user_id": 10, "duration": 5.5},
    {"event_id": 2, "user_id": 11, "duration": "7"},        # invalid: duration as string
    {"event_id": 3, "user_id": None, "duration": 3.2},      # invalid: user_id is missing
    {"event_id": 4, "user_id": 12, "duration": -2},         # invalid: negative duration
    {"event_id": 5, "user_id": 13}                          # invalid: missing duration
]

def validate_event(event):

    """
    Validates a single event record.

    Conditions for a valid event:
    - user_id must be an integer and not None
    - duration must be a positive number (int or float)
    - duration must be greater than 0

    Returns:
    - True if the event is valid, False otherwise.  
    """

    # extract fields safely from the directory
    user_id = event.get("user_id")
    duration = event.get("duration")

    # validate user_id type and presence
    if not isinstance(user_id, int) or user_id is None:
        return False
    
    # validate duration type
    if not isinstance(duration, (int, float)):
        return False
    
    # validate duration value
    if duration <= 0:
        return False
    
    return True

# list to hold valid events
valid_events = []

# loop through all events and only keep valid ones
for event in events:
    if validate_event(event):
        valid_events.append(event)

# output the valid events
print("Valid Events:", valid_events)