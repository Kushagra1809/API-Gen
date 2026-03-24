"""
Curated API Knowledge Base — 100+ real-world APIs across 15+ categories.
Seeds the database on first run.
"""
from sqlalchemy.orm import Session
from models import APICategory, APIEntry

CATEGORIES = [
    {"name": "maps_location",      "display_name": "Maps & Location",       "icon": "🗺️",  "description": "Geocoding, directions, places, and mapping services",        "keywords": ["map", "location", "geocode", "directions", "places", "navigation", "routing", "gps", "address"]},
    {"name": "weather",            "display_name": "Weather",               "icon": "🌦️",  "description": "Weather forecasts, historical data, and climate info",        "keywords": ["weather", "forecast", "climate", "temperature", "rain", "wind", "humidity"]},
    {"name": "payments",           "display_name": "Payments & Finance",    "icon": "💳",   "description": "Payment processing, billing, and financial data",             "keywords": ["payment", "billing", "stripe", "checkout", "finance", "banking", "money", "transaction", "invoice", "subscription"]},
    {"name": "messaging",          "display_name": "Messaging & Chat",      "icon": "💬",   "description": "SMS, email, push notifications, and chat APIs",              "keywords": ["sms", "email", "chat", "messaging", "notification", "push", "whatsapp", "telegram", "communicate"]},
    {"name": "ai_ml",              "display_name": "AI & Machine Learning", "icon": "🤖",   "description": "AI models, NLP, vision, and ML inference APIs",              "keywords": ["ai", "ml", "machine learning", "nlp", "vision", "gpt", "llm", "deep learning", "neural", "model", "prediction", "classification", "sentiment"]},
    {"name": "flights_travel",     "display_name": "Flights & Travel",      "icon": "✈️",   "description": "Flight search, booking, and travel data APIs",               "keywords": ["flight", "airline", "travel", "booking", "airport", "trip", "itinerary", "vacation", "tourism"]},
    {"name": "hotels",             "display_name": "Hotels & Accommodation","icon": "🏨",   "description": "Hotel search, booking, and accommodation APIs",              "keywords": ["hotel", "accommodation", "booking", "lodging", "resort", "room", "stay", "airbnb", "hostel"]},
    {"name": "currency_exchange",  "display_name": "Currency & Exchange",   "icon": "💱",   "description": "Currency conversion and exchange rate APIs",                  "keywords": ["currency", "exchange", "conversion", "forex", "rate", "money"]},
    {"name": "translation",        "display_name": "Translation & Language","icon": "🌐",   "description": "Language translation and detection APIs",                     "keywords": ["translation", "translate", "language", "localization", "i18n", "multilingual"]},
    {"name": "authentication",     "display_name": "Auth & Identity",       "icon": "🔐",   "description": "Authentication, OAuth, and identity management",              "keywords": ["auth", "authentication", "login", "oauth", "identity", "sso", "jwt", "user", "signup", "registration"]},
    {"name": "storage",            "display_name": "Storage & CDN",         "icon": "☁️",   "description": "Cloud storage, file hosting, and CDN services",              "keywords": ["storage", "file", "upload", "cloud", "cdn", "s3", "blob", "image hosting", "media"]},
    {"name": "database",           "display_name": "Database & Backend",    "icon": "🗄️",  "description": "Database-as-a-service and backend platforms",                 "keywords": ["database", "backend", "baas", "firebase", "supabase", "realtime", "nosql", "sql"]},
    {"name": "search",             "display_name": "Search",                "icon": "🔍",   "description": "Full-text search, web search, and search-as-a-service",      "keywords": ["search", "fulltext", "elasticsearch", "algolia", "index", "query", "find"]},
    {"name": "social_media",       "display_name": "Social Media",          "icon": "📱",   "description": "Social media data, posting, and analytics APIs",             "keywords": ["social", "twitter", "facebook", "instagram", "linkedin", "reddit", "youtube", "tiktok", "social media"]},
    {"name": "ecommerce",          "display_name": "E-Commerce",            "icon": "🛒",   "description": "Product catalogs, shopping carts, and marketplace APIs",      "keywords": ["ecommerce", "product", "shop", "cart", "marketplace", "order", "catalog", "inventory"]},
    {"name": "video_media",        "display_name": "Video & Media",         "icon": "🎬",   "description": "Video streaming, processing, and media management",          "keywords": ["video", "stream", "media", "encode", "transcode", "player", "recording", "screen"]},
    {"name": "analytics",          "display_name": "Analytics & Monitoring","icon": "📊",   "description": "Analytics, logging, error tracking, and monitoring",          "keywords": ["analytics", "monitoring", "log", "tracking", "error", "apm", "metrics", "dashboard"]},
    {"name": "devtools",           "display_name": "Developer Tools",       "icon": "🛠️",  "description": "CI/CD, testing, code quality, and developer utilities",       "keywords": ["devtools", "ci", "cd", "testing", "deployment", "code quality", "linting", "formatting"]},
    {"name": "crypto",             "display_name": "Crypto & Blockchain",  "icon": "🪙",   "description": "Cryptocurrency rates, blockchain data, and wallet APIs",             "keywords": ["crypto", "blockchain", "bitcoin", "ethereum", "nft", "wallet", "web3"]},
    {"name": "finance_investment",  "display_name": "Stocks & Investment",  "icon": "📈",   "description": "Stock market data, investment tracking, and trading APIs",          "keywords": ["stocks", "trading", "investment", "market", "portfolio", "equity", "etf"]},
    {"name": "music_audio",        "display_name": "Music & Audio",         "icon": "🎵",   "description": "Music streaming, podcasts, and audio processing APIs",           "keywords": ["music", "audio", "podcast", "streaming", "player", "playlist", "track", "artist"]},
    {"name": "news",               "display_name": "News & Content",        "icon": "📰",   "description": "Global news, articles, and content discovery APIs",                "keywords": ["news", "article", "headline", "content", "rss", "blog"]},
    {"name": "blockchain_web3",    "display_name": "Blockchain & Web3",     "icon": "🔗",   "description": "Blockchain infrastructure, NFTs, and Web3 data APIs",                "keywords": ["blockchain", "web3", "crypto", "nft", "ethereum", "solana", "smart-contract"]},
    {"name": "cybersecurity",      "display_name": "Cybersecurity",         "icon": "🛡️",  "description": "Security auditing, threat intelligence, and identity protection",  "keywords": ["security", "cyber", "threat", "breach", "password", "vulnerability", "malware"]},
    {"name": "iot_hardware",       "display_name": "IoT & Hardware",        "icon": "🔌",   "description": "Internet of Things, hardware control, and sensor data APIs",        "keywords": ["iot", "hardware", "arduino", "raspberrypi", "sensor", "mqtt", "device management"]},
    {"name": "productivity",       "display_name": "Productivity",          "icon": "📝",   "description": "Collaboration, project management, and workspace automation APIs",  "keywords": ["productivity", "collaboration", "task", "project", "kanban", "notion", "workspace"]},
]


APIS = [
    # ─── Maps & Location ────────────────────────────────
    {"name": "Google Maps Platform", "slug": "google-maps", "provider": "Google", "category": "maps_location",
     "description": "Industry-leading maps, geocoding, directions, places, and Street View APIs.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "$200/month free credit, then pay-per-use",
     "auth_type": "api_key", "documentation_url": "https://developers.google.com/maps/documentation",
     "base_url": "https://maps.googleapis.com", "sdk_languages": ["python", "javascript", "java", "go", "ruby"],
     "request_limit": "Varies by endpoint", "github_url": "https://github.com/googlemaps",
     "popularity_score": 98, "doc_quality_score": 95, "reliability_score": 99, "latency_score": 92, "pricing_score": 60,
     "tags": ["maps", "geocoding", "directions", "places"], "alternatives": ["mapbox", "here-maps", "openstreetmap"]},

    {"name": "Mapbox", "slug": "mapbox", "provider": "Mapbox", "category": "maps_location",
     "description": "Custom maps, navigation, geocoding, and location search with beautiful styling.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "50k map loads free/month",
     "auth_type": "api_key", "documentation_url": "https://docs.mapbox.com",
     "base_url": "https://api.mapbox.com", "sdk_languages": ["python", "javascript", "ios", "android"],
     "request_limit": "50,000 free map loads/month", "github_url": "https://github.com/mapbox",
     "popularity_score": 88, "doc_quality_score": 90, "reliability_score": 95, "latency_score": 90, "pricing_score": 75,
     "tags": ["maps", "navigation", "custom-maps"], "alternatives": ["google-maps", "here-maps"]},

    {"name": "HERE Maps", "slug": "here-maps", "provider": "HERE Technologies", "category": "maps_location",
     "description": "Enterprise-grade location APIs for routing, geocoding, and fleet management.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "250k transactions free/month",
     "auth_type": "api_key", "documentation_url": "https://developer.here.com/documentation",
     "base_url": "https://geocode.search.hereapi.com", "sdk_languages": ["python", "javascript", "java"],
     "request_limit": "250,000 free/month", "github_url": "https://github.com/heremaps",
     "popularity_score": 72, "doc_quality_score": 82, "reliability_score": 93, "latency_score": 88, "pricing_score": 80,
     "tags": ["maps", "enterprise", "fleet"], "alternatives": ["google-maps", "mapbox"]},

    {"name": "OpenStreetMap / Nominatim", "slug": "openstreetmap", "provider": "OpenStreetMap Foundation", "category": "maps_location",
     "description": "Free and open-source geocoding and map data from community-driven mapping project.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Completely free, open-source",
     "auth_type": "none", "documentation_url": "https://nominatim.org/release-docs/latest/",
     "base_url": "https://nominatim.openstreetmap.org", "sdk_languages": ["python", "javascript"],
     "request_limit": "1 request/second (free tier)", "github_url": "https://github.com/openstreetmap",
     "popularity_score": 80, "doc_quality_score": 70, "reliability_score": 78, "latency_score": 65, "pricing_score": 100,
     "tags": ["maps", "open-source", "geocoding"], "alternatives": ["google-maps", "mapbox"]},

    # ─── Weather ─────────────────────────────────────────
    {"name": "OpenWeatherMap", "slug": "openweathermap", "provider": "OpenWeather", "category": "weather",
     "description": "Current weather, forecasts, historical data, and weather maps for any location.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1,000 calls/day free",
     "auth_type": "api_key", "documentation_url": "https://openweathermap.org/api",
     "base_url": "https://api.openweathermap.org", "sdk_languages": ["python", "javascript", "java"],
     "request_limit": "1,000 calls/day free", "github_url": "https://github.com/openweathermap",
     "popularity_score": 90, "doc_quality_score": 80, "reliability_score": 88, "latency_score": 85, "pricing_score": 85,
     "tags": ["weather", "forecast", "free"], "alternatives": ["weatherapi", "visual-crossing"]},

    {"name": "WeatherAPI", "slug": "weatherapi", "provider": "WeatherAPI.com", "category": "weather",
     "description": "Real-time weather, forecast, astronomy, time zone, and sports weather API.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1M calls/month free",
     "auth_type": "api_key", "documentation_url": "https://www.weatherapi.com/docs/",
     "base_url": "https://api.weatherapi.com/v1", "sdk_languages": ["python", "javascript"],
     "request_limit": "1,000,000 calls/month free", "github_url": "",
     "popularity_score": 78, "doc_quality_score": 82, "reliability_score": 85, "latency_score": 88, "pricing_score": 90,
     "tags": ["weather", "forecast", "astronomy"], "alternatives": ["openweathermap", "visual-crossing"]},

    {"name": "Visual Crossing Weather", "slug": "visual-crossing", "provider": "Visual Crossing", "category": "weather",
     "description": "Historical and forecast weather data with high accuracy and 50+ years of history.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1,000 records/day free",
     "auth_type": "api_key", "documentation_url": "https://www.visualcrossing.com/resources/documentation/",
     "base_url": "https://weather.visualcrossing.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "1,000 records/day free", "github_url": "",
     "popularity_score": 65, "doc_quality_score": 78, "reliability_score": 90, "latency_score": 82, "pricing_score": 80,
     "tags": ["weather", "historical", "forecast"], "alternatives": ["openweathermap", "weatherapi"]},

    # ─── Payments & Finance ──────────────────────────────
    {"name": "Stripe", "slug": "stripe", "provider": "Stripe Inc.", "category": "payments",
     "description": "Complete payments platform with cards, wallets, subscriptions, invoicing, and fraud prevention.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "2.9% + 30¢ per transaction",
     "auth_type": "api_key", "documentation_url": "https://stripe.com/docs/api",
     "base_url": "https://api.stripe.com", "sdk_languages": ["python", "javascript", "ruby", "java", "go", "php", "dotnet"],
     "request_limit": "Unlimited (rate limited)", "github_url": "https://github.com/stripe",
     "popularity_score": 98, "doc_quality_score": 99, "reliability_score": 99, "latency_score": 95, "pricing_score": 65,
     "tags": ["payments", "subscriptions", "invoicing"], "alternatives": ["paypal", "square", "razorpay"]},

    {"name": "PayPal", "slug": "paypal", "provider": "PayPal Holdings", "category": "payments",
     "description": "Global payment processing with buyer/seller protection and checkout integration.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "2.99% + 49¢ per transaction",
     "auth_type": "oauth2", "documentation_url": "https://developer.paypal.com/docs/api/overview/",
     "base_url": "https://api.paypal.com", "sdk_languages": ["python", "javascript", "java", "php", "ruby"],
     "request_limit": "Unlimited", "github_url": "https://github.com/paypal",
     "popularity_score": 92, "doc_quality_score": 80, "reliability_score": 95, "latency_score": 80, "pricing_score": 60,
     "tags": ["payments", "checkout", "global"], "alternatives": ["stripe", "square"]},

    {"name": "Razorpay", "slug": "razorpay", "provider": "Razorpay", "category": "payments",
     "description": "Payment gateway popular in India supporting UPI, cards, wallets, and EMI.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "2% per transaction",
     "auth_type": "api_key", "documentation_url": "https://razorpay.com/docs/api/",
     "base_url": "https://api.razorpay.com", "sdk_languages": ["python", "javascript", "java", "php", "ruby", "go"],
     "request_limit": "Unlimited", "github_url": "https://github.com/razorpay",
     "popularity_score": 75, "doc_quality_score": 85, "reliability_score": 92, "latency_score": 88, "pricing_score": 75,
     "tags": ["payments", "india", "upi"], "alternatives": ["stripe", "paypal"]},

    {"name": "Square", "slug": "square", "provider": "Block Inc.", "category": "payments",
     "description": "Commerce platform with payment processing, POS, and business tools.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "2.6% + 10¢ per transaction",
     "auth_type": "oauth2", "documentation_url": "https://developer.squareup.com/docs",
     "base_url": "https://connect.squareup.com", "sdk_languages": ["python", "javascript", "java", "ruby", "php"],
     "request_limit": "Unlimited", "github_url": "https://github.com/square",
     "popularity_score": 80, "doc_quality_score": 88, "reliability_score": 95, "latency_score": 85, "pricing_score": 70,
     "tags": ["payments", "pos", "commerce"], "alternatives": ["stripe", "paypal"]},

    # ─── Messaging & Chat ────────────────────────────────
    {"name": "Twilio", "slug": "twilio", "provider": "Twilio Inc.", "category": "messaging",
     "description": "SMS, voice, video, WhatsApp, and email APIs for communication.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free trial with $15 credit, then pay-per-use",
     "auth_type": "api_key", "documentation_url": "https://www.twilio.com/docs",
     "base_url": "https://api.twilio.com", "sdk_languages": ["python", "javascript", "java", "php", "ruby", "csharp", "go"],
     "request_limit": "Pay-per-use", "github_url": "https://github.com/twilio",
     "popularity_score": 95, "doc_quality_score": 95, "reliability_score": 97, "latency_score": 90, "pricing_score": 55,
     "tags": ["sms", "voice", "whatsapp", "messaging"], "alternatives": ["sendgrid", "vonage", "messagebird"]},

    {"name": "SendGrid", "slug": "sendgrid", "provider": "Twilio (SendGrid)", "category": "messaging",
     "description": "Email delivery and marketing API with templates, analytics, and deliverability tools.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "100 emails/day free",
     "auth_type": "api_key", "documentation_url": "https://docs.sendgrid.com/",
     "base_url": "https://api.sendgrid.com", "sdk_languages": ["python", "javascript", "java", "ruby", "go", "csharp", "php"],
     "request_limit": "100 emails/day free", "github_url": "https://github.com/sendgrid",
     "popularity_score": 90, "doc_quality_score": 88, "reliability_score": 95, "latency_score": 88, "pricing_score": 70,
     "tags": ["email", "marketing", "transactional"], "alternatives": ["mailgun", "postmark", "ses"]},

    {"name": "Mailgun", "slug": "mailgun", "provider": "Sinch (Mailgun)", "category": "messaging",
     "description": "Transactional email API with validation, templates, and inbound routing.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "100 emails/day free for 3 months",
     "auth_type": "api_key", "documentation_url": "https://documentation.mailgun.com/",
     "base_url": "https://api.mailgun.net", "sdk_languages": ["python", "javascript", "java", "ruby", "php", "go", "csharp"],
     "request_limit": "100 emails/day free", "github_url": "https://github.com/mailgun",
     "popularity_score": 82, "doc_quality_score": 82, "reliability_score": 90, "latency_score": 85, "pricing_score": 65,
     "tags": ["email", "transactional", "validation"], "alternatives": ["sendgrid", "postmark"]},

    {"name": "Firebase Cloud Messaging", "slug": "firebase-fcm", "provider": "Google", "category": "messaging",
     "description": "Free push notification service for Android, iOS, and Web applications.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Completely free",
     "auth_type": "api_key", "documentation_url": "https://firebase.google.com/docs/cloud-messaging",
     "base_url": "https://fcm.googleapis.com", "sdk_languages": ["python", "javascript", "java", "swift", "kotlin", "go"],
     "request_limit": "Unlimited", "github_url": "https://github.com/firebase",
     "popularity_score": 92, "doc_quality_score": 90, "reliability_score": 97, "latency_score": 95, "pricing_score": 100,
     "tags": ["push", "notification", "mobile", "free"], "alternatives": ["onesignal", "pusher"]},

    # ─── AI & Machine Learning ───────────────────────────
    {"name": "OpenAI API", "slug": "openai", "provider": "OpenAI", "category": "ai_ml",
     "description": "GPT-4, DALL·E, Whisper, and embedding models for text, image, and audio AI.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "$5 free credit, then pay-per-token",
     "auth_type": "api_key", "documentation_url": "https://platform.openai.com/docs",
     "base_url": "https://api.openai.com", "sdk_languages": ["python", "javascript", "go"],
     "request_limit": "Rate limited by tier", "github_url": "https://github.com/openai",
     "popularity_score": 99, "doc_quality_score": 95, "reliability_score": 92, "latency_score": 80, "pricing_score": 50,
     "tags": ["ai", "llm", "gpt", "chatbot", "nlp"], "alternatives": ["google-gemini", "anthropic-claude", "cohere"]},

    {"name": "Google Gemini API", "slug": "google-gemini", "provider": "Google", "category": "ai_ml",
     "description": "Gemini multimodal AI models for text, image, video, and code understanding.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier available, pay-per-token after",
     "auth_type": "api_key", "documentation_url": "https://ai.google.dev/docs",
     "base_url": "https://generativelanguage.googleapis.com", "sdk_languages": ["python", "javascript", "go", "swift", "kotlin"],
     "request_limit": "60 requests/min free", "github_url": "https://github.com/google-gemini",
     "popularity_score": 90, "doc_quality_score": 90, "reliability_score": 93, "latency_score": 85, "pricing_score": 75,
     "tags": ["ai", "llm", "multimodal", "vision"], "alternatives": ["openai", "anthropic-claude"]},

    {"name": "Anthropic Claude API", "slug": "anthropic-claude", "provider": "Anthropic", "category": "ai_ml",
     "description": "Claude AI models optimized for safety, helpfulness, and long-context understanding.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "Pay-per-token, starts at $3/M input tokens",
     "auth_type": "api_key", "documentation_url": "https://docs.anthropic.com/",
     "base_url": "https://api.anthropic.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "Rate limited by tier", "github_url": "https://github.com/anthropics",
     "popularity_score": 85, "doc_quality_score": 92, "reliability_score": 94, "latency_score": 82, "pricing_score": 55,
     "tags": ["ai", "llm", "safety", "long-context"], "alternatives": ["openai", "google-gemini"]},

    {"name": "Mistral AI API", "slug": "mistral-ai", "provider": "Mistral AI", "category": "ai_ml",
     "description": "High-performance open-weight LLMs (Mistral 7B, Mixtral 8x7B) via API.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier available for experimentation",
     "auth_type": "api_key", "documentation_url": "https://docs.mistral.ai/",
     "base_url": "https://api.mistral.ai", "sdk_languages": ["python", "javascript"],
     "request_limit": "Varies by tier", "github_url": "https://github.com/mistralai",
     "popularity_score": 85, "doc_quality_score": 88, "reliability_score": 92, "latency_score": 90, "pricing_score": 85,
     "tags": ["ai", "llm", "open-source", "mixture-of-experts"], "alternatives": ["openai", "google-gemini", "groq"]},

    {"name": "Groq Cloud API", "slug": "groq", "provider": "Groq Inc.", "category": "ai_ml",
     "description": "Ultra-fast LLM inference (Llama3, Mixtral) using LPU hardware acceleration.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier for beta testers",
     "auth_type": "api_key", "documentation_url": "https://console.groq.com/docs",
     "base_url": "https://api.groq.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "Rate limited by tokens/min", "github_url": "https://github.com/groq",
     "popularity_score": 80, "doc_quality_score": 85, "reliability_score": 88, "latency_score": 100, "pricing_score": 90,
     "tags": ["ai", "llm", "inference", "speed"], "alternatives": ["mistral-ai", "together-ai"]},

    {"name": "ElevenLabs API", "slug": "elevenlabs", "provider": "ElevenLabs", "category": "ai_ml",
     "description": "The most realistic AI speech platform — Text-to-Speech (TTS) and Voice Cloning.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "10k characters/month free",
     "auth_type": "api_key", "documentation_url": "https://elevenlabs.io/docs",
     "base_url": "https://api.elevenlabs.io", "sdk_languages": ["python", "javascript"],
     "request_limit": "10,000 chars/month free", "github_url": "https://github.com/elevenlabs",
     "popularity_score": 90, "doc_quality_score": 92, "reliability_score": 95, "latency_score": 85, "pricing_score": 65,
     "tags": ["ai", "tts", "audio", "voice-cloning"], "alternatives": ["play-ht", "deepgram"]},

    {"name": "AssemblyAI", "slug": "assemblyai", "provider": "AssemblyAI", "category": "ai_ml",
     "description": "Production-ready speech-to-text, speaker diarization, and audio intelligence.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "$50 free credit for new accounts",
     "auth_type": "api_key", "documentation_url": "https://www.assemblyai.com/docs",
     "base_url": "https://api.assemblyai.com", "sdk_languages": ["python", "javascript", "go", "ruby", "java"],
     "request_limit": "Varies by tier", "github_url": "https://github.com/assemblyai",
     "popularity_score": 82, "doc_quality_score": 95, "reliability_score": 94, "latency_score": 88, "pricing_score": 75,
     "tags": ["ai", "stt", "transcription", "audio-analysis"], "alternatives": ["deepgram", "openai-whisper"]},

    {"name": "Pinecone API", "slug": "pinecone", "provider": "Pinecone Systems", "category": "ai_ml",
     "description": "Managed vector database for long-term memory in AI agents and RAG applications.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1 index free (Starter plan)",
     "auth_type": "api_key", "documentation_url": "https://docs.pinecone.io/",
     "base_url": "https://api.pinecone.io", "sdk_languages": ["python", "javascript", "go", "java"],
     "request_limit": "Rate limited on free tier", "github_url": "https://github.com/pinecone-io",
     "popularity_score": 88, "doc_quality_score": 92, "reliability_score": 97, "latency_score": 94, "pricing_score": 70,
     "tags": ["ai", "vector-db", "rag", "embeddings"], "alternatives": ["weaviate", "milvus", "qdrant"]},

    {"name": "Perplexity API", "slug": "perplexity", "provider": "Perplexity AI", "category": "ai_ml",
     "description": "LLM-powered search and answer engine with real-time web access.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "$5/M tokens",
     "auth_type": "api_key", "documentation_url": "https://docs.perplexity.ai/",
     "base_url": "https://api.perplexity.ai", "sdk_languages": ["python", "javascript"],
     "request_limit": "Rate limited", "github_url": "",
     "popularity_score": 88, "doc_quality_score": 82, "reliability_score": 90, "latency_score": 85, "pricing_score": 75,
     "tags": ["ai", "search", "llm", "real-time"], "alternatives": ["openai", "google-gemini"]},

    {"name": "Together AI", "slug": "together-ai", "provider": "Together AI", "category": "ai_ml",
     "description": "Fast and affordable API for 100+ open-source models (Llama 3, Qwen, DBRX).",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "$25 free credit",
     "auth_type": "api_key", "documentation_url": "https://docs.together.ai/",
     "base_url": "https://api.together.xyz", "sdk_languages": ["python", "javascript"],
     "request_limit": "Varies by model", "github_url": "https://github.com/togethercomputer",
     "popularity_score": 82, "doc_quality_score": 88, "reliability_score": 92, "latency_score": 95, "pricing_score": 92,
     "tags": ["ai", "llm", "open-source", "inference"], "alternatives": ["groq", "anyscale"]},

    {"name": "Hugging Face Inference API", "slug": "huggingface", "provider": "Hugging Face", "category": "ai_ml",
     "description": "Run 200,000+ open-source ML models via API — NLP, vision, audio, and more.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier for popular models",
     "auth_type": "api_key", "documentation_url": "https://huggingface.co/docs/api-inference/",
     "base_url": "https://api-inference.huggingface.co", "sdk_languages": ["python", "javascript"],
     "request_limit": "Rate limited on free tier", "github_url": "https://github.com/huggingface",
     "popularity_score": 92, "doc_quality_score": 88, "reliability_score": 85, "latency_score": 70, "pricing_score": 85,
     "tags": ["ai", "open-source", "nlp", "vision"], "alternatives": ["openai", "replicate"]},

    {"name": "Replicate", "slug": "replicate", "provider": "Replicate Inc.", "category": "ai_ml",
     "description": "Run open-source ML models in the cloud with a simple API — Stable Diffusion, LLaMA, etc.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free predictions for some models",
     "auth_type": "api_key", "documentation_url": "https://replicate.com/docs",
     "base_url": "https://api.replicate.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "Pay-per-prediction", "github_url": "https://github.com/replicate",
     "popularity_score": 78, "doc_quality_score": 85, "reliability_score": 82, "latency_score": 65, "pricing_score": 70,
     "tags": ["ai", "open-source", "image-gen", "stable-diffusion"], "alternatives": ["huggingface", "openai"]},

    {"name": "Google Cloud Vision", "slug": "google-vision", "provider": "Google Cloud", "category": "ai_ml",
     "description": "Image analysis API: OCR, label detection, face detection, and object localization.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1,000 units/month free",
     "auth_type": "api_key", "documentation_url": "https://cloud.google.com/vision/docs",
     "base_url": "https://vision.googleapis.com", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "csharp", "php"],
     "request_limit": "1,000 units/month free", "github_url": "https://github.com/googleapis",
     "popularity_score": 88, "doc_quality_score": 92, "reliability_score": 97, "latency_score": 88, "pricing_score": 65,
     "tags": ["vision", "ocr", "image-analysis"], "alternatives": ["aws-rekognition", "azure-vision"]},

    # ─── Flights & Travel ────────────────────────────────
    {"name": "Amadeus for Developers", "slug": "amadeus", "provider": "Amadeus IT", "category": "flights_travel",
     "description": "Flight search, booking, airports, airlines, trip purpose prediction, and more.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free test environment, pay for production",
     "auth_type": "oauth2", "documentation_url": "https://developers.amadeus.com/self-service",
     "base_url": "https://api.amadeus.com", "sdk_languages": ["python", "javascript", "java"],
     "request_limit": "Free test: 500 calls/month", "github_url": "https://github.com/amadeus4dev",
     "popularity_score": 82, "doc_quality_score": 85, "reliability_score": 90, "latency_score": 75, "pricing_score": 60,
     "tags": ["flights", "booking", "airlines", "travel"], "alternatives": ["skyscanner", "kiwi-flights"]},

    {"name": "Skyscanner API", "slug": "skyscanner", "provider": "Skyscanner (Trip.com)", "category": "flights_travel",
     "description": "Flight, hotel, and car rental search with global coverage.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier via RapidAPI",
     "auth_type": "api_key", "documentation_url": "https://developers.skyscanner.net/docs",
     "base_url": "https://partners.api.skyscanner.net", "sdk_languages": ["python", "javascript"],
     "request_limit": "Varies by plan", "github_url": "",
     "popularity_score": 78, "doc_quality_score": 75, "reliability_score": 82, "latency_score": 80, "pricing_score": 70,
     "tags": ["flights", "hotels", "car-rental"], "alternatives": ["amadeus", "kiwi-flights"]},

    {"name": "Kiwi.com Tequila API", "slug": "kiwi-flights", "provider": "Kiwi.com", "category": "flights_travel",
     "description": "Flight search API combining airlines and ground transport for complex itineraries.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for affiliates",
     "auth_type": "api_key", "documentation_url": "https://tequila.kiwi.com/portal/docs",
     "base_url": "https://api.tequila.kiwi.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "Rate limited", "github_url": "",
     "popularity_score": 65, "doc_quality_score": 72, "reliability_score": 80, "latency_score": 78, "pricing_score": 85,
     "tags": ["flights", "multi-city", "budget-travel"], "alternatives": ["amadeus", "skyscanner"]},

    # ─── Hotels & Accommodation ──────────────────────────
    {"name": "Booking.com API", "slug": "booking-com", "provider": "Booking Holdings", "category": "hotels",
     "description": "Hotel search, availability, pricing, and booking for 28M+ listings worldwide.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "Affiliate program",
     "auth_type": "api_key", "documentation_url": "https://developers.booking.com/",
     "base_url": "https://distribution-xml.booking.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "Varies by partner", "github_url": "",
     "popularity_score": 90, "doc_quality_score": 75, "reliability_score": 92, "latency_score": 78, "pricing_score": 55,
     "tags": ["hotels", "booking", "accommodation"], "alternatives": ["hotels-com", "airbnb-api"]},

    {"name": "Hotels.com API", "slug": "hotels-com", "provider": "Expedia Group", "category": "hotels",
     "description": "Hotel search and booking with loyalty rewards integration.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "Affiliate program via RapidAPI",
     "auth_type": "api_key", "documentation_url": "https://rapidapi.com/apidojo/api/hotels4",
     "base_url": "https://hotels4.p.rapidapi.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "500 requests/month free", "github_url": "",
     "popularity_score": 72, "doc_quality_score": 68, "reliability_score": 85, "latency_score": 80, "pricing_score": 60,
     "tags": ["hotels", "booking", "rewards"], "alternatives": ["booking-com"]},

    # ─── Currency & Exchange ─────────────────────────────
    {"name": "ExchangeRate-API", "slug": "exchangerate-api", "provider": "ExchangeRate-API", "category": "currency_exchange",
     "description": "Free currency exchange rates for 161 currencies, updated daily.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1,500 requests/month free",
     "auth_type": "api_key", "documentation_url": "https://www.exchangerate-api.com/docs/overview",
     "base_url": "https://v6.exchangerate-api.com", "sdk_languages": ["python", "javascript"],
     "request_limit": "1,500 requests/month free", "github_url": "",
     "popularity_score": 80, "doc_quality_score": 78, "reliability_score": 90, "latency_score": 92, "pricing_score": 90,
     "tags": ["currency", "exchange", "forex"], "alternatives": ["fixer-io", "open-exchange-rates"]},

    {"name": "Fixer.io", "slug": "fixer-io", "provider": "Apilayer", "category": "currency_exchange",
     "description": "Foreign exchange rates API with 170 currencies and historical data.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "100 calls/month free",
     "auth_type": "api_key", "documentation_url": "https://fixer.io/documentation",
     "base_url": "https://data.fixer.io/api", "sdk_languages": ["python", "javascript", "php"],
     "request_limit": "100 calls/month free", "github_url": "",
     "popularity_score": 75, "doc_quality_score": 80, "reliability_score": 88, "latency_score": 85, "pricing_score": 70,
     "tags": ["currency", "forex", "historical"], "alternatives": ["exchangerate-api", "open-exchange-rates"]},

    {"name": "Open Exchange Rates", "slug": "open-exchange-rates", "provider": "Open Exchange Rates", "category": "currency_exchange",
     "description": "Real-time and historical exchange rates for 200+ currencies.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1,000 calls/month free (USD base only)",
     "auth_type": "api_key", "documentation_url": "https://docs.openexchangerates.org/",
     "base_url": "https://openexchangerates.org/api", "sdk_languages": ["python", "javascript"],
     "request_limit": "1,000 calls/month free", "github_url": "https://github.com/openexchangerates",
     "popularity_score": 72, "doc_quality_score": 82, "reliability_score": 90, "latency_score": 88, "pricing_score": 75,
     "tags": ["currency", "exchange", "historical"], "alternatives": ["exchangerate-api", "fixer-io"]},

    # ─── Translation & Language ──────────────────────────
    {"name": "Google Cloud Translation", "slug": "google-translate", "provider": "Google Cloud", "category": "translation",
     "description": "Neural machine translation for 130+ languages with auto-detection.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "500k characters/month free",
     "auth_type": "api_key", "documentation_url": "https://cloud.google.com/translate/docs",
     "base_url": "https://translation.googleapis.com", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "php"],
     "request_limit": "500,000 characters/month free", "github_url": "https://github.com/googleapis",
     "popularity_score": 95, "doc_quality_score": 92, "reliability_score": 98, "latency_score": 90, "pricing_score": 65,
     "tags": ["translation", "languages", "nlp"], "alternatives": ["deepl", "microsoft-translator"]},

    {"name": "DeepL API", "slug": "deepl", "provider": "DeepL SE", "category": "translation",
     "description": "High-quality neural translation for 30+ languages, often rated above Google.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "500k characters/month free",
     "auth_type": "api_key", "documentation_url": "https://www.deepl.com/docs-api",
     "base_url": "https://api-free.deepl.com", "sdk_languages": ["python", "javascript", "java", "go"],
     "request_limit": "500,000 characters/month free", "github_url": "https://github.com/DeepLcom",
     "popularity_score": 85, "doc_quality_score": 88, "reliability_score": 95, "latency_score": 88, "pricing_score": 75,
     "tags": ["translation", "high-quality", "european-languages"], "alternatives": ["google-translate", "microsoft-translator"]},

    {"name": "Microsoft Translator", "slug": "microsoft-translator", "provider": "Microsoft Azure", "category": "translation",
     "description": "Text and document translation for 100+ languages with customization.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "2M characters/month free",
     "auth_type": "api_key", "documentation_url": "https://learn.microsoft.com/en-us/azure/ai-services/translator/",
     "base_url": "https://api.cognitive.microsofttranslator.com", "sdk_languages": ["python", "javascript", "java", "csharp"],
     "request_limit": "2,000,000 characters/month free", "github_url": "https://github.com/MicrosoftTranslator",
     "popularity_score": 82, "doc_quality_score": 85, "reliability_score": 96, "latency_score": 88, "pricing_score": 80,
     "tags": ["translation", "azure", "documents"], "alternatives": ["google-translate", "deepl"]},

    # ─── Auth & Identity ─────────────────────────────────
    {"name": "Auth0", "slug": "auth0", "provider": "Okta (Auth0)", "category": "authentication",
     "description": "Universal authentication and authorization platform with social login, MFA, and SSO.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "7,500 active users free",
     "auth_type": "oauth2", "documentation_url": "https://auth0.com/docs",
     "base_url": "https://YOUR_DOMAIN.auth0.com", "sdk_languages": ["python", "javascript", "java", "swift", "kotlin", "go", "ruby", "php"],
     "request_limit": "7,500 active users free", "github_url": "https://github.com/auth0",
     "popularity_score": 92, "doc_quality_score": 95, "reliability_score": 97, "latency_score": 90, "pricing_score": 70,
     "tags": ["auth", "sso", "social-login", "mfa"], "alternatives": ["firebase-auth", "supabase-auth", "clerk"]},

    {"name": "Firebase Authentication", "slug": "firebase-auth", "provider": "Google", "category": "authentication",
     "description": "Easy drop-in authentication with email, phone, social login, and anonymous auth.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for most use cases",
     "auth_type": "api_key", "documentation_url": "https://firebase.google.com/docs/auth",
     "base_url": "https://identitytoolkit.googleapis.com", "sdk_languages": ["python", "javascript", "java", "swift", "kotlin", "go"],
     "request_limit": "Phone auth: 10k/month free", "github_url": "https://github.com/firebase",
     "popularity_score": 90, "doc_quality_score": 90, "reliability_score": 97, "latency_score": 92, "pricing_score": 90,
     "tags": ["auth", "firebase", "mobile", "social-login"], "alternatives": ["auth0", "supabase-auth"]},

    {"name": "Clerk", "slug": "clerk", "provider": "Clerk Inc.", "category": "authentication",
     "description": "Modern user management with pre-built UI, embeddable components, and webhooks.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "10,000 MAU free",
     "auth_type": "api_key", "documentation_url": "https://clerk.com/docs",
     "base_url": "https://api.clerk.dev", "sdk_languages": ["javascript", "python"],
     "request_limit": "10,000 MAU free", "github_url": "https://github.com/clerk",
     "popularity_score": 78, "doc_quality_score": 90, "reliability_score": 92, "latency_score": 88, "pricing_score": 80,
     "tags": ["auth", "user-management", "embeddable"], "alternatives": ["auth0", "firebase-auth"]},

    # ─── Storage & CDN ───────────────────────────────────
    {"name": "AWS S3", "slug": "aws-s3", "provider": "Amazon Web Services", "category": "storage",
     "description": "Industry-standard object storage with 99.999999999% durability.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "5GB free for 12 months",
     "auth_type": "api_key", "documentation_url": "https://docs.aws.amazon.com/s3/",
     "base_url": "https://s3.amazonaws.com", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "php", "csharp"],
     "request_limit": "20,000 GET, 2,000 PUT free/month", "github_url": "https://github.com/aws",
     "popularity_score": 98, "doc_quality_score": 90, "reliability_score": 99, "latency_score": 92, "pricing_score": 60,
     "tags": ["storage", "s3", "object-storage", "cloud"], "alternatives": ["google-cloud-storage", "cloudflare-r2"]},

    {"name": "Cloudflare R2", "slug": "cloudflare-r2", "provider": "Cloudflare", "category": "storage",
     "description": "S3-compatible object storage with zero egress fees.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "10GB storage, 10M reads/month free",
     "auth_type": "api_key", "documentation_url": "https://developers.cloudflare.com/r2/",
     "base_url": "https://api.cloudflare.com", "sdk_languages": ["python", "javascript", "go"],
     "request_limit": "10M reads, 1M writes/month free", "github_url": "https://github.com/cloudflare",
     "popularity_score": 78, "doc_quality_score": 82, "reliability_score": 95, "latency_score": 92, "pricing_score": 90,
     "tags": ["storage", "s3-compatible", "zero-egress"], "alternatives": ["aws-s3", "google-cloud-storage"]},

    {"name": "Cloudinary", "slug": "cloudinary", "provider": "Cloudinary", "category": "storage",
     "description": "Media management with image/video upload, transformation, optimization, and CDN delivery.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "25 credits/month free",
     "auth_type": "api_key", "documentation_url": "https://cloudinary.com/documentation",
     "base_url": "https://api.cloudinary.com", "sdk_languages": ["python", "javascript", "java", "ruby", "php", "go"],
     "request_limit": "25 credits/month free", "github_url": "https://github.com/cloudinary",
     "popularity_score": 85, "doc_quality_score": 88, "reliability_score": 95, "latency_score": 90, "pricing_score": 72,
     "tags": ["media", "image", "video", "cdn", "optimization"], "alternatives": ["imgix", "aws-s3"]},

    # ─── Database & Backend ──────────────────────────────
    {"name": "Supabase", "slug": "supabase", "provider": "Supabase Inc.", "category": "database",
     "description": "Open-source Firebase alternative with Postgres, auth, storage, edge functions, and realtime.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "500MB database, 1GB storage free",
     "auth_type": "api_key", "documentation_url": "https://supabase.com/docs",
     "base_url": "https://YOUR_PROJECT.supabase.co", "sdk_languages": ["python", "javascript", "flutter", "swift", "kotlin"],
     "request_limit": "500MB database free", "github_url": "https://github.com/supabase",
     "popularity_score": 88, "doc_quality_score": 90, "reliability_score": 90, "latency_score": 85, "pricing_score": 85,
     "tags": ["backend", "postgres", "realtime", "open-source"], "alternatives": ["firebase", "appwrite"]},

    {"name": "Firebase", "slug": "firebase", "provider": "Google", "category": "database",
     "description": "Complete app development platform with Firestore, auth, hosting, and cloud functions.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Generous free tier (Spark plan)",
     "auth_type": "api_key", "documentation_url": "https://firebase.google.com/docs",
     "base_url": "https://firestore.googleapis.com", "sdk_languages": ["python", "javascript", "java", "swift", "kotlin", "go", "csharp"],
     "request_limit": "50k reads, 20k writes/day free", "github_url": "https://github.com/firebase",
     "popularity_score": 95, "doc_quality_score": 92, "reliability_score": 97, "latency_score": 90, "pricing_score": 80,
     "tags": ["backend", "realtime", "nosql", "hosting"], "alternatives": ["supabase", "appwrite"]},

    # ─── Search ──────────────────────────────────────────
    {"name": "Algolia", "slug": "algolia", "provider": "Algolia", "category": "search",
     "description": "Lightning-fast search and discovery API with typo tolerance and instant results.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "10k search requests/month free",
     "auth_type": "api_key", "documentation_url": "https://www.algolia.com/doc/",
     "base_url": "https://YOUR_APP.algolia.net", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "php", "csharp", "swift", "kotlin"],
     "request_limit": "10,000 search requests/month free", "github_url": "https://github.com/algolia",
     "popularity_score": 88, "doc_quality_score": 95, "reliability_score": 98, "latency_score": 99, "pricing_score": 60,
     "tags": ["search", "instant", "typo-tolerance"], "alternatives": ["meilisearch", "typesense"]},

    {"name": "MeiliSearch", "slug": "meilisearch", "provider": "Meili", "category": "search",
     "description": "Open-source, lightning-fast search engine with typo tolerance — easy to deploy.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Open-source, free self-hosted",
     "auth_type": "api_key", "documentation_url": "https://www.meilisearch.com/docs",
     "base_url": "https://cloud.meilisearch.com", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "php", "rust"],
     "request_limit": "Unlimited (self-hosted)", "github_url": "https://github.com/meilisearch",
     "popularity_score": 80, "doc_quality_score": 88, "reliability_score": 88, "latency_score": 95, "pricing_score": 98,
     "tags": ["search", "open-source", "self-hosted"], "alternatives": ["algolia", "typesense"]},

    # ─── Social Media ────────────────────────────────────
    {"name": "Twitter/X API", "slug": "twitter-api", "provider": "X Corp.", "category": "social_media",
     "description": "Tweets, users, spaces, trends, and direct messages on the X platform.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free: write-only, Basic: $100/month",
     "auth_type": "oauth2", "documentation_url": "https://developer.twitter.com/en/docs",
     "base_url": "https://api.twitter.com", "sdk_languages": ["python", "javascript", "java", "ruby"],
     "request_limit": "Free: 1,500 tweets/month", "github_url": "https://github.com/twitterdev",
     "popularity_score": 85, "doc_quality_score": 72, "reliability_score": 80, "latency_score": 82, "pricing_score": 45,
     "tags": ["social", "tweets", "trends"], "alternatives": ["reddit-api", "meta-graph-api"]},

    {"name": "YouTube Data API", "slug": "youtube-data-api", "provider": "Google", "category": "social_media",
     "description": "Search videos, manage channels, playlists, comments, and live streams.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "10,000 units/day free",
     "auth_type": "api_key", "documentation_url": "https://developers.google.com/youtube/v3",
     "base_url": "https://www.googleapis.com/youtube/v3", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "php"],
     "request_limit": "10,000 units/day free", "github_url": "https://github.com/googleapis",
     "popularity_score": 92, "doc_quality_score": 88, "reliability_score": 97, "latency_score": 85, "pricing_score": 90,
     "tags": ["video", "social", "youtube", "streaming"], "alternatives": ["vimeo-api", "twitch-api"]},

    # ─── E-Commerce ──────────────────────────────────────
    {"name": "Shopify Storefront API", "slug": "shopify-storefront", "provider": "Shopify", "category": "ecommerce",
     "description": "Product catalog, cart, checkout, and customer data for headless commerce.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free with Shopify subscription",
     "auth_type": "api_key", "documentation_url": "https://shopify.dev/docs/api/storefront",
     "base_url": "https://YOUR_STORE.myshopify.com", "sdk_languages": ["python", "javascript", "ruby"],
     "request_limit": "Rate limited per plan", "github_url": "https://github.com/Shopify",
     "popularity_score": 90, "doc_quality_score": 92, "reliability_score": 97, "latency_score": 88, "pricing_score": 55,
     "tags": ["ecommerce", "headless", "products", "checkout"], "alternatives": ["woocommerce-api", "snipcart"]},

    # ─── Video & Media ───────────────────────────────────
    {"name": "Mux Video", "slug": "mux-video", "provider": "Mux Inc.", "category": "video_media",
     "description": "Video upload, encoding, streaming, and analytics API built for developers.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free: 10 mins of video storage",
     "auth_type": "api_key", "documentation_url": "https://docs.mux.com/",
     "base_url": "https://api.mux.com", "sdk_languages": ["python", "javascript", "go", "ruby"],
     "request_limit": "Pay-per-use after free tier", "github_url": "https://github.com/muxinc",
     "popularity_score": 78, "doc_quality_score": 92, "reliability_score": 95, "latency_score": 88, "pricing_score": 60,
     "tags": ["video", "streaming", "encoding", "analytics"], "alternatives": ["cloudinary", "api-video"]},

    # ─── Analytics & Monitoring ──────────────────────────
    {"name": "Sentry", "slug": "sentry", "provider": "Sentry (Functional Software)", "category": "analytics",
     "description": "Error tracking and performance monitoring for every major language and framework.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "5,000 errors/month free",
     "auth_type": "api_key", "documentation_url": "https://docs.sentry.io/",
     "base_url": "https://sentry.io/api/", "sdk_languages": ["python", "javascript", "java", "go", "ruby", "php", "csharp", "rust", "swift"],
     "request_limit": "5,000 errors/month free", "github_url": "https://github.com/getsentry",
     "popularity_score": 90, "doc_quality_score": 92, "reliability_score": 96, "latency_score": 90, "pricing_score": 75,
     "tags": ["errors", "monitoring", "performance", "open-source"], "alternatives": ["datadog", "new-relic"]},

    {"name": "Mixpanel", "slug": "mixpanel", "provider": "Mixpanel Inc.", "category": "analytics",
     "description": "Product analytics with event tracking, funnels, retention, and A/B testing.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "20M events/month free",
     "auth_type": "api_key", "documentation_url": "https://developer.mixpanel.com/docs",
     "base_url": "https://api.mixpanel.com", "sdk_languages": ["python", "javascript", "java", "swift", "kotlin"],
     "request_limit": "20M events/month free", "github_url": "https://github.com/mixpanel",
     "popularity_score": 85, "doc_quality_score": 85, "reliability_score": 94, "latency_score": 88, "pricing_score": 80,
     "tags": ["analytics", "product", "events", "funnels"], "alternatives": ["amplitude", "posthog"]},

    # ─── Developer Tools ─────────────────────────────────
    {"name": "GitHub API", "slug": "github-api", "provider": "GitHub (Microsoft)", "category": "devtools",
     "description": "Repos, issues, pull requests, actions, and user management on GitHub.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "5,000 requests/hour authenticated",
     "auth_type": "oauth2", "documentation_url": "https://docs.github.com/en/rest",
     "base_url": "https://api.github.com", "sdk_languages": ["python", "javascript", "java", "ruby", "go"],
     "request_limit": "5,000 requests/hour", "github_url": "https://github.com/github",
     "popularity_score": 98, "doc_quality_score": 95, "reliability_score": 99, "latency_score": 92, "pricing_score": 95,
     "tags": ["git", "repos", "ci-cd", "devtools"], "alternatives": ["gitlab-api", "bitbucket-api"]},

    {"name": "Vercel API", "slug": "vercel-api", "provider": "Vercel", "category": "devtools",
     "description": "Deploy, manage, and monitor frontend projects and serverless functions.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Hobby plan free",
     "auth_type": "api_key", "documentation_url": "https://vercel.com/docs/rest-api",
     "base_url": "https://api.vercel.com", "sdk_languages": ["javascript", "python"],
     "request_limit": "Varies by plan", "github_url": "https://github.com/vercel",
     "popularity_score": 85, "doc_quality_score": 88, "reliability_score": 97, "latency_score": 95, "pricing_score": 80,
     "tags": ["deployment", "serverless", "frontend", "hosting"], "alternatives": ["netlify-api", "railway-api"]},

    # ─── Crypto & Blockchain ────────────────────────────
    {"name": "CoinGecko API", "slug": "coingecko", "provider": "CoinGecko", "category": "crypto",
     "description": "Comprehensive cryptocurrency data: price, volume, market cap, and exchange data.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free demo plan available",
     "auth_type": "api_key", "documentation_url": "https://www.coingecko.com/en/api/documentation",
     "base_url": "https://api.coingecko.com/api/v3", "sdk_languages": ["python", "javascript"],
     "request_limit": "10-30 calls/min free", "github_url": "https://github.com/coingecko",
     "popularity_score": 92, "doc_quality_score": 85, "reliability_score": 90, "latency_score": 88, "pricing_score": 85,
     "tags": ["crypto", "prices", "market-cap"], "alternatives": ["coinmarketcap", "binance-api"]},

    {"name": "Coinbase Cloud API", "slug": "coinbase-cloud", "provider": "Coinbase", "category": "crypto",
     "description": "Access blockchain infrastructure, wallets, trading, and NFTs on Coinbase.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Pay-as-you-go available",
     "auth_type": "api_key", "documentation_url": "https://docs.cloud.coinbase.com/",
     "base_url": "https://api.coinbase.com", "sdk_languages": ["python", "javascript", "go", "ruby"],
     "request_limit": "Varies by service", "github_url": "https://github.com/coinbase",
     "popularity_score": 88, "doc_quality_score": 92, "reliability_score": 97, "latency_score": 90, "pricing_score": 75,
     "tags": ["crypto", "wallet", "trading", "web3"], "alternatives": ["binance-api", "coingecko"]},

    # ─── Stocks & Investment ────────────────────────────
    {"name": "Alpha Vantage", "slug": "alpha-vantage", "provider": "Alpha Vantage Inc.", "category": "finance_investment",
     "description": "Real-time and historical stock market data, forex, and cryptocurrency APIs.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "5 calls/min, 500 calls/day free",
     "auth_type": "api_key", "documentation_url": "https://www.alphavantage.co/documentation/",
     "base_url": "https://www.alphavantage.co", "sdk_languages": ["python", "javascript", "php"],
     "request_limit": "500 calls/day free", "github_url": "",
     "popularity_score": 85, "doc_quality_score": 80, "reliability_score": 88, "latency_score": 85, "pricing_score": 90,
     "tags": ["stocks", "finance", "forex", "historical"], "alternatives": ["yahoo-finance", "polygon-io"]},

    {"name": "Polygon.io", "slug": "polygon-io", "provider": "Polygon.io", "category": "finance_investment",
     "description": "Financial data platform for stocks, options, forex, and crypto with high accuracy.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier for end-of-day data",
     "auth_type": "api_key", "documentation_url": "https://polygon.io/docs",
     "base_url": "https://api.polygon.io", "sdk_languages": ["python", "javascript", "go"],
     "request_limit": "5 calls/min free", "github_url": "https://github.com/polygon-io",
     "popularity_score": 82, "doc_quality_score": 90, "reliability_score": 95, "latency_score": 92, "pricing_score": 80,
     "tags": ["stocks", "finance", "real-time", "options"], "alternatives": ["alpha-vantage", "iex-cloud"]},

    # ─── Music & Audio ──────────────────────────────────
    {"name": "Spotify Web API", "slug": "spotify", "provider": "Spotify AB", "category": "music_audio",
     "description": "Access Spotify's music library, playlists, user profile, and playback control.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Free for developers",
     "auth_type": "oauth2", "documentation_url": "https://developer.spotify.com/documentation/web-api/",
     "base_url": "https://api.spotify.com/v1", "sdk_languages": ["python", "javascript", "java", "swift", "kotlin"],
     "request_limit": "Varies by rate limit", "github_url": "https://github.com/spotify",
     "popularity_score": 98, "doc_quality_score": 95, "reliability_score": 97, "latency_score": 90, "pricing_score": 95,
     "tags": ["music", "streaming", "spotify", "playlist"], "alternatives": ["apple-music", "last-fm"]},

    {"name": "Last.fm API", "slug": "last-fm", "provider": "Last.fm (CBS Interactive)", "category": "music_audio",
     "description": "Music data API for charts, metadata, and user listening history.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Free for non-commercial use",
     "auth_type": "api_key", "documentation_url": "https://www.last.fm/api",
     "base_url": "http://ws.audioscrobbler.com/2.0/", "sdk_languages": ["python", "javascript"],
     "request_limit": "Fair use policy", "github_url": "",
     "popularity_score": 80, "doc_quality_score": 75, "reliability_score": 85, "latency_score": 82, "pricing_score": 100,
     "tags": ["music", "metadata", "charts", "scrobbling"], "alternatives": ["spotify", "musicbrainz"]},

    # ─── News & Content ─────────────────────────────────
    {"name": "NewsAPI", "slug": "news-api", "provider": "NewsAPI.org", "category": "news",
     "description": "Search and retrieve live articles from all over the web.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "100 requests/day free (dev only)",
     "auth_type": "api_key", "documentation_url": "https://newsapi.org/docs",
     "base_url": "https://newsapi.org/v2", "sdk_languages": ["python", "javascript", "java"],
     "request_limit": "100 requests/day free", "github_url": "https://github.com/newsapi-org",
     "popularity_score": 85, "doc_quality_score": 82, "reliability_score": 88, "latency_score": 85, "pricing_score": 85,
     "tags": ["news", "articles", "headlines"], "alternatives": ["gnews", "currents-api"]},

    {"name": "GNews API", "slug": "gnews", "provider": "GNews.io", "category": "news",
     "description": "Simple and fast news API to search for articles and get worldwide headlines.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "100 requests/day free",
     "auth_type": "api_key", "documentation_url": "https://gnews.io/docs/v4",
     "base_url": "https://gnews.io/api/v4", "sdk_languages": ["python", "javascript"],
     "request_limit": "100 requests/day free", "github_url": "",
     "popularity_score": 78, "doc_quality_score": 80, "reliability_score": 85, "latency_score": 88, "pricing_score": 80,
     "tags": ["news", "headlines", "search"], "alternatives": ["news-api", "mediastack"]},

    # ─── Blockchain & Web3 ──────────────────────────────
    {"name": "Alchemy API", "slug": "alchemy", "provider": "Alchemy Insights", "category": "blockchain_web3",
     "description": "Leading blockchain developer platform for Ethereum, Solana, and Polygon infrastructure.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free tier with generous compute units",
     "auth_type": "api_key", "documentation_url": "https://docs.alchemy.com/",
     "base_url": "https://eth-mainnet.g.alchemy.com", "sdk_languages": ["javascript", "python"],
     "request_limit": "Varies by plan", "github_url": "https://github.com/alchemyplatform",
     "popularity_score": 90, "doc_quality_score": 95, "reliability_score": 97, "latency_score": 94, "pricing_score": 80,
     "tags": ["web3", "ethereum", "node-provider", "nft"], "alternatives": ["infura", "moralis"]},

    {"name": "OpenSea API", "slug": "opensea", "provider": "OpenSea", "category": "blockchain_web3",
     "description": "Access world's largest NFT marketplace data — assets, orders, and collections.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Free with API key approval",
     "auth_type": "api_key", "documentation_url": "https://docs.opensea.io/",
     "base_url": "https://api.opensea.io", "sdk_languages": ["javascript", "python"],
     "request_limit": "Rate limited", "github_url": "https://github.com/ProjectOpenSea",
     "popularity_score": 88, "doc_quality_score": 82, "reliability_score": 88, "latency_score": 80, "pricing_score": 85,
     "tags": ["web3", "nft", "marketplace"], "alternatives": ["rarible-api", "alchemy"]},

    {"name": "Infura API", "slug": "infura", "provider": "ConsenSys", "category": "blockchain_web3",
     "description": "Scalable blockchain infrastructure for Ethereum, IPFS, and layer 2 networks.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "100k requests/day free",
     "auth_type": "api_key", "documentation_url": "https://docs.infura.io/",
     "base_url": "https://mainnet.infura.io/v3/", "sdk_languages": ["javascript", "python", "go"],
     "request_limit": "100,000 requests/day", "github_url": "https://github.com/infura",
     "popularity_score": 92, "doc_quality_score": 90, "reliability_score": 97, "latency_score": 92, "pricing_score": 75,
     "tags": ["web3", "ethereum", "infrastructure", "ipfs"], "alternatives": ["alchemy", "quicknode"]},

    {"name": "Moralis API", "slug": "moralis", "provider": "Moralis Web3", "category": "blockchain_web3",
     "description": "Enterprise-grade Web3 APIs for NFT, Token, Balance, and Transaction data.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for personal projects",
     "auth_type": "api_key", "documentation_url": "https://docs.moralis.io/",
     "base_url": "https://deep-index.moralis.io/api/v2", "sdk_languages": ["javascript", "python"],
     "request_limit": "Rate limited by CU", "github_url": "https://github.com/moralisweb3",
     "popularity_score": 85, "doc_quality_score": 92, "reliability_score": 90, "latency_score": 88, "pricing_score": 80,
     "tags": ["web3", "nft", "token-api", "blockchain-data"], "alternatives": ["alchemy", "covalent"]},

    # ─── Cybersecurity ──────────────────────────────────
    {"name": "VirusTotal API", "slug": "virustotal", "provider": "Google (Chronicle)", "category": "cybersecurity",
     "description": "Scan files, URLs, and IPs against 70+ antivirus engines and URL scanners.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for non-commercial/limited use",
     "auth_type": "api_key", "documentation_url": "https://developers.virustotal.com/reference",
     "base_url": "https://www.virustotal.com/api/v3", "sdk_languages": ["python", "javascript"],
     "request_limit": "4 requests/min free", "github_url": "https://github.com/VirusTotal",
     "popularity_score": 92, "doc_quality_score": 88, "reliability_score": 95, "latency_score": 85, "pricing_score": 75,
     "tags": ["security", "malware", "scanning", "threat-intel"], "alternatives": ["shodan", "hybrid-analysis"]},

    {"name": "Have I Been Pwned API", "slug": "hibp", "provider": "Troy Hunt", "category": "cybersecurity",
     "description": "Check if an email or phone number has been compromised in a data breach.",
     "free_tier": False, "pricing_model": "paid", "pricing_details": "$3.50/month starter plan",
     "auth_type": "api_key", "documentation_url": "https://haveibeenpwned.com/API/v3",
     "base_url": "https://haveibeenpwned.com/api/v3", "sdk_languages": ["python", "javascript"],
     "request_limit": "Rate limited", "github_url": "",
     "popularity_score": 85, "doc_quality_score": 92, "reliability_score": 98, "latency_score": 94, "pricing_score": 95,
     "tags": ["security", "breach", "password", "privacy"], "alternatives": ["leakcheck"]},

    # ─── IoT & Hardware ─────────────────────────────────
    {"name": "Particle Cloud API", "slug": "particle", "provider": "Particle Industries", "category": "iot_hardware",
     "description": "Manage IoT devices, OTA firmware updates, and sensor data messaging.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for up to 100 devices",
     "auth_type": "api_key", "documentation_url": "https://docs.particle.io/reference/cloud-api/",
     "base_url": "https://api.particle.io", "sdk_languages": ["javascript", "python", "c++"],
     "request_limit": "Varies by cellular data", "github_url": "https://github.com/particle-iot",
     "popularity_score": 78, "doc_quality_score": 90, "reliability_score": 92, "latency_score": 85, "pricing_score": 80,
     "tags": ["iot", "hardware", "ota", "cellular"], "alternatives": ["arduino-cloud", "blynk"]},

    {"name": "Arduino Cloud API", "slug": "arduino-cloud", "provider": "Arduino", "category": "iot_hardware",
     "description": "Connect and manage Arduino, ESP32, and ESP8266 devices with ease.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for up to 2 devices",
     "auth_type": "api_key", "documentation_url": "https://www.arduino.cc/reference/en/iot/api/",
     "base_url": "https://api2.arduino.cc/iot/v2", "sdk_languages": ["javascript", "python", "c++"],
     "request_limit": "Rate limited", "github_url": "https://github.com/arduino",
     "popularity_score": 85, "doc_quality_score": 88, "reliability_score": 94, "latency_score": 90, "pricing_score": 85,
     "tags": ["iot", "hardware", "arduino", "cloud"], "alternatives": ["particle", "blynk"]},

    {"name": "Adafruit IO API", "slug": "adafruit-io", "provider": "Adafruit Industries", "category": "iot_hardware",
     "description": "Simple data hosting and visualization for IoT devices via MQTT and REST.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "Free for active usage",
     "auth_type": "api_key", "documentation_url": "https://io.adafruit.com/api/docs/",
     "base_url": "https://io.adafruit.com/api/v2", "sdk_languages": ["python", "javascript", "ruby"],
     "request_limit": "30 data points / minute", "github_url": "https://github.com/adafruit/adafruit-io-python",
     "popularity_score": 80, "doc_quality_score": 95, "reliability_score": 95, "latency_score": 92, "pricing_score": 95,
     "tags": ["iot", "hardware", "sensors", "mqtt"], "alternatives": ["blynk", "particle"]},

    # ─── Productivity ───────────────────────────────────
    {"name": "Notion API", "slug": "notion", "provider": "Notion Labs", "category": "productivity",
     "description": "Connect your Notion workspace to other apps — read/write pages, databases, and blocks.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Free for developers",
     "auth_type": "oauth2", "documentation_url": "https://developers.notion.com/",
     "base_url": "https://api.notion.com/v1", "sdk_languages": ["javascript", "python"],
     "request_limit": "3 requests/second", "github_url": "https://github.com/makenotion",
     "popularity_score": 95, "doc_quality_score": 95, "reliability_score": 94, "latency_score": 88, "pricing_score": 98,
     "tags": ["productivity", "workspace", "automation", "notion"], "alternatives": ["trello-api", "asana"]},

    {"name": "Trello API", "slug": "trello", "provider": "Atlassian", "category": "productivity",
     "description": "Automate Trello boards, lists, and cards using the REST API.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Unlimited key usage",
     "auth_type": "api_key", "documentation_url": "https://developer.atlassian.com/cloud/trello/",
     "base_url": "https://api.trello.com/1", "sdk_languages": ["javascript", "python"],
     "request_limit": "300 requests / 10 seconds", "github_url": "",
     "popularity_score": 88, "doc_quality_score": 85, "reliability_score": 96, "latency_score": 90, "pricing_score": 95,
     "tags": ["productivity", "kanban", "trello", "project-management"], "alternatives": ["asana", "clickup"]},

    {"name": "Asana API", "slug": "asana", "provider": "Asana Inc.", "category": "productivity",
     "description": "Build apps and automate workflows in Asana — manage tasks, projects, and users.",
     "free_tier": True, "pricing_model": "free", "pricing_details": "Free for personal use",
     "auth_type": "oauth2", "documentation_url": "https://developers.asana.com/docs/",
     "base_url": "https://app.asana.com/api/1.0", "sdk_languages": ["python", "javascript", "ruby", "java", "php"],
     "request_limit": "150 requests/minute", "github_url": "https://github.com/asana",
     "popularity_score": 85, "doc_quality_score": 90, "reliability_score": 95, "latency_score": 88, "pricing_score": 80,
     "tags": ["productivity", "project-management", "workflow"], "alternatives": ["trello", "monday-com"]},

    # ─── Developer Tools Expansion ──────────────────────
    {"name": "Railway API", "slug": "railway", "provider": "Railway Corp.", "category": "devtools",
     "description": "Deploy infrastructure and manage environments programmatically with Railway.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "$5 one-time credit, then usage-based",
     "auth_type": "api_key", "documentation_url": "https://docs.railway.app/reference/api",
     "base_url": "https://backboard.railway.app/graphql", "sdk_languages": ["javascript", "python"],
     "request_limit": "Varies by plan", "github_url": "https://github.com/railwayapp",
     "popularity_score": 82, "doc_quality_score": 88, "reliability_score": 94, "latency_score": 92, "pricing_score": 85,
     "tags": ["deployment", "paas", "infra", "cloud"], "alternatives": ["vercel", "render", "fly-io"]},

    {"name": "Postman API", "slug": "postman", "provider": "Postman Inc.", "category": "devtools",
     "description": "Manage Postman collections, environments, and mocks programmatically.",
     "free_tier": True, "pricing_model": "freemium", "pricing_details": "1,000 calls/month free",
     "auth_type": "api_key", "documentation_url": "https://learning.postman.com/docs/developer/postman-api/intro-api/",
     "base_url": "https://api.getpostman.com", "sdk_languages": ["javascript", "python"],
     "request_limit": "1,000 calls/month free", "github_url": "",
     "popularity_score": 95, "doc_quality_score": 92, "reliability_score": 97, "latency_score": 90, "pricing_score": 80,
     "tags": ["api-testing", "documentation", "collections", "devtools"], "alternatives": ["insomnia", "swagger"]},
]


def compute_composite(api: dict) -> float:
    """Compute composite score using weighted formula."""
    from config import SCORING_WEIGHTS
    return round(
        api["popularity_score"]  * SCORING_WEIGHTS["popularity"]   +
        api["doc_quality_score"] * SCORING_WEIGHTS["documentation"]+
        api["reliability_score"] * SCORING_WEIGHTS["reliability"]  +
        api["pricing_score"]     * SCORING_WEIGHTS["pricing"]      +
        api["latency_score"]     * SCORING_WEIGHTS["latency"],
        2
    )


def seed_database(db: Session) -> None:
    """Populate the database with curated API data (idempotent for new entries)."""
    # 1. Seed Categories (idempotent)
    cat_map = {}
    for cat in CATEGORIES:
        existing_cat = db.query(APICategory).filter(APICategory.name == cat["name"]).first()
        if not existing_cat:
            obj = APICategory(**cat)
            db.add(obj)
            db.flush()
            cat_map[cat["name"]] = obj.id
        else:
            cat_map[cat["name"]] = existing_cat.id

    # 2. Seed API Entries (idempotent by slug)
    added_count = 0
    for api_data in APIS:
        api = api_data.copy()  # Avoid modifying original dict
        cat_name = api.pop("category")
        api["category_id"] = cat_map[cat_name]
        api["composite_score"] = compute_composite(api)

        existing_api = db.query(APIEntry).filter(APIEntry.slug == api["slug"]).first()
        if not existing_api:
            obj = APIEntry(**api)
            db.add(obj)
            added_count += 1
        else:
            # Optionally update existing entries here if needed
            pass

    db.commit()
    if added_count > 0:
        print(f"✅  Seeded {added_count} new APIs across {len(CATEGORIES)} categories")
    else:
        print("ℹ️  Knowledge base is already up to date.")
