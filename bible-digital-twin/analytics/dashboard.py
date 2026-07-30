"""
Analytics & Dashboard Module - Enhancements #19-28
#19: Real-time Usage Analytics
#20: User Behavior Tracking
#21: Search Pattern Analysis
#22: Popular Verses Ranking
#23: Reading Progress Analytics
#24: Geographic Distribution (mock)
#25: Time-series Trends
#26: A/B Testing Framework
#27: Performance Metrics Dashboard
#28: Custom Report Generation
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import json

class UsageAnalytics:
    """Enhancement #19: Real-time Usage Analytics"""
    
    def __init__(self):
        self.events = []
        self.page_views = Counter()
        self.api_calls = Counter()
    
    def track_event(self, event_type: str, user_id: str, data: Dict[str, Any]):
        """Track custom event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "data": data
        }
        self.events.append(event)
    
    def track_page_view(self, page: str, user_id: str):
        """Track page view"""
        self.page_views[page] += 1
        self.track_event("page_view", user_id, {"page": page})
    
    def track_api_call(self, endpoint: str, method: str, duration_ms: float):
        """Track API call with performance"""
        self.api_calls[f"{method}:{endpoint}"] += 1
    
    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_events = [e for e in self.events if datetime.fromisoformat(e["timestamp"]) > cutoff]
        
        return {
            "total_events": len(recent_events),
            "unique_users": len(set(e["user_id"] for e in recent_events)),
            "top_pages": dict(self.page_views.most_common(10)),
            "top_endpoints": dict(self.api_calls.most_common(10)),
            "event_types": dict(Counter(e["event_type"] for e in recent_events))
        }

class UserBehaviorTracker:
    """Enhancement #20: User Behavior Tracking"""
    
    def __init__(self):
        self.user_sessions = defaultdict(list)
        self.user_preferences = defaultdict(dict)
    
    def start_session(self, user_id: str, session_id: str):
        """Start user session"""
        self.user_sessions[user_id].append({
            "session_id": session_id,
            "start_time": datetime.utcnow().isoformat(),
            "actions": []
        })
    
    def track_action(self, user_id: str, action: str, details: Dict[str, Any]):
        """Track user action within session"""
        if self.user_sessions[user_id]:
            self.user_sessions[user_id][-1]["actions"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "details": details
            })
    
    def save_preference(self, user_id: str, key: str, value: Any):
        """Save user preference"""
        self.user_preferences[user_id][key] = value
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile"""
        sessions = self.user_sessions.get(user_id, [])
        total_actions = sum(len(s["actions"]) for s in sessions)
        
        return {
            "user_id": user_id,
            "total_sessions": len(sessions),
            "total_actions": total_actions,
            "preferences": self.user_preferences.get(user_id, {}),
            "last_active": sessions[-1]["start_time"] if sessions else None
        }

class SearchPatternAnalyzer:
    """Enhancement #21: Search Pattern Analysis"""
    
    def __init__(self):
        self.search_queries = []
        self.search_results = []
    
    def log_search(self, query: str, results_count: int, user_id: str, filters: Dict[str, Any]):
        """Log search query and results"""
        self.search_queries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "results_count": results_count,
            "user_id": user_id,
            "filters": filters
        })
    
    def get_trending_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending search queries"""
        query_counts = Counter(q["query"] for q in self.search_queries)
        return [
            {"query": query, "count": count}
            for query, count in query_counts.most_common(limit)
        ]
    
    def get_zero_result_queries(self) -> List[str]:
        """Get queries with no results"""
        return list(set(
            q["query"] for q in self.search_queries if q["results_count"] == 0
        ))

class PopularVersesRanker:
    """Enhancement #22: Popular Verses Ranking"""
    
    def __init__(self):
        self.verse_views = Counter()
        self.verse_shares = Counter()
        self.verse_bookmarks = Counter()
    
    def track_view(self, verse_ref: str):
        """Track verse view"""
        self.verse_views[verse_ref] += 1
    
    def track_share(self, verse_ref: str):
        """Track verse share"""
        self.verse_shares[verse_ref] += 1
    
    def track_bookmark(self, verse_ref: str):
        """Track verse bookmark"""
        self.verse_bookmarks[verse_ref] += 1
    
    def get_ranking(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get popular verses ranking"""
        # Weighted score: views (1) + shares (3) + bookmarks (2)
        scores = {}
        all_verses = set(self.verse_views.keys()) | set(self.verse_shares.keys()) | set(self.verse_bookmarks.keys())
        
        for verse in all_verses:
            score = (
                self.verse_views[verse] * 1 +
                self.verse_shares[verse] * 3 +
                self.verse_bookmarks[verse] * 2
            )
            scores[verse] = score
        
        sorted_verses = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {"reference": verse, "score": score, "rank": i+1}
            for i, (verse, score) in enumerate(sorted_verses[:50])
        ]

class ReadingProgressTracker:
    """Enhancement #23: Reading Progress Analytics"""
    
    def __init__(self):
        self.user_progress = defaultdict(lambda: {
            "books_read": set(),
            "chapters_read": set(),
            "verses_read": set(),
            "streak_days": 0,
            "last_read": None
        })
    
    def log_reading(self, user_id: str, book: str, chapter: int, verse: int):
        """Log reading activity"""
        progress = self.user_progress[user_id]
        progress["books_read"].add(book)
        progress["chapters_read"].add(f"{book}:{chapter}")
        progress["verses_read"].add(f"{book}:{chapter}:{verse}")
        progress["last_read"] = datetime.utcnow().isoformat()
        
        # Calculate streak (simplified)
        if progress["streak_days"] == 0:
            progress["streak_days"] = 1
    
    def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user reading progress"""
        progress = self.user_progress[user_id]
        total_books = 66  # Protestant Bible
        total_chapters = 1189
        
        return {
            "books_completed": len(progress["books_read"]),
            "books_percentage": round(len(progress["books_read"]) / total_books * 100, 2),
            "chapters_completed": len(progress["chapters_read"]),
            "chapters_percentage": round(len(progress["chapters_read"]) / total_chapters * 100, 2),
            "streak_days": progress["streak_days"],
            "last_read": progress["last_read"]
        }

class GeographicDistribution:
    """Enhancement #24: Geographic Distribution (Mock)"""
    
    def __init__(self):
        self.country_stats = Counter()
    
    def log_access(self, country: str, region: str = None):
        """Log geographic access"""
        self.country_stats[country] += 1
    
    def get_distribution(self) -> List[Dict[str, Any]]:
        """Get geographic distribution"""
        total = sum(self.country_stats.values())
        return [
            {
                "country": country,
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0
            }
            for country, count in self.country_stats.most_common(20)
        ]

class TimeSeriesTrends:
    """Enhancement #25: Time-series Trends"""
    
    def __init__(self):
        self.hourly_data = defaultdict(int)
        self.daily_data = defaultdict(int)
    
    def log_activity(self, timestamp: datetime = None):
        """Log activity for time series"""
        ts = timestamp or datetime.utcnow()
        hour_key = ts.strftime("%Y-%m-%d %H:00")
        day_key = ts.strftime("%Y-%m-%d")
        
        self.hourly_data[hour_key] += 1
        self.daily_data[day_key] += 1
    
    def get_hourly_trend(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get hourly trend"""
        now = datetime.utcnow()
        trends = []
        for i in range(hours):
            hour = now - timedelta(hours=i)
            key = hour.strftime("%Y-%m-%d %H:00")
            trends.append({
                "hour": key,
                "count": self.hourly_data.get(key, 0)
            })
        return list(reversed(trends))
    
    def get_daily_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily trend"""
        now = datetime.utcnow()
        trends = []
        for i in range(days):
            day = now - timedelta(days=i)
            key = day.strftime("%Y-%m-%d")
            trends.append({
                "date": key,
                "count": self.daily_data.get(key, 0)
            })
        return list(reversed(trends))

class ABTestingFramework:
    """Enhancement #26: A/B Testing Framework"""
    
    def __init__(self):
        self.variants = defaultdict(lambda: {"A": 0, "B": 0})
        self.conversions = defaultdict(lambda: {"A": 0, "B": 0})
    
    def assign_variant(self, test_id: str, user_id: str) -> str:
        """Assign user to variant"""
        # Simple hash-based assignment
        hash_val = hash(user_id) % 2
        variant = "A" if hash_val == 0 else "B"
        self.variants[test_id][variant] += 1
        return variant
    
    def log_conversion(self, test_id: str, variant: str):
        """Log conversion for variant"""
        self.conversions[test_id][variant] += 1
    
    def get_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results"""
        variants = self.variants[test_id]
        conversions = self.conversions[test_id]
        
        results = {}
        for variant in ["A", "B"]:
            total = variants[variant]
            conv = conversions[variant]
            rate = conv / total if total > 0 else 0
            results[variant] = {
                "users": total,
                "conversions": conv,
                "conversion_rate": round(rate * 100, 2)
            }
        
        return results

class PerformanceMetrics:
    """Enhancement #27: Performance Metrics Dashboard"""
    
    def __init__(self):
        self.response_times = defaultdict(list)
        self.error_rates = defaultdict(int)
        self.request_counts = defaultdict(int)
    
    def log_request(self, endpoint: str, duration_ms: float, status_code: int):
        """Log request metrics"""
        self.response_times[endpoint].append(duration_ms)
        self.request_counts[endpoint] += 1
        if status_code >= 400:
            self.error_rates[endpoint] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = {}
        for endpoint in self.request_counts.keys():
            times = self.response_times[endpoint]
            requests = self.request_counts[endpoint]
            errors = self.error_rates[endpoint]
            
            metrics[endpoint] = {
                "requests": requests,
                "avg_response_ms": round(sum(times) / len(times), 2) if times else 0,
                "p95_response_ms": round(sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times) if times else 0, 2),
                "error_rate": round(errors / requests * 100, 2) if requests > 0 else 0
            }
        
        return metrics

class ReportGenerator:
    """Enhancement #28: Custom Report Generation"""
    
    def generate_report(self, report_type: str, date_range: tuple, **kwargs) -> Dict[str, Any]:
        """Generate custom report"""
        reports = {
            "usage": self._generate_usage_report,
            "engagement": self._generate_engagement_report,
            "search": self._generate_search_report,
            "performance": self._generate_performance_report
        }
        
        generator = reports.get(report_type)
        if not generator:
            return {"error": "Unknown report type"}
        
        return generator(date_range, **kwargs)
    
    def _generate_usage_report(self, date_range: tuple, **kwargs) -> Dict[str, Any]:
        """Generate usage report"""
        return {
            "report_type": "usage",
            "date_range": date_range,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": "Usage report data would go here"
        }
    
    def _generate_engagement_report(self, date_range: tuple, **kwargs) -> Dict[str, Any]:
        """Generate engagement report"""
        return {
            "report_type": "engagement",
            "date_range": date_range,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": "Engagement report data would go here"
        }
    
    def _generate_search_report(self, date_range: tuple, **kwargs) -> Dict[str, Any]:
        """Generate search report"""
        return {
            "report_type": "search",
            "date_range": date_range,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": "Search report data would go here"
        }
    
    def _generate_performance_report(self, date_range: tuple, **kwargs) -> Dict[str, Any]:
        """Generate performance report"""
        return {
            "report_type": "performance",
            "date_range": date_range,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": "Performance report data would go here"
        }
