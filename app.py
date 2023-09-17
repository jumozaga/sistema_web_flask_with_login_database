from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # SQLite database
db = SQLAlchemy(app)

# Definir o modelo Post para o banco de dados
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

# Criar a tabela post no banco de dados (execute isso apenas uma vez)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Listar todos os posts em ordem decrescente
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['logged_in'] = True
            flash('Login realizado com sucesso', 'success')
            # Redirecione o usuário para a página create_post
            return redirect(url_for('create_post'))    
        else:
            flash('Login falhot. Usuário ou senha incorreto', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Até logo, volte sempre!', 'success')
    return render_template('volte_sempre.html')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if not session.get('logged_in'):
        flash('Precisa estar logado para criar postagens.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Obter os dados do formulário
        title = request.form['title']
        text = request.form['text']

        # Criar um novo post e adicioná-lo ao banco de dados
        new_post = Post(title=title, text=text)
        db.session.add(new_post)
        db.session.commit()

        flash('Post criado com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('create_post.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get(post_id)

    if not session.get('logged_in'):
        flash('Precisa realizar login para editar um post', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Atualizar os dados do post com base no formulário
        post.title = request.form['title']
        post.text = request.form['text']
        db.session.commit()

        flash('Post updated successfully', 'success')
        return redirect(url_for('index'))

    return render_template('edit_post.html', post=post)

@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)

    if not session.get('logged_in'):
        flash('Precisa estar logado para excluir um post.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Excluir o post do banco de dados
        db.session.delete(post)
        db.session.commit()

        flash('Post deleted successfully', 'success')
        return redirect(url_for('index'))

    return render_template('delete_post.html', post=post)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
