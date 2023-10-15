from flask import Flask, render_template, request, redirect, url_for
from services.scheduler import get_plan

app = Flask(__name__)

fake_db = [{'id': 1, 'name': 'worker1'}, {'id': 2, 'name': 'worker2'}, {'id': 3, 'name': 'worker3'},
           {'id': 4, 'name': 'worker4'}, {'id': 5, 'name': 'worker5'}, {'id': 6, 'name': 'worker6'},
           {'id': 7, 'name': 'worker7'}, {'id': 8, 'name': 'worker8'}, {'id': 9, 'name': 'worker9'},
           {'id': 10, 'name': 'worker10'}]


@app.route('/')
def index():
    return redirect(url_for('scheduler'))


@app.route('/scheduler', methods=["GET", "POST"])
def scheduler():
    if request.method == "POST":
        start = request.form.get('start')
        end = request.form.get('end')
        shift = request.form.get('shift')
        start_date = request.form.get('start_date').replace('-', '/')
        end_date = request.form.get('end_date').replace('-', '/')
        hpm = int(request.form.get('hpm'))
        return render_template('scheduler.html',
                               plan=get_plan(fake_db, start, end, shift, start_date, end_date, hpm))
    return render_template('scheduler.html')


if __name__ == '__main__':
    app.run()
