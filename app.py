from flask import Flask, render_template, request, redirect, url_for, session
from models import *
from vui import db, app

@app.route('/')
def index():
    variants = Variant.query.limit(100)
    return render_template('ajax_table.html', title='Ajax Table')

@app.route('/api/data')
def data():
    # pagination
    query =  Variant.query

    if filter_chrom := request.args.get('filter_chrom'):
         query = query.filter_by(chr=filter_chrom)

    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    print([variant.to_dict() for variant in query])
    return {
        'data': [variant.to_dict() for variant in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Variant.query.count(),
        'draw': request.args.get('draw', type=int),
        }

app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)