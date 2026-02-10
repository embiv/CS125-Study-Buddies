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
    with open('Schedules/mockweek.json', 'r',encoding="utf-8") as f:
        mock_json = json.load(f)

    busy_intervals = parse_google_freebusy(mock_json)

    # timezone
    tz = pytz.timezone("America/Los_Angeles")

    # define the week you want (Monday to Friday)
    start_date = datetime(2026, 2, 10).date()  # Monday
    week_days = [start_date + timedelta(days=i) for i in range(5)]

    # compute and print free times for each day
    for day in week_days:
        free_times = get_free_times_for_day(busy_intervals, day, tz, start_hour=8, end_hour=22, min_duration=30)
        print(f"Free time blocks for {day.strftime('%A %Y-%m-%d')}:")
        if free_times:
            for start, end in free_times:
                print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
        else:
            print("  No free time")
        print()

if __name__ == "__main__":
    main()
