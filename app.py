"""
sweesa_ecommerce_db - Streamlit CRUD Panel
==========================================

The dashboard supports:
- Live metrics and charts
- Add products
- Update prices and stock
- Update or delete orders
- Product recommendation system
- Excel report export

Run with:
streamlit run app.py
"""

import io

import streamlit as st
import pandas as pd
import plotly.express as px
from mysql.connector import Error
from sqlalchemy import text

from db_config import get_connection, get_engine
from recommendations import (
    load_order_items,
    build_pivot_table,
    compute_product_correlation,
    top_3_recommendations,
)


ORDER_STATUSES = ["قيد الانتظار", "تم الشحن", "تم التوصيل"]


st.set_page_config(
    page_title="Sweesa E-Commerce | لوحة التحكم",
    page_icon="🛍️",
    layout="wide",
)


# Visual style
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
    }

    .stApp {
        background-color: #F6F8F6;
    }

    [data-testid="stSidebar"] {
        background-color: #EAF1EC;
        border-left: 1px solid #D7E4DC;
    }

    [data-testid="stSidebar"] h1 {
        color: #2B5D50;
        font-weight: 800;
    }

    h1, h2, h3 {
        color: #2B5D50;
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E1E8E4;
        border-right: 5px solid #3A7D6E;
        border-radius: 14px;
        padding: 18px 16px;
        box-shadow: 0 2px 8px rgba(43, 93, 80, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #5C6F68;
        font-weight: 500;
    }

    [data-testid="stMetricValue"] {
        color: #2B5D50;
        font-weight: 800;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background-color: #3A7D6E;
        color: #FFFFFF;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        padding: 0.55rem 1rem;
        transition: background-color 0.15s ease-in-out;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #E8A23B;
        color: #2B3A36;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E1E8E4;
    }

    input, textarea, select {
        font-family: 'Tajawal', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Database helpers
def run_query(query):
    """Run a SELECT query and return a DataFrame."""
    engine = get_engine()

    if engine is None:
        st.error("❌ تعذّر الاتصال بقاعدة البيانات.")
        return pd.DataFrame()

    try:
        return pd.read_sql(text(query), engine)

    except Exception as e:
        st.error(f"❌ خطأ في الاستعلام: {e}")
        return pd.DataFrame()

    finally:
        engine.dispose()


def run_action(query, params=None):
    """Run INSERT, UPDATE or DELETE queries."""
    conn = get_connection()

    if conn is None:
        return False, "تعذّر الاتصال بقاعدة البيانات"

    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return True, "تمت العملية بنجاح"

    except Error as e:
        conn.rollback()
        return False, f"حدث خطأ: {e}"

    finally:
        if cursor:
            cursor.close()

        if conn.is_connected():
            conn.close()


def create_excel_report(
    kpi_df,
    orders_over_time,
    products_by_category,
    low_stock,
):
    """Create an Excel report from dashboard data."""

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        if not kpi_df.empty:

            summary_df = pd.DataFrame(
                {
                    "المؤشر": [
                        "إجمالي الأرباح",
                        "عدد المنتجات",
                        "عدد الطلبات",
                        "عدد العملاء",
                    ],
                    "القيمة": [
                        kpi_df["total_revenue"].iloc[0],
                        kpi_df["total_products"].iloc[0],
                        kpi_df["total_orders"].iloc[0],
                        kpi_df["total_customers"].iloc[0],
                    ],
                }
            )

            summary_df.to_excel(
                writer,
                sheet_name="Summary",
                index=False,
            )

        orders_over_time.to_excel(
            writer,
            sheet_name="Orders_Over_Time",
            index=False,
        )

        products_by_category.to_excel(
            writer,
            sheet_name="Products_By_Category",
            index=False,
        )

        low_stock.to_excel(
            writer,
            sheet_name="Low_Stock",
            index=False,
        )

    return output.getvalue()


# Sidebar
st.sidebar.title("🛍️ Sweesa Admin Panel")

page = st.sidebar.radio(
    "التنقل",
    [
        "📊 لوحة العرض",
        "➕ إدخال المنتجات",
        "✏️ تعديل الأسعار والمخزون",
        "📦 إدارة الطلبات",
        "💡 نظام التوصيات",
    ],
)


# Dashboard
if page == "📊 لوحة العرض":

    st.title("📊 لوحة العرض الحية")

    kpi_df = run_query(
        """
        SELECT
            (SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
             FROM order_items oi) AS total_revenue,

            (SELECT COUNT(*) FROM products) AS total_products,

            (SELECT COUNT(*) FROM orders) AS total_orders,

            (SELECT COUNT(*) FROM customers) AS total_customers
        """
    )

    if not kpi_df.empty:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💰 إجمالي الأرباح",
            f"{kpi_df['total_revenue'].iloc[0]:,.2f} ريال",
        )

        col2.metric(
            "📦 عدد المنتجات",
            int(kpi_df["total_products"].iloc[0]),
        )

        col3.metric(
            "🧾 عدد الطلبات",
            int(kpi_df["total_orders"].iloc[0]),
        )

        col4.metric(
            "👥 عدد العملاء",
            int(kpi_df["total_customers"].iloc[0]),
        )

    st.divider()

    st.subheader("📌 عدد الطلبات حسب الحالة")

    status_counts_df = run_query(
        """
        SELECT status, COUNT(*) AS status_count
        FROM orders
        GROUP BY status
        """
    )

    status_counts_map = (
        dict(
            zip(
                status_counts_df["status"],
                status_counts_df["status_count"],
            )
        )
        if not status_counts_df.empty
        else {}
    )

    scol1, scol2, scol3 = st.columns(3)

    scol1.metric(
        "⏳ قيد الانتظار",
        int(status_counts_map.get("قيد الانتظار", 0)),
    )

    scol2.metric(
        "🚚 تم الشحن",
        int(status_counts_map.get("تم الشحن", 0)),
    )

    scol3.metric(
        "✅ تم التوصيل",
        int(status_counts_map.get("تم التوصيل", 0)),
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("📈 حركة الطلبات عبر الوقت")

        orders_over_time = run_query(
            """
            SELECT
                DATE(order_date) AS order_day,
                COUNT(*) AS orders_count
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY order_day
            """
        )

        if not orders_over_time.empty:

            fig = px.line(
                orders_over_time,
                x="order_day",
                y="orders_count",
                markers=True,
                labels={
                    "order_day": "التاريخ",
                    "orders_count": "عدد الطلبات",
                },
            )

            st.plotly_chart(
                fig,
                width="stretch",
            )

        else:
            st.info("لا توجد بيانات طلبات بعد.")

    with c2:

        st.subheader("🗂️ عدد المنتجات حسب القسم")

        products_by_category = run_query(
            """
            SELECT
                c.category_name,
                COUNT(p.product_id) AS product_count
            FROM categories c
            LEFT JOIN products p
                ON p.category_id = c.category_id
            GROUP BY c.category_name
            ORDER BY product_count DESC
            """
        )

        if not products_by_category.empty:

            fig2 = px.bar(
                products_by_category,
                x="category_name",
                y="product_count",
                labels={
                    "category_name": "القسم",
                    "product_count": "عدد المنتجات",
                },
            )

            st.plotly_chart(
                fig2,
                width="stretch",
            )

        else:
            st.info("لا توجد بيانات أقسام بعد.")

    st.divider()

    st.subheader("⚠️ منتجات أوشكت على النفاد (أقل من 5 قطع)")

    low_stock = run_query(
        """
        SELECT
            p.product_name AS "اسم المنتج",
            c.category_name AS "القسم",
            p.stock_quantity AS "الكمية المتبقية"
        FROM products p
        JOIN categories c
            ON c.category_id = p.category_id
        WHERE p.stock_quantity < 5
        ORDER BY p.stock_quantity ASC
        """
    )

    if not low_stock.empty:

        st.dataframe(
            low_stock,
            width="stretch",
            hide_index=True,
        )

    else:
        st.success("لا توجد منتجات على وشك النفاد 🎉")

    st.divider()

    st.subheader("📥 تصدير تقرير لوحة العرض")

    try:

        excel_report = create_excel_report(
            kpi_df,
            orders_over_time,
            products_by_category,
            low_stock,
        )

        st.download_button(
            label="📊 تحميل التقرير بصيغة Excel",
            data=excel_report,
            file_name="sweesa_dashboard_report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            width="stretch",
        )

    except Exception as e:

        st.error(
            f"❌ تعذّر إنشاء تقرير Excel: {e}"
        )


# Add product
elif page == "➕ إدخال المنتجات":

    st.title("➕ إضافة منتج جديد")

    categories_df = run_query(
        """
        SELECT category_id, category_name
        FROM categories
        ORDER BY category_name
        """
    )

    if categories_df.empty:

        st.warning("لا توجد أقسام في قاعدة البيانات.")

    else:

        with st.form(
            "add_product_form",
            clear_on_submit=True,
        ):

            col1, col2 = st.columns(2)

            with col1:

                product_name = st.text_input(
                    "اسم المنتج *"
                )

                price = st.number_input(
                    "السعر (ريال) *",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                )

            with col2:

                category_name = st.selectbox(
                    "القسم *",
                    categories_df["category_name"],
                )

                stock_quantity = st.number_input(
                    "الكمية بالمخزون *",
                    min_value=0,
                    step=1,
                )

            description = st.text_area(
                "الوصف"
            )

            submitted = st.form_submit_button(
                "💾 حفظ المنتج",
                width="stretch",
            )

            if submitted:

                if not product_name.strip():

                    st.error(
                        "الرجاء إدخال اسم المنتج."
                    )

                else:

                    category_id = int(
                        categories_df.loc[
                            categories_df[
                                "category_name"
                            ] == category_name,
                            "category_id",
                        ].iloc[0]
                    )

                    success, message = run_action(
                        """
                        INSERT INTO products
                            (
                                product_name,
                                description,
                                price,
                                stock_quantity,
                                category_id
                            )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            product_name.strip(),
                            description.strip(),
                            price,
                            stock_quantity,
                            category_id,
                        ),
                    )

                    if success:

                        st.success(
                            f'✅ {message}: تمت إضافة '
                            f'"{product_name}" بنجاح.'
                        )

                        st.balloons()

                    else:

                        st.error(
                            f"❌ {message}"
                        )

    st.divider()

    st.subheader(
        "📋 آخر المنتجات المضافة"
    )

    latest_products = run_query(
        """
        SELECT
            product_id AS "المعرّف",
            product_name AS "اسم المنتج",
            price AS "السعر",
            stock_quantity AS "المخزون"
        FROM products
        ORDER BY product_id DESC
        LIMIT 10
        """
    )

    if not latest_products.empty:

        st.dataframe(
            latest_products,
            width="stretch",
            hide_index=True,
        )


# Update price and stock
elif page == "✏️ تعديل الأسعار والمخزون":

    st.title(
        "✏️ تعديل الأسعار والمخزون"
    )

    products_df = run_query(
        """
        SELECT
            p.product_id,
            p.product_name,
            p.price,
            p.stock_quantity,
            c.category_name
        FROM products p
        JOIN categories c
            ON c.category_id = p.category_id
        ORDER BY p.product_name
        """
    )

    if products_df.empty:

        st.info(
            "لا توجد منتجات بعد."
        )

    else:

        search = st.text_input(
            "🔍 ابحثي عن منتج بالاسم"
        )

        filtered = (
            products_df[
                products_df["product_name"]
                .str.contains(
                    search,
                    case=False,
                    na=False,
                )
            ]
            if search
            else products_df
        )

        if filtered.empty:

            st.warning(
                "لا يوجد منتج مطابق للبحث."
            )

        else:

            selected_name = st.selectbox(
                "اختاري المنتج",
                filtered[
                    "product_name"
                ].tolist(),
            )

            row = products_df[
                products_df["product_name"]
                == selected_name
            ].iloc[0]

            st.caption(
                f"القسم: {row['category_name']} | "
                f"المعرّف: {row['product_id']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                new_price = st.number_input(
                    "السعر الجديد (ريال)",
                    min_value=0.0,
                    step=0.01,
                    value=float(
                        row["price"]
                    ),
                    format="%.2f",
                )

            with col2:

                new_stock = st.number_input(
                    "الكمية الجديدة بالمخزون",
                    min_value=0,
                    step=1,
                    value=int(
                        row["stock_quantity"]
                    ),
                )

            if st.button(
                "💾 حفظ التعديلات",
                width="stretch",
            ):

                success, message = run_action(
                    """
                    UPDATE products
                    SET
                        price = %s,
                        stock_quantity = %s
                    WHERE product_id = %s
                    """,
                    (
                        new_price,
                        new_stock,
                        int(
                            row["product_id"]
                        ),
                    ),
                )

                if success:

                    st.success(
                        f'✅ {message}: تم تحديث '
                        f'"{selected_name}".'
                    )

                    st.rerun()

                else:

                    st.error(
                        f"❌ {message}"
                    )

    st.divider()

    st.subheader(
        "📋 جميع المنتجات"
    )

    if not products_df.empty:

        display_df = products_df.rename(
            columns={
                "product_id": "المعرّف",
                "product_name": "اسم المنتج",
                "price": "السعر",
                "stock_quantity": "المخزون",
                "category_name": "القسم",
            }
        )

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
        )


# Manage orders
elif page == "📦 إدارة الطلبات":

    st.title(
        "📦 إدارة الطلبات"
    )

    orders_df = run_query(
        """
        SELECT
            o.order_id,
            o.order_date,
            c.full_name,
            o.status
        FROM orders o
        JOIN customers c
            ON c.customer_id = o.customer_id
        ORDER BY o.order_date DESC
        LIMIT 200
        """
    )

    if orders_df.empty:

        st.info(
            "لا توجد طلبات بعد."
        )

    else:

        st.subheader(
            "🔍 البحث والفلترة"
        )

        col_search, col_status = st.columns(2)

        with col_search:

            search_order = st.text_input(
                "ابحثي برقم الطلب أو اسم العميل"
            )

        with col_status:

            status_filter = st.selectbox(
                "فلترة حسب حالة الطلب",
                ["الكل"] + ORDER_STATUSES,
            )

        filtered_orders = orders_df.copy()

        if search_order:

            search_order = search_order.strip()

            name_match = filtered_orders[
                "full_name"
            ].str.contains(
                search_order,
                case=False,
                na=False,
                regex=False,
            )

            id_match = (
                filtered_orders[
                    "order_id"
                ]
                .astype(str)
                .str.contains(
                    search_order,
                    regex=False,
                )
            )

            filtered_orders = filtered_orders[
                name_match | id_match
            ]

        if status_filter != "الكل":

            filtered_orders = filtered_orders[
                filtered_orders["status"]
                == status_filter
            ]

        display_df = filtered_orders.rename(
            columns={
                "order_id": "رقم الطلب",
                "order_date": "تاريخ الطلب",
                "full_name": "العميل",
                "status": "الحالة",
            }
        )

        if filtered_orders.empty:

            st.warning(
                "لا توجد طلبات مطابقة "
                "لخيارات البحث والفلترة."
            )

        else:

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
            )

            st.caption(
                f"عدد الطلبات الظاهرة: "
                f"{len(filtered_orders)}"
            )

            st.divider()

            st.subheader(
                "تعديل / إلغاء طلب"
            )

            order_options = filtered_orders.apply(
                lambda r:
                    f"#{r['order_id']} - "
                    f"{r['full_name']} "
                    f"({r['status']})",
                axis=1,
            )

            selected = st.selectbox(
                "اختاري الطلب",
                order_options.tolist(),
            )

            selected_order_id = int(
                selected.split(" ")[0]
                .replace("#", "")
            )

            current_status = (
                filtered_orders.loc[
                    filtered_orders["order_id"]
                    == selected_order_id,
                    "status",
                ].iloc[0]
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "**تحديث حالة الطلب**"
                )

                new_status = st.selectbox(
                    "الحالة الجديدة",
                    ORDER_STATUSES,
                    index=ORDER_STATUSES.index(
                        current_status
                    ),
                )

                if st.button(
                    "💾 حفظ الحالة",
                    width="stretch",
                ):

                    success, message = run_action(
                        """
                        UPDATE orders
                        SET status = %s
                        WHERE order_id = %s
                        """,
                        (
                            new_status,
                            selected_order_id,
                        ),
                    )

                    if success:

                        st.success(
                            f"✅ {message}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"❌ {message}"
                        )

            with col2:

                st.markdown(
                    "**إلغاء / حذف الطلب**"
                )

                st.caption(
                    "سيتم حذف الطلب "
                    "وكل عناصره نهائيًا."
                )

                confirm = st.checkbox(
                    f"أؤكد حذف الطلب رقم "
                    f"#{selected_order_id}"
                )

                if st.button(
                    "🗑️ حذف الطلب",
                    width="stretch",
                    disabled=not confirm,
                ):

                    success, message = run_action(
                        """
                        DELETE FROM orders
                        WHERE order_id = %s
                        """,
                        (
                            selected_order_id,
                        ),
                    )

                    if success:

                        st.success(
                            f"✅ {message}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"❌ {message}"
                        )


# Recommendation system
elif page == "💡 نظام التوصيات":

    st.title(
        "💡 نظام التوصيات الذكي"
    )

    st.write(
        "اختاري منتجًا لعرض أعلى 3 "
        "منتجات مرتبطة به بناءً على "
        "أنماط الشراء السابقة."
    )

    engine = get_engine()

    if engine is None:

        st.error(
            "❌ تعذّر الاتصال بقاعدة البيانات."
        )

    else:

        try:

            order_items_df = load_order_items(
                engine
            )

            if order_items_df.empty:

                st.info(
                    "لا توجد بيانات كافية "
                    "لبناء التوصيات."
                )

            else:

                pivot = build_pivot_table(
                    order_items_df
                )

                corr_matrix = (
                    compute_product_correlation(
                        pivot
                    )
                )

                if corr_matrix.empty:

                    st.info(
                        "لا توجد بيانات كافية "
                        "لحساب الارتباط."
                    )

                else:

                    selected_product = st.selectbox(
                        "🛍️ اختاري المنتج",
                        sorted(
                            corr_matrix.columns.tolist()
                        ),
                    )

                    recommendations = (
                        top_3_recommendations(
                            corr_matrix,
                            selected_product,
                        )
                        .dropna()
                    )

                    st.subheader(
                        f"أعلى 3 منتجات مقترحة مع: "
                        f"{selected_product}"
                    )

                    if recommendations.empty:

                        st.info(
                            "لا توجد توصيات كافية "
                            "لهذا المنتج."
                        )

                    else:

                        recommendations_df = (
                            recommendations
                            .rename(
                                "correlation"
                            )
                            .reset_index()
                        )

                        recommendations_df.columns = [
                            "المنتج المقترح",
                            "معامل الارتباط",
                        ]

                        recommendations_df[
                            "معامل الارتباط"
                        ] = recommendations_df[
                            "معامل الارتباط"
                        ].round(3)

                        st.dataframe(
                            recommendations_df,
                            width="stretch",
                            hide_index=True,
                        )

        except Exception as e:

            st.error(
                f"❌ حدث خطأ أثناء تشغيل "
                f"نظام التوصيات: {e}"
            )

        finally:

            engine.dispose()