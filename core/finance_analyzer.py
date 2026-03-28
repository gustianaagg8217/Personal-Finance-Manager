"""Financial intelligence and analysis engine."""

import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict


logger = logging.getLogger(__name__)


@dataclass
class FinancialHealth:
    """Financial health assessment result."""
    
    status: str  # "healthy" | "warning" | "critical"
    score: int  # 0-100
    insights: List[str]
    spending_trend: str  # "increasing" | "decreasing" | "stable"
    savings_rate: float  # percentage
    recommendations: List[str]


class FinanceAnalyzer:
    """Provides financial analysis and recommendations."""
    
    def __init__(self):
        """Initialize finance analyzer."""
        self.MIN_SAVINGS_RATE = 0.15  # 15% minimum recommended
        self.HEALTHY_SCORE_THRESHOLD = 70
        self.WARNING_SCORE_THRESHOLD = 50
        logger.info("FinanceAnalyzer initialized")
    
    def analyze_financial_health(
        self,
        total_income: float,
        total_expense: float,
        monthly_budgets: Dict[str, float],
        transactions: List,
        recent_months_data: Optional[Dict] = None
    ) -> FinancialHealth:
        """
        Analyze overall financial health.
        
        Args:
            total_income: Total income amount
            total_expense: Total expense amount
            monthly_budgets: Dict of category budgets
            transactions: List of transaction objects
            recent_months_data: Optional dict of recent monthly data
            
        Returns:
            FinancialHealth assessment
        """
        balance = total_income - total_expense
        savings_rate = (balance / total_income) if total_income > 0 else 0
        
        # Calculate scores
        balance_score = self._calculate_balance_score(balance, total_income)
        budget_score = self._calculate_budget_compliance_score(transactions, monthly_budgets)
        savings_score = self._calculate_savings_score(savings_rate)
        trend_score = self._calculate_trend_score(recent_months_data) if recent_months_data else 50
        
        # Weighted overall score
        overall_score = int(
            balance_score * 0.25 +
            budget_score * 0.35 +
            savings_score * 0.25 +
            trend_score * 0.15
        )
        
        # Determine status
        if overall_score >= self.HEALTHY_SCORE_THRESHOLD:
            status = "healthy"
        elif overall_score >= self.WARNING_SCORE_THRESHOLD:
            status = "warning"
        else:
            status = "critical"
        
        # Generate insights
        spending_trend = self._detect_spending_trend(recent_months_data) if recent_months_data else "stable"
        insights = self._generate_insights(
            total_income,
            total_expense,
            balance,
            savings_rate,
            budget_score,
            spending_trend
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            status,
            total_income,
            total_expense,
            balance,
            savings_rate,
            budget_score,
            spending_trend
        )
        
        return FinancialHealth(
            status=status,
            score=overall_score,
            insights=insights,
            spending_trend=spending_trend,
            savings_rate=savings_rate * 100,
            recommendations=recommendations
        )
    
    def _calculate_balance_score(self, balance: float, total_income: float) -> int:
        """Calculate balance-based score."""
        if balance < 0:
            return 10
        
        balance_ratio = balance / total_income if total_income > 0 else 0
        
        if balance_ratio >= 0.3:
            return 100
        elif balance_ratio >= 0.2:
            return 85
        elif balance_ratio >= 0.1:
            return 70
        elif balance_ratio >= 0:
            return 50
        else:
            return 10
    
    def _calculate_budget_compliance_score(
        self,
        transactions: List,
        monthly_budgets: Dict[str, float]
    ) -> int:
        """Calculate budget compliance score."""
        if not monthly_budgets or not transactions:
            return 75
        
        current_month = datetime.now().strftime("%Y-%m")
        current_month_expenses = defaultdict(float)
        
        for transaction in transactions:
            if transaction.date.startswith(current_month) and transaction.transaction_type == "expense":
                current_month_expenses[transaction.category] += transaction.amount
        
        total_budget = sum(monthly_budgets.values())
        exceeded_count = 0
        
        for category, budget in monthly_budgets.items():
            if current_month_expenses[category] > budget:
                exceeded_count += 1
        
        if exceeded_count == 0:
            return 100
        elif exceeded_count <= len(monthly_budgets) * 0.25:
            return 85
        elif exceeded_count <= len(monthly_budgets) * 0.5:
            return 60
        else:
            return 35
    
    def _calculate_savings_score(self, savings_rate: float) -> int:
        """Calculate savings rate score."""
        min_recommended = self.MIN_SAVINGS_RATE
        
        if savings_rate >= min_recommended:
            return 100
        elif savings_rate >= min_recommended * 0.75:
            return 80
        elif savings_rate >= 0:
            return 60
        else:
            return 20
    
    def _calculate_trend_score(self, recent_months_data: Dict) -> int:
        """Calculate trend-based score."""
        if not recent_months_data or len(recent_months_data) < 2:
            return 50
        
        months = sorted(recent_months_data.keys())
        recent_balance_changes = []
        
        for i in range(1, min(4, len(months))):
            prev_month = months[-i]
            curr_month = months[-i-1] if i < len(months) else None
            
            if curr_month:
                prev_balance = recent_months_data[prev_month].get("balance", 0)
                curr_balance = recent_months_data[curr_month].get("balance", 0)
                recent_balance_changes.append(curr_balance - prev_balance)
        
        if not recent_balance_changes:
            return 50
        
        improving = sum(1 for change in recent_balance_changes if change > 0)
        improvement_rate = improving / len(recent_balance_changes)
        
        return int(50 + (improvement_rate * 50))
    
    def _detect_spending_trend(self, recent_months_data: Dict) -> str:
        """Detect spending trend direction."""
        if not recent_months_data or len(recent_months_data) < 2:
            return "stable"
        
        months = sorted(recent_months_data.keys())
        last_3_months = months[-3:]
        
        expenses = [recent_months_data[m].get("expense", 0) for m in last_3_months if m in recent_months_data]
        
        if len(expenses) < 2:
            return "stable"
        
        avg_prev = sum(expenses[:-1]) / (len(expenses) - 1) if len(expenses) > 1 else expenses[-1]
        latest = expenses[-1]
        
        change_rate = (latest - avg_prev) / avg_prev if avg_prev > 0 else 0
        
        if change_rate > 0.1:
            return "increasing"
        elif change_rate < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_insights(
        self,
        total_income: float,
        total_expense: float,
        balance: float,
        savings_rate: float,
        budget_score: int,
        spending_trend: str
    ) -> List[str]:
        """Generate financial insights."""
        insights = []
        
        if balance < 0:
            insights.append("❌ Pengeluaran melebihi pendapatan")
        elif balance < total_income * 0.1:
            insights.append("⚠️ Margin keuntungan sangat tipis")
        else:
            insights.append("✅ Pendapatan melebihi pengeluaran")
        
        if savings_rate < 0.1:
            insights.append("⚠️ Tingkat tabungan di bawah 10%")
        elif savings_rate >= 0.3:
            insights.append("✅ Tingkat tabungan sangat baik (≥30%)")
        
        if spending_trend == "increasing":
            insights.append("📈 Pengeluaran menunjukkan tren meningkat")
        elif spending_trend == "decreasing":
            insights.append("📉 Pengeluaran menunjukkan tren menurun (Baik!)")
        
        if budget_score < 60:
            insights.append("⚠️ Banyak kategori yang melebihi anggaran")
        elif budget_score >= 90:
            insights.append("✅ Kepatuhan anggaran sangat baik")
        
        return insights
    
    def _generate_recommendations(
        self,
        status: str,
        total_income: float,
        total_expense: float,
        balance: float,
        savings_rate: float,
        budget_score: int,
        spending_trend: str
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if status == "critical":
            recommendations.append("🚨 Segera kurangi pengeluaran atau tingkatkan pendapatan")
            recommendations.append("🚨 Prioritaskan kebutuhan pokok dan cicilan")
            recommendations.append("🚨 Hindari pembelian yang tidak perlu")
        
        if balance < 0:
            recommendations.append("📌 Cari cara untuk menambah pendapatan")
            recommendations.append("📌 Lakukan audit pengeluaran item per item")
        
        if savings_rate < self.MIN_SAVINGS_RATE:
            recommendations.append(f"💰 Target tabungan minimal {int(self.MIN_SAVINGS_RATE * 100)}% dari pendapatan")
            target_savings = total_income * self.MIN_SAVINGS_RATE
            gap = target_savings - (total_income - total_expense)
            recommendations.append(f"💰 Kurangi pengeluaran minimal Rp{int(gap):,} per bulan")
        
        if budget_score < 70 and spending_trend == "increasing":
            recommendations.append("📊 Fokus pada kategori dengan pengeluaran tertinggi")
            recommendations.append("📊 Terapkan batas harian untuk pengeluaran diskresioner")
        
        if status == "healthy" and spending_trend == "decreasing":
            recommendations.append("⭐ Pertahankan tren pengeluaran yang menurun")
            recommendations.append("⭐ Pertimbangkan menaikkan target tabungan")
        
        if total_expense < total_income * 0.7:
            recommendations.append("🎯 Anda memiliki ruang untuk meningkatkan kualitas hidup atau investasi")
        
        return recommendations
    
    def get_spending_insights(self, expenses_by_category: Dict[str, float]) -> Dict[str, str]:
        """
        Get insights about spending distribution.
        
        Args:
            expenses_by_category: Dict of category to expense amount
            
        Returns:
            Dict of category to insight
        """
        if not expenses_by_category:
            return {}
        
        total = sum(expenses_by_category.values())
        insights = {}
        
        for category, amount in expenses_by_category.items():
            percentage = (amount / total) * 100
            
            if percentage > 30:
                insights[category] = f"🔴 {category} adalah pengeluaran utama ({percentage:.1f}%)"
            elif percentage > 15:
                insights[category] = f"🟡 {category} cukup signifikan ({percentage:.1f}%)"
            else:
                insights[category] = f"🟢 {category} terkendali ({percentage:.1f}%)"
        
        return insights
