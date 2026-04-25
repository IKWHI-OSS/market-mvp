import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/market_logo_title.dart';
import '../search/product_detail_screen.dart';

class RouteScreen extends StatefulWidget {
  const RouteScreen({super.key});

  @override
  State<RouteScreen> createState() => _RouteScreenState();
}

class _RouteScreenState extends State<RouteScreen> {
  final List<_RouteStop> _stops = [
    const _RouteStop(
      title: '정선 할머니 한과',
      distance: '현재 위치에서 80m',
      zone: 'A구역 12호',
      productId: 'product_001',
      imageUrl: 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=200&q=80',
    ),
    const _RouteStop(
      title: '원조 마약김밥 2호점',
      distance: '+150m',
      zone: 'B구역 05호',
      productId: 'product_002',
      imageUrl: 'https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=200&q=80',
    ),
    const _RouteStop(
      title: '대성 축산물 도매',
      distance: '+220m',
      zone: 'C구역 08호',
      productId: 'product_001',
      imageUrl: 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=200&q=80',
    ),
    const _RouteStop(
      title: '청정 채소 달래상회',
      distance: '+320m',
      zone: 'A구역 20호',
      productId: 'product_003',
      imageUrl: 'https://images.unsplash.com/photo-1518843875459-f738682238a6?auto=format&fit=crop&w=200&q=80',
    ),
  ];

  int _currentIndex = 0;
  final Set<int> _visited = <int>{};

  void _markVisited() {
    final doneIndex = _currentIndex;
    setState(() {
      _visited.add(doneIndex);
      if (_currentIndex < _stops.length - 1) {
        _currentIndex += 1;
      }
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('방문 완료: ${_stops[doneIndex].title}'),
        duration: const Duration(milliseconds: 1200),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final current = _stops[_currentIndex];

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5EB),
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.network(
              'https://images.unsplash.com/photo-1577086664693-894d8405334a?auto=format&fit=crop&w=1200&q=80',
              fit: BoxFit.cover,
            ),
          ),
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.20),
              ),
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(14, 8, 14, 10),
              child: Column(
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF1F4EC),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        InkWell(
                          onTap: () {
                            Navigator.pushNamedAndRemoveUntil(
                              context,
                              AppRoutes.consumerShell,
                              (route) => false,
                            );
                          },
                          borderRadius: BorderRadius.circular(12),
                          child: const Icon(Icons.arrow_back, color: Color(0xFF4A7B29)),
                        ),
                        const SizedBox(width: 8),
                        const MarketLogoTitle(),
                        const Spacer(),
                        InkWell(
                          onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                          borderRadius: BorderRadius.circular(12),
                          child: const Icon(Icons.notifications_none, size: 20, color: Color(0xFF4A7B29)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF1F4EC),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      children: [
                        const CircleAvatar(
                          radius: 18,
                          backgroundColor: Color(0xFFDEE8D2),
                          child: Icon(Icons.directions_walk, color: Color(0xFF447A25)),
                        ),
                        const SizedBox(width: 10),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('추천 경로 진행 중', style: TextStyle(fontSize: 12, color: Color(0xFF6D7567), fontWeight: FontWeight.w600)),
                              SizedBox(height: 2),
                              Text('예상 소요 15분 / 450m', style: TextStyle(fontSize: 16, color: Color(0xFF252B24), fontWeight: FontWeight.w900)),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF7D9C8),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: const Text('● LIVE', style: TextStyle(fontSize: 11, color: Color(0xFFAA5B3B), fontWeight: FontWeight.w800)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          DraggableScrollableSheet(
            initialChildSize: 0.38,
            minChildSize: 0.28,
            maxChildSize: 0.74,
            builder: (context, scrollController) {
              return Container(
                width: double.infinity,
                padding: const EdgeInsets.fromLTRB(14, 10, 14, 12),
                decoration: const BoxDecoration(
                  color: Color(0xFFF0F4EC),
                  borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                ),
                child: ListView(
                  controller: scrollController,
                  children: [
                    Align(
                      child: Container(
                        width: 44,
                        height: 5,
                        decoration: BoxDecoration(
                          color: const Color(0xFFD0D7C8),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Text(
                          '방문 리스트',
                          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                                color: const Color(0xFF2C312B),
                                height: 1.0,
                              ),
                        ),
                        const Spacer(),
                        Text(
                          '${_visited.length} / ${_stops.length}',
                          style: const TextStyle(fontSize: 22, color: Color(0xFF3F7A1E), fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(width: 4),
                        const Text('완료', style: TextStyle(fontSize: 13, color: Color(0xFF7D8578), fontWeight: FontWeight.w700)),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Text('동선에 따라 상점이 정렬되었습니다.', style: TextStyle(fontSize: 13, color: Color(0xFF6F766D))),
                    const SizedBox(height: 10),
                    _NextStoreCard(
                      stop: current,
                      onViewStore: () => Navigator.pushNamed(
                        context,
                        AppRoutes.productDetail,
                        arguments: ProductDetailArgs(productId: current.productId),
                      ),
                      onDone: _markVisited,
                    ),
                    const SizedBox(height: 10),
                    ..._stops.asMap().entries.where((e) => e.key != _currentIndex).map(
                          (entry) => Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: _StoreRow(
                              title: entry.value.title,
                              distance: entry.value.distance,
                              zone: entry.value.zone,
                              done: _visited.contains(entry.key),
                              onTap: () => Navigator.pushNamed(
                                context,
                                AppRoutes.productDetail,
                                arguments: ProductDetailArgs(productId: entry.value.productId),
                              ),
                            ),
                          ),
                        ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _NextStoreCard extends StatelessWidget {
  const _NextStoreCard({required this.stop, required this.onViewStore, required this.onDone});

  final _RouteStop stop;
  final VoidCallback onViewStore;
  final VoidCallback onDone;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFE8EEE1),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF3C7A1C), width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const DecoratedBox(
                decoration: BoxDecoration(color: Color(0xFF3C7A1C), borderRadius: BorderRadius.all(Radius.circular(12))),
                child: Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  child: Text('NEXT', style: TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.w800)),
                ),
              ),
              const SizedBox(width: 8),
              Text(stop.distance, style: const TextStyle(fontSize: 14, color: Color(0xFF3C7A1C), fontWeight: FontWeight.w800)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Text(
                  stop.title,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2C312B)),
                ),
              ),
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.network(
                  stop.imageUrl,
                  width: 72,
                  height: 72,
                  fit: BoxFit.cover,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            height: 26,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFDCE6D1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text('구역 안내: ${stop.zone}', style: const TextStyle(fontSize: 12, color: Color(0xFF586252), fontWeight: FontWeight.w700)),
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: FilledButton(
                  onPressed: onDone,
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF3C7A1C),
                    minimumSize: const Size.fromHeight(42),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('방문 완료 체크'),
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                onPressed: onViewStore,
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(90, 42),
                  side: const BorderSide(color: Color(0xFF98B488)),
                  foregroundColor: const Color(0xFF3C7A1C),
                ),
                child: const Text('점포 보기'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _StoreRow extends StatelessWidget {
  const _StoreRow({
    required this.title,
    required this.distance,
    required this.zone,
    required this.done,
    required this.onTap,
  });

  final String title;
  final String distance;
  final String zone;
  final bool done;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFE8EDE3),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          padding: const EdgeInsets.fromLTRB(14, 14, 10, 14),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF434940))),
                        ),
                        if (done)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFD9E9CD),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text('방문 완료', style: TextStyle(fontSize: 11, color: Color(0xFF3F7A1E), fontWeight: FontWeight.w700)),
                          ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text('구역 안내: $zone', style: const TextStyle(fontSize: 12, color: Color(0xFF7F877C))),
                  ],
                ),
              ),
              Column(
                children: [
                  Text(distance, style: const TextStyle(fontSize: 12, color: Color(0xFF8B9089), fontWeight: FontWeight.w700)),
                  const SizedBox(height: 10),
                  const CircleAvatar(
                    radius: 14,
                    backgroundColor: Color(0xFFD7DDD0),
                    child: Icon(Icons.chevron_right, size: 18, color: Color(0xFF848C80)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RouteStop {
  const _RouteStop({
    required this.title,
    required this.distance,
    required this.zone,
    required this.productId,
    required this.imageUrl,
  });

  final String title;
  final String distance;
  final String zone;
  final String productId;
  final String imageUrl;
}
