import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/market_logo_title.dart';

class MerchantDashboardScreen extends StatelessWidget {
  const MerchantDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => Navigator.pushNamedAndRemoveUntil(
            context,
            AppRoutes.login,
            (route) => false,
          ),
        ),
        title: const MarketLogoTitle(),
        actions: [
          IconButton(
            onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('알림 기능은 준비 중입니다.')),
            ),
            icon: const Icon(Icons.notifications_none),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
        children: [
          const SizedBox(height: 14),
          Text(
            '반갑습니다, 김민석님',
            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontSize: 36,
                  fontWeight: FontWeight.w800,
                  color: const Color(0xFF2F5710),
                ),
          ),
          const SizedBox(height: 6),
          const Text(
            '오늘의 시장 현황과 관리할 업무를 확인하세요.',
            style: TextStyle(fontSize: 13, color: Color(0xFF625E55)),
          ),
          const SizedBox(height: 14),
          const _PulseCard(
            visitors: 350,
            changeRate: 12,
          ),
          const SizedBox(height: 10),
          const _AlertCard(riskCount: 3),
          const SizedBox(height: 18),
          Row(
            children: [
              Text(
                '상점 관리 도구',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: const Color(0xFF1E1D18),
                    ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: const Color(0xFFE8EDE3),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Text(
                  '3개의 할 일',
                  style: TextStyle(fontSize: 11, color: Color(0xFF625E55), fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          _TaskTile(
            icon: Icons.location_on_outlined,
            iconBg: const Color(0xFFDFF0CF),
            title: '신규 드랍 등록',
            subtitle: '설정 안 된 신선 산지 직송 예약',
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('드랍 등록 화면은 다음 단계에서 연결됩니다.')),
            ),
          ),
          const SizedBox(height: 8),
          _TaskTile(
            icon: Icons.sell_outlined,
            iconBg: const Color(0xFFF5CDB5),
            title: '가격 정보 갱신',
            subtitle: '정보 변경 반영',
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('재고/가격 관리(SCR-M-05)는 Phase 2 범위입니다.')),
            ),
          ),
          const SizedBox(height: 8),
          _TaskTile(
            icon: Icons.verified_outlined,
            iconBg: const Color(0xFFE8E5DE),
            title: '상인 스토리 생성',
            subtitle: '점포 소개문 자동 생성 후 검토',
            onTap: () => Navigator.pushNamed(context, AppRoutes.merchantStory),
          ),
          const SizedBox(height: 14),
          _PromoCard(
            onTap: () => Navigator.pushNamed(context, AppRoutes.merchantProductForm),
          ),
        ],
      ),
      floatingActionButton: Padding(
        padding: const EdgeInsets.only(bottom: 20),
        child: FloatingActionButton.extended(
          onPressed: () => Navigator.pushNamed(context, AppRoutes.merchantProductForm),
          backgroundColor: const Color(0xFF4A7D1A),
          foregroundColor: const Color(0xFFF2F7EC),
          icon: const Icon(Icons.add_circle_outline),
          label: const Text('상품 등록'),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    );
  }
}

class _PulseCard extends StatelessWidget {
  const _PulseCard({required this.visitors, required this.changeRate});

  final int visitors;
  final int changeRate;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFE8EDE3),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Spacer(),
              Icon(Icons.show_chart, size: 30, color: Color(0xFFA8D175)),
            ],
          ),
          const SizedBox(height: 2),
          const Text('오늘의 시장 방문자', style: TextStyle(fontSize: 12, color: Color(0xFF625E55))),
          const SizedBox(height: 2),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '$visitors',
                style: const TextStyle(
                  fontSize: 46,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF000000),
                  height: 0.95,
                ),
              ),
              const Spacer(),
              Text(
                '↑ $changeRate%',
                style: const TextStyle(fontSize: 12, color: Color(0xFF2F5710), fontWeight: FontWeight.w800),
              ),
              const SizedBox(width: 4),
              const Text('vs yesterday', style: TextStyle(fontSize: 10, color: Color(0xFF928E84))),
            ],
          ),
        ],
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  const _AlertCard({required this.riskCount});

  final int riskCount;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF5CDB5),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          const Icon(Icons.inventory_2_outlined, size: 18, color: Color(0xFFA34220)),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('재고 부족 상품', style: TextStyle(fontSize: 12, color: Color(0xFFA34220), fontWeight: FontWeight.w700)),
                const SizedBox(height: 2),
                Text('$riskCount', style: Theme.of(context).textTheme.headlineLarge?.copyWith(color: const Color(0xFF6E2B12))),
                const Text('품목 보충 필요', style: TextStyle(fontSize: 11, color: Color(0xFFA34220))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TaskTile extends StatelessWidget {
  const _TaskTile({
    required this.icon,
    required this.iconBg,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFEBF3E3),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(color: iconBg, shape: BoxShape.circle),
                child: Icon(icon, size: 18, color: const Color(0xFF2F5710)),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF1E1D18))),
                    const SizedBox(height: 2),
                    Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF625E55))),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Color(0xFF928E84)),
            ],
          ),
        ),
      ),
    );
  }
}

class _PromoCard extends StatelessWidget {
  const _PromoCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Ink(
          height: 118,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            image: const DecorationImage(
              image: NetworkImage('https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1200&q=80'),
              fit: BoxFit.cover,
            ),
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: const LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [Color(0x9A1E1D18), Color(0x331E1D18)],
              ),
            ),
            padding: const EdgeInsets.all(12),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Text('드랍 아이템 등록', style: TextStyle(fontSize: 18, color: Color(0xFFF2F7EC), fontWeight: FontWeight.w800)),
                SizedBox(height: 2),
                Text('명산물 제휴에 대한 드랍 게시를 등록해 보세요.', style: TextStyle(fontSize: 11, color: Color(0xFFE8E5DE))),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
