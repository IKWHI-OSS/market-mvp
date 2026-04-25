import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/error_state.dart';
import '../../shared/widgets/market_logo_title.dart';
import '../home/spotlight_screen.dart';

class ProductDetailArgs {
  const ProductDetailArgs({required this.productId});

  final String productId;
}

class ProductDetailScreen extends StatefulWidget {
  const ProductDetailScreen({super.key, required this.args});

  final ProductDetailArgs args;

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  late Future<ProductDetailData> _future;

  @override
  void initState() {
    super.initState();
    _future = ApiClient.instance.getProductDetail(widget.args.productId);
  }

  String _imageForProduct(String productId) {
    switch (productId) {
      case 'product_001':
        return 'https://images.unsplash.com/photo-1498579809087-ef1e558fd1da?auto=format&fit=crop&w=1200&q=80';
      case 'product_002':
        return 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1200&q=80';
      default:
        return 'https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1200&q=80';
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'in_stock':
        return '재고 풍부';
      case 'low_stock':
        return '재고 적음';
      case 'out_of_stock':
        return '품절';
      default:
        return '확인 필요';
    }
  }

  String _priceText(int price) => '₩${price.toString()}';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5EB),
      body: FutureBuilder<ProductDetailData>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || snapshot.data == null) {
            return ErrorStateWidget(
              title: '상세 정보를 가져오지 못했어요',
              description: '잠시 후 다시 시도해주세요.',
              onRetry: () {
                setState(() {
                  _future = ApiClient.instance.getProductDetail(widget.args.productId);
                });
              },
              onSecondary: () => Navigator.pop(context),
              secondaryLabel: '인근 시장 안내',
            );
          }

          final detail = snapshot.data!;
          final isSoldOut = detail.stockStatus == 'out_of_stock';
          final hasZone = detail.zoneLabel.trim().isNotEmpty;

          return Column(
            children: [
              Expanded(
                child: ListView(
                  padding: EdgeInsets.zero,
                  children: [
                    SafeArea(
                      bottom: false,
                      child: Padding(
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
                              child: const Icon(Icons.arrow_back, color: Color(0xFF4A7B29)),
                            ),
                            const SizedBox(width: 8),
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
                      ),
                    ),
                    Stack(
                      clipBehavior: Clip.none,
                      children: [
                        Image.network(
                          _imageForProduct(detail.productId),
                          width: double.infinity,
                          height: 320,
                          fit: BoxFit.cover,
                        ),
                        Positioned(
                          left: 14,
                          right: 14,
                          bottom: -78,
                          child: Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF7F2ED),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    const Text(
                                      '프리미엄 농산물',
                                      style: TextStyle(fontSize: 11, color: Color(0xFFCA8854), fontWeight: FontWeight.w700),
                                    ),
                                    const Spacer(),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFE9EDE2),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Text(
                                        _statusLabel(detail.stockStatus),
                                        style: const TextStyle(fontSize: 11, color: Color(0xFF5D6855), fontWeight: FontWeight.w700),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  detail.productName,
                                  style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                                        color: const Color(0xFF222222),
                                        height: 1.02,
                                      ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  _priceText(detail.price),
                                  style: const TextStyle(fontSize: 37, fontWeight: FontWeight.w900, color: Color(0xFF3D7B1D)),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 92),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'MARKET MERCHANT',
                            style: TextStyle(fontSize: 11, color: Color(0xFF8C9587), fontWeight: FontWeight.w700, letterSpacing: 0.8),
                          ),
                          const SizedBox(height: 8),
                          Material(
                            color: const Color(0xFFE8EEE1),
                            borderRadius: BorderRadius.circular(16),
                            child: InkWell(
                              borderRadius: BorderRadius.circular(16),
                              onTap: () => Navigator.push(
                                context,
                                MaterialPageRoute(builder: (_) => SpotlightScreen(storeId: detail.storeId)),
                              ),
                              child: Container(
                                padding: const EdgeInsets.all(14),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        ClipOval(
                                          child: Image.network(
                                            'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=160&q=80',
                                            width: 46,
                                            height: 46,
                                            fit: BoxFit.cover,
                                          ),
                                        ),
                                        const SizedBox(width: 10),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(detail.storeName, style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: Color(0xFF2A3229))),
                                              const SizedBox(height: 2),
                                              Text(
                                                hasZone ? '중곡동도깨비시장 ${detail.zoneLabel}' : '중곡동도깨비시장 구역 정보 미확인',
                                                style: const TextStyle(fontSize: 12, color: Color(0xFF4E7E31), fontWeight: FontWeight.w700),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 10),
                                    Text(
                                      '"${detail.description}"',
                                      style: const TextStyle(fontSize: 12, color: Color(0xFF505A4D), height: 1.45),
                                    ),
                                    const SizedBox(height: 10),
                                    const Row(
                                      children: [
                                        Icon(Icons.access_time, size: 14, color: Color(0xFF6D7667)),
                                        SizedBox(width: 4),
                                        Text('영업시간', style: TextStyle(fontSize: 11, color: Color(0xFF6D7667))),
                                        SizedBox(width: 12),
                                        Text('09:00 - 20:00', style: TextStyle(fontSize: 11, color: Color(0xFF3F473D), fontWeight: FontWeight.w700)),
                                        Spacer(),
                                        Text('#당일 알림', style: TextStyle(fontSize: 11, color: Color(0xFFC16F52), fontWeight: FontWeight.w700)),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          if (isSoldOut) ...[
                            const SizedBox(height: 10),
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF1F2EE),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Text(
                                '품절 상태입니다. 대체 점포를 검색해보세요.',
                                style: TextStyle(fontSize: 12, color: Color(0xFF687066)),
                              ),
                            ),
                          ],
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              const Text(
                                'SHOP LOCATION',
                                style: TextStyle(fontSize: 11, color: Color(0xFF8C9587), fontWeight: FontWeight.w700, letterSpacing: 0.8),
                              ),
                              const Spacer(),
                              TextButton(
                                onPressed: () => Navigator.pushNamed(context, AppRoutes.route),
                                child: const Text('위치 자세히 보기'),
                              ),
                            ],
                          ),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.network(
                              'https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&w=1200&q=80',
                              width: double.infinity,
                              height: 188,
                              fit: BoxFit.cover,
                            ),
                          ),
                          const SizedBox(height: 8),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(14, 8, 14, 14),
                child: Row(
                  children: [
                    Expanded(
                      child: FilledButton.tonal(
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.drop),
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFFF7C2A8),
                          foregroundColor: const Color(0xFF8A3E1F),
                          minimumSize: const Size.fromHeight(46),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        child: const Text('드랍 알림 설정'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: FilledButton(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: const Text('장보기 동선에 추가되었습니다.'),
                              action: SnackBarAction(
                                label: '동선 보기',
                                onPressed: () => Navigator.pushNamed(context, AppRoutes.route),
                              ),
                            ),
                          );
                        },
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF3D7A1A),
                          minimumSize: const Size.fromHeight(46),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        child: const Text('장보기 동선에 추가'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
