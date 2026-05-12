import '../network/api_client.dart';

class MarketRepository {
  MarketRepository({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient.instance;

  final ApiClient _apiClient;

  AuthUser? get currentUser => _apiClient.currentUser;

  Future<AuthSession> login({required String email, required String password}) {
    return _apiClient.login(email: email, password: password);
  }

  void logout() => _apiClient.logout();

  Future<List<ProductSummary>> searchProducts({required String query}) {
    return _apiClient.searchProducts(query: query);
  }

  Future<ProductDetailData> getProductDetail(String productId) {
    return _apiClient.getProductDetail(productId);
  }

  Future<List<DropData>> getDrops() => _apiClient.getDrops();

  Future<void> setDropSubscription({required String dropId, required bool subscribe}) {
    return _apiClient.setDropSubscription(dropId: dropId, subscribe: subscribe);
  }

  Future<List<NotificationData>> getNotifications() => _apiClient.getNotifications();

  Future<void> markNotificationRead(String notificationId) {
    return _apiClient.markNotificationRead(notificationId);
  }

  Future<List<EventSummary>> getEvents() => _apiClient.getEvents();

  Future<EventDetailData> getEventDetail(String eventId) {
    return _apiClient.getEventDetail(eventId);
  }

  Future<List<SpotlightSummary>> getSpotlights() => _apiClient.getSpotlights();

  Future<SpotlightDetailData> getSpotlightDetail(String storeId) {
    return _apiClient.getSpotlightDetail(storeId);
  }

  Future<MerchantStoryData> createMerchantStory({
    String? storeId,
    required String interviewText,
    required List<String> keywords,
    required String tone,
    required String selectedLength,
    bool saveToStore = false,
  }) {
    return _apiClient.createMerchantStory(
      storeId: storeId,
      interviewText: interviewText,
      keywords: keywords,
      tone: tone,
      selectedLength: selectedLength,
      saveToStore: saveToStore,
    );
  }

  Future<List<Map<String, dynamic>>> listMyStories() => _apiClient.listMyStories();

  Future<Map<String, dynamic>> getStory(String storyId) => _apiClient.getStory(storyId);

  Future<Map<String, dynamic>> publishStory(String storyId, {required bool publish}) {
    return _apiClient.publishStory(storyId, publish: publish);
  }

  Future<void> deleteStory(String storyId) => _apiClient.deleteStory(storyId);

  Future<Map<String, dynamic>?> getPublishedStoryForStore(String storeId) {
    return _apiClient.getPublishedStoryForStore(storeId);
  }

  Future<List<Map<String, dynamic>>> getProductPriceHistory(String productId) {
    return _apiClient.getProductPriceHistory(productId);
  }

  Future<ShoppingAgentData> requestShoppingAgent({
    required String query,
    int? people,
    int? budget,
    List<String>? preferences,
    String? marketId,
    bool saveAsList = true,
  }) {
    return _apiClient.requestShoppingAgent(
      query: query,
      people: people,
      budget: budget,
      preferences: preferences,
      marketId: marketId,
      saveAsList: saveAsList,
    );
  }
}
