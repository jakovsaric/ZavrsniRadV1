import sqlite3
from difflib import SequenceMatcher


# Function to calculate similarity between two strings
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Function to clear existing data from the database
def clear_data():
    conn = sqlite3.connect("productsV3.db")
    c = conn.cursor()
    c.execute("DELETE FROM productsCompared")
    conn.commit()
    conn.close()

# Connect to the database
conn = sqlite3.connect('productsV3.db')
cursor = conn.cursor()

# Create the productsCompared table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS productsCompared (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        screen_size TEXT,
        manufacturer TEXT,
        screen_type TEXT,
        tv_code TEXT,
        product_link TEXT,
        image_link TEXT,
        store TEXT,
        another_stores TEXT,
        stores_links TEXT
    )
''')

# Load all products from all tables
tables = ["productsSanctaDomenica", "productsInstar", "productsCentarTehnike"]
all_tvs = []

clear_data()

for table in tables:
    cursor.execute(f"SELECT * FROM {table}")
    all_tvs += cursor.fetchall()

# Compare TVs and store the results
processed = set()
for i, tv1 in enumerate(all_tvs):
    if i in processed:
        continue

    # Skip TVs with tv_code = "Unknown"
    if tv1[6] == "Unknown":
        cursor.execute('''
            INSERT INTO productsCompared (name, price, screen_size, manufacturer, screen_type, tv_code, product_link, image_link, store)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tv1[1], tv1[2], tv1[3], tv1[4], tv1[5], tv1[6], tv1[7], tv1[8], tv1[9]))
        processed.add(i)
        continue

    same_tvs = [tv1]
    for j, tv2 in enumerate(all_tvs):
        if i != j and j not in processed:
            # Check if one tv_code is a substring of another or if they have 100% similarity
            if tv1[6] in tv2[6] or tv2[6] in tv1[6] or similarity(tv1[6], tv2[6]) >= 1:
                same_tvs.append(tv2)
                processed.add(j)

    # Identify the TV with the lowest price
    same_tvs.sort(key=lambda x: x[2])
    main_tv = same_tvs[0]

    # Prepare values for another_stores and stores_links
    another_stores = ",".join(tv[9] for tv in same_tvs[1:])
    stores_links = ",".join(tv[7] for tv in same_tvs[1:])

    # Insert the result into productsCompared
    cursor.execute('''
        INSERT INTO productsCompared (name, price, screen_size, manufacturer, screen_type, 
        tv_code, product_link, image_link, store, another_stores, stores_links)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (main_tv[1], main_tv[2], main_tv[3], main_tv[4], main_tv[5], main_tv[6],
          main_tv[7], main_tv[8], main_tv[9],
          another_stores if another_stores else None, stores_links if stores_links else None))

    processed.add(i)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Comparing finished!")