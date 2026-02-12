import json
from datetime import datetime, timedelta
import pytz

# parse mock file
def parse_google_freebusy(json_response):
    busy_intervals = []
    for calendar_id, data in json_response['calendars'].items():
        for period in data.get('busy', []):
            start = datetime.fromisoformat(period['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(period['end'].replace('Z', '+00:00'))
            busy_intervals.append({'start': start, 'end': end})
    return busy_intervals

# compute free time given busy intervals & time window 
def find_free_time(busy_intervals, window_start, window_end, min_duration_minutes=0):
    """
    Computes free intervals given busy intervals and a time window
    """
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

# helper to get free times per day
def get_free_times_for_day(busy_intervals, day, tz, start_hour=8, end_hour=22, min_duration=30):
    """
    day: datetime.date object for the day you want free times
    """
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


def main():
    # load mock json schedule
    with open('Schedules/mockweek.json', 'r', encoding="utf-8") as f:
        mock_json = json.load(f)

    busy_intervals = parse_google_freebusy(mock_json)

    tz = pytz.timezone("America/Los_Angeles")

    start_date = datetime(2026, 2, 10).date()
    week_days = [start_date + timedelta(days=i) for i in range(5)]

    # ask questionnaire
    prefs = ask_user_preferences()

    with open("study_plan.txt", "w", encoding="utf-8") as out_file:
        out_file.write("=== User Preferences ===\n")
        out_file.write(f"Library: {prefs['library']}\n")
        out_file.write(f"Group size: {prefs['group_size']}\n")
        out_file.write(f"Study style: {prefs['noise']}\n")
        out_file.write(f"Room size: {prefs['room_size']}\n\n")

        out_file.write("=== Available Free Time Blocks ===\n\n")

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

    print("Saved study preferences and free times to study_plan.txt")

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

if __name__ == "__main__":
    main()

# questionaire
# langson or science library?
# how many people ?
# quiet or collaborative ?
# spacious or compact ?