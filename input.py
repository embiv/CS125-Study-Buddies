import json
from datetime import datetime, timedelta
import pytz
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_calendar_service():
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None
    
    # stores user's access and refresh tokens into token.json
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # let the user log in if there are valid credentials aren't available
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=3000, open_browser=True)
        
        # save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def fetch_freebusy_from_api(calendar_ids, days_ahead=7):
    try:
        service = get_calendar_service()
        
        # set time range
        tz = pytz.timezone("America/Los_Angeles")
        time_min = datetime.now(tz)
        time_max = time_min + timedelta(days=days_ahead)
        
        # time formats
        time_min_str = time_min.isoformat().replace('+00:00', 'Z')
        time_max_str = time_max.isoformat().replace('+00:00', 'Z')
        
        # prepare request body
        freebusy_request = {
            'timeMin': time_min_str,
            'timeMax': time_max_str,
            'timeZone': 'America/Los_Angeles',
            'items': [{'id': cal_id} for cal_id in calendar_ids]
        }
        
        # execute freebusy query
        freebusy_response = service.freebusy().query(body=freebusy_request).execute()
        
        # parse response
        busy_intervals = []
        calendars_data = freebusy_response.get('calendars', {})
        
        for cal_id, cal_data in calendars_data.items():
            for busy_period in cal_data.get('busy', []):
                start = datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00'))
                busy_intervals.append({'start': start, 'end': end})
        
        return busy_intervals
        
    except HttpError as error:
        print(f'Google Calendar API error: {error}')
        return None
    except Exception as e:
        print(f'Error fetching calendar data: {e}')
        return None


# parse mock file
def parse_google_freebusy(json_response):
    busy_intervals = []
    for calendar_id, data in json_response['calendars'].items():
        for period in data.get('busy', []):
            start = datetime.fromisoformat(period['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(period['end'].replace('Z', '+00:00'))
            busy_intervals.append({'start': start, 'end': end})
    return busy_intervals

# compute free time 
def find_free_time(busy_intervals, window_start, window_end, min_duration_minutes=0):
    if not busy_intervals:
        total_free = [(window_start, window_end)]
        if min_duration_minutes > 0:
            total_free = [(s, e) for s, e in total_free if (e - s).total_seconds() >= min_duration_minutes*60]
        return total_free

    # sort and merge overlapping busy intervals
    busy_intervals.sort(key=lambda x: x['start'])
    merged = []
    current = busy_intervals[0]
    for next_interval in busy_intervals[1:]:
        if next_interval['start'] <= current['end']:
            current['end'] = max(current['end'], next_interval['end'])
        else:
            merged.append(current)
            current = next_interval
    merged.append(current)

    # compute free intervals
    free_intervals = []
    pointer = window_start
    for interval in merged:
        busy_start = max(interval['start'], window_start)
        busy_end = min(interval['end'], window_end)
        if pointer < busy_start:
            free_intervals.append((pointer, busy_start))
        pointer = max(pointer, busy_end)
    if pointer < window_end:
        free_intervals.append((pointer, window_end))

    # filter by minimum duration
    if min_duration_minutes > 0:
        free_intervals = [
            (s, e) for s, e in free_intervals if (e - s).total_seconds() >= min_duration_minutes*60
        ]

    return free_intervals

# get free times per day
def get_free_times_for_day(busy_intervals, day, tz, start_hour=8, end_hour=22, min_duration=30):
    window_start = tz.localize(datetime.combine(day, datetime.min.time()).replace(hour=start_hour))
    window_end = tz.localize(datetime.combine(day, datetime.min.time()).replace(hour=end_hour))
    
    # filter busy intervals for this day
    day_busy = [
        b for b in busy_intervals
        if b['start'].date() == day
        or b['end'].date() == day
        or (b['start'].date() < day and b['end'].date() > day)
    ]
    
    return find_free_time(day_busy, window_start, window_end, min_duration_minutes=min_duration)


def ask_user_preferences():
    print("=== Study Room Preferences ===")

    # library preference
    while True:
        library = input("Which library do you prefer? (SCIENCE/LANGSON/NONE): ").strip().lower()
        if library in ["science", "langson", "none"]:
            break
        print("Please enter science, langson, or none.")

    # group size
    while True:
        try:
            group_size = int(input("How many people will study together? "))
            if library == "science" and 1 <= group_size <= 8:
                break
            elif library == "langson" and 1 <= group_size <= 6:
                break
            elif library == "none" and 1 <= group_size <= 8:
                break
            else:
                print("Invalid group size for that library.")
        except ValueError:
            print("Please enter a number.")

    # noise preference
    while True:
        noise = input("Do you prefer QUIET or COLLABORATIVE?: ").strip().lower()
        if noise in ["quiet", "collaborative"]:
            break
        print("Please enter quiet or collaborative.")
    
    # room size preference
    while True:
        room_size = input("Would you like a SPACIOUS or COMPACT space or EITHER?: ").strip().lower()
        if room_size in ["spacious", "compact", "either"]:
            break
        print("Please enter a valid room size.")

    return {
        "library": library,
        "group_size": group_size,
        "noise": noise,
        "room_size": room_size
    }

def main():
    print("=== Study Room Preferences ===")
    print("Fetching your calendar availability...")
    
    # get real calendar data
    busy_intervals = fetch_freebusy_from_api(['primary'], days_ahead=7)
    
    # use mock if API fails
    if busy_intervals is None:
        print("Using mock schedule data (API not available)")
        with open('Schedules/mockweek.json', 'r', encoding="utf-8") as f:
            mock_json = json.load(f)
        busy_intervals = parse_google_freebusy(mock_json)
    else:
        print("Successfully loaded your calendar!")
    
    tz = pytz.timezone("America/Los_Angeles")
    
    # dates for the next 5 weekdays
    today = datetime.now(tz).date()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    start_date = today + timedelta(days=days_until_monday)
    week_days = [start_date + timedelta(days=i) for i in range(5)]
    
    prefs = ask_user_preferences()
    
    # save to file 
    with open("study_plan.txt", "w", encoding="utf-8") as out_file:
        out_file.write("=== User Preferences ===\n")
        out_file.write(f"Library: {prefs['library']}\n")
        out_file.write(f"Group size: {prefs['group_size']}\n")
        out_file.write(f"Study style: {prefs['noise']}\n")
        out_file.write(f"Room size: {prefs['room_size']}\n\n")
        
        out_file.write("=== Available Free Time Blocks ===\n")
        
        for day in week_days:
            free_times = get_free_times_for_day(
                busy_intervals, day, tz,
                start_hour=8, end_hour=22, min_duration=30
            )
            
            out_file.write(f"{day.strftime('%A %Y-%m-%d')}:\n")
            
            if free_times:
                for start, end in free_times:
                    out_file.write(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}\n")
            else:
                out_file.write("  No free time\n")
            
            out_file.write("\n")
    
    print("\nSaved study preferences and free times to study_plan.txt")

if __name__ == "__main__":
    main()

# questionaire
# langson or science library?
# how many people ?
# quiet or collaborative ?
# spacious or compact ?
