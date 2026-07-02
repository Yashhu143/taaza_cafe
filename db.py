import os
import pymysql

# Helper to load .env variables
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()

load_env()

DEFAULT_MENU_ITEMS = [
    # TIFFINS (breakfast)
    {"id": "t1", "name": "Idli (2 Pieces)", "price": 30, "category": "breakfast", "description": "Soft steamed rice cakes served with sambar and traditional chutneys.", "image": "images/idly_vada.png"},
    {"id": "t2", "name": "Sambar Idli (2 Pieces)", "price": 50, "category": "breakfast", "description": "Soft idlis fully immersed in piping hot, delicious sambar.", "image": "images/idly_vada.png"},
    {"id": "t3", "name": "Rasam Idli (2 Pieces)", "price": 50, "category": "breakfast", "description": "Soft steamed idlis served immersed in hot, spicy pepper rasam.", "image": "images/idly_vada.png"},
    {"id": "t4", "name": "Ghee Karam Idli (2 Pieces)", "price": 55, "category": "breakfast", "description": "Steamed idlis smeared with spicy karam podi and pure ghee.", "image": "images/idly_vada.png"},
    {"id": "t5", "name": "Button Idli (12 Pieces)", "price": 60, "category": "breakfast", "description": "Twelve bite-sized mini idlis served floating in hot sambar.", "image": "images/idly_vada.png"},
    {"id": "t6", "name": "Idli (1 Pc) & Vada (1 Pc)", "price": 40, "category": "breakfast", "description": "A classic combo of one soft idli and one crispy medu vada.", "image": "images/idly_vada.png"},
    {"id": "t7", "name": "Idli (2 Pcs) & Vada (1 Pc)", "price": 55, "category": "breakfast", "description": "A satisfying breakfast combo of two soft idlis and one crispy medu vada.", "image": "images/idly_vada.png"},
    {"id": "t8", "name": "Bonda (2 Pieces)", "price": 25, "category": "breakfast", "description": "Crispy golden fried flour bonda dumplings seasoned with cumin.", "image": "images/mysore_bajji.png"},
    {"id": "t9", "name": "Vada (2 Pieces)", "price": 50, "category": "breakfast", "description": "Crispy, savory fried black gram donuts seasoned with peppercorns.", "image": "images/idly_vada.png"},
    {"id": "t10", "name": "Sambar Vada (2 Pieces)", "price": 60, "category": "breakfast", "description": "Savory lentil donuts soaked in spicy lentil sambar curry.", "image": "images/idly_vada.png"},
    {"id": "t11", "name": "Rasam Vada (2 Pieces)", "price": 60, "category": "breakfast", "description": "Crispy medu vadas dipped in hot, aromatic spicy rasam soup.", "image": "images/idly_vada.png"},
    {"id": "t12", "name": "Poori (2 Pieces)", "price": 50, "category": "breakfast", "description": "Puffed wheat flatbreads served with traditional potato curry.", "image": "images/poori_sabji.png"},
    {"id": "t13", "name": "Ragi Idli (2 Pieces)", "price": 50, "category": "breakfast", "description": "Nutritious finger-millet steamed cakes served with fresh chutneys.", "image": "images/idly_vada.png"},
    {"id": "t14", "name": "Upma", "price": 50, "category": "breakfast", "description": "Savory semolina porridge cooked with mustard seeds, nuts, and curry leaves.", "image": "images/mysore_bajji.png"},
    {"id": "t15", "name": "Pongal", "price": 50, "category": "breakfast", "description": "Comforting rice and lentil mash seasoned with black pepper, cumin, and ghee.", "image": "images/mysore_bajji.png"},
    {"id": "t16", "name": "Udala Kichidi", "price": 90, "category": "breakfast", "description": "Traditional semolina and vegetable kichidi cooked with spices.", "image": "images/lemon_rice.png"},
    {"id": "t17", "name": "Plain Dosa", "price": 50, "category": "breakfast", "description": "Crispy golden fermented crepe made of rice and lentils.", "image": "images/masala_dosa.png"},
    {"id": "t18", "name": "Masala Dosa", "price": 65, "category": "breakfast", "description": "Thin crispy crepe stuffed with seasoned potato mash.", "image": "images/masala_dosa.png"},
    {"id": "t19", "name": "Onion Dosa", "price": 75, "category": "breakfast", "description": "Crispy crepe topped with chopped raw onions and green chillies.", "image": "images/masala_dosa.png"},
    {"id": "t20", "name": "Onion Masala Dosa", "price": 80, "category": "breakfast", "description": "Crispy dosa layered with onions and stuffed with potato mash.", "image": "images/masala_dosa.png"},
    {"id": "t21", "name": "Pesarattu", "price": 70, "category": "breakfast", "description": "A green gram lentil crepe traditional to Andhra cuisine.", "image": "images/masala_dosa.png"},
    {"id": "t22", "name": "Onion Pesarattu", "price": 80, "category": "breakfast", "description": "Green gram crepe loaded with finely chopped fresh onions.", "image": "images/masala_dosa.png"},
    {"id": "t23", "name": "Upma Pesarattu", "price": 90, "category": "breakfast", "description": "Healthy green gram crepe stuffed with warm savory semolina upma.", "image": "images/masala_dosa.png"},
    {"id": "t24", "name": "Uttappa", "price": 85, "category": "breakfast", "description": "Thick rice pancake topped with onions and green coriander.", "image": "images/masala_dosa.png"},
    {"id": "t25", "name": "Upma Dosa", "price": 90, "category": "breakfast", "description": "Crispy dosa stuffed with a layer of delicious hot semolina upma.", "image": "images/masala_dosa.png"},
    {"id": "t26", "name": "Butter Paneer Dosa", "price": 90, "category": "breakfast", "description": "Golden crepe stuffed with paneer crumble and loaded with butter.", "image": "images/masala_dosa.png"},
    {"id": "t27", "name": "Ghee Karam Dosa", "price": 95, "category": "breakfast", "description": "Dosa smeared with hot red chilli chutney and rich melted ghee.", "image": "images/masala_dosa.png"},
    {"id": "t28", "name": "Cheese Dosa", "price": 95, "category": "breakfast", "description": "Crispy dosa loaded with grated melted cheddar cheese.", "image": "images/masala_dosa.png"},
    {"id": "t29", "name": "Set Dosa", "price": 95, "category": "breakfast", "description": "Set of three small, soft and spongy pancakes served with butter.", "image": "images/masala_dosa.png"},
    {"id": "t30", "name": "Ravva Dosa", "price": 95, "category": "breakfast", "description": "Super-crispy crepe made with semolina flour and buttermilk.", "image": "images/masala_dosa.png"},
    {"id": "t31", "name": "Korra Dosa", "price": 95, "category": "breakfast", "description": "Healthy millet-crepe made with foxtail millets.", "image": "images/masala_dosa.png"},
    {"id": "t32", "name": "Ragi Dosa", "price": 95, "category": "breakfast", "description": "Nutritious and high-fiber ragi (finger millet) crepe.", "image": "images/masala_dosa.png"},

    # RICES (mains)
    {"id": "m1", "name": "Jeera Rice", "price": 90, "category": "mains", "description": "Fragrant basmati rice seasoned with dry cumin seeds and coriander.", "image": "images/lemon_rice.png"},
    {"id": "m2", "name": "Tomato Rice", "price": 90, "category": "mains", "description": "Tangy rice dish flavored with fresh tomatoes, garlic, and spices.", "image": "images/lemon_rice.png"},
    {"id": "m3", "name": "Sambar Rice", "price": 90, "category": "mains", "description": "Comforting soft rice cooked with fresh vegetables and sambar.", "image": "images/lemon_rice.png"},
    {"id": "m4", "name": "Curd Rice", "price": 90, "category": "mains", "description": "Cool, comforting rice mixed with curd and tempered with mustard seeds.", "image": "images/lemon_rice.png"},
    {"id": "m5", "name": "Veg Biryani", "price": 90, "category": "mains", "description": "Spiced basmati rice layered with garden fresh vegetables.", "image": "images/lemon_rice.png"},
    {"id": "m6", "name": "Meals", "price": 150, "category": "mains", "description": "Full South Indian platter served with rice, dal, curries, sambar, and curd.", "image": "images/lemon_rice.png"},

    # BEVERAGES (beverages)
    {"id": "b1", "name": "Irani Chai", "price": 25, "category": "beverages", "description": "Slow-brewed thick tea, sweet, creamy, and traditional.", "image": "images/irani_chai.png"},
    {"id": "b2", "name": "Osmania Biscuits (1 Pc)", "price": 5, "category": "beverages", "description": "Traditional sweet-and-salt biscuit perfect with Irani Chai.", "image": "images/irani_chai.png"},
    {"id": "b3", "name": "Malai Bun", "price": 50, "category": "beverages", "description": "Soft sweet bun sliced and stuffed with rich fresh milk cream.", "image": "images/irani_chai.png"},
    {"id": "b4", "name": "Lemon Tea", "price": 25, "category": "beverages", "description": "Light black tea brewed with fresh lemon juice and mint.", "image": "images/irani_chai.png"},
    {"id": "b5", "name": "Green Tea", "price": 25, "category": "beverages", "description": "Mild and relaxing green tea leaves brewed to order.", "image": "images/irani_chai.png"},
    {"id": "b6", "name": "Filter Coffee", "price": 30, "category": "beverages", "description": "Authentic brass tumbler frothy South Indian chicory blend coffee.", "image": "images/filter_coffee.png"},
    {"id": "b7", "name": "Milk", "price": 30, "category": "beverages", "description": "Hot, pure pasteurized milk served warm with sugar.", "image": "images/filter_coffee.png"},
    {"id": "b8", "name": "Boost", "price": 35, "category": "beverages", "description": "Hot milk mixed with healthy, energy-boosting chocolate powder.", "image": "images/filter_coffee.png"},
    {"id": "b9", "name": "Badam Milk", "price": 35, "category": "beverages", "description": "Warm milk flavored with real crushed almonds and saffron.", "image": "images/filter_coffee.png"},
    {"id": "b10", "name": "Bournvita", "price": 35, "category": "beverages", "description": "Warm milk blended with classic chocolate Bournvita malt.", "image": "images/filter_coffee.png"},
    {"id": "b11", "name": "Horlicks", "price": 35, "category": "beverages", "description": "Hot milk whisked with nutritious Horlicks malted grain drink.", "image": "images/filter_coffee.png"},

    # SNACKS (snacks)
    {"id": "s1", "name": "Mirchi Bajji", "price": 45, "category": "snacks", "description": "Deep-fried green chili fritters stuffed with peanuts and onions.", "image": "images/mysore_bajji.png"},
    {"id": "s2", "name": "Masala Vada", "price": 45, "category": "snacks", "description": "Crunchy chana dal patties seasoned with dill leaves and spices.", "image": "images/idly_vada.png"},
    {"id": "s3", "name": "Punugulu", "price": 45, "category": "snacks", "description": "Crispy golden street-food dumplings made with dosa batter.", "image": "images/mysore_bajji.png"},

    # JUICES (juices)
    {"id": "j1", "name": "Watermelon Juice", "price": 50, "category": "juices", "description": "Freshly squeezed sweet watermelon juice, served chilled.", "image": "images/irani_chai.png"},
    {"id": "j2", "name": "Pineapple Juice", "price": 70, "category": "juices", "description": "Tangy and sweet fresh pineapple pulp juice.", "image": "images/irani_chai.png"},
    {"id": "j3", "name": "Black Grapes Juice", "price": 80, "category": "juices", "description": "Rich and sweet fresh black seedless grape juice.", "image": "images/irani_chai.png"},
    {"id": "j4", "name": "Pomegranate Juice", "price": 100, "category": "juices", "description": "Antioxidant-rich fresh pomegranate seed juice.", "image": "images/irani_chai.png"},
    {"id": "j5", "name": "Mosambi Juice", "price": 60, "category": "juices", "description": "Freshly squeezed sweet lime juice, rich in Vitamin C.", "image": "images/irani_chai.png"},
    {"id": "j6", "name": "Muskmelon Juice", "price": 70, "category": "juices", "description": "Thick and creamy sweet muskmelon juice.", "image": "images/irani_chai.png"},
    {"id": "j7", "name": "Papaya Juice", "price": 60, "category": "juices", "description": "Fresh papaya fruit blended into a refreshing cold drink.", "image": "images/irani_chai.png"},
    {"id": "j8", "name": "Apple Juice", "price": 100, "category": "juices", "description": "Pure pressed sweet red apple juice.", "image": "images/irani_chai.png"},
    {"id": "j9", "name": "Sapota Juice", "price": 80, "category": "juices", "description": "Creamy sapota (chikoo) milkshake style fresh juice.", "image": "images/irani_chai.png"},
    {"id": "j10", "name": "Kiwi Juice", "price": 120, "category": "juices", "description": "Fresh sweet-tart green kiwi fruit juice.", "image": "images/irani_chai.png"},
    {"id": "j11", "name": "Dragon Fruit Juice", "price": 120, "category": "juices", "description": "Exotic pink dragon fruit juice, served chilled.", "image": "images/irani_chai.png"},
    {"id": "j12", "name": "Lemon Juice", "price": 20, "category": "juices", "description": "Classic fresh limeade made with sugar, salt, and water.", "image": "images/irani_chai.png"},
    {"id": "j13", "name": "Banana Juice", "price": 50, "category": "juices", "description": "Creamy banana milkshake style fruit drink.", "image": "images/irani_chai.png"},
    {"id": "j14", "name": "Mango Juice", "price": 100, "category": "juices", "description": "Sweet, tropical fresh mango pulp juice.", "image": "images/irani_chai.png"},
    {"id": "j15", "name": "Avocado Juice", "price": 150, "category": "juices", "description": "Thick, rich, and creamy avocado shake.", "image": "images/irani_chai.png"},
    {"id": "j16", "name": "Sitaphal Juice", "price": 100, "category": "juices", "description": "Delicious seasonal custard apple fresh juice.", "image": "images/irani_chai.png"},
    {"id": "j17", "name": "Cocktail Juice", "price": 80, "category": "juices", "description": "Mixed fruit juice containing lime, orange, and pineapple.", "image": "images/irani_chai.png"},
    {"id": "j18", "name": "Ganga Jamuna", "price": 80, "category": "juices", "description": "Traditional blend of sweet lime (mosambi) and orange juice.", "image": "images/irani_chai.png"},
    {"id": "j19", "name": "ABC Juice", "price": 120, "category": "juices", "description": "Healthy detox blend of Apple, Beetroot, and Carrot juice.", "image": "images/irani_chai.png"},
    {"id": "j20", "name": "Apple Carrot", "price": 120, "category": "juices", "description": "Freshly blended sweet red apple and carrot juice.", "image": "images/irani_chai.png"},
    {"id": "j21", "name": "Apple Beetroot", "price": 120, "category": "juices", "description": "Earthy, sweet blend of fresh apple and beetroot juice.", "image": "images/irani_chai.png"},
    {"id": "j22", "name": "Beetroot Carrot", "price": 120, "category": "juices", "description": "Healthy mineral-rich carrot and beetroot juice blend.", "image": "images/irani_chai.png"},
    {"id": "j23", "name": "Strawberry Juice", "price": 120, "category": "juices", "description": "Sweet, blended fresh strawberries served cold.", "image": "images/irani_chai.png"},
    {"id": "j24", "name": "Fruit Bowl", "price": 100, "category": "juices", "description": "A fresh selection of cut seasonal fruits (apple, papaya, banana, grapes).", "image": "images/lemon_rice.png"}
]

def init_db():
    """Initializes the MySQL database, tables, and seeds the product list."""
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'taaza_cafe')

    # Step 1: Connect to server without database to create it if it doesn't exist
    conn = pymysql.connect(host=host, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    conn.commit()
    conn.close()

    # Step 2: Connect to the specific database to create tables
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')

    # Create menu_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price DOUBLE NOT NULL,
        category VARCHAR(50) NOT NULL,
        description TEXT,
        image VARCHAR(255)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')

    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id VARCHAR(50) PRIMARY KEY,
        user_id INT,
        customer_name VARCHAR(255) NOT NULL,
        customer_phone VARCHAR(50) NOT NULL,
        order_type VARCHAR(50) NOT NULL,
        table_number VARCHAR(50),
        total_amount DOUBLE NOT NULL,
        payment_status VARCHAR(50) DEFAULT 'pending',
        upi_utr VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')

    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id VARCHAR(50) NOT NULL,
        item_id VARCHAR(50) NOT NULL,
        item_name VARCHAR(255) NOT NULL,
        quantity INT NOT NULL,
        price DOUBLE NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')

    conn.commit()

    # Step 3: Seed default menu items if the table is empty
    cursor.execute("SELECT COUNT(*) as count FROM menu_items")
    count_res = cursor.fetchone()
    if count_res[0] == 0:
        print("Seeding default menu items into MySQL database...")
        for item in DEFAULT_MENU_ITEMS:
            cursor.execute(
                'INSERT INTO menu_items (id, name, price, category, description, image) VALUES (%s, %s, %s, %s, %s, %s)',
                (item['id'], item['name'], item['price'], item['category'], item['description'], item['image'])
            )
        conn.commit()
    else:
        # Self-healing migration: Ensure all existing records prepend 'images/' path
        cursor.execute("UPDATE menu_items SET image = CONCAT('images/', image) WHERE image NOT LIKE 'images/%' AND image IS NOT NULL AND image != ''")
        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    print("MySQL Database and Tables initialized successfully.")
