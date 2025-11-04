from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    bids = db.relationship('Bid', backref='user', lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    starting_price = db.Column(db.Float, nullable=False, default=0.0)
    end_time = db.Column(db.DateTime, nullable=False)
    bids = db.relationship('Bid', backref='item', lazy=True, cascade='all, delete-orphan')

    @property
    def current_price(self):
        if not self.bids:
            return float(self.starting_price)
        return max(b.amount for b in self.bids)

    @property
    def highest_bidder(self):
        if not self.bids:
            return None
        top = max(self.bids, key=lambda b: b.amount)
        return top.user

    @property
    def is_closed(self):
        return datetime.utcnow() >= self.end_time


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)


# Ensure DB is created when app starts
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    items = Item.query.order_by(Item.end_time.asc()).all()
    recent_bids = Bid.query.order_by(Bid.created_at.desc()).limit(10).all()
    return render_template('index.html', items=items, recent_bids=recent_bids, now=datetime.utcnow())


@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        if not name or not email:
            flash('Nome e e-mail são obrigatórios.', 'danger')
            return redirect(url_for('new_user'))
        if User.query.filter((User.name == name) | (User.email == email)).first():
            flash('Nome ou e-mail já cadastrados.', 'warning')
            return redirect(url_for('new_user'))
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('users_new.html')


@app.route('/items/new', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        starting_price = request.form.get('starting_price', '0').strip()
        end_time_str = request.form.get('end_time', '').strip()

        if not title or not end_time_str:
            flash('Título e término do leilão são obrigatórios.', 'danger')
            return redirect(url_for('new_item'))

        try:
            starting_price = float(starting_price)
        except ValueError:
            flash('Preço inicial inválido.', 'danger')
            return redirect(url_for('new_item'))

        try:
            # Expect input type=datetime-local -> 'YYYY-MM-DDTHH:MM'
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Data/hora de término inválida.', 'danger')
            return redirect(url_for('new_item'))

        if end_time <= datetime.utcnow():
            flash('A data de término deve ser no futuro.', 'warning')
            return redirect(url_for('new_item'))

        item = Item(title=title, description=description, starting_price=starting_price, end_time=end_time)
        db.session.add(item)
        db.session.commit()
        flash('Item de leilão criado!', 'success')
        return redirect(url_for('item_detail', item_id=item.id))

    return render_template('items_new.html')


@app.route('/items/<int:item_id>', methods=['GET', 'POST'])
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    users = User.query.order_by(User.name.asc()).all()

    if request.method == 'POST':
        if item.is_closed:
            flash('Leilão encerrado. Não é possível ofertar.', 'warning')
            return redirect(url_for('item_detail', item_id=item.id))

        user_id = request.form.get('user_id')
        amount_str = request.form.get('amount', '').strip()
        try:
            amount = float(amount_str)
        except ValueError:
            flash('Valor da oferta inválido.', 'danger')
            return redirect(url_for('item_detail', item_id=item.id))

        user = User.query.get(user_id)
        if not user:
            flash('Selecione um usuário válido.', 'danger')
            return redirect(url_for('item_detail', item_id=item.id))

        min_required = item.current_price + 0.01
        if amount < min_required:
            flash(f'A oferta deve ser maior que R$ {item.current_price:.2f}.', 'warning')
            return redirect(url_for('item_detail', item_id=item.id))

        bid = Bid(amount=amount, user_id=user.id, item_id=item.id)
        db.session.add(bid)
        db.session.commit()
        flash('Oferta registrada com sucesso!', 'success')
        return redirect(url_for('item_detail', item_id=item.id))

    bids = Bid.query.filter_by(item_id=item.id).order_by(Bid.amount.desc()).all()
    return render_template('item_show.html', item=item, bids=bids, users=users, now=datetime.utcnow())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
