import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from utils.converters import process_file, ALLOWED_EXTENSIONS
from dotenv import load_dotenv
import stripe

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-me')

# Stripe configuration (utilise des clés test en dev)
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', publishable_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/process', methods=['POST'])
def upload_and_process():
    if 'file' not in request.files:
        flash('Aucun fichier envoyé')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        flash('Type de fichier non supporté')
        return redirect(url_for('index'))
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(saved_path)

    # options envoyées depuis le formulaire
    action = request.form.get('action') or 'extract_text'

    # mode payant ? on accepte un paramètre 'paid' pour simuler paiement
    paid = request.form.get('paid') == 'true' or request.args.get('paid') == 'true'

    try:
        output_path, mime_type = process_file(saved_path, action, paid=paid)
    except Exception as e:
        flash(f"Erreur lors du traitement : {e}")
        return redirect(url_for('index'))

    return send_file(output_path, mimetype=mime_type, as_attachment=True, download_name=os.path.basename(output_path))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    price_cents = int(request.form.get('amount_cents', 100))
    # Use {CHECKOUT_SESSION_ID} template per Stripe docs so you can look up session after redirect
    success_url = request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.host_url
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Traitement de fichier premium',
                    },
                    'unit_amount': price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Erreur paiement: {e}")
        return redirect(url_for('index'))

@app.route('/success')
def success_page():
    session_id = request.args.get('session_id')
    return render_template('success.html', session_id=session_id)

if __name__ == '__main__':
    app.run(debug=True)
