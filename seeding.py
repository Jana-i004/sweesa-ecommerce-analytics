import mysql.connector
from mysql.connector import Error
from faker import Faker
from datetime import datetime, timedelta
import random

# Generate Saudi Arabic fake data
fake = Faker("ar_SA")

# Keep generated data consistent while testing
Faker.seed(42)
random.seed(42)

connection = None
cursor = None


# Categories data
categories = [
    ("الإلكترونيات", "أجهزة ومنتجات إلكترونية متنوعة"),
    ("الجوالات وملحقاتها", "هواتف ذكية وإكسسوارات الجوال"),
    ("الحاسب الآلي", "أجهزة الحاسب وملحقاتها"),
    ("المنزل والمطبخ", "منتجات منزلية وأجهزة للمطبخ"),
    ("العناية الشخصية", "منتجات العناية والجمال")
]


# Saudi cities
cities = [
    "الرياض",
    "جدة",
    "مكة المكرمة",
    "المدينة المنورة",
    "الدمام",
    "الخبر",
    "بريدة",
    "عنيزة",
    "أبها",
    "تبوك",
    "حائل",
    "جازان"
]


# Saudi mobile number prefixes
saudi_prefixes = [
    "050",
    "053",
    "054",
    "055",
    "056",
    "057",
    "058",
    "059"
]


# Products data
products = [

    # Electronics
    ("تلفزيون ذكي 55 بوصة", "تلفزيون ذكي بدقة عالية", 2199.00, 12, "الإلكترونيات"),
    ("سماعة لاسلكية", "سماعة لاسلكية بتقنية البلوتوث", 349.00, 3, "الإلكترونيات"),
    ("ساعة ذكية", "ساعة ذكية لمتابعة النشاط اليومي", 799.00, 18, "الإلكترونيات"),
    ("كاميرا رقمية", "كاميرا رقمية عالية الدقة", 1899.00, 6, "الإلكترونيات"),
    ("مكبر صوت بلوتوث", "مكبر صوت محمول لاسلكي", 249.00, 21, "الإلكترونيات"),
    ("جهاز لوحي 10 بوصة", "جهاز لوحي للاستخدام اليومي", 1299.00, 9, "الإلكترونيات"),
    ("قارئ إلكتروني", "قارئ رقمي للكتب الإلكترونية", 499.00, 2, "الإلكترونيات"),
    ("جهاز ألعاب محمول", "جهاز محمول للألعاب الإلكترونية", 1699.00, 7, "الإلكترونيات"),

    # Mobile phones and accessories
    ("هاتف ذكي 128GB", "هاتف ذكي بسعة تخزين 128 جيجابايت", 2299.00, 15, "الجوالات وملحقاتها"),
    ("هاتف ذكي 256GB", "هاتف ذكي بسعة تخزين 256 جيجابايت", 3099.00, 8, "الجوالات وملحقاتها"),
    ("شاحن سريع 65W", "شاحن سريع للأجهزة الذكية", 149.00, 30, "الجوالات وملحقاتها"),
    ("كابل USB-C", "كابل شحن ونقل بيانات", 59.00, 40, "الجوالات وملحقاتها"),
    ("غطاء حماية للجوال", "غطاء مقاوم للصدمات", 89.00, 25, "الجوالات وملحقاتها"),
    ("واقي شاشة", "واقي شاشة زجاجي", 49.00, 34, "الجوالات وملحقاتها"),
    ("باور بانك 20000mAh", "بطارية متنقلة عالية السعة", 199.00, 4, "الجوالات وملحقاتها"),
    ("حامل جوال للسيارة", "حامل جوال قابل للتعديل", 79.00, 16, "الجوالات وملحقاتها"),

    # Computers
    ("لابتوب 14 بوصة", "حاسب محمول للاستخدام الدراسي والعملي", 3599.00, 10, "الحاسب الآلي"),
    ("لابتوب 16 بوصة", "حاسب محمول بشاشة كبيرة", 4899.00, 5, "الحاسب الآلي"),
    ("فأرة لاسلكية", "فأرة لاسلكية مريحة", 129.00, 33, "الحاسب الآلي"),
    ("لوحة مفاتيح ميكانيكية", "لوحة مفاتيح للألعاب والعمل", 299.00, 17, "الحاسب الآلي"),
    ("شاشة 27 بوصة", "شاشة حاسب عالية الدقة", 1099.00, 11, "الحاسب الآلي"),
    ("قرص SSD 1TB", "وحدة تخزين سريعة بسعة 1 تيرابايت", 399.00, 14, "الحاسب الآلي"),
    ("حقيبة لابتوب", "حقيبة مبطنة لحماية الحاسب المحمول", 159.00, 3, "الحاسب الآلي"),
    ("كاميرا ويب HD", "كاميرا للاجتماعات والدراسة عن بعد", 219.00, 20, "الحاسب الآلي"),

    # Home and kitchen
    ("آلة قهوة", "آلة لتحضير القهوة المنزلية", 699.00, 9, "المنزل والمطبخ"),
    ("خلاط كهربائي", "خلاط متعدد الاستخدامات", 299.00, 13, "المنزل والمطبخ"),
    ("قلاية هوائية", "قلاية هوائية للطهي الصحي", 549.00, 8, "المنزل والمطبخ"),
    ("مكنسة كهربائية", "مكنسة كهربائية للاستخدام المنزلي", 899.00, 6, "المنزل والمطبخ"),
    ("غلاية كهربائية", "غلاية مياه سريعة", 149.00, 22, "المنزل والمطبخ"),
    ("محمصة خبز", "محمصة خبز كهربائية", 179.00, 18, "المنزل والمطبخ"),
    ("ميزان مطبخ", "ميزان رقمي لقياس مكونات الطعام", 89.00, 4, "المنزل والمطبخ"),
    ("طقم أواني طبخ", "مجموعة أواني للاستخدام اليومي", 449.00, 7, "المنزل والمطبخ"),

    # Personal care
    ("مجفف شعر", "مجفف شعر بعدة سرعات", 199.00, 16, "العناية الشخصية"),
    ("مكواة شعر", "مكواة لتصفيف الشعر", 249.00, 10, "العناية الشخصية"),
    ("ماكينة حلاقة", "ماكينة حلاقة كهربائية", 279.00, 12, "العناية الشخصية"),
    ("فرشاة تنظيف الوجه", "فرشاة كهربائية للعناية بالوجه", 169.00, 5, "العناية الشخصية"),
    ("جهاز مساج", "جهاز مساج منزلي محمول", 349.00, 3, "العناية الشخصية"),
    ("مرآة مضيئة", "مرآة مزودة بإضاءة للعناية الشخصية", 139.00, 19, "العناية الشخصية"),
    ("ميزان ذكي", "ميزان رقمي ذكي لقياس الوزن", 229.00, 8, "العناية الشخصية"),
    ("جهاز عناية بالبشرة", "جهاز منزلي للعناية بالبشرة", 399.00, 2, "العناية الشخصية")
]


# Return the first day of a month using a month offset
def get_month_start(base_date, months_back):
    month_number = (
        base_date.year * 12
        + base_date.month
        - 1
        - months_back
    )

    year = month_number // 12
    month = month_number % 12 + 1

    return datetime(year, month, 1)


try:

    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ENTER_YOUR_MYSQL_PASSWORD",
        database="sweesa_ecommerce_db",
        charset="utf8mb4"
    )

    cursor = connection.cursor()

    print("Connected to sweesa_ecommerce_db successfully!")


    # Clear old data before generating new data
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM customers")


    # Insert categories
    insert_category = """
        INSERT INTO categories
        (category_name, description)
        VALUES (%s, %s)
    """

    cursor.executemany(
        insert_category,
        categories
    )


    # Get category IDs
    cursor.execute("""
        SELECT category_id, category_name
        FROM categories
    """)

    category_map = {
        category_name: category_id
        for category_id, category_name in cursor.fetchall()
    }


    # Generate customers
    customers = []
    used_phones = set()

    today = datetime.now()

    # Customers are registered before the order period
    first_order_month = get_month_start(today, 6)

    registration_start = today - timedelta(days=730)
    registration_end = first_order_month - timedelta(days=1)

    registration_range = (
        registration_end - registration_start
    ).days


    for i in range(1, 151):

        # Generate a unique Saudi mobile number
        while True:

            prefix = random.choice(saudi_prefixes)

            phone = prefix + "".join(
                str(random.randint(0, 9))
                for _ in range(7)
            )

            if phone not in used_phones:
                used_phones.add(phone)
                break

        full_name = fake.name()

        # Generate a unique email
        email = f"customer{i:03d}@sweesa.example"

        # Generate a random registration date
        registration_date = (
            registration_start
            + timedelta(
                days=random.randint(
                    0,
                    registration_range
                )
            )
        ).date()

        city = random.choice(cities)

        customers.append(
            (
                full_name,
                email,
                phone,
                registration_date,
                city
            )
        )


    # Insert customers
    insert_customer = """
        INSERT INTO customers
        (
            full_name,
            email,
            phone,
            registration_date,
            city
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.executemany(
        insert_customer,
        customers
    )


    # Prepare products with category IDs
    product_rows = []

    for product in products:

        product_name = product[0]
        description = product[1]
        price = product[2]
        stock_quantity = product[3]
        category_name = product[4]

        category_id = category_map[category_name]

        product_rows.append(
            (
                product_name,
                description,
                price,
                stock_quantity,
                category_id
            )
        )


    # Insert products
    insert_product = """
        INSERT INTO products
        (
            product_name,
            description,
            price,
            stock_quantity,
            category_id
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.executemany(
        insert_product,
        product_rows
    )


    # Get customer IDs
    cursor.execute("""
        SELECT customer_id
        FROM customers
    """)

    customer_ids = [
        row[0]
        for row in cursor.fetchall()
    ]


    # Get product IDs and prices
    cursor.execute("""
        SELECT product_id, price
        FROM products
    """)

    product_data = cursor.fetchall()


    # Available order statuses
    order_statuses = [
        "قيد الانتظار",
        "تم الشحن",
        "تم التوصيل"
    ]


    # Create seven calendar month ranges
    month_ranges = []

    for months_back in range(6, -1, -1):

        month_start = get_month_start(
            today,
            months_back
        )

        if months_back == 0:
            month_end = today
        else:
            next_month_start = get_month_start(
                today,
                months_back - 1
            )

            month_end = (
                next_month_start
                - timedelta(seconds=1)
            )

        month_ranges.append(
            (
                month_start,
                month_end
            )
        )


    # Distribute 200 orders across all seven months
    month_indexes = [
        i % 7
        for i in range(200)
    ]

    random.shuffle(month_indexes)


    # Generate 200 orders
    for month_index in month_indexes:

        customer_id = random.choice(customer_ids)

        month_start, month_end = (
            month_ranges[month_index]
        )

        # Generate a random date inside the selected month
        available_seconds = int(
            (
                month_end
                - month_start
            ).total_seconds()
        )

        random_seconds = random.randint(
            0,
            available_seconds
        )

        order_date = (
            month_start
            + timedelta(
                seconds=random_seconds
            )
        )

        status = random.choice(
            order_statuses
        )


        # Insert order
        cursor.execute(
            """
            INSERT INTO orders
            (
                order_date,
                customer_id,
                status
            )
            VALUES (%s, %s, %s)
            """,
            (
                order_date,
                customer_id,
                status
            )
        )


        # Get the new order ID
        order_id = cursor.lastrowid


        # Select between 1 and 4 different products
        selected_products = random.sample(
            product_data,
            random.randint(1, 4)
        )


        # Insert order items
        for product_id, price in selected_products:

            quantity = random.randint(
                1,
                3
            )

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
            )


    # Save all changes
    connection.commit()


    # Count generated records
    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    orders_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM order_items"
    )

    order_items_count = cursor.fetchone()[0]


    # Print generated data summary
    print(
        f"Successfully inserted "
        f"{len(categories)} categories."
    )

    print(
        f"Successfully inserted "
        f"{len(customers)} customers."
    )

    print(
        f"Successfully inserted "
        f"{len(product_rows)} products."
    )

    print(
        f"Successfully inserted "
        f"{orders_count} orders."
    )

    print(
        f"Successfully inserted "
        f"{order_items_count} order items."
    )


except Error as e:

    # Undo changes if an error happens
    if connection:
        connection.rollback()

    print(f"Database error: {e}")


finally:

    # Close database resources
    if cursor:
        cursor.close()

    if connection and connection.is_connected():
        connection.close()
        print("Connection closed.")