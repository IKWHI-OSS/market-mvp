import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/error_state.dart';

class SpotlightScreen extends StatefulWidget {
  const SpotlightScreen({super.key, this.storeId});

  final String? storeId;

  @override
  State<SpotlightScreen> createState() => _SpotlightScreenState();
}

class _SpotlightScreenState extends State<SpotlightScreen> {
  late Future<List<SpotlightSummary>> _listFuture;
  Future<SpotlightDetailData>? _detailFuture;

  @override
  void initState() {
    super.initState();
    _listFuture = ApiClient.instance.getSpotlights();
    if (widget.storeId != null) {
      _detailFuture = ApiClient.instance.getSpotlightDetail(widget.storeId!);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_detailFuture != null) {
      return _SpotlightDetailView(detailFuture: _detailFuture!);
    }
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(title: const Text('점포 스포트라이트')),
      body: FutureBuilder<List<SpotlightSummary>>(
        future: _listFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return ErrorStateWidget(
              title: '점포 정보를 불러오지 못했어요',
              description: '잠시 후 다시 시도해주세요.',
              onRetry: () => setState(() => _listFuture = ApiClient.instance.getSpotlights()),
              onSecondary: () => Navigator.pushNamed(context, AppRoutes.route),
              secondaryLabel: '인근 시장 안내',
            );
          }
          final stores = snapshot.data ?? const <SpotlightSummary>[];
          if (stores.isEmpty) {
            return ErrorStateWidget(
              title: '스포트라이트 점포가 없어요',
              description: '기본 점포 프로필을 확인해보세요.',
              onRetry: () => setState(() => _listFuture = ApiClient.instance.getSpotlights()),
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: stores.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final store = stores[index];
              return Material(
                color: const Color(0xFFEBF3E3),
                borderRadius: BorderRadius.circular(14),
                child: InkWell(
                  borderRadius: BorderRadius.circular(14),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => SpotlightScreen(storeId: store.storeId)),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(store.storeName, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2F5710))),
                        const SizedBox(height: 6),
                        Text(store.summary, style: const TextStyle(color: Color(0xFF4D5A43), height: 1.4)),
                        const SizedBox(height: 10),
                        FilledButton.tonal(
                          onPressed: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => SpotlightScreen(storeId: store.storeId)),
                          ),
                          child: const Text('상세 소개 보기'),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class _SpotlightDetailView extends StatelessWidget {
  const _SpotlightDetailView({required this.detailFuture});

  final Future<SpotlightDetailData> detailFuture;

  String _heroImage(String storeId) {
    switch (storeId) {
      case 'store_003':
        return 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1200&q=80';
      case 'store_004':
        return 'https://images.unsplash.com/photo-1517433670267-08bbd4be890f?auto=format&fit=crop&w=1200&q=80';
      default:
        return 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1200&q=80';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      body: FutureBuilder<SpotlightDetailData>(
        future: detailFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || snapshot.data == null) {
            return ErrorStateWidget(
              title: '점포 상세를 불러오지 못했어요',
              description: '잠시 후 다시 시도해주세요.',
              onRetry: () => Navigator.pop(context),
              onSecondary: () => Navigator.pushNamed(context, AppRoutes.route),
              secondaryLabel: '인근 시장 안내',
            );
          }

          final detail = snapshot.data!;
          final zoneText = detail.zoneLabel.trim().isEmpty ? '구역 정보 미지원' : detail.zoneLabel;

          return Column(
            children: [
              Expanded(
                child: ListView(
                  padding: EdgeInsets.zero,
                  children: [
                    SafeArea(
                      bottom: false,
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
                        child: Row(
                          children: [
                            InkWell(
                              onTap: () => Navigator.pop(context),
                              borderRadius: BorderRadius.circular(12),
                              child: const Icon(Icons.arrow_back, size: 18, color: Color(0xFF4A7D1A)),
                            ),
                            const SizedBox(width: 5),
                            const Text('Market Info', style: TextStyle(fontSize: 12, color: Color(0xFF4A7D1A), fontWeight: FontWeight.w700)),
                            const Spacer(),
                            InkWell(
                              onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                              borderRadius: BorderRadius.circular(12),
                              child: const Icon(Icons.notifications_none, size: 16, color: Color(0xFF4A7D1A)),
                            ),
                          ],
                        ),
                      ),
                    ),
                    ClipRRect(
                      borderRadius: const BorderRadius.vertical(bottom: Radius.circular(16)),
                      child: Image.network(
                        _heroImage(detail.storeId),
                        height: 220,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFDFF0CF),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Text('Authentic Heritage', style: TextStyle(fontSize: 11, color: Color(0xFF4A7D1A), fontWeight: FontWeight.w700)),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            '청년 과일 상점',
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2F5710)),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '"${detail.summary}"',
                            style: const TextStyle(fontSize: 14, color: Color(0xFF3D3B34), height: 1.45, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 10),
                          const Text(
                            '매일 아침 제철 과일을 선별해 소개합니다. 신선한 품질과 합리적 가격을 함께 전하고 있어요.',
                            style: TextStyle(fontSize: 13, color: Color(0xFF5E5B53), height: 1.5),
                          ),
                          const SizedBox(height: 10),
                          _InfoRow(title: '상호', value: detail.storeName),
                          const SizedBox(height: 8),
                          _InfoRow(title: '운영 시간', value: detail.openHours),
                          const SizedBox(height: 8),
                          _InfoRow(title: '구역 안내', value: zoneText),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: FilledButton.tonal(
                                  onPressed: () => Navigator.pushNamed(context, AppRoutes.drop),
                                  style: FilledButton.styleFrom(
                                    backgroundColor: const Color(0xFFF7CBB2),
                                    foregroundColor: const Color(0xFFA34220),
                                  ),
                                  child: const Text('입고 알림 받기'),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: OutlinedButton(
                                  onPressed: () => Navigator.pushNamed(context, AppRoutes.route),
                                  child: const Text('점포 보러가기'),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 14),
                          Text('오늘의 추천 품목', style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2F5710))),
                          const SizedBox(height: 8),
                          const _ProductCard(
                            name: '유기농 현미',
                            subtitle: '갓 도정한 신선한 곡물',
                            price: '₩12,000',
                            image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80',
                          ),
                          const SizedBox(height: 8),
                          const _ProductCard(
                            name: '붉은 강낭콩',
                            subtitle: '영양 가득한 제철 콩',
                            price: '₩6,500',
                            image: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80',
                          ),
                          const SizedBox(height: 8),
                          _ProductCard(
                            name: detail.highlightProduct,
                            subtitle: '오늘 가장 많이 찾는 인기 품목',
                            price: '₩8,900',
                            image: 'https://images.unsplash.com/photo-1586201375761-83865001e17c?auto=format&fit=crop&w=800&q=80',
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
                child: FilledButton(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.route),
                  style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(46)),
                  child: const Text('점포로 길 안내받기'),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.title, required this.value});

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFE8EDE3),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Text(title, style: const TextStyle(fontSize: 12, color: Color(0xFF7A8176), fontWeight: FontWeight.w700)),
          const Spacer(),
          Text(value, style: const TextStyle(fontSize: 13, color: Color(0xFF2F5710), fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class _ProductCard extends StatelessWidget {
  const _ProductCard({
    required this.name,
    required this.subtitle,
    required this.price,
    required this.image,
  });

  final String name;
  final String subtitle;
  final String price;
  final String image;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFFFDFBF5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: Image.network(image, width: 72, height: 72, fit: BoxFit.cover),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF2F5710))),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: Color(0xFF6A7366))),
                const SizedBox(height: 8),
                Text(price, style: const TextStyle(fontSize: 14, color: Color(0xFFD4663A), fontWeight: FontWeight.w800)),
              ],
            ),
          ),
          const Icon(Icons.add_circle_outline, color: Color(0xFF4A7D1A), size: 18),
        ],
      ),
    );
  }
}
