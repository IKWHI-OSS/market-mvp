import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/error_state.dart';
import '../../shared/widgets/market_logo_title.dart';
import 'spotlight_screen.dart';

class EventScreen extends StatefulWidget {
  const EventScreen({super.key, this.eventId});

  final String? eventId;

  @override
  State<EventScreen> createState() => _EventScreenState();
}

class _EventScreenState extends State<EventScreen> {
  late Future<List<EventSummary>> _listFuture;
  Future<EventDetailData>? _detailFuture;
  int _tabIndex = 0;

  @override
  void initState() {
    super.initState();
    _listFuture = ApiClient.instance.getEvents();
    if (widget.eventId != null) {
      _detailFuture = ApiClient.instance.getEventDetail(widget.eventId!);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_detailFuture != null) {
      return _EventDetailView(detailFuture: _detailFuture!);
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      floatingActionButton: FloatingActionButton.small(
        onPressed: () => Navigator.pushNamed(context, AppRoutes.notification),
        backgroundColor: const Color(0xFF4A7D1A),
        child: const Icon(Icons.add, color: Color(0xFFF2F7EC)),
      ),
      body: SafeArea(
        child: FutureBuilder<List<EventSummary>>(
          future: _listFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return ErrorStateWidget(
                title: '행사 정보를 불러오지 못했어요',
                description: '잠시 후 다시 시도해주세요.',
                onRetry: () => setState(() => _listFuture = ApiClient.instance.getEvents()),
                onSecondary: () => Navigator.pushNamed(context, AppRoutes.home),
                secondaryLabel: '운영 공지 보기',
              );
            }
            final events = snapshot.data ?? const <EventSummary>[];
            if (events.isEmpty) {
              return ErrorStateWidget(
                title: '행사가 없어요',
                description: '인근 시장 행사 추천을 확인해보세요.',
                onRetry: () => setState(() => _listFuture = ApiClient.instance.getEvents()),
                onSecondary: () => Navigator.pushNamed(context, AppRoutes.home),
                secondaryLabel: '인근 시장 행사 추천',
              );
            }

            return ListView(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 24),
              children: [
                Row(
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
                      child: const Icon(Icons.arrow_back, size: 18, color: Color(0xFF4A7D1A)),
                    ),
                    const SizedBox(width: 6),
                    const SizedBox(
                      height: 12,
                      child: Align(
                        alignment: Alignment.centerLeft,
                        child: MarketLogoTitle(),
                      ),
                    ),
                    const Spacer(),
                    InkWell(
                      onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                      borderRadius: BorderRadius.circular(12),
                      child: const Icon(Icons.notifications_none, size: 16, color: Color(0xFF4A7D1A)),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  '이번 달\n우리 시장 행사',
                  style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                        color: const Color(0xFF2F5710),
                        height: 1.02,
                      ),
                ),
                const SizedBox(height: 6),
                const Text('다양한 테마와 참여형 콘텐츠를 준비했어요', style: TextStyle(fontSize: 12, color: Color(0xFF7A8376))),
                const SizedBox(height: 10),
                Row(
                  children: [
                    _EventTab(label: '모든 행사', selected: _tabIndex == 0, onTap: () => setState(() => _tabIndex = 0)),
                    const SizedBox(width: 8),
                    _EventTab(label: '수확', selected: _tabIndex == 1, onTap: () => setState(() => _tabIndex = 1)),
                    const SizedBox(width: 8),
                    _EventTab(label: '할인 행사', selected: _tabIndex == 2, onTap: () => setState(() => _tabIndex = 2)),
                  ],
                ),
                const SizedBox(height: 10),
                _HeroEventCard(
                  event: events.first,
                  onDetail: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => EventScreen(eventId: events.first.eventId)),
                  ),
                  onNotify: () => Navigator.pushNamed(context, AppRoutes.notification),
                ),
                const SizedBox(height: 10),
                _BannerCard(
                  title: '한가위 햇채소 대전',
                  subtitle: '가을 장보기에 딱 맞는 신선 채소를 통해\n30% 할인된 행사로 만나보세요.',
                  image: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80',
                  onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                ),
                const SizedBox(height: 10),
                _SimpleEventRow(
                  category: '운영',
                  title: '전통 먹거리 체험 행사',
                  subtitle: '08.01 - 08.06',
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => EventScreen(eventId: events.first.eventId)),
                  ),
                ),
                const SizedBox(height: 8),
                _SimpleEventRow(
                  category: '시장기획',
                  title: '산지직송 로컬 푸드 플리마켓',
                  subtitle: '08.07 - 08.10',
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => EventScreen(eventId: events.last.eventId)),
                  ),
                ),
                const SizedBox(height: 8),
                _SimpleEventRow(
                  category: '이벤트',
                  title: '인기 점포 할인 릴레이 1일전 개시',
                  subtitle: '오늘부터',
                  accent: true,
                  onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                ),
                const SizedBox(height: 10),
                _BannerCard(
                  title: '전통 도자기 장인 박람회',
                  subtitle: '지역 장인 부스와 공예 체험 프로그램 운영',
                  image: 'https://images.unsplash.com/photo-1510166089176-b57564a542b1?auto=format&fit=crop&w=1200&q=80',
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const SpotlightScreen(storeId: 'store_003')),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _EventDetailView extends StatelessWidget {
  const _EventDetailView({required this.detailFuture});

  final Future<EventDetailData> detailFuture;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(title: const Text('행사 상세')),
      body: FutureBuilder<EventDetailData>(
        future: detailFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || snapshot.data == null) {
            return ErrorStateWidget(
              title: '행사 상세를 불러오지 못했어요',
              description: '잠시 후 다시 시도해주세요.',
              onRetry: () => Navigator.pop(context),
            );
          }
          final detail = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(detail.title, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2F5710))),
              const SizedBox(height: 8),
              Text('${detail.periodText} · ${detail.zoneLabel}', style: const TextStyle(color: Color(0xFF7A8376))),
              const SizedBox(height: 10),
              Text(detail.description, style: const TextStyle(color: Color(0xFF3D3B34), height: 1.45)),
              const SizedBox(height: 18),
              Row(
                children: [
                  Expanded(
                    child: FilledButton(
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.notification),
                      child: const Text('행사 알림 받기'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => SpotlightScreen(storeId: detail.relatedStoreId)),
                      ),
                      child: const Text('점포 연결'),
                    ),
                  ),
                ],
              ),
            ],
          );
        },
      ),
    );
  }
}

class _EventTab extends StatelessWidget {
  const _EventTab({required this.label, required this.selected, required this.onTap});

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF4A7D1A) : const Color(0xFFE1E8DA),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: selected ? const Color(0xFFF2F7EC) : const Color(0xFF6F776A)),
        ),
      ),
    );
  }
}

class _HeroEventCard extends StatelessWidget {
  const _HeroEventCard({required this.event, required this.onDetail, required this.onNotify});

  final EventSummary event;
  final VoidCallback onDetail;
  final VoidCallback onNotify;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF0E4),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: Image.network(
              'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?auto=format&fit=crop&w=1200&q=80',
              height: 140,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Text('PREMIUM FESTIVAL', style: TextStyle(fontSize: 9, color: Color(0xFFC26B41), fontWeight: FontWeight.w700)),
              const Spacer(),
              Text(event.periodText, style: const TextStyle(fontSize: 10, color: Color(0xFF7E867A))),
            ],
          ),
          const SizedBox(height: 4),
          Text(event.title, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2D332C), height: 1.02)),
          const SizedBox(height: 8),
          Row(
            children: [
              FilledButton.tonal(
                onPressed: onNotify,
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFFDCE8D0),
                  foregroundColor: const Color(0xFF3F6F22),
                  minimumSize: const Size(92, 34),
                ),
                child: const Text('알림 받기'),
              ),
              const SizedBox(width: 8),
              FilledButton(
                onPressed: onDetail,
                style: FilledButton.styleFrom(minimumSize: const Size(102, 34)),
                child: const Text('상세 보기'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SimpleEventRow extends StatelessWidget {
  const _SimpleEventRow({
    required this.category,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.accent = false,
  });

  final String category;
  final String title;
  final String subtitle;
  final bool accent;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: accent ? const Color(0xFFFCC4A8) : const Color(0xFFE7EDE1),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(category, style: TextStyle(fontSize: 10, color: accent ? const Color(0xFF9D4F2D) : const Color(0xFF74806E), fontWeight: FontWeight.w700)),
                    const SizedBox(height: 4),
                    Text(title, style: const TextStyle(fontSize: 13, color: Color(0xFF323831), fontWeight: FontWeight.w700)),
                    const SizedBox(height: 2),
                    Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF7C8479))),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward, size: 16, color: Color(0xFF6F776A)),
            ],
          ),
        ),
      ),
    );
  }
}

class _BannerCard extends StatelessWidget {
  const _BannerCard({
    required this.title,
    required this.subtitle,
    required this.image,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final String image;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: Stack(
          children: [
            Image.network(
              image,
              height: 168,
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
                      Colors.black.withValues(alpha: 0.08),
                      Colors.black.withValues(alpha: 0.56),
                    ],
                  ),
                ),
              ),
            ),
            Positioned(
              left: 12,
              right: 12,
              bottom: 12,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: Colors.white)),
                  const SizedBox(height: 4),
                  Text(subtitle, style: const TextStyle(fontSize: 12, color: Color(0xFFEAF0E3))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
