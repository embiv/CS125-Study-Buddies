class UserPreferences {
  String preferredLibrary;
  int? maxCapacity;
  int duration;
  Set<String> features;

  double userLat;
  double userLon;

  UserPreferences({
    this.preferredLibrary = "Any",
    this.maxCapacity,
    this.duration = 30,
    Set<String>? features,
    this.userLat = 33.643,     // default (UCI area)
    this.userLon = -117.8465,
  }) : features = features ?? {};
}