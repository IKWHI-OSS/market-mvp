import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/market_logo_title.dart';
import '../home/spotlight_screen.dart';

class AgentScreen extends StatefulWidget {
  const AgentScreen({super.key});

  @override
  State<AgentScreen> createState() => _AgentScreenState();
}

class _AgentScreenState extends State<AgentScreen> {
  final TextEditingController _queryController = TextEditingController(text: '2인 저녁용 찌개 재료 추천해줘');
  String _userQuery = '2인 저녁용 찌개 재료 추천해줘';

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  void _submitQuery() {
    if (_queryController.text.trim().isEmpty) {
      return;
    }
    setState(() {
      _userQuery = _queryController.text.trim();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 8, 14, 10),
              child: Row(
                children: [
                  InkWell(
                    onTap: () {
                      if (Navigator.canPop(context)) {
                        Navigator.pop(context);
                        return;
                      }
                      Navigator.pushNamed(context, AppRoutes.home);
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: const Icon(Icons.arrow_back, color: Color(0xFF3E7C18)),
                  ),
                  const SizedBox(width: 8),
                  const SizedBox(
                    height: 24,
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: MarketLogoTitle(),
                    ),
                  ),
                  const Spacer(),
                  InkWell(
                    onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                    borderRadius: BorderRadius.circular(12),
                    child: const Icon(Icons.notifications_none, size: 20, color: Color(0xFF3E7C18)),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 16),
                children: [
                  Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E9DD),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Text(
                        '2024년 5월 24일 금요일',
                        style: TextStyle(fontSize: 13, color: Color(0xFF61695C), fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Align(
                    alignment: Alignment.centerRight,
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 270),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF3E7C18),
                        borderRadius: BorderRadius.circular(22),
                      ),
                      child: Text(
                        _userQuery,
                        style: const TextStyle(fontSize: 17, color: Colors.white, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Align(
                    alignment: Alignment.centerRight,
                    child: Text('오후 5:42', style: TextStyle(fontSize: 12, color: Color(0xFF7A8376))),
                  ),
                  const SizedBox(height: 10),
                  const Row(
                    children: [
                      CircleAvatar(
                        radius: 16,
                        backgroundColor: Color(0xFF3E7C18),
                        child: Icon(Icons.auto_awesome, size: 18, color: Colors.white),
                      ),
                      SizedBox(width: 10),
                      Text(
                        '장보기 에이전트',
                        style: TextStyle(fontSize: 28, color: Color(0xFF2E5F12), fontWeight: FontWeight.w900),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE1E8DD),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: const Text(
                      '네, 제철 재료로 만드는 얼큰한 고추장찌개는 어떠신가요? 예산 2만원 내외로 맞춘 장보기 리스트와 매칭 점포입니다.',
                      style: TextStyle(fontSize: 17, color: Color(0xFF3C4437), height: 1.35),
                    ),
                  ),
                  const SizedBox(height: 14),
                  _RecommendationCard(
                    onStoreTap1: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const SpotlightScreen(storeId: 'store_003')),
                    ),
                    onStoreTap2: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const SpotlightScreen(storeId: 'store_004')),
                    ),
                    onStartRoute: () => Navigator.pushNamed(context, AppRoutes.route),
                  ),
                  const SizedBox(height: 8),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text('오후 5:42', style: TextStyle(fontSize: 12, color: Color(0xFF7A8376))),
                  ),
                  const SizedBox(height: 10),
                  const Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _QuickChip(icon: Icons.eco_outlined, label: '제철 반찬'),
                      _QuickChip(icon: Icons.savings_outlined, label: '1만원 이하'),
                      _QuickChip(icon: Icons.restaurant_menu, label: '2인 찌개 재료'),
                    ],
                  ),
                  const SizedBox(height: 12),
                ],
              ),
            ),
            Container(
              color: const Color(0xFFF2F7EC),
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFE7EDE0),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.08),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.add_circle_outline, color: Color(0xFF6C7467)),
                    ),
                    Expanded(
                      child: TextField(
                        controller: _queryController,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          isDense: true,
                          hintText: 'AI에게 물어보세요...',
                          hintStyle: TextStyle(color: Color(0xFF7B8377)),
                        ),
                        onSubmitted: (_) => _submitQuery(),
                      ),
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.mic_none, color: Color(0xFF6C7467)),
                    ),
                    SizedBox(
                      width: 42,
                      height: 42,
                      child: FilledButton(
                        onPressed: _submitQuery,
                        style: FilledButton.styleFrom(
                          padding: EdgeInsets.zero,
                          backgroundColor: const Color(0xFF3E7C18),
                          shape: const CircleBorder(),
                        ),
                        child: const Icon(Icons.send_rounded, size: 20),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: 1,
        onDestinationSelected: (value) {
          switch (value) {
            case 0:
              Navigator.pushNamedAndRemoveUntil(context, AppRoutes.consumerShell, (route) => false);
              break;
            case 1:
              break;
            case 2:
              Navigator.pushNamed(context, AppRoutes.route);
              break;
            case 3:
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('마이페이지는 Phase 2에서 제공돼요.')),
              );
              break;
          }
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'HOME'),
          NavigationDestination(icon: Icon(Icons.shopping_bag_outlined), selectedIcon: Icon(Icons.shopping_bag), label: 'SHOPPING'),
          NavigationDestination(icon: Icon(Icons.map_outlined), selectedIcon: Icon(Icons.map), label: 'MAP'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'MY'),
        ],
      ),
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  const _RecommendationCard({
    required this.onStoreTap1,
    required this.onStoreTap2,
    required this.onStartRoute,
  });

  final VoidCallback onStoreTap1;
  final VoidCallback onStoreTap2;
  final VoidCallback onStartRoute;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF6F7F4),
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
            child: Stack(
              children: [
                Image.network(
                  'https://images.unsplash.com/photo-1574484284002-952d92456975?auto=format&fit=crop&w=1200&q=80',
                  width: double.infinity,
                  height: 130,
                  fit: BoxFit.cover,
                ),
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.black.withValues(alpha: 0.04),
                          Colors.black.withValues(alpha: 0.28),
                        ],
                      ),
                    ),
                  ),
                ),
                const Positioned(
                  left: 14,
                  bottom: 14,
                  child: Text(
                    '제철 고추장찌개 세트',
                    style: TextStyle(fontSize: 28, color: Color(0xFF1E2619), fontWeight: FontWeight.w900),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Expanded(child: Text('품목 리스트', style: TextStyle(fontSize: 12, color: Color(0xFF7A8376)))),
                    Text('금액', style: TextStyle(fontSize: 12, color: Color(0xFF7A8376))),
                  ],
                ),
                const SizedBox(height: 10),
                const _PriceRow(name: '국내산 돼지고기 (앞다리살)', sub: '300g / 1팩', price: '₩7,800'),
                const SizedBox(height: 8),
                const _PriceRow(name: '제철 햇감자', sub: '2알 / 소량', price: '₩2,400'),
                const SizedBox(height: 8),
                const _PriceRow(name: '애호박 & 대파 세트', sub: '1세트', price: '₩3,500'),
                const SizedBox(height: 12),
                const Divider(height: 1, color: Color(0xFFD6DED0)),
                const SizedBox(height: 12),
                const Row(
                  children: [
                    Expanded(
                      child: Text('합계 예상', style: TextStyle(fontSize: 18, color: Color(0xFF3E7C18), fontWeight: FontWeight.w800)),
                    ),
                    Text('₩13,700', style: TextStyle(fontSize: 30, color: Color(0xFF3E7C18), fontWeight: FontWeight.w900)),
                  ],
                ),
                const SizedBox(height: 12),
                const Text('추천 매칭 점포', style: TextStyle(fontSize: 13, color: Color(0xFF798274), fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                _StoreTile(
                  icon: Icons.storefront,
                  iconBg: const Color(0xFF3E7C18),
                  title: '진흥청과 (A구역)',
                  sub: '120m  ·  재고 여유',
                  onTap: onStoreTap1,
                ),
                const SizedBox(height: 8),
                _StoreTile(
                  icon: Icons.restaurant,
                  iconBg: const Color(0xFFE2865E),
                  title: '우리축산 (B구역)',
                  sub: '250m  ·  5팩 남음',
                  onTap: onStoreTap2,
                ),
                const SizedBox(height: 14),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: FilledButton(
                    onPressed: onStartRoute,
                    style: FilledButton.styleFrom(
                      backgroundColor: const Color(0xFF3E7C18),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
                    ),
                    child: const Text('이 구성으로 길찾기 시작', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PriceRow extends StatelessWidget {
  const _PriceRow({required this.name, required this.sub, required this.price});

  final String name;
  final String sub;
  final String price;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name, style: const TextStyle(fontSize: 19, color: Color(0xFF2A2E27), fontWeight: FontWeight.w700)),
              const SizedBox(height: 2),
              Text(sub, style: const TextStyle(fontSize: 12, color: Color(0xFF6F766D))),
            ],
          ),
        ),
        const SizedBox(width: 10),
        Padding(
          padding: const EdgeInsets.only(top: 2),
          child: Text(price, style: const TextStyle(fontSize: 28, color: Color(0xFF252A23), fontWeight: FontWeight.w900)),
        ),
      ],
    );
  }
}

class _StoreTile extends StatelessWidget {
  const _StoreTile({
    required this.icon,
    required this.iconBg,
    required this.title,
    required this.sub,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final String title;
  final String sub;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFE6ECE0),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
          child: Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: iconBg,
                child: Icon(icon, size: 16, color: Colors.white),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 14, color: Color(0xFF2D332B), fontWeight: FontWeight.w800)),
                    const SizedBox(height: 2),
                    Text(sub, style: const TextStyle(fontSize: 12, color: Color(0xFF727A6E))),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Color(0xFF7E8679)),
            ],
          ),
        ),
      ),
    );
  }
}

class _QuickChip extends StatelessWidget {
  const _QuickChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFE3E9DC),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: const Color(0xFF5A634F)),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 13, color: Color(0xFF5A634F), fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}
