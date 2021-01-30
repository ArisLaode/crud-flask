from flask import Flask, flash, render_template, redirect, url_for, request, session
from module.database import Database
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
app.secret_key = "mys3cr3tk3y"
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')
db = Database()

common_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

@app.route('/')
def index():
    data = db.read(None)

    return render_template('index.html', data = data)

@app.route('/add/')
@common_counter
def add():
    return render_template('add.html')

@app.route('/addphone', methods = ['POST', 'GET'])
def addphone():
    if request.method == 'POST' and request.form['save']:
        if db.insert(request.form):
            flash("A new phone number has been added")
        else:
            flash("A new phone number can not be added")

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/update/<int:id>/')
def update(id):
    data = db.read(id);

    if len(data) == 0:
        return redirect(url_for('index'))
    else:
        session['update'] = id
        return render_template('update.html', data = data)

@app.route('/updatephone', methods = ['POST'])
def updatephone():
    if request.method == 'POST' and request.form['update']:

        if db.update(session['update'], request.form):
            flash('A phone number has been updated')

        else:
            flash('A phone number can not be updated')

        session.pop('update', None)

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/delete/<int:id>/')
def delete(id):
    data = db.read(id);

    if len(data) == 0:
        return redirect(url_for('index'))
    else:
        session['delete'] = id
        return render_template('delete.html', data = data)

@app.route('/deletephone', methods = ['POST'])
def deletephone():
    if request.method == 'POST' and request.form['delete']:

        if db.delete(session['delete']):
            flash('A phone number has been deleted')

        else:
            flash('A phone number can not be deleted')

        session.pop('delete', None)

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html')

@app.route('/long-running', methods = ['GET'])
@metrics.gauge('in_progress', 'Long running requests in progress')
def long_running():
    return 'tesss'

@app.route('/eko', methods = ['GET'])
def eko():
    print('eko')
    return 'eko'

# app = Flask(__name__)
# metrics = PrometheusMetrics(app)

# @app.route('/')
# def main():
#     pass  # requests tracked by default

# @app.route('/skip')
# @metrics.do_not_track()
# def skip():
#     pass  # default metrics are not collected

# # custom metric to be applied to multiple endpoints
# common_counter = metrics.counter(
#     'by_endpoint_counter', 'Request count by endpoints',
#     labels={'endpoint': lambda: request.endpoint}
# )

# @app.route('/common/one')
# @common_counter
# def endpoint_one():
#     pass  # tracked by the custom and the default metrics

# @app.route('/common/two')
# @common_counter
# def endpoint_two():
#     pass  # also tracked by the custom and the default metrics

# register additional default metrics
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

if __name__ == '__main__':
    app.run(port=8181, host="0.0.0.0")
