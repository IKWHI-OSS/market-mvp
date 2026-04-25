import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/error_state.dart';
import '../../shared/widgets/market_logo_title.dart';
import 'product_detail_screen.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _controller = TextEditingController();
  Future<List<ProductSummary>>? _future;
  int _selectedFilter = 0;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submitSearch() {
    final query = _controller.text.trim();
    if (query.isEmpty) {
      setState(() {
        _future = null;
      });
      return;
    }
    setState(() {
      _future = ApiClient.instance.searchProducts(query: query);
    });
  }

  String _stockLabel(String stockStatus) {
    switch (stockStatus) {
      case 'in_stock':
        return '재고 있음';
      case 'low_stock':
        return '적음';
      case 'out_of_stock':
        return '품절';
      default:
        return '확인중';
    }
  }

  String _priceText(int value) => '₩${value.toString()}';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5EB),
      body: SafeArea(
        child: Stack(
          children: [
            ListView(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 132),
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
                  child: const Icon(Icons.arrow_back, color: Color(0xFF4A7B29)),
                ),
                const SizedBox(width: 10),
                const SizedBox(
                  height: 37,
                    child: Align(
                    alignment: Alignment.centerLeft,
                    child: MarketLogoTitle(),
                  ),
                ),
                const Spacer(),
                InkWell(
                  onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                  borderRadius: BorderRadius.circular(12),
                  child: const Icon(Icons.notifications_none, size: 20, color: Color(0xFF4A7B29)),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Container(
              height: 48,
              decoration: BoxDecoration(
                color: const Color(0xFFDEE4DA),
                borderRadius: BorderRadius.circular(12),
              ),
              child: TextField(
                controller: _controller,
                onSubmitted: (_) => _submitSearch(),
                decoration: const InputDecoration(
                  contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  border: InputBorder.none,
                  prefixIcon: Icon(Icons.search, size: 20, color: Color(0xFF73826B)),
                  hintText: '신선한 유기농 딸기',
                  hintStyle: TextStyle(color: Color(0xFF8A9584)),
                ),
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                _FilterChip(
                  label: '가격순',
                  selected: _selectedFilter == 0,
                  onTap: () => setState(() => _selectedFilter = 0),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: '거리순',
                  selected: _selectedFilter == 1,
                  onTap: () => setState(() => _selectedFilter = 1),
                ),
                const SizedBox(width: 8),
                _FilterChip(
                  label: '재고있음',
                  selected: _selectedFilter == 2,
                  onTap: () => setState(() => _selectedFilter = 2),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_future == null)
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFE8EDE3),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Text(
                  '검색어를 입력하면 점포별 비교 결과를 보여드릴게요.',
                  style: TextStyle(fontSize: 14, color: Color(0xFF6F766D)),
                ),
              )
            else
              FutureBuilder<List<ProductSummary>>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()));
                }
                if (snapshot.hasError) {
                  return ErrorStateWidget(
                    title: '검색 중 문제가 발생했어요',
                    description: '잠시 후 다시 시도해주세요.',
                    onRetry: _submitSearch,
                    onSecondary: _submitSearch,
                    secondaryLabel: '유사 상품 추천',
                  );
                }
                final items = snapshot.data ?? const <ProductSummary>[];
                if (items.isEmpty) {
                  return ErrorStateWidget(
                    title: '검색 결과가 없어요',
                    description: '유사 상품으로 다시 찾아볼 수 있어요.',
                    onRetry: () {
                      _controller.text = '단감';
                      _submitSearch();
                    },
                    onSecondary: () => Navigator.pushNamed(context, AppRoutes.home),
                    secondaryLabel: '인근 시장 안내',
                  );
                }
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          '비교 결과',
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF1F1F1F)),
                        ),
                        const SizedBox(width: 8),
                        Text('${items.length}개 매장', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF4F8A2E))),
                        const Spacer(),
                        const Text('최근 업데이트 순', style: TextStyle(fontSize: 11, color: Color(0xFF929A8E))),
                      ],
                    ),
                    const SizedBox(height: 12),
                    ...items.asMap().entries.map((entry) {
                      final index = entry.key;
                      final item = entry.value;
                      final isSoldOut = item.stockStatus == 'out_of_stock';
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: _CompareCard(
                          title: item.productName,
                          storeName: item.storeName,
                          price: _priceText(item.price),
                          statusText: _stockLabel(item.stockStatus),
                          subText: index == 0 ? '2시간 전  ·  450m' : index == 1 ? '1시간 전  ·  1.2km' : '30분 전  ·  800m',
                          disabled: isSoldOut,
                          imageUrl: index == 0
                              ? 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=200&q=80'
                              : index == 1
                                  ? 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=200&q=80'
                                  : 'https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=200&q=80',
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.productDetail,
                            arguments: ProductDetailArgs(productId: item.productId),
                          ),
                          onAddRoute: () => Navigator.pushNamed(context, AppRoutes.route),
                        ),
                      );
                    }),
                    const SizedBox(height: 12),
                    _BestChoiceCard(
                      item: items.first,
                      imageUrl: 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=500&q=80',
                      onAddRoute: () => Navigator.pushNamed(context, AppRoutes.route),
                      onTap: () => Navigator.pushNamed(
                        context,
                        AppRoutes.productDetail,
                        arguments: ProductDetailArgs(productId: items.first.productId),
                      ),
                    ),
                  ],
                );
              },
            ),
              ],
            ),
            Positioned(
              left: 28,
              right: 28,
              bottom: 14,
              child: SizedBox(
                height: 48,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF356C14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                  ),
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.route),
                  child: const Text('추천 동선 보기', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF3D7C13) : const Color(0xFFE3E8DD),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: selected ? Colors.white : const Color(0xFF6C7865),
          ),
        ),
      ),
    );
  }
}

class _CompareCard extends StatelessWidget {
  const _CompareCard({
    required this.title,
    required this.storeName,
    required this.price,
    required this.statusText,
    required this.subText,
    required this.disabled,
    required this.imageUrl,
    required this.onTap,
    required this.onAddRoute,
  });

  final String title;
  final String storeName;
  final String price;
  final String statusText;
  final String subText;
  final bool disabled;
  final String imageUrl;
  final VoidCallback onTap;
  final VoidCallback onAddRoute;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.network(imageUrl, width: 78, height: 78, fit: BoxFit.cover),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            storeName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w800,
                              color: disabled ? const Color(0xFF8E938C) : const Color(0xFF30342F),
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: disabled ? const Color(0xFFE6E8E3) : const Color(0xFFD7EFC2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            statusText,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w700,
                              color: disabled ? const Color(0xFF8B918A) : const Color(0xFF4A8129),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 3),
                    Text(
                      price,
                      style: TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.w800,
                        color: disabled ? const Color(0xFF8E938C) : const Color(0xFF386D19),
                      ),
                    ),
                    Text(subText, style: const TextStyle(fontSize: 11, color: Color(0xFF9AA194))),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              SizedBox(
                width: 52,
                height: 52,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    padding: EdgeInsets.zero,
                    backgroundColor: disabled ? const Color(0xFFE6EBE3) : const Color(0xFFF8B89B),
                    foregroundColor: disabled ? const Color(0xFFA3AAA1) : const Color(0xFF8D4E32),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  ),
                  onPressed: disabled ? null : onAddRoute,
                  child: const Icon(Icons.route, size: 28),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BestChoiceCard extends StatelessWidget {
  const _BestChoiceCard({
    required this.item,
    required this.imageUrl,
    required this.onAddRoute,
    required this.onTap,
  });

  final ProductSummary item;
  final String imageUrl;
  final VoidCallback onAddRoute;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFF417C19),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('BEST CHOICE', style: TextStyle(fontSize: 12, color: Color(0xFFB6E28F), fontWeight: FontWeight.w800, letterSpacing: 1)),
              const SizedBox(height: 6),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      '서울 파머스 마켓',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            color: Colors.white,
                            fontSize: 30,
                          ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.network(
                      imageUrl,
                      width: 89,
                      height: 89,
                      fit: BoxFit.cover,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 1),
              Text(
                '₩${item.price}',
                style: const TextStyle(fontSize: 34, color: Colors.white, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: const Color(0xFF8FCC64),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Text('재고 풍부', style: TextStyle(fontSize: 11, color: Color(0xFF315A1A), fontWeight: FontWeight.w800)),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: const Color(0x669EDC8F),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.location_on, size: 14, color: Colors.white),
                        SizedBox(width: 4),
                        Text('2.4km', style: TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.w700)),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                height: 46,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: const Color(0xFF3D7B17),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
                  ),
                  onPressed: onAddRoute,
                  child: const Text('동선에 추가하기', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
