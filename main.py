from location import get_closest_libraries, load_library
from retrieval import load_room_docstore, retrieve_5_rooms, print_topres


def main():
    print("\nStuddy Buddies!\n\tEveryone's favorite study spot recommendor")
    print("-" * 40)

    # load room data
    load_room_docstore()

    # set user location
    user_location = (33.646, -117.843)

    libraries = [
        load_library(r"C:\Users\katly\CS125-Study-Buddies\Study Spots\Langson_Library.json"),
        load_library(r"C:\Users\katly\CS125-Study-Buddies\Study Spots\Science_Library.json")
    ]

    # find closest library
    libraries_results = get_closest_libraries(user_location, libraries)
    closest_library = libraries_results[0][0]

    print(f"\nclosest library: {closest_library}")

    # # filters
    # min_cap = input("min capacity (press Enter to skip): ").strip()
    # duration = input("study duration in min (press Enter to skip): ").strip()

    # min_cap = int(min_cap) if min_cap else None
    # duration = int(duration) if duration else 30

    # search_options = ("\nSEARCH OPTIONS:"
    #                   "\n\tlibs: langson, science"
    #                   "\n\tcaps: cap 1, cap 4, cap 5, cap 6, cap 8"
    #                   "\n\tfeatures: whiteboard, group, collaborative, table, large,"
    #                   "\n\t          huge, big, quiet, single, private, display,"
    #                   "\n\t          tech enhanced, groups"
    #                   "\n        eg: 'langson whiteboard cap 4'"
    #                   "\n\nsearch for (press Enter to skip): ")

    # user_query = input(search_options).strip()
    load_room_docstore()
    print("\nStudy Spot Seach (Early Demo)")
    print("Type a query. Optional commands:")
    print("     :cap N")
    print("     :dur MIN")
    print("     :clear")
    print("     quit/exit")

    min_cap = None
    duration= None

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

        results = retrieve_5_rooms(query, min_capacity=min_cap, duration_minutes=(duration or 30), k=5)
        print_topres(results)

    # include closest library in the query
    enhanced_query = f"{closest_library} {query}"

    # retrieve results 
    results = retrieve_5_rooms(enhanced_query, min_capacity=min_cap, duration_minutes=duration, k=5)
    print_topres(results)


if __name__ == "__main__":
    main()
