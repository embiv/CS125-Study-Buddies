class UserPreferences {
  String preferredLibrary;
  int? maxCapacity;
  int duration;
  Set<String> features;

  UserPreferences({
    this.preferredLibrary = "Any",
    this.maxCapacity,
    this.duration = 30,
    Set<String>? features,
  }) : features = features ?? {};
}