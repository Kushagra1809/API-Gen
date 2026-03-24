"""
API Discovery Engine — the brain of the recommendation system.

Takes a developer's application idea → breaks it into features →
maps features to API categories → returns ranked recommendations.
"""
from sqlalchemy.orm import Session
from models import APIEntry, APICategory
from discovery.ranking import rank_apis


# ─── Feature-to-Category Mapping ───────────────────────────
# Maps common features/keywords to API categories
FEATURE_CATEGORY_MAP = {
    # Maps & Location
    "map":           "maps_location",
    "maps":          "maps_location",
    "location":      "maps_location",
    "gps":           "maps_location",
    "directions":    "maps_location",
    "navigation":    "maps_location",
    "geocoding":     "maps_location",
    "address":       "maps_location",
    "places":        "maps_location",
    "routing":       "maps_location",

    # Weather
    "weather":       "weather",
    "forecast":      "weather",
    "temperature":   "weather",
    "climate":       "weather",

    # Payments
    "payment":       "payments",
    "payments":      "payments",
    "checkout":      "payments",
    "billing":       "payments",
    "subscription":  "payments",
    "invoice":       "payments",
    "money":         "payments",
    "transaction":   "payments",
    "stripe":        "payments",

    # Messaging
    "sms":           "messaging",
    "email":         "messaging",
    "chat":          "messaging",
    "messaging":     "messaging",
    "notification":  "messaging",
    "push":          "messaging",
    "whatsapp":      "messaging",

    # AI / ML
    "ai":            "ai_ml",
    "machine learning": "ai_ml",
    "ml":            "ai_ml",
    "nlp":           "ai_ml",
    "chatbot":       "ai_ml",
    "sentiment":     "ai_ml",
    "image recognition": "ai_ml",
    "ocr":           "ai_ml",
    "text generation": "ai_ml",
    "gpt":           "ai_ml",
    "llm":           "ai_ml",
    "prediction":    "ai_ml",
    "classification": "ai_ml",
    "vision":        "ai_ml",
    "deep learning": "ai_ml",

    # Flights & Travel
    "flight":        "flights_travel",
    "flights":       "flights_travel",
    "airline":       "flights_travel",
    "travel":        "flights_travel",
    "booking":       "flights_travel",
    "trip":          "flights_travel",
    "itinerary":     "flights_travel",
    "vacation":      "flights_travel",
    "tourism":       "flights_travel",

    # Hotels
    "hotel":         "hotels",
    "hotels":        "hotels",
    "accommodation": "hotels",
    "lodging":       "hotels",
    "resort":        "hotels",
    "hostel":        "hotels",
    "stay":          "hotels",

    # Currency
    "currency":      "currency_exchange",
    "exchange rate":  "currency_exchange",
    "forex":         "currency_exchange",
    "conversion":    "currency_exchange",

    # Translation
    "translate":     "translation",
    "translation":   "translation",
    "language":      "translation",
    "localization":  "translation",
    "multilingual":  "translation",

    # Auth
    "auth":          "authentication",
    "authentication":"authentication",
    "login":         "authentication",
    "signup":        "authentication",
    "oauth":         "authentication",
    "sso":           "authentication",
    "identity":      "authentication",
    "user management": "authentication",

    # Storage
    "storage":       "storage",
    "file upload":   "storage",
    "cloud storage": "storage",
    "cdn":           "storage",
    "image hosting": "storage",
    "media":         "storage",

    # Database
    "database":      "database",
    "backend":       "database",
    "realtime":      "database",
    "firebase":      "database",
    "supabase":      "database",

    # Search
    "search":        "search",
    "full-text":     "search",
    "elasticsearch": "search",

    # Social
    "social media":  "social_media",
    "twitter":       "social_media",
    "facebook":      "social_media",
    "instagram":     "social_media",
    "youtube":       "social_media",

    # E-Commerce
    "ecommerce":     "ecommerce",
    "e-commerce":    "ecommerce",
    "shopping":      "ecommerce",
    "product":       "ecommerce",
    "cart":          "ecommerce",
    "marketplace":   "ecommerce",
    "store":         "ecommerce",
    "shop":          "ecommerce",

    # Video
    "video":         "video_media",
    "streaming":     "video_media",
    "video editing": "video_media",
    "live stream":   "video_media",

    # Analytics
    "analytics":     "analytics",
    "monitoring":    "analytics",
    "error tracking":"analytics",
    "logging":       "analytics",

    # DevTools
    "ci/cd":         "devtools",
    "deployment":    "devtools",
    "github":        "devtools",
    "hosting":       "devtools",
}

# ─── Idea → Features Mapping ───────────────────────────────
# Common application types and their required feature categories
IDEA_TEMPLATES = {
    "travel": {
        "features": [
            {"feature": "Flight Search & Booking",  "category": "flights_travel", "icon": "✈️"},
            {"feature": "Hotel Reservations",        "category": "hotels",         "icon": "🏨"},
            {"feature": "Maps & Navigation",         "category": "maps_location",  "icon": "🗺️"},
            {"feature": "Weather Information",        "category": "weather",        "icon": "🌦️"},
            {"feature": "Currency Conversion",        "category": "currency_exchange","icon": "💱"},
            {"feature": "Language Translation",       "category": "translation",    "icon": "🌐"},
            {"feature": "Payment Processing",         "category": "payments",       "icon": "💳"},
            {"feature": "User Authentication",        "category": "authentication", "icon": "🔐"},
            {"feature": "Push Notifications",         "category": "messaging",      "icon": "💬"},
        ],
        "keywords": ["travel", "trip", "planner", "vacation", "tourism", "itinerary", "backpack"],
    },
    "ecommerce": {
        "features": [
            {"feature": "Product Catalog",           "category": "ecommerce",      "icon": "🛒"},
            {"feature": "Payment Processing",         "category": "payments",       "icon": "💳"},
            {"feature": "User Authentication",        "category": "authentication", "icon": "🔐"},
            {"feature": "Search & Discovery",         "category": "search",         "icon": "🔍"},
            {"feature": "Email Notifications",        "category": "messaging",      "icon": "💬"},
            {"feature": "Media Management",           "category": "storage",        "icon": "☁️"},
            {"feature": "Analytics & Monitoring",     "category": "analytics",      "icon": "📊"},
            {"feature": "Maps & Delivery Tracking",   "category": "maps_location",  "icon": "🗺️"},
        ],
        "keywords": ["ecommerce", "e-commerce", "shop", "store", "marketplace", "sell", "buy", "product"],
    },
    "social": {
        "features": [
            {"feature": "User Authentication",        "category": "authentication", "icon": "🔐"},
            {"feature": "Real-time Messaging",        "category": "messaging",      "icon": "💬"},
            {"feature": "Media Upload & Storage",     "category": "storage",        "icon": "☁️"},
            {"feature": "Social Media Integration",   "category": "social_media",   "icon": "📱"},
            {"feature": "Video Streaming",            "category": "video_media",    "icon": "🎬"},
            {"feature": "Search",                     "category": "search",         "icon": "🔍"},
            {"feature": "Push Notifications",         "category": "messaging",      "icon": "📲"},
            {"feature": "Analytics",                  "category": "analytics",      "icon": "📊"},
        ],
        "keywords": ["social", "community", "forum", "chat", "connect", "network", "friend"],
    },
    "ai_app": {
        "features": [
            {"feature": "AI / LLM Models",           "category": "ai_ml",          "icon": "🤖"},
            {"feature": "User Authentication",        "category": "authentication", "icon": "🔐"},
            {"feature": "File Storage",               "category": "storage",        "icon": "☁️"},
            {"feature": "Payment Processing",         "category": "payments",       "icon": "💳"},
            {"feature": "Analytics & Monitoring",     "category": "analytics",      "icon": "📊"},
            {"feature": "Database Backend",           "category": "database",       "icon": "🗄️"},
        ],
        "keywords": ["ai", "ml", "machine learning", "chatbot", "gpt", "llm", "intelligent", "smart",
                      "prediction", "recommendation", "automated", "deep learning", "neural"],
    },
    "video": {
        "features": [
            {"feature": "Video Streaming & Encoding", "category": "video_media",    "icon": "🎬"},
            {"feature": "Media Storage & CDN",        "category": "storage",        "icon": "☁️"},
            {"feature": "AI-Powered Video Analysis",  "category": "ai_ml",          "icon": "🤖"},
            {"feature": "User Authentication",        "category": "authentication", "icon": "🔐"},
            {"feature": "Payment / Subscription",     "category": "payments",       "icon": "💳"},
            {"feature": "Search",                     "category": "search",         "icon": "🔍"},
            {"feature": "Analytics",                  "category": "analytics",      "icon": "📊"},
            {"feature": "Social Sharing",             "category": "social_media",   "icon": "📱"},
        ],
        "keywords": ["video", "stream", "editor", "youtube", "player", "recording", "watch"],
    },
    "fintech": {
        "features": [
            {"feature": "Payment Processing",         "category": "payments",       "icon": "💳"},
            {"feature": "Currency Exchange Rates",     "category": "currency_exchange","icon": "💱"},
            {"feature": "User Authentication & KYC",   "category": "authentication", "icon": "🔐"},
            {"feature": "Database Backend",           "category": "database",       "icon": "🗄️"},
            {"feature": "SMS / Email Notifications",   "category": "messaging",      "icon": "💬"},
            {"feature": "Analytics & Monitoring",     "category": "analytics",      "icon": "📊"},
        ],
        "keywords": ["fintech", "banking", "finance", "money", "wallet", "budget", "invest", "trading", "crypto"],
    },
}


def _match_idea_template(idea: str) -> str | None:
    """Check if the idea matches any known template by keywords."""
    idea_lower = idea.lower()
    for template_name, template in IDEA_TEMPLATES.items():
        for kw in template["keywords"]:
            if kw in idea_lower:
                return template_name
    return None


def _extract_features_from_text(idea: str) -> list[dict]:
    """
    Extract features from free-text by keyword matching against FEATURE_CATEGORY_MAP.
    Returns deduplicated list of {feature, category, icon}.
    """
    idea_lower = idea.lower()
    seen_categories = set()
    features = []

    # Sort by length (longest first) to prefer "machine learning" over "machine"
    sorted_keys = sorted(FEATURE_CATEGORY_MAP.keys(), key=len, reverse=True)

    for keyword in sorted_keys:
        if keyword in idea_lower:
            cat = FEATURE_CATEGORY_MAP[keyword]
            if cat not in seen_categories:
                seen_categories.add(cat)
                # Find the category icon from the knowledge base
                from discovery.knowledge_base import CATEGORIES as KB_CATS
                icon = "🔗"
                display = cat.replace("_", " ").title()
                for c in KB_CATS:
                    if c["name"] == cat:
                        icon = c["icon"]
                        display = c["display_name"]
                        break
                features.append({
                    "feature": display,
                    "category": cat,
                    "icon": icon,
                })

    return features


def discover_apis(idea: str, db: Session) -> dict:
    """
    Main discovery function.
    1. Match idea against templates or extract features from text
    2. For each feature/category, fetch APIs from DB
    3. Rank and return results
    """
    # Step 1: Identify features
    template_name = _match_idea_template(idea)
    if template_name:
        features = IDEA_TEMPLATES[template_name]["features"]
    else:
        features = _extract_features_from_text(idea)

    # If still empty, provide generic suggestions
    if not features:
        features = [
            {"feature": "User Authentication",   "category": "authentication", "icon": "🔐"},
            {"feature": "Database Backend",       "category": "database",       "icon": "🗄️"},
            {"feature": "Analytics",              "category": "analytics",      "icon": "📊"},
        ]

    # Step 2: Fetch APIs for each category
    result_features = []
    total_apis = 0

    for feat in features:
        cat = db.query(APICategory).filter_by(name=feat["category"]).first()
        if not cat:
            continue

        apis = (
            db.query(APIEntry)
            .filter_by(category_id=cat.id, is_active=True)
            .order_by(APIEntry.composite_score.desc())
            .all()
        )

        api_list = []
        for api in apis:
            api_list.append({
                "name": api.name,
                "provider": api.provider,
                "category": cat.display_name,
                "description": api.description,
                "free_tier": api.free_tier,
                "pricing_model": api.pricing_model,
                "pricing_details": api.pricing_details,
                "auth_type": api.auth_type,
                "documentation_url": api.documentation_url,
                "base_url": api.base_url,
                "sdk_languages": api.sdk_languages or [],
                "request_limit": api.request_limit,
                "github_url": api.github_url,
                "composite_score": api.composite_score,
                "popularity_score": api.popularity_score,
                "reliability_score": api.reliability_score,
                "alternatives": api.alternatives or [],
                "tags": api.tags or [],
            })

        api_list = rank_apis(api_list)
        total_apis += len(api_list)

        result_features.append({
            "feature": feat["feature"],
            "category": cat.display_name,
            "icon": feat["icon"],
            "apis": api_list,
        })

    return {
        "idea": idea,
        "features": result_features,
        "total_apis": total_apis,
    }
