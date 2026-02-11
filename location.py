import json
from haversine import haversine, Unit

# loads library data: name and location
def load_library(path):
    with open(path) as f:
        data = json.load(f)

    library_name = data["space"]["name"]
    library_latitude = data["space"]["location"]["lat"]
    library_longitude = data["space"]["location"]["lon"]

    return library_name, (library_latitude, library_longitude)

def main():
    # user_location = (latitude, longitude)
    user_location = (33.646, -117.843)

    libraries = [
        load_library(r"C:\Users\katly\CS125-Study-Buddies\Study Spots\Langson_Library.json"),
        load_library(r"C:\Users\katly\CS125-Study-Buddies\Study Spots\Science_Library.json")
    ]

    # sorted by closest distance
    results = []

    # calculates the distance between the user and each library
    for library_name, library_location in libraries:
        # haversine: calculates distance between two points on a sphere
        distance = haversine(user_location, library_location, unit=Unit.MILES)
        print(library_name, round(distance, 2), "miles")

    results.sort(key=lambda x: x[1])

    for library_name, library_distance in results:
        print(library_name, round(library_distance, 2), "miles")

if __name__ == "__main__":
    main()
