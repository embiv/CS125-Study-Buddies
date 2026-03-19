from location import get_closest_libraries, load_library
from retrieval import load_room_docstore, retrieve_5_rooms, print_topres
from input import fetch_freebusy_from_api, parse_google_freebusy, get_free_times_for_day, find_free_time
import json
from datetime import datetime, timedelta
import pytz

def check_user_availability(duration_minutes=30):
    print("\nChecking your Google Calendar availability...")
    
    # try to get calendar data
    busy_intervals = fetch_freebusy_from_api(['primary'], days_ahead=7)
    
    # if api fails use mock schedule
    if busy_intervals is None:
        print("API not available, using mock schedule data")
        try:
            with open('Schedules/mockweek.json', 'r', encoding="utf-8") as f:
                mock_json = json.load(f)
            busy_intervals = parse_google_freebusy(mock_json)
        except FileNotFoundError:
            print("   No mock schedule found, continuing without availability data")
            return None, None, None
    else:
        print("Successfully loaded your calendar!")
    
    tz = pytz.timezone("America/Los_Angeles")
    
    # get free times from today
    today = datetime.now(tz).date()
    free_times = get_free_times_for_day(
        busy_intervals, today, tz,
        start_hour=8, end_hour=22, 
        min_duration=duration_minutes
    )
    
    return free_times, busy_intervals, tz

def save_study_plan(busy_intervals, tz):
    today = datetime.now(tz).date()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    start_date = today + timedelta(days=days_until_monday)
    week_days = [start_date + timedelta(days=i) for i in range(5)]
    
    # save to file 
    with open("study_plan.txt", "w", encoding="utf-8") as out_file: 
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

def main():
    print("\nStuddy Buddies!\n\tEveryone's favorite study spot recommender")
    print("-" * 40)

    # load room data
    load_room_docstore()

    # set user location
    user_location = (33.643, -117.8465)

    libraries = [
        load_library(r"C:\Users\katly\CS125-Study-Buddies\Study Spots\Langson_Library.json"),
        load_library(r"C:\Users\katly\CS125-Study-Buddies\Study Spots\Science_Library.json")
        # load_library(r"/home/ecasasca/cs125/CS125-Study-Buddies/Study Spots/Langson_Library.json"),
        # load_library(r"/home/ecasasca/cs125/CS125-Study-Buddies/Study Spots/Science_Library.json")
    ]

    # find closest library
    libraries_results = get_closest_libraries(user_location, libraries)
    closest_library = libraries_results[0][0]

    print(f"\nclosest library: {closest_library}")

    print("\nChecking your availability...")
    free_times, busy_intervals, tz = check_user_availability(30)
    save_study_plan(busy_intervals, tz)

    # display free times
    if free_times:
        print(f"\nYou have {len(free_times)} free time slot(s) today:")
        for start, end in free_times:
            print(f"   {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")

    load_room_docstore()
    print("\nStudy Spot Seach (Early Demo)")
    print("Type a query. Optional commands:")
    print("     :cap N")
    print("     :dur MIN")
    print("     :clear")
    print("     quit/exit")

    print("\nSearch for options:"
                      "\n\tlibs: langson, science"
                      "\n\tcaps: 1, 4, 5, 6, 8"
                      "\n\tfeatures: whiteboard, group, collaborative, table, large,"
                      "\n\t          huge, big, quiet, single, private, display,"
                      "\n\t          tech enhanced, groups, study"
                      "\nExample queries: :cap 4, :dur 45, group, big\n")

    min_cap = None
    duration= None
    specified_library = False
    search_query = None

    while True:
        query = input("\nSearch for: ").strip()
        if not query:
            continue
        
        if query.lower() in {"quit", "exit"}:
            break

        if query.startswith(":cap"):
            min_cap = int(query.split()[1])
            print(f"Min capacity set to {min_cap}")
            continue

        if query.startswith(":dur"):
            duration = int(query.split()[1])
            print(f"Duration set to {duration} minutes")
            continue

        if query.startswith(":clear"):
            min_cap = None
            duration = None
            print(f"Filters cleared")
            continue

        query_lower = query.lower()
        specified_library = ('langson' in query_lower) or ('science' in query_lower)

        if specified_library:
            search_query = query
        else:
            search_query = f"{closest_library} {query}"

        results = retrieve_5_rooms(search_query, min_capacity=min_cap, duration_minutes=(duration or 30), k=5)
        print_topres(results)

    # # retrieve results 
    # results = retrieve_5_rooms(search_query, min_capacity=min_cap, duration_minutes=duration, k=5)
    # print_topres(results)


if __name__ == "__main__":
    main()
