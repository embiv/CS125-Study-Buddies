import 'package:flutter/material.dart';
import 'models/user_preferences.dart';
import 'screens/profile_page.dart';
import 'screens/study_spots_page.dart';

void main() {
  runApp(const StudyBuddiesApp());
}

class StudyBuddiesApp extends StatelessWidget {
  const StudyBuddiesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int currentIndex = 0;
  int searchTrigger = 0;

  UserPreferences preferences = UserPreferences();

  @override
  Widget build(BuildContext context) {
    final pages = [
      StudySpotsPage(
        preferences: preferences,
        searchTrigger: searchTrigger,
        ),
      ProfilePage(
        preferences: preferences,
        onPreferencesChanged: (newPrefs) {
          setState(() {
            preferences = newPrefs;
          });
        },
        onSavedGoToResults: () {
          setState(() {
            currentIndex = 0;
            searchTrigger++;
          });
        },
      ),
    ];

    return Scaffold(
      body: IndexedStack(
        index: currentIndex,
        children: pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            currentIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.search),
            label: "Study Spots",
          ),
          NavigationDestination(
            icon: Icon(Icons.person),
            label: "Profile",
          ),
        ],
      ),
    );
  }
}