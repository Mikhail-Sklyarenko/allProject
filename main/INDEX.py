from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask_bcrypt import Bcrypt

# Создаем экземпляр Flask-приложения и подключаем модуль Bcrypt для хэширования паролей
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Секретный ключ для шифрования сессий (замените на более сложный)
bcrypt = Bcrypt(app)

# Имя файла базы данных SQLite
DB_FILE = 'store.db'

# Функция подключения к базе данных
# Позволяет подключаться к SQLite базе данных и возвращать соединение
# conn.row_factory делает строки базы данных похожими на словари для удобства работы

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Преобразуем строки базы данных в словари
    return conn

# Инициализация базы данных
# Создает необходимые таблицы (если они не существуют)

def init_db():
    conn = get_db_connection()
    with conn:
        # Таблица для хранения информации о товарах
        conn.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор товара
            name TEXT NOT NULL,  # Название товара
            description TEXT NOT NULL,  # Описание товара
            composition TEXT,  # Состав товара
            recommendations TEXT,  # Рекомендации по применению
            price REAL NOT NULL,  # Цена товара
            stock INTEGER NOT NULL,  # Количество товара на складе
            age_restriction INTEGER DEFAULT 0,  # Ограничение по возрасту (например, 18+)
            image_url TEXT  # Ссылка на изображение товара
        )''')
        # Таблица для хранения данных о заказах
        conn.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор заказа
            user_id INTEGER NOT NULL,  # Идентификатор пользователя, оформившего заказ
            total REAL NOT NULL,  # Общая стоимость заказа
            payment_method TEXT NOT NULL,  # Способ оплаты
            delivery_method TEXT NOT NULL,  # Способ доставки (например, курьер, самовывоз)
            address TEXT NOT NULL,  # Адрес доставки
            status TEXT DEFAULT 'Pending'  # Статус заказа (по умолчанию "в ожидании")
        )''')
        # Таблица для отзывов о товарах
        conn.execute('''CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор отзыва
            product_id INTEGER NOT NULL,  # Идентификатор товара, к которому относится отзыв
            user_id INTEGER NOT NULL,  # Идентификатор пользователя, оставившего отзыв
            review_text TEXT,  # Текст отзыва
            rating INTEGER  # Рейтинг (например, от 1 до 5)
        )''')
        # Таблица для избранных товаров
        conn.execute('''CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор избранного
            user_id INTEGER NOT NULL,  # Идентификатор пользователя
            product_id INTEGER NOT NULL  # Идентификатор товара
        )''')
        # Таблица для пользователей
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор пользователя
            username TEXT NOT NULL UNIQUE,  # Уникальное имя пользователя (логин)
            password TEXT NOT NULL,  # Хэшированный пароль
            is_admin INTEGER DEFAULT 0  # Флаг администратора (0 - обычный пользователь, 1 - администратор)
        )''')
    conn.close()  # Закрываем соединение с базой данных

# Инициализация базы данных при запуске приложения
init_db()

# Главная страница
@app.route('/')
def index():
    # Получаем значение возрастного ограничения из сессии пользователя (по умолчанию 0)
    age_restriction = session.get('age_restriction', 0)
    conn = get_db_connection()
    # Получаем товары из базы данных, которые подходят под возрастное ограничение
    products = conn.execute(
        'SELECT * FROM products WHERE age_restriction <= ?', (age_restriction,)
    ).fetchall()
    conn.close()
    # Передаем список товаров в шаблон index.html для отображения
    return render_template('index.html', products=products)

# Страница с информацией о товаре
@app.route('/product/<int:product_id>')
def product(product_id):
    conn = get_db_connection()
    # Получаем данные о конкретном товаре из базы данных по его идентификатору
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    # Получаем отзывы, оставленные для этого товара
    reviews = conn.execute('SELECT * FROM reviews WHERE product_id = ?', (product_id,)).fetchall()
    conn.close()
    if product is None:
        # Если товар не найден, возвращаем ошибку 404
        return "Товар не найден", 404
    # Передаем данные о товаре и отзывы в шаблон product.html
    return render_template('product.html', product=product, reviews=reviews)

# Добавление товара в список избранного
@app.route('/favorite/<int:product_id>', methods=['POST'])
def favorite(product_id):
    # Проверяем, авторизован ли пользователь (должен быть user_id в сессии)
    user_id = session.get('user_id')
    if user_id is None:
        # Если пользователь не авторизован, перенаправляем его на страницу входа
        return redirect(url_for('login'))
    conn = get_db_connection()
    # Добавляем товар в таблицу избранных товаров для текущего пользователя
    conn.execute('INSERT INTO favorites (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    conn.commit()
    conn.close()
    # Возвращаем пользователя на страницу товара после добавления в избранное
    return redirect(url_for('product', product_id=product_id))

# Страница корзины покупок
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    # Если корзина отсутствует в сессии, инициализируем её как пустой список
    if 'cart' not in session:
        session['cart'] = []
    if request.method == 'POST':
        # Получаем идентификатор добавляемого товара из формы
        product_id = int(request.form['product_id'])
        # Добавляем товар в корзину (сохраняется в сессии)
        session['cart'].append(product_id)
    conn = get_db_connection()
    # Получаем информацию о товарах, добавленных в корзину, из базы данных
    cart_products = [
        conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        for product_id in session['cart']
    ]
    conn.close()
    # Рассчитываем общую стоимость товаров в корзине
    total = sum(product['price'] for product in cart_products if product)
    # Передаем данные о товарах и общей стоимости в шаблон cart.html
    return render_template('cart.html', cart=cart_products, total=total)

# Страница оформления заказа
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Проверяем, авторизован ли пользователь
        user_id = session.get('user_id')
        if user_id is None:
            # Если пользователь не авторизован, перенаправляем его на страницу входа
            return redirect(url_for('login'))
        # Получаем данные из формы оформления заказа
        address = request.form['address']
        payment_method = request.form['payment_method']
        delivery_method = request.form['delivery_method']
        conn = get_db_connection()
        # Создаем запись о заказе в базе данных
        conn.execute('''INSERT INTO orders (user_id, total, payment_method, delivery_method, address)
                        VALUES (?, ?, ?, ?, ?)''',
                     (user_id, request.form['total'], payment_method, delivery_method, address))
        conn.commit()
        conn.close()
        # После успешного оформления очищаем корзину
        session.pop('cart', None)
        # Перенаправляем пользователя на главную страницу
        return redirect(url_for('index'))
    # Если метод GET, отображаем страницу оформления заказа
    return render_template('checkout.html')

# Административная панель для управления товарами и заказами
@app.route('/admin', methods=['GET
