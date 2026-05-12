import 'package:flutter/material.dart';

import '../home/home_screen.dart';
import '../route/route_screen.dart';
import '../search/search_screen.dart';
import '../shopping/shopping_list_screen.dart';
import '../../core/repositories/repository_provider.dart';

class ConsumerShellScreen extends StatefulWidget {
  const ConsumerShellScreen({super.key, this.initialIndex = 0});

  final int initialIndex;

  @override
  State<ConsumerShellScreen> createState() => _ConsumerShellScreenState();
}

class _ConsumerShellScreenState extends State<ConsumerShellScreen> {
  late int _index;

  final _pages = const [
    HomeScreen(),
    SearchScreen(),
    ShoppingListScreen(),
    RouteScreen(),
    _MyPage(),
  ];

  @override
  void initState() {
    super.initState();
    _index = widget.initialIndex.clamp(0, _pages.length - 1);
  }

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
    final userName = context.marketRepository.currentUser?.name ?? '사용자';
    return Scaffold(
      backgroundColor: const Color(0xFFF1F7EA),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '마이페이지',
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                      color: const Color(0xFF2A3228),
                    ),
              ),
              const SizedBox(height: 8),
              const Text(
                '마이페이지는 앱 출시 시 회원 데이터 수집과 함께 제공됩니다.',
                style: TextStyle(
                  fontSize: 13,
                  color: Color(0xFF667161),
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFEAF2E2),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFD9E7CC)),
                ),
                child: Row(
                  children: [
                    const CircleAvatar(
                      radius: 22,
                      backgroundColor: Color(0xFFD0E2BE),
                      child: Icon(Icons.person, color: Color(0xFF4B6A37)),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(userName, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF2A3228))),
                          const SizedBox(height: 2),
                          const Text('알림 3개 · 즐겨찾기 6개', style: TextStyle(fontSize: 12, color: Color(0xFF60705A))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              _MenuTile(icon: Icons.notifications_none, title: '알림 설정', subtitle: '드랍/행사/점포 알림 관리'),
              _MenuTile(icon: Icons.favorite_border, title: '관심 점포', subtitle: '자주 보는 점포 빠른 접근'),
              _MenuTile(icon: Icons.route_outlined, title: '최근 동선', subtitle: '최근 방문 경로 다시 보기'),
              _MenuTile(icon: Icons.help_outline, title: '도움말', subtitle: '이용 가이드 및 문의'),
            ],
          ),
        ),
      ),
    );
  }
}

class _MenuTile extends StatelessWidget {
  const _MenuTile({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE1E8DA)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: const Color(0xFF58744B)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF2E352D))),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF72816D))),
              ],
            ),
          ),
          const Icon(Icons.chevron_right, color: Color(0xFFA0AA9A)),
        ],
      ),
    );
  }
}
