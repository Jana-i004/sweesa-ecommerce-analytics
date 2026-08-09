"""
sql_reports.py
تقارير الأعمال (Business Analytics Reports) عبر استعلامات SQL متقدمة.

التقارير:
1. تقرير المبيعات الإجمالي مقسم بالشهور.
2. أعلى 10 عملاء شراءً (برنامج الولاء).
3. المنتجات التي أوشكت على النفاد (مخزون أقل من 5) مع اسم القسم.
"""

import pandas as pd
from sqlalchemy import text
from db_config import get_engine


def monthly_sales_report(engine):
    """
    تقرير المبيعات الإجمالي مقسم بالشهور.
    يعتمد على دمج orders مع order_items وتجميع الإجمالي شهرياً.
    """
    query = """
        SELECT
            DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month,
            COUNT(DISTINCT o.order_id)         AS total_orders,
            SUM(oi.quantity * oi.unit_price)   AS total_sales
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY sales_month
        ORDER BY sales_month;
    """
    try:
        df = pd.read_sql(text(query), engine)
        return df
    except Exception as e:
        print(f"❌ خطأ في تقرير المبيعات الشهرية: {e}")
        return pd.DataFrame()


def top_10_customers_report(engine):
    """
    أعلى 10 عملاء من حيث إجمالي المبلغ المدفوع (برنامج الولاء).
    """
    query = """
        SELECT
            c.customer_id,
            c.full_name,
            c.city,
            COUNT(DISTINCT o.order_id)       AS total_orders,
            SUM(oi.quantity * oi.unit_price) AS total_spent
        FROM customers c
        JOIN orders o       ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id    = oi.order_id
        GROUP BY c.customer_id, c.full_name, c.city
        ORDER BY total_spent DESC
        LIMIT 10;
    """
    try:
        df = pd.read_sql(text(query), engine)
        return df
    except Exception as e:
        print(f"❌ خطأ في تقرير أعلى 10 عملاء: {e}")
        return pd.DataFrame()


def low_stock_report(engine, threshold: int = 5):
    """
    المنتجات التي أوشكت على النفاد (الكمية أقل من threshold) مع اسم القسم.
    """
    query = """
        SELECT
            p.product_id,
            p.product_name,
            p.stock_quantity,
            cat.category_name
        FROM products p
        JOIN categories cat ON p.category_id = cat.category_id
        WHERE p.stock_quantity < :threshold
        ORDER BY p.stock_quantity ASC;
    """
    try:
        df = pd.read_sql(text(query), engine, params={"threshold": threshold})
        return df
    except Exception as e:
        print(f"❌ خطأ في تقرير المنتجات الموشكة على النفاد: {e}")
        return pd.DataFrame()


def run_all_reports():
    engine = get_engine()
    if engine is None:
        print("تعذر تشغيل التقارير بسبب فشل الاتصال بقاعدة البيانات.")
        return

    try:
        print("=" * 60)
        print("📊 تقرير المبيعات الإجمالي حسب الشهر")
        print("=" * 60)
        monthly_df = monthly_sales_report(engine)
        print(monthly_df.to_string(index=False))

        print("\n" + "=" * 60)
        print("🏆 أعلى 10 عملاء شراءً (برنامج الولاء)")
        print("=" * 60)
        top_customers_df = top_10_customers_report(engine)
        print(top_customers_df.to_string(index=False))

        print("\n" + "=" * 60)
        print("⚠️  المنتجات الموشكة على النفاد (أقل من 5 قطع)")
        print("=" * 60)
        low_stock_df = low_stock_report(engine)
        print(low_stock_df.to_string(index=False))

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء تشغيل التقارير: {e}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_all_reports()
