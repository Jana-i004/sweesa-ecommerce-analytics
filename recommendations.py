"""
recommendations.py
تحليلات متقدمة باستخدام Pandas + نظام توصيات بسيط (Item-based).

الخطوات:
1. سحب بيانات order_items (مع أسماء المنتجات) باستخدام Pandas.
2. إنشاء Pivot Table بين الطلبات (orders) والمنتجات (products) — الكمية المشتراة.
3. حساب معامل الارتباط (Correlation) بين المنتجات بناءً على أنماط الشراء المشتركة.
4. اقتراح أعلى 3 منتجات مرتبطة بمنتج معيّن (منتجات غالباً ما تُشترى معه).
"""

import pandas as pd
from sqlalchemy import text
from db_config import get_engine


def load_order_items(engine):
    """
    سحب بيانات order_items مع اسم المنتج ورقم الطلب باستخدام Pandas.
    """
    query = """
        SELECT
            oi.order_id,
            oi.product_id,
            p.product_name,
            oi.quantity,
            oi.unit_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id;
    """
    try:
        df = pd.read_sql(text(query), engine)
        return df
    except Exception as e:
        print(f"❌ خطأ في سحب بيانات order_items: {e}")
        return pd.DataFrame()


def build_pivot_table(order_items_df: pd.DataFrame) -> pd.DataFrame:
    """
    إنشاء Pivot Table:
        الصفوف   -> order_id
        الأعمدة  -> product_name
        القيم    -> إجمالي الكمية المشتراة (0 إن لم يُشترَ المنتج ضمن الطلب)
    """
    if order_items_df.empty:
        return pd.DataFrame()

    pivot = order_items_df.pivot_table(
        index="order_id",
        columns="product_name",
        values="quantity",
        aggfunc="sum",
        fill_value=0,
    )
    return pivot


def compute_product_correlation(pivot: pd.DataFrame) -> pd.DataFrame:
    """
    حساب معامل الارتباط (Pearson Correlation) بين المنتجات
    بناءً على أنماط الشراء المشتركة عبر الطلبات.
    """
    if pivot.empty:
        return pd.DataFrame()

    return pivot.corr()


def top_3_recommendations(corr_matrix: pd.DataFrame, product_name: str) -> pd.Series:
    """
    إرجاع أعلى 3 منتجات مرتبطة (Correlation) بمنتج معيّن — أي المنتجات
    التي يميل العملاء لشرائها معه.
    """
    if corr_matrix.empty or product_name not in corr_matrix.columns:
        return pd.Series(dtype=float)

    correlations = corr_matrix[product_name].drop(labels=[product_name])
    return correlations.sort_values(ascending=False).head(3)


def run_recommendation_pipeline():
    engine = get_engine()
    if engine is None:
        print("تعذر تشغيل نظام التوصيات بسبب فشل الاتصال بقاعدة البيانات.")
        return

    try:
        order_items_df = load_order_items(engine)
        if order_items_df.empty:
            print("لا توجد بيانات order_items لعرضها.")
            return

        print("=" * 60)
        print("🧾 عيّنة من بيانات order_items")
        print("=" * 60)
        print(order_items_df.head(10).to_string(index=False))

        pivot = build_pivot_table(order_items_df)
        print("\n" + "=" * 60)
        print("📐 Pivot Table (الطلبات × المنتجات) — عيّنة")
        print("=" * 60)
        print(pivot.head(10).to_string())

        corr_matrix = compute_product_correlation(pivot)
        print("\n" + "=" * 60)
        print("🔗 مصفوفة الارتباط (Correlation) بين المنتجات — عيّنة")
        print("=" * 60)
        print(corr_matrix.iloc[:5, :5].round(2).to_string())

        # اختيار أكثر منتج مبيعاً كمثال لعرض التوصيات
        best_selling_product = (
            order_items_df.groupby("product_name")["quantity"].sum().idxmax()
        )

        print("\n" + "=" * 60)
        print(f"💡 أعلى 3 منتجات مقترحة مع: {best_selling_product}")
        print("=" * 60)
        recommendations = top_3_recommendations(corr_matrix, best_selling_product)
        if recommendations.empty:
            print("لا توجد توصيات كافية (البيانات غير كافية لحساب الارتباط).")
        else:
            print(recommendations.round(3).to_string())

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء تشغيل نظام التوصيات: {e}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_recommendation_pipeline()
