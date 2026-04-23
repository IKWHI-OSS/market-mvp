import 'dart:convert';
import 'package:http/http.dart' as http;

const _baseUrl = 'https://market-api-production-6e52.up.railway.app/api/v1';
const _defaultMarketId = 'f1a2b3c4-d5e6-4789-a012-b3c4d5e6f701';

// ─── Data models ────────────────────────────────────────────────────────────

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

class MerchantStoryData {
  const MerchantStoryData({
    required this.storeId,
    required this.storeName,
    required this.story,
    required this.storyVersions,
    required this.selectedLength,
    required this.tone,
    required this.hashtags,
    required this.interviewMasked,
    required this.fallbackMode,
    required this.productsUsed,
  });

  final String storeId;
  final String storeName;
  final String story;
  final Map<String, String> storyVersions;
  final String selectedLength;
  final String tone;
  final List<String> hashtags;
  final String interviewMasked;
  final bool fallbackMode;
  final List<String> productsUsed;
}

class ShoppingAgentIngredient {
  const ShoppingAgentIngredient({
    required this.name,
    required this.qty,
    required this.unit,
    required this.matchStatus,
    required this.alternatives,
    this.storeName,
    this.zoneLabel,
    this.price,
  });

  final String name;
  final int qty;
  final String unit;
  final String matchStatus;
  final List<String> alternatives;
  final String? storeName;
  final String? zoneLabel;
  final int? price;
}

class ShoppingAgentStoreMatch {
  const ShoppingAgentStoreMatch({
    required this.storeId,
    required this.storeName,
    required this.zoneLabel,
    required this.distanceM,
    required this.priceTotal,
    required this.stockPriority,
    required this.matchedItems,
  });

  final String storeId;
  final String storeName;
  final String zoneLabel;
  final int distanceM;
  final int priceTotal;
  final String stockPriority;
  final List<String> matchedItems;
}

class ShoppingAgentData {
  const ShoppingAgentData({
    required this.query,
    required this.clarificationNeeded,
    required this.clarificationQuestion,
    required this.menuTitle,
    required this.menuReason,
    required this.ragSource,
    required this.ingredients,
    required this.storeMatches,
    required this.matchingFailed,
    required this.generalListOnly,
    required this.shoppingListId,
    required this.fallbackMode,
    required this.retryGuide,
  });

  final String query;
  final bool clarificationNeeded;
  final String? clarificationQuestion;
  final String? menuTitle;
  final String? menuReason;
  final String? ragSource;
  final List<ShoppingAgentIngredient> ingredients;
  final List<ShoppingAgentStoreMatch> storeMatches;
  final bool matchingFailed;
  final bool generalListOnly;
  final String? shoppingListId;
  final bool fallbackMode;
  final String? retryGuide;
}

// ─── ApiClient ──────────────────────────────────────────────────────────────

class ApiClient {
  ApiClient._();

  static final ApiClient instance = ApiClient._();

  String? _accessToken;

  String? get accessToken => _accessToken;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_accessToken != null) 'Authorization': 'Bearer $_accessToken',
      };

  // Unwrap {"success": true, "data": {...}} → data map. Throws on error.
  Map<String, dynamic> _unwrap(http.Response res) {
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (body['success'] == true) {
      return (body['data'] as Map<String, dynamic>?) ?? {};
    }
    throw Exception(body['message'] as String? ?? '서버 오류가 발생했습니다.');
  }

  // Unwrap paginated {"data": {"items": [...], ...}} → items list.
  List<dynamic> _unwrapItems(http.Response res) {
    final data = _unwrap(res);
    return data['items'] as List<dynamic>? ?? [];
  }

  // ── Auth ──────────────────────────────────────────────────────────────────

  Future<AuthSession> login({required String email, required String password}) async {
    final res = await http.post(
      Uri.parse('$_baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email.trim(), 'password': password}),
    );
    final data = _unwrap(res);
    final u = data['user'] as Map<String, dynamic>;
    _accessToken = data['access_token'] as String;
    return AuthSession(
      accessToken: _accessToken!,
      user: AuthUser(
        userId: u['user_id'] as String,
        email: u['email'] as String,
        name: u['name'] as String,
        role: u['role'] as String,
      ),
      homeScreenId: data['home_screen_id'] as String,
    );
  }

  void logout() => _accessToken = null;
  void clearSession() => _accessToken = null;

  // ── Profile ───────────────────────────────────────────────────────────────

  Future<AuthUser> getMyProfile() async {
    final res = await http.get(Uri.parse('$_baseUrl/auth/me'), headers: _headers);
    final d = _unwrap(res);
    return AuthUser(
      userId: d['user_id'] as String,
      email: d['email'] as String,
      name: d['name'] as String,
      role: d['role'] as String,
    );
  }

  // ── Products ──────────────────────────────────────────────────────────────

  Future<List<ProductSummary>> searchProducts({required String query}) async {
    final q = query.trim();
    if (q.isEmpty) return const [];
    final uri = Uri.parse('$_baseUrl/products/search').replace(
      queryParameters: {'q': q, 'market_id': _defaultMarketId},
    );
    final res = await http.get(uri, headers: _headers);
    return _unwrapItems(res).map((e) {
      final m = e as Map<String, dynamic>;
      return ProductSummary(
        productId: m['product_id'] as String,
        productName: m['product_name'] as String,
        storeId: m['store_id'] as String,
        storeName: m['store_name'] as String,
        zoneLabel: m['zone_label'] as String,
        price: m['price'] as int,
        stockStatus: m['stock_status'] as String,
      );
    }).toList();
  }

  Future<ProductDetailData> getProductDetail(String productId) async {
    final res = await http.get(
      Uri.parse('$_baseUrl/products/$productId'),
      headers: _headers,
    );
    final d = _unwrap(res);
    final store = d['store'] as Map<String, dynamic>? ?? {};
    return ProductDetailData(
      productId: d['product_id'] as String,
      productName: d['product_name'] as String,
      storeId: store['store_id'] as String? ?? '',
      storeName: store['store_name'] as String? ?? '',
      zoneLabel: store['zone_label'] as String? ?? '',
      price: d['price'] as int,
      stockStatus: d['stock_status'] as String,
      description: d['quality_note'] as String? ?? '',
    );
  }

  // ── Drops ─────────────────────────────────────────────────────────────────

  Future<List<DropData>> getDrops() async {
    final uri = Uri.parse('$_baseUrl/drops').replace(
      queryParameters: {'market_id': _defaultMarketId},
    );
    final res = await http.get(uri, headers: _headers);
    return _unwrapItems(res).map((e) {
      final m = e as Map<String, dynamic>;
      return DropData(
        dropId: m['drop_id'] as String,
        productId: m['product_id'] as String,
        productName: m['product_name'] as String,
        storeId: m['store_id'] as String,
        storeName: m['store_name'] as String,
        expectedAt: m['expected_at'] as String,
        status: m['status'] as String,
        isSubscribed: m['is_subscribed'] as bool? ?? false,
        estimatedPrice: 0,
      );
    }).toList();
  }

  Future<void> setDropSubscription({required String dropId, required bool subscribe}) async {
    final uri = Uri.parse('$_baseUrl/drops/$dropId/subscribe');
    final res = subscribe
        ? await http.post(uri, headers: _headers)
        : await http.delete(uri, headers: _headers);
    if (res.statusCode < 200 || res.statusCode >= 300) {
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      throw Exception(body['message'] as String? ?? '구독 처리에 실패했습니다.');
    }
  }

  // ── Notifications ─────────────────────────────────────────────────────────

  Future<List<NotificationData>> getNotifications() async {
    final res = await http.get(
      Uri.parse('$_baseUrl/notifications'),
      headers: _headers,
    );
    return _unwrapItems(res).map((e) {
      final m = e as Map<String, dynamic>;
      return NotificationData(
        notificationId: m['notification_id'] as String,
        title: m['title'] as String,
        body: m['body'] as String? ?? '',
        type: m['type'] as String,
        targetType: m['target_type'] as String? ?? '',
        targetId: m['target_id'] as String? ?? '',
        isRead: m['is_read'] as bool,
        createdAt: m['created_at'] as String,
      );
    }).toList();
  }

  Future<void> markNotificationRead(String notificationId) async {
    final res = await http.patch(
      Uri.parse('$_baseUrl/notifications/$notificationId/read'),
      headers: _headers,
    );
    if (res.statusCode < 200 || res.statusCode >= 300) {
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      throw Exception(body['message'] as String? ?? '알림 읽음 처리에 실패했습니다.');
    }
  }

  // ── Events (event_cards from /home) ───────────────────────────────────────

  Future<List<EventSummary>> getEvents() async {
    final res = await http.get(Uri.parse('$_baseUrl/home'), headers: _headers);
    final data = _unwrap(res);
    final cards = data['event_cards'] as List<dynamic>? ?? [];
    return cards.map((e) {
      final m = e as Map<String, dynamic>;
      return EventSummary(
        eventId: m['catalog_item_id'] as String,
        title: m['title'] as String,
        imageUrl: m['image_url'] as String? ?? '',
        periodText: '',
        zoneLabel: '',
      );
    }).toList();
  }

  Future<EventDetailData> getEventDetail(String eventId) async {
    final res = await http.get(
      Uri.parse('$_baseUrl/events/$eventId'),
      headers: _headers,
    );
    final d = _unwrap(res);
    return EventDetailData(
      eventId: d['catalog_item_id'] as String,
      title: d['title'] as String,
      description: d['description'] as String? ?? '',
      periodText: _formatPeriod(
        d['valid_from'] as String?,
        d['valid_until'] as String?,
      ),
      zoneLabel: d['zone_label'] as String? ?? '',
      relatedStoreId: d['store_id'] as String? ?? '',
    );
  }

  // ── Spotlights (store_spotlights from /home) ───────────────────────────────

  Future<List<SpotlightSummary>> getSpotlights() async {
    final res = await http.get(Uri.parse('$_baseUrl/home'), headers: _headers);
    final data = _unwrap(res);
    final spots = data['store_spotlights'] as List<dynamic>? ?? [];
    return spots.map((e) {
      final m = e as Map<String, dynamic>;
      return SpotlightSummary(
        storeId: m['store_id'] as String,
        storeName: m['store_name'] as String,
        summary: m['summary'] as String? ?? '',
        imageUrl: m['image_url'] as String? ?? '',
      );
    }).toList();
  }

  Future<SpotlightDetailData> getSpotlightDetail(String storeId) async {
    final res = await http.get(
      Uri.parse('$_baseUrl/stores/$storeId/spotlight'),
      headers: _headers,
    );
    final d = _unwrap(res);
    final products = d['products'] as List<dynamic>? ?? [];
    final highlight = products.isNotEmpty
        ? (products.first as Map<String, dynamic>)['product_name'] as String? ?? ''
        : '';
    return SpotlightDetailData(
      storeId: d['store_id'] as String,
      storeName: d['store_name'] as String,
      summary: d['summary'] as String? ?? '',
      zoneLabel: d['zone_label'] as String? ?? '',
      openHours: '',
      highlightProduct: highlight,
    );
  }

  // ── Preorders ─────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> createPreorder({
    required String storeId,
    required String productName,
    required int qty,
  }) async {
    final res = await http.post(
      Uri.parse('$_baseUrl/preorders'),
      headers: _headers,
      body: jsonEncode({'store_id': storeId, 'product_name': productName, 'qty': qty}),
    );
    return _unwrap(res);
  }

  Future<List<Map<String, dynamic>>> getMyPreorders({String? status}) async {
    final uri = Uri.parse('$_baseUrl/preorders').replace(
      queryParameters: {if (status != null) 'status': status},
    );
    final res = await http.get(uri, headers: _headers);
    return _unwrapItems(res).map((e) => e as Map<String, dynamic>).toList();
  }

  Future<void> cancelPreorder(String preorderId) async {
    final res = await http.delete(
      Uri.parse('$_baseUrl/preorders/$preorderId'),
      headers: _headers,
    );
    if (res.statusCode < 200 || res.statusCode >= 300) {
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      throw Exception(body['message'] as String? ?? '취소에 실패했습니다.');
    }
  }

  // ── Price Suggestions (merchant) ──────────────────────────────────────────

  Future<List<Map<String, dynamic>>> getPriceSuggestions() async {
    final res = await http.get(
      Uri.parse('$_baseUrl/merchant/dashboard/price-suggestions'),
      headers: _headers,
    );
    final d = _unwrap(res);
    return (d['suggestions'] as List<dynamic>? ?? [])
        .map((e) => e as Map<String, dynamic>)
        .toList();
  }

  // ── Merchant Story Agent ─────────────────────────────────────────────────

  Future<MerchantStoryData> createMerchantStory({
    String? storeId,
    required String interviewText,
    required List<String> keywords,
    required String tone,
    required String selectedLength,
    bool saveToStore = false,
  }) async {
    final res = await http.post(
      Uri.parse('$_baseUrl/merchant/stories'),
      headers: _headers,
      body: jsonEncode({
        if (storeId != null && storeId.isNotEmpty) 'store_id': storeId,
        'interview_text': interviewText,
        'keywords': keywords,
        'tone': tone,
        'selected_length': selectedLength,
        'save_to_store': saveToStore,
      }),
    );
    final d = _unwrap(res);
    final versionsRaw = d['story_versions'] as Map<String, dynamic>? ?? {};
    return MerchantStoryData(
      storeId: d['store_id'] as String,
      storeName: d['store_name'] as String? ?? '',
      story: d['story'] as String? ?? '',
      storyVersions: {
        'short': versionsRaw['short'] as String? ?? '',
        'normal': versionsRaw['normal'] as String? ?? '',
        'detailed': versionsRaw['detailed'] as String? ?? '',
      },
      selectedLength: d['selected_length'] as String? ?? 'normal',
      tone: d['tone'] as String? ?? tone,
      hashtags: (d['hashtags'] as List<dynamic>? ?? const []).map((e) => '$e').toList(growable: false),
      interviewMasked: d['interview_masked'] as String? ?? '',
      fallbackMode: d['fallback_mode'] as bool? ?? false,
      productsUsed: (d['products_used'] as List<dynamic>? ?? const []).map((e) => '$e').toList(growable: false),
    );
  }

  // ── Shopping Agent (SCR-C-05) ────────────────────────────────────────────

  Future<ShoppingAgentData> requestShoppingAgent({
    required String query,
    int? people,
    int? budget,
    List<String>? preferences,
    String? marketId,
    bool saveAsList = true,
  }) async {
    final res = await http.post(
      Uri.parse('$_baseUrl/shopping-agent/recommendations'),
      headers: _headers,
      body: jsonEncode({
        'query': query.trim(),
        if (people != null) 'people': people,
        if (budget != null) 'budget': budget,
        if (preferences != null) 'preferences': preferences,
        if (marketId != null && marketId.isNotEmpty) 'market_id': marketId,
        'save_as_list': saveAsList,
      }),
    );
    final d = _unwrap(res);
    final menu = d['menu'] as Map<String, dynamic>?;
    final ingredientsRaw = d['ingredients'] as List<dynamic>? ?? const [];
    final storesRaw = d['store_matches'] as List<dynamic>? ?? const [];

    return ShoppingAgentData(
      query: d['query'] as String? ?? query,
      clarificationNeeded: d['clarification_needed'] as bool? ?? false,
      clarificationQuestion: d['clarification_question'] as String?,
      menuTitle: menu?['title'] as String?,
      menuReason: menu?['reason'] as String?,
      ragSource: menu?['rag_source'] as String?,
      ingredients: ingredientsRaw.map((e) {
        final m = e as Map<String, dynamic>;
        final matchedStore = m['matched_store'] as Map<String, dynamic>?;
        return ShoppingAgentIngredient(
          name: m['name'] as String? ?? '',
          qty: m['qty'] as int? ?? 1,
          unit: m['unit'] as String? ?? '',
          matchStatus: m['match_status'] as String? ?? 'unmatched',
          alternatives: (m['alternatives'] as List<dynamic>? ?? const [])
              .map((x) => '$x')
              .toList(growable: false),
          storeName: matchedStore?['store_name'] as String?,
          zoneLabel: matchedStore?['zone_label'] as String?,
          price: matchedStore?['price'] as int?,
        );
      }).toList(growable: false),
      storeMatches: storesRaw.map((e) {
        final m = e as Map<String, dynamic>;
        return ShoppingAgentStoreMatch(
          storeId: m['store_id'] as String? ?? '',
          storeName: m['store_name'] as String? ?? '',
          zoneLabel: m['zone_label'] as String? ?? '',
          distanceM: m['distance_m'] as int? ?? 0,
          priceTotal: m['price_total'] as int? ?? 0,
          stockPriority: m['stock_priority'] as String? ?? 'in_stock',
          matchedItems: (m['matched_items'] as List<dynamic>? ?? const [])
              .map((x) => '$x')
              .toList(growable: false),
        );
      }).toList(growable: false),
      matchingFailed: d['matching_failed'] as bool? ?? false,
      generalListOnly: d['general_list_only'] as bool? ?? false,
      shoppingListId: d['shopping_list_id'] as String?,
      fallbackMode: d['fallback_mode'] as bool? ?? false,
      retryGuide: d['retry_guide'] as String?,
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  // "4/22 12:00 ~ 4/22 18:00" 형식. null이면 빈 문자열.
  String _formatPeriod(String? from, String? until) {
    if (from == null && until == null) return '';
    String fmt(String iso) {
      try {
        final d = DateTime.parse(iso).toLocal();
        final mm = d.month;
        final dd = d.day;
        final hh = d.hour.toString().padLeft(2, '0');
        final min = d.minute.toString().padLeft(2, '0');
        return '$mm/$dd $hh:$min';
      } catch (_) {
        return iso;
      }
    }

    if (from != null && until != null) return '${fmt(from)} ~ ${fmt(until)}';
    if (from != null) return '${fmt(from)} ~';
    return '~ ${fmt(until!)}';
  }
}
