"""Data visualization utilities for financial reports."""

import matplotlib.pyplot as plt
from collections import defaultdict
from typing import Optional


def plot_monthly_report(transactions: list) -> None:
    """
    Plot monthly income and expense report.
    
    Args:
        transactions: List of Transaction objects
    """
    if not transactions:
        print("\n❌ Tidak ada data transaksi untuk ditampilkan.")
        return
    
    # Group by month
    monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
    
    for transaction in transactions:
        month = transaction.date[:7]  # YYYY-MM
        if transaction.transaction_type == "income":
            monthly_data[month]["income"] += transaction.amount
        else:
            monthly_data[month]["expense"] += transaction.amount
    
    if not monthly_data:
        print("\n❌ Tidak ada data transaksi untuk ditampilkan.")
        return
    
    months = sorted(monthly_data.keys())
    incomes = [monthly_data[month]["income"] for month in months]
    expenses = [monthly_data[month]["expense"] for month in months]
    balances = [monthly_data[month]["income"] - monthly_data[month]["expense"] for month in months]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("Laporan Keuangan Bulanan", fontsize=16, fontweight="bold")
    
    # Plot 1: Income vs Expense
    x_pos = range(len(months))
    width = 0.35
    
    ax1.bar([x - width/2 for x in x_pos], incomes, width, label="Pendapatan", color="#2ecc71", alpha=0.8)
    ax1.bar([x + width/2 for x in x_pos], expenses, width, label="Pengeluaran", color="#e74c3c", alpha=0.8)
    ax1.set_xlabel("Bulan", fontweight="bold")
    ax1.set_ylabel("Jumlah (Rp)", fontweight="bold")
    ax1.set_title("Pendapatan vs Pengeluaran", fontweight="bold")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(months)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    
    # Format y-axis as currency
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"Rp{x/1e6:.0f}M" if x >= 1e6 else f"Rp{x/1e3:.0f}K"))
    
    # Plot 2: Balance trend
    ax2.plot(months, balances, marker="o", linewidth=2, markersize=8, color="#3498db", label="Saldo")
    ax2.fill_between(range(len(months)), balances, alpha=0.3, color="#3498db")
    ax2.set_xlabel("Bulan", fontweight="bold")
    ax2.set_ylabel("Saldo (Rp)", fontweight="bold")
    ax2.set_title("Tren Saldo Bulanan", fontweight="bold")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Format y-axis as currency
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"Rp{x/1e6:.0f}M" if x >= 1e6 else f"Rp{x/1e3:.0f}K"))
    
    plt.tight_layout()
    plt.show()


def plot_category_expenses(expenses_by_category: dict) -> None:
    """
    Plot expense distribution by category.
    
    Args:
        expenses_by_category: Dictionary of category -> amount
    """
    if not expenses_by_category:
        print("\n❌ Tidak ada data pengeluaran untuk ditampilkan.")
        return
    
    categories = list(expenses_by_category.keys())
    amounts = list(expenses_by_category.values())
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = plt.cm.Set3(range(len(categories)))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors
    )
    
    # Enhance text
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(10)
    
    for text in texts:
        text.set_fontsize(11)
        text.set_fontweight("bold")
    
    ax.set_title("Distribusi Pengeluaran Berdasarkan Kategori", fontsize=14, fontweight="bold", pad=20)
    
    # Add legend with amounts
    legend_labels = [f"{cat}: Rp{amt:,.0f}" for cat, amt in zip(categories, amounts)]
    ax.legend(legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
    
    plt.tight_layout()
    plt.show()


def plot_budget_status(budget_status_list: list) -> None:
    """
    Plot budget status comparison.
    
    Args:
        budget_status_list: List of budget status dictionaries
    """
    if not budget_status_list:
        print("\n❌ Tidak ada data anggaran untuk ditampilkan.")
        return
    
    categories = [status["category"] for status in budget_status_list]
    budgets = [status["budget"] for status in budget_status_list]
    spendings = [status["spending"] for status in budget_status_list]
    
    # Filter out zero budgets
    valid_data = [(cat, bud, spen) for cat, bud, spen in zip(categories, budgets, spendings) if bud > 0]
    
    if not valid_data:
        print("\n❌ Tidak ada anggaran yang ditetapkan.")
        return
    
    categories, budgets, spendings = zip(*valid_data)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = range(len(categories))
    width = 0.35
    
    bars1 = ax.bar([x - width/2 for x in x_pos], budgets, width, label="Anggaran", color="#3498db", alpha=0.8)
    bars2 = ax.bar([x + width/2 for x in x_pos], spendings, width, label="Pengeluaran", color="#e67e22", alpha=0.8)
    
    ax.set_xlabel("Kategori", fontweight="bold")
    ax.set_ylabel("Jumlah (Rp)", fontweight="bold")
    ax.set_title("Status Anggaran per Kategori", fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"Rp{x/1e6:.0f}M" if x >= 1e6 else f"Rp{x/1e3:.0f}K"))
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f"Rp{height/1e6:.1f}M" if height >= 1e6 else f"Rp{height/1e3:.0f}K",
                   ha="center", va="bottom", fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f"Rp{height/1e6:.1f}M" if height >= 1e6 else f"Rp{height/1e3:.0f}K",
                   ha="center", va="bottom", fontsize=9)
    
    plt.tight_layout()
    plt.show()


def plot_yearly_report(transactions: list) -> None:
    """
    Plot yearly income and expense report.
    
    Args:
        transactions: List of Transaction objects
    """
    if not transactions:
        print("\n❌ Tidak ada data transaksi untuk ditampilkan.")
        return
    
    # Group by year
    yearly_data = defaultdict(lambda: {"income": 0, "expense": 0})
    
    for transaction in transactions:
        year = transaction.date[:4]  # YYYY
        if transaction.transaction_type == "income":
            yearly_data[year]["income"] += transaction.amount
        else:
            yearly_data[year]["expense"] += transaction.amount
    
    if not yearly_data:
        print("\n❌ Tidak ada data transaksi untuk ditampilkan.")
        return
    
    years = sorted(yearly_data.keys())
    incomes = [yearly_data[year]["income"] for year in years]
    expenses = [yearly_data[year]["expense"] for year in years]
    balances = [yearly_data[year]["income"] - yearly_data[year]["expense"] for year in years]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("Laporan Keuangan Tahunan", fontsize=16, fontweight="bold")
    
    # Plot 1: Income vs Expense
    x_pos = range(len(years))
    width = 0.35
    
    ax1.bar([x - width/2 for x in x_pos], incomes, width, label="Pendapatan", color="#2ecc71", alpha=0.8)
    ax1.bar([x + width/2 for x in x_pos], expenses, width, label="Pengeluaran", color="#e74c3c", alpha=0.8)
    ax1.set_xlabel("Tahun", fontweight="bold")
    ax1.set_ylabel("Jumlah (Rp)", fontweight="bold")
    ax1.set_title("Pendapatan vs Pengeluaran", fontweight="bold")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(years)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    
    # Format y-axis as currency
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"Rp{x/1e9:.1f}M" if x >= 1e9 else f"Rp{x/1e6:.0f}M" if x >= 1e6 else f"Rp{x/1e3:.0f}K"))
    
    # Plot 2: Balance trend
    ax2.plot(years, balances, marker="o", linewidth=2.5, markersize=10, color="#9b59b6", label="Saldo")
    ax2.fill_between(range(len(years)), balances, alpha=0.3, color="#9b59b6")
    ax2.set_xlabel("Tahun", fontweight="bold")
    ax2.set_ylabel("Saldo (Rp)", fontweight="bold")
    ax2.set_title("Tren Saldo Tahunan", fontweight="bold")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Format y-axis as currency
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"Rp{x/1e9:.1f}M" if x >= 1e9 else f"Rp{x/1e6:.0f}M" if x >= 1e6 else f"Rp{x/1e3:.0f}K"))
    
    plt.tight_layout()
    plt.show()
