import 'dart:async';

class AuthUser {
  const AuthUser({required this.userId, required this.email, required this.name, required this.role});

  final String userId;
  final String email;
  final String name;
  final String role;
}

class AuthSession {
  const AuthSession({required this.accessToken, required this.user, required this.homeScreenId});

  final String accessToken;
  final AuthUser user;
  final String homeScreenId;
}

class ProductSummary {
  const ProductSummary({
    required this.productId,
    required this.productName,
    required this.storeId,
    required this.storeName,
    required this.zoneLabel,
    required this.price,
    required this.stockStatus,
  });

  final String productId;
  final String productName;
  final String storeId;
  final String storeName;
  final String zoneLabel;
  final int price;
  final String stockStatus;
}

class ProductDetailData {
  const ProductDetailData({
    required this.productId,
    required this.productName,
    required this.storeId,
    required this.storeName,
    required this.zoneLabel,
    required this.price,
    required this.stockStatus,
    required this.description,
  });

  final String productId;
  final String productName;
  final String storeId;
  final String storeName;
  final String zoneLabel;
  final int price;
  final String stockStatus;
  final String description;
}

class DropData {
  const DropData({
    required this.dropId,
    required this.productId,
    required this.productName,
    required this.storeId,
    required this.storeName,
    required this.expectedAt,
    required this.status,
    required this.isSubscribed,
    required this.estimatedPrice,
  });

  final String dropId;
  final String productId;
  final String productName;
  final String storeId;
  final String storeName;
  final String expectedAt;
  final String status;
  final bool isSubscribed;
  final int estimatedPrice;
}

class NotificationData {
  const NotificationData({
    required this.notificationId,
    required this.title,
    required this.body,
    required this.type,
    required this.targetType,
    required this.targetId,
    required this.isRead,
    required this.createdAt,
  });

  final String notificationId;
  final String title;
  final String body;
  final String type;
  final String targetType;
  final String targetId;
  final bool isRead;
  final String createdAt;
}

class EventSummary {
  const EventSummary({
    required this.eventId,
    required this.title,
    required this.imageUrl,
    required this.periodText,
    required this.zoneLabel,
  });

  final String eventId;
  final String title;
  final String imageUrl;
  final String periodText;
  final String zoneLabel;
}

class EventDetailData {
  const EventDetailData({
    required this.eventId,
    required this.title,
    required this.description,
    required this.periodText,
    required this.zoneLabel,
    required this.relatedStoreId,
  });

  final String eventId;
  final String title;
  final String description;
  final String periodText;
  final String zoneLabel;
  final String relatedStoreId;
}

class SpotlightSummary {
  const SpotlightSummary({
    required this.storeId,
    required this.storeName,
    required this.summary,
    required this.imageUrl,
  });

  final String storeId;
  final String storeName;
  final String summary;
  final String imageUrl;
}

class SpotlightDetailData {
  const SpotlightDetailData({
    required this.storeId,
    required this.storeName,
    required this.summary,
    required this.zoneLabel,
    required this.openHours,
    required this.highlightProduct,
  });

  final String storeId;
  final String storeName;
  final String summary;
  final String zoneLabel;
  final String openHours;
  final String highlightProduct;
}

class ApiClient {
  ApiClient._();

  static final ApiClient instance = ApiClient._();

  String? _accessToken;
  final Set<String> _subscribedDropIds = {'drop_002'};
  final Set<String> _readNotificationIds = <String>{};

  String? get accessToken => _accessToken;

  Future<AuthSession> login({required String email, required String password}) async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    if (email.isEmpty || password.isEmpty) {
      throw Exception('이메일/비밀번호를 입력해주세요.');
    }

    const registeredAccounts = <String, ({String password, String role, String userId, String name})>{
      'consumer@example.com': (
        password: 'password123',
        role: 'consumer',
        userId: 'user_consumer_001',
        name: '일반 사용자',
      ),
      'merchant@example.com': (
        password: 'password123',
        role: 'merchant',
        userId: 'user_merchant_001',
        name: '상인 사용자',
      ),
    };
    final normalizedEmail = email.trim().toLowerCase();
    final account = registeredAccounts[normalizedEmail];
    if (account == null || account.password != password) {
      throw Exception('아이디 또는 비밀번호를 확인해주세요.');
    }

    final user = AuthUser(
      userId: account.userId,
      email: normalizedEmail,
      name: account.name,
      role: account.role,
    );
    final session = AuthSession(
      accessToken: 'mock-jwt-token',
      user: user,
      homeScreenId: account.role == 'merchant' ? 'SCR-M-01' : 'SCR-C-01',
    );
    _accessToken = session.accessToken;
    return session;
  }

  void logout() {
    _accessToken = null;
  }

  Future<List<ProductSummary>> searchProducts({required String query}) async {
    await Future<void>.delayed(const Duration(milliseconds: 350));
    final keyword = query.trim().toLowerCase();
    if (keyword.isEmpty) {
      return const [];
    }
    return _productSeed
        .where((item) => item.productName.toLowerCase().contains(keyword))
        .toList(growable: false);
  }

  Future<ProductDetailData> getProductDetail(String productId) async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    return _productDetailSeed.firstWhere(
      (item) => item.productId == productId,
      orElse: () => throw Exception('상품 정보를 찾을 수 없습니다.'),
    );
  }

  Future<List<DropData>> getDrops() async {
    await Future<void>.delayed(const Duration(milliseconds: 350));
    return _dropSeed
        .map(
          (drop) => DropData(
            dropId: drop.dropId,
            productId: drop.productId,
            productName: drop.productName,
            storeId: drop.storeId,
            storeName: drop.storeName,
            expectedAt: drop.expectedAt,
            status: drop.status,
            isSubscribed: _subscribedDropIds.contains(drop.dropId),
            estimatedPrice: drop.estimatedPrice,
          ),
        )
        .toList(growable: false);
  }

  Future<void> setDropSubscription({required String dropId, required bool subscribe}) async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    if (subscribe) {
      _subscribedDropIds.add(dropId);
      return;
    }
    _subscribedDropIds.remove(dropId);
  }

  Future<List<NotificationData>> getNotifications() async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    return _notificationSeed
        .map(
          (item) => NotificationData(
            notificationId: item.notificationId,
            title: item.title,
            body: item.body,
            type: item.type,
            targetType: item.targetType,
            targetId: item.targetId,
            isRead: _readNotificationIds.contains(item.notificationId),
            createdAt: item.createdAt,
          ),
        )
        .toList(growable: false);
  }

  Future<void> markNotificationRead(String notificationId) async {
    await Future<void>.delayed(const Duration(milliseconds: 180));
    _readNotificationIds.add(notificationId);
  }

  Future<List<EventSummary>> getEvents() async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    return _eventSeed;
  }

  Future<EventDetailData> getEventDetail(String eventId) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return _eventDetailSeed.firstWhere(
      (item) => item.eventId == eventId,
      orElse: () => throw Exception('행사 정보를 찾을 수 없습니다.'),
    );
  }

  Future<List<SpotlightSummary>> getSpotlights() async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    return _spotlightSeed;
  }

  Future<SpotlightDetailData> getSpotlightDetail(String storeId) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return _spotlightDetailSeed.firstWhere(
      (item) => item.storeId == storeId,
      orElse: () => throw Exception('점포 스포트라이트 정보를 찾을 수 없습니다.'),
    );
  }
}

const List<ProductSummary> _productSeed = [
  ProductSummary(
    productId: 'product_001',
    productName: '유기농 토종 당근',
    storeId: 'store_001',
    storeName: '망원 채소마트',
    zoneLabel: 'A-1구역',
    price: 4200,
    stockStatus: 'in_stock',
  ),
  ProductSummary(
    productId: 'product_002',
    productName: '하동 단감',
    storeId: 'store_002',
    storeName: '망원 과일나라',
    zoneLabel: 'B-2구역',
    price: 5600,
    stockStatus: 'low_stock',
  ),
];

const List<ProductDetailData> _productDetailSeed = [
  ProductDetailData(
    productId: 'product_001',
    productName: '유기농 토종 당근',
    storeId: 'store_001',
    storeName: '망원 채소마트',
    zoneLabel: 'A-1구역',
    price: 4200,
    stockStatus: 'in_stock',
    description: '아침 입고 기준으로 신선도 상급. 볶음/샐러드 모두 적합.',
  ),
  ProductDetailData(
    productId: 'product_002',
    productName: '하동 단감',
    storeId: 'store_002',
    storeName: '망원 과일나라',
    zoneLabel: 'B-2구역',
    price: 5600,
    stockStatus: 'low_stock',
    description: '제철 산지 직송 상품. 오전 타임 재고 소진이 빠른 편.',
  ),
];

const List<DropData> _dropSeed = [
  DropData(
    dropId: 'drop_001',
    productId: 'product_002',
    productName: '하동 단감',
    storeId: 'store_002',
    storeName: '망원 과일나라',
    expectedAt: '오늘 08:00',
    status: 'scheduled',
    isSubscribed: false,
    estimatedPrice: 5600,
  ),
  DropData(
    dropId: 'drop_002',
    productId: 'product_003',
    productName: '프리미엄 생연어',
    storeId: 'store_005',
    storeName: '제주 씨푸드',
    expectedAt: '오늘 10:30',
    status: 'arrived',
    isSubscribed: true,
    estimatedPrice: 18900,
  ),
];

const List<NotificationData> _notificationSeed = [
  NotificationData(
    notificationId: 'noti_001',
    title: '단감 드랍이 도착했어요',
    body: '망원 과일나라에서 드랍 상태가 도착으로 변경되었습니다.',
    type: 'drop',
    targetType: 'drop',
    targetId: 'drop_001',
    isRead: false,
    createdAt: '방금 전',
  ),
  NotificationData(
    notificationId: 'noti_002',
    title: '오늘의 시장 행사 시작',
    body: '전통시장 이벤트가 시작되었어요. 행사 상세를 확인해보세요.',
    type: 'event',
    targetType: 'event',
    targetId: 'event_001',
    isRead: false,
    createdAt: '10분 전',
  ),
];

const List<EventSummary> _eventSeed = [
  EventSummary(
    eventId: 'event_001',
    title: '전통시장 봄 이벤트',
    imageUrl: 'https://example.com/event_001.jpg',
    periodText: '오늘 12:00~18:00',
    zoneLabel: '중앙광장',
  ),
  EventSummary(
    eventId: 'event_002',
    title: '수산 특가 라이브',
    imageUrl: 'https://example.com/event_002.jpg',
    periodText: '오늘 15:00~17:00',
    zoneLabel: '수산동 B-4',
  ),
];

const List<EventDetailData> _eventDetailSeed = [
  EventDetailData(
    eventId: 'event_001',
    title: '전통시장 봄 이벤트',
    description: '현장 참여형 경품 이벤트와 시즌 특가를 함께 운영합니다.',
    periodText: '오늘 12:00~18:00',
    zoneLabel: '중앙광장',
    relatedStoreId: 'store_003',
  ),
  EventDetailData(
    eventId: 'event_002',
    title: '수산 특가 라이브',
    description: '선어 특가 상품 실시간 공개와 즉시 구매 링크를 제공합니다.',
    periodText: '오늘 15:00~17:00',
    zoneLabel: '수산동 B-4',
    relatedStoreId: 'store_005',
  ),
];

const List<SpotlightSummary> _spotlightSeed = [
  SpotlightSummary(
    storeId: 'store_003',
    storeName: '청정 채소 달라상회',
    summary: '당일 입고 채소 큐레이션',
    imageUrl: 'https://example.com/store_003.jpg',
  ),
  SpotlightSummary(
    storeId: 'store_004',
    storeName: '골목 과일공방',
    summary: '제철 과일 소분 패키지',
    imageUrl: 'https://example.com/store_004.jpg',
  ),
];

const List<SpotlightDetailData> _spotlightDetailSeed = [
  SpotlightDetailData(
    storeId: 'store_003',
    storeName: '청정 채소 달라상회',
    summary: '당일 입고 채소 큐레이션',
    zoneLabel: '채소동 A-3',
    openHours: '07:30~19:00',
    highlightProduct: '친환경 시금치',
  ),
  SpotlightDetailData(
    storeId: 'store_004',
    storeName: '골목 과일공방',
    summary: '제철 과일 소분 패키지',
    zoneLabel: '과일동 B-1',
    openHours: '08:00~20:00',
    highlightProduct: '하동 단감',
  ),
];
