import 'package:flutter/material.dart';

import '../home/home_screen.dart';
import '../route/route_screen.dart';
import '../search/search_screen.dart';
import '../shopping/shopping_list_screen.dart';

class ConsumerShellScreen extends StatefulWidget {
  const ConsumerShellScreen({super.key});

  @override
  State<ConsumerShellScreen> createState() => _ConsumerShellScreenState();
}

class _ConsumerShellScreenState extends State<ConsumerShellScreen> {
  int _index = 0;

  final _pages = const [
    HomeScreen(),
    SearchScreen(),
    ShoppingListScreen(),
    RouteScreen(),
    _MyPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) => setState(() => _index = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: '홈'),
          NavigationDestination(icon: Icon(Icons.search), label: '검색'),
          NavigationDestination(icon: Icon(Icons.shopping_bag_outlined), label: '장보기'),
          NavigationDestination(icon: Icon(Icons.map_outlined), label: '지도'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: '마이'),
        ],
      ),
    );
  }
}

class _MyPage extends StatelessWidget {
  const _MyPage();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: Center(child: Text('마이페이지 (MVP)')),
      ),
    );
  }
}
