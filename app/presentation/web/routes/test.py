from flask import Blueprint, render_template

test = Blueprint('test', __name__)

@test.route('/test')
def hello():
    return render_template('danh_dau.html')

@test.route('/test2')
def hello2():
    return render_template('tong_quan.html')

@test.route('/test3')
def hello3():
    return render_template('dang_nhap.html')

@test.route('/test4')
def hello4():
    return render_template('dang_ky.html')

@test.route('/test5')
def hello5():
    return render_template('xac_thuc.html')

@test.route('/test6')
def hello6():
    return render_template('cho_xet_duyet.html')

@test.route('/test7')
def hello7():
    return render_template('403.html')


@test.route('/test8')
def hello8():
    return render_template('yeu_cau_xac_thuc.html')