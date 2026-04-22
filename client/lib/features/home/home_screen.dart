import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/market_logo_title.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F7EA),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(12, 12, 12, 24),
        children: [
          SafeArea(
            bottom: false,
            child: Row(
              children: [
                const SizedBox(
                  height: 24,
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: MarketLogoTitle(),
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE2EED7),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.location_on, size: 14, color: Color(0xFF5F7A4F)),
                      SizedBox(width: 4),
                      Text(
                        '중곡제일도깨비시장',
                        style: TextStyle(fontSize: 11, color: Color(0xFF5F7A4F), fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                InkWell(
                  onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                  borderRadius: BorderRadius.circular(12),
                  child: const Icon(Icons.notifications_none, size: 19, color: Color(0xFF5F7A4F)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Container(
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFFE6EEE0),
              borderRadius: BorderRadius.circular(12),
            ),
            child: TextField(
              readOnly: true,
              onTap: () => Navigator.pushNamed(context, AppRoutes.search),
              decoration: const InputDecoration(
                contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 11),
                border: InputBorder.none,
                hintText: '어떤 상품을 찾으시나요?',
                hintStyle: TextStyle(fontSize: 12, color: Color(0xFF98A48E)),
                suffixIcon: Icon(Icons.search, size: 18, color: Color(0xFF5F7A4F)),
              ),
            ),
          ),
          const SizedBox(height: 18),
          _SectionHeader(
            title: '오늘의 드랍',
            actionLabel: '전체 보기',
            onTap: () => Navigator.pushNamed(context, AppRoutes.drop),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Stack(
              children: [
                Image.network(
                  'https://images.unsplash.com/photo-1605027990121-cbae9e0642df?auto=format&fit=crop&w=900&q=80',
                  height: 320,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.black.withValues(alpha: 0.06),
                          Colors.black.withValues(alpha: 0.56),
                        ],
                      ),
                    ),
                  ),
                ),
                const Positioned(
                  left: 14,
                  top: 12,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: Color(0xCC181818),
                      borderRadius: BorderRadius.all(Radius.circular(14)),
                    ),
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      child: Text(
                        '예정 | 09:00',
                        style: TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                ),
                Positioned(
                  left: 14,
                  bottom: 68,
                  child: Text(
                    '하동에서 온 꿀맛 단감',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          color: Colors.white,
                          height: 1.03,
                        ),
                  ),
                ),
                Positioned(
                  left: 14,
                  right: 14,
                  bottom: 14,
                  child: SizedBox(
                    height: 40,
                    child: FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF4B8A2A),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.drop),
                      icon: const Icon(Icons.notifications_none, size: 18),
                      label: const Text('알림 받기'),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              _QuickAction(
                icon: Icons.storefront_outlined,
                label: '점포 찾기',
                color: const Color(0xFFFFD79C),
                onTap: () => Navigator.pushNamed(context, AppRoutes.search),
              ),
              _QuickAction(
                icon: Icons.notifications_active_outlined,
                label: '입고 알림',
                color: const Color(0xFFD8F2C5),
                onTap: () => Navigator.pushNamed(context, AppRoutes.drop),
              ),
              _QuickAction(
                icon: Icons.inventory_2_outlined,
                label: '장보기 에이전트',
                color: const Color(0xFFCDE8FF),
                onTap: () => Navigator.pushNamed(context, AppRoutes.agent),
              ),
              _QuickAction(
                icon: Icons.route_outlined,
                label: '장보기 동선',
                color: const Color(0xFFEFD4FF),
                onTap: () => Navigator.pushNamed(context, AppRoutes.route),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _SectionHeader(
            title: '시장 이벤트',
            actionLabel: '전체 보기',
            onTap: () => Navigator.pushNamed(context, AppRoutes.event),
          ),
          const SizedBox(height: 10),
          SizedBox(
            height: 204,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                _EventCard(
                  title: '전통시장 이벤트',
                  subtitle: '이번 주말, 봄 프로모션 5개 테마가 준비돼요',
                  imageUrl: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=80',
                  onTap: () => Navigator.pushNamed(context, AppRoutes.event),
                ),
                _EventCard(
                  title: '청과 특별전',
                  subtitle: '제철 과일 시식과 라이브 특가를 만나보세요',
                  imageUrl: 'https://images.unsplash.com/photo-1519996521439-75b6d4d6f2f2?auto=format&fit=crop&w=900&q=80',
                  onTap: () => Navigator.pushNamed(context, AppRoutes.event),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          _SectionHeader(
            title: '지금 뜨는 점포',
            actionLabel: '전체 보기',
            onTap: () => Navigator.pushNamed(context, AppRoutes.spotlight),
          ),
          const SizedBox(height: 10),
          _SpotlightCard(
            storeName: '중앙 채소점',
            category: '청과/채소',
            description: '“매일 새벽 선별해 신선한 채소만 판매하고 있습니다.”',
            onTap: () => Navigator.pushNamed(context, AppRoutes.spotlight),
          ),
          const SizedBox(height: 10),
          _SpotlightCard(
            storeName: '연서 베이커리',
            category: '간편식/빵',
            description: '“시장표 베이커리의 진짜 매력, 매일 아침 직접 굽습니다.”',
            onTap: () => Navigator.pushNamed(context, AppRoutes.spotlight),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, required this.actionLabel, required this.onTap});

  final String title;
  final String actionLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF262626))),
        const Spacer(),
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: Text(
            actionLabel,
            style: const TextStyle(fontSize: 12, color: Color(0xFF4F8D2F), fontWeight: FontWeight.w700),
          ),
        ),
      ],
    );
  }
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Column(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, size: 24, color: const Color(0xFF536348)),
            ),
            const SizedBox(height: 6),
            Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF586254))),
          ],
        ),
      ),
    );
  }
}

class _EventCard extends StatelessWidget {
  const _EventCard({
    required this.title,
    required this.subtitle,
    required this.imageUrl,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final String imageUrl;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 240,
        margin: const EdgeInsets.only(right: 10),
        decoration: BoxDecoration(
          color: const Color(0xFFF5F5F5),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE2E2E2)),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                height: 106,
                width: double.infinity,
                child: Image.network(
                  imageUrl,
                  fit: BoxFit.cover,
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF2D2D2D))),
                    const SizedBox(height: 8),
                    Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF707070), height: 1.4)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SpotlightCard extends StatelessWidget {
  const _SpotlightCard({
    required this.storeName,
    required this.category,
    required this.description,
    required this.onTap,
  });

  final String storeName;
  final String category;
  final String description;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFEBF3E3),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFD8E6CC)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              ClipOval(
                child: Image.network(
                  'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=120&q=80',
                  width: 34,
                  height: 34,
                  fit: BoxFit.cover,
                ),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(storeName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                  Text(category, style: const TextStyle(fontSize: 10, color: Color(0xFFB17B2F))),
                ],
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(description, style: const TextStyle(fontSize: 12, color: Color(0xFF516044), height: 1.4)),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            height: 34,
            child: FilledButton.tonal(
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFFE0EAD5),
                foregroundColor: const Color(0xFF4E6A39),
              ),
              onPressed: onTap,
              child: const Text('장보기 동선에 추가하기', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
            ),
          ),
        ],
      ),
    );
  }
}
