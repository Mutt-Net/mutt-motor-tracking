import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from backend.extensions import db

basedir = os.path.join(os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database", "logbook.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from backend.models import Vehicle, Maintenance, Mod, Cost, Note, VCDSFault, Guide, VehiclePhoto, FuelEntry, Reminder
from backend.routes import routes

app.register_blueprint(routes, url_prefix='/api')

@app.route('/')
def index():
    with open(os.path.join(basedir, 'frontend', 'index.html'), 'r') as f:
        return f.read()

@app.route('/css/<path:filename>')
def serve_css(filename):
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return 'Forbidden', 403
    safe_path = os.path.join(basedir, 'frontend', 'css', filename)
    if not os.path.normpath(safe_path).startswith(os.path.join(basedir, 'frontend', 'css')):
        return 'Forbidden', 403
    if not os.path.exists(safe_path):
        return 'Not Found', 404
    with open(safe_path, 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@app.route('/js/<path:filename>')
def serve_js(filename):
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return 'Forbidden', 403
    safe_path = os.path.join(basedir, 'frontend', 'js', filename)
    if not os.path.normpath(safe_path).startswith(os.path.join(basedir, 'frontend', 'js')):
        return 'Forbidden', 403
    if not os.path.exists(safe_path):
        return 'Not Found', 404
    with open(safe_path, 'r') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

with app.app_context():
    db.create_all()
    
    if not Vehicle.query.first():
        default_vehicle = Vehicle(
            name='VW EOS',
            vin='WVWZZZ1FZ7V033393',
            year=2007,
            make='VW',
            model='EOS',
            engine='2.0 R4/4V TFSI (AXX)',
            transmission='6-speed Manual',
            mileage=116000
        )
        db.session.add(default_vehicle)
        db.session.commit()
        print("Created default vehicle: VW EOS")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
