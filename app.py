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
    }

    sort_by, order = sort_options.get(sort_option, ('id', 'asc'))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM productsSanctaDomenica ORDER BY {sort_by} {order}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return render_template('index.html', rows=rows, sort_option=sort_option)

if __name__ == "__main__":
    app.run(debug=True)

