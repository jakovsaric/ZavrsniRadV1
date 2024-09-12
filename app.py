from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Path to your database (relative to the location of app.py)
DATABASE = r'productsV3.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=['GET'])
def index():
    sort_option = request.args.get('sort_option', 'id_asc')
    selected_manufacturer = request.args.get('manufacturer', 'All')

    sort_options = {
        'id_asc': ('id', 'asc'),
        'id_desc': ('id', 'desc'),
        'name_asc': ('name', 'asc'),
        'name_desc': ('name', 'desc'),
        'price_asc': ('price', 'asc'),
        'price_desc': ('price', 'desc'),
        'screen_size_asc': ('screen_size', 'asc'),
        'screen_size_desc': ('screen_size', 'desc'),
        'manufacturer_asc': ('manufacturer', 'asc'),
        'manufacturer_desc': ('manufacturer', 'desc'),
        'screen_type_asc': ('screen_type', 'asc'),
        'screen_type_desc': ('screen_type', 'desc'),
        'tv_code_asc': ('tv_code', 'asc'),
        'tv_code_desc': ('tv_code', 'desc'),
        'store_asc': ('store', 'asc'),
        'store_desc': ('store', 'desc'),
    }

    sort_by, order = sort_options.get(sort_option, ('id', 'asc'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the list of manufacturers for the dropdown filter
    cursor.execute("SELECT DISTINCT manufacturer FROM productsCompared")
    manufacturers = cursor.fetchall()

    # Prepare the query with an optional manufacturer filter
    query = f"SELECT * FROM productsCompared WHERE 1=1"

    if selected_manufacturer and selected_manufacturer != 'All':
        query += f" AND manufacturer = ?"
        cursor.execute(query + f" ORDER BY {sort_by} {order}", (selected_manufacturer,))
    else:
        cursor.execute(query + f" ORDER BY {sort_by} {order}")

    rows = cursor.fetchall()
    conn.close()

    # Pre-process another_stores and stores_links
    processed_rows = []
    for row in rows:
        row_dict = dict(row)
        if row_dict['another_stores'] and row_dict['stores_links']:
            # Split the another_stores and stores_links by ', '
            stores = row_dict['another_stores'].split(',')
            links = row_dict['stores_links'].split(',')
            # Zip them together
            row_dict['store_link_pairs'] = list(zip(stores, links))
        else:
            row_dict['store_link_pairs'] = []
        processed_rows.append(row_dict)

    return render_template('index.html', rows=processed_rows, sort_option=sort_option, manufacturers=manufacturers,
                           selected_manufacturer=selected_manufacturer)


if __name__ == "__main__":
    app.run(debug=True)
