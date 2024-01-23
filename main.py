from flask import Flask,render_template,session,redirect,url_for,flash,send_from_directory,request
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from werkzeug.exceptions import HTTPException, BadRequest
from wtforms.validators import DataRequired
from markdown import markdown
import bleach
import os
#记得装依赖
app = Flask(__name__)
app.config['SECRET_KEY']='Kingwho123!'#表单密钥
app.config['FONT_PATH'] = '/static/fonts/YouYuan.ttf'#字体
app.config['BOOTSTRAP_SERVE_LOCAL'] = True #离线化
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = './upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
bootstrap = Bootstrap(app)
cwd = os.getcwd().replace("\\", "/")
urled="http://localhost/"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def markdowned(inputcon):#看看行不行
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong',
                    'ul','h1', 'h2', 'h3', 'p', 'img']
    attrs = {
        'img': ['src', 'alt']
    }
    markdown_result = bleach.linkify(bleach.clean(markdown(inputcon,output_format='html'),tags=allowed_tags,attributes=attrs,strip=True))
    return markdown_result


def tryread(file_name):
    file = str(file_name)
    file = open(file,'r',encoding="utf-8-sig")
    file1 = file.read()
    file1 = file1
    file1 = eval(file1)[0]
    file.close()
    return file1

def trywrite(file_name,atr):
    file = str(file_name)
    file = open(file,'w',encoding="utf-8-sig")
    file.write(atr)
    file.close()

def tryfinding():
    finalcontent=[]
    num=0
    getartcont=open("config.txt","r",encoding="utf-8-sig")
    cont=getartcont.read()
    getartcont.close()
    for i in range(int(cont)):
        readlib="{}/article/{}.txt".format(cwd,i)
        con = tryread(readlib)
        finalcontent.append(con)
    finalcontent.reverse()
    for markcon in finalcontent:
        markcon['content']=markdowned(markcon['content'])
    return finalcontent
def newaricle():

    getartcont=open("config.txt","r",encoding="utf-8-sig")
    cont=getartcont.read()
    getartcont.close()
    newart=open("{}/article/{}.txt".format(cwd,cont),'w',encoding="utf-8-sig")
    form = POSTForm()
    readlib = "{}/article/{}.txt".format(cwd, cont)
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['body'] = form.body.data
        timed=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writedict={'id':'','writer':'','content':'','time':''}
        writedict['id'] = cont
        writedict['writer']=session.get('name')
        writedict['content'] = session.get('body')
        writedict['time']=timed
        trywrite(readlib,'['+str(writedict)+']')
        print(cont)
        recont=int(cont)+1
        getartcont=open("config.txt","w",encoding="utf-8-sig")
        getartcont.write(str(recont))
        getartcont.close()
class POSTForm(FlaskForm):
    name = StringField('昵称',validators=[DataRequired()])  #昵称form
    body = TextAreaField('内容',validators=[DataRequired()])  #内容form
    submit = SubmitField('确认')


def getwhen():
    now = datetime.now()
 
    if now.hour < 12:
        return "☀️早上好"
    elif now.hour >= 12 and now.hour < 18:
        return "☕下午好"
    else:
        return "🌙晚上好"

@app.errorhandler(413)
def file_out_of_size(e):
    return render_template('413.html'), 413    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/',methods=['GET','POST'])
def index():
    if not session.get('name') == None:
        flash("文章已发布")
    hisname=session.get('name')
    session['name']= None
    form = POSTForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['body'] = form.body.data
        newaricle()
        return redirect(url_for('index'))
        

        
        
    return render_template('index.html',whattime=getwhen(),form=form,name=hisname,rescont=tryfinding())
#index 变量解释：whattime:反馈早中晚，form:表单，name:名字,rescont:文章全局

@app.route('/article/<artid>',methods=['GET','POST'])
def article(artid):
    getartcont=open("config.txt","r",encoding="utf-8-sig")
    cont=getartcont.read()
    getartcont.close()
    #try:
    if  0<=int(artid)<int(cont):
        artview=open("{}/article/{}.txt".format(cwd,artid),'r',encoding="utf-8-sig")
        wz = artview.read()
        wz = eval(wz)[0]
        wz['content']=markdowned(wz['content'])
        artview.close()
        if not session.get('name') == None:
            flash("评论已发布")
        hisname = session.get('name')
        session['name'] = None
        form = POSTForm()
        if form.validate_on_submit():
            session['name'] = form.name.data
            session['body'] = form.body.data
            artall = open("{}/article/{}.txt".format(cwd, artid), 'r', encoding="utf-8-sig")
            atra = artall.read()
            atra = eval(atra)
            artall.close()
            timed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writedict = {'id': '', 'writer': '', 'content': '', 'time': ''}
            writedict['id'] = len(atra)-1
            writedict['writer'] = session.get('name')
            writedict['content'] = session.get('body')
            writedict['time'] = timed
            atra.append(writedict)
            artall = open("{}/article/{}.txt".format(cwd, artid), 'w', encoding="utf-8-sig")
            artall.write(str(atra))
            artall.close()

            return redirect(url_for('article',artid=artid))
        artall = open("{}/article/{}.txt".format(cwd, artid), 'r', encoding="utf-8-sig")
        artcm = artall.read()
        artcm = eval(artcm)
        del artcm[0]

        artcm = artcm[::-1]
        artall.close()

        return render_template('article.html', wz=wz,form=form,name=hisname,comments=artcm)
    else:
        return render_template('404.html'), 404
    #except:
        #return render_template('404.html'), 404

@app.route('/imagehost',methods=['GET','POST'])
def imagehost():
    return render_template('imagehost.html')

@app.route('/upload/<filename>/',methods=['GET','POST'])
def upload(filename):
    return send_from_directory(cwd+'/upload',filename)

@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    # 从请求中获取上传的文件
    file = request.files['file']

    # 如果文件已经存在，就提示该文件存在
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)):
        #os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))# 如果文件已经存在，就删除
        flash("呜呜，已存在该文件")
        return render_template('failed.html')
    # 检查文件类型是否允许上传
    if file and allowed_file(file.filename):
        # 保存文件到指定路径
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        # 重定向到上传成功页面，并传递文件名参数
        flash("恭喜！已成功上传，以下将会出现一条Markdown代码。注意，这将只会出现一次，请妥善保存")
        markdownop = '![' + file.filename + '](' + urled + 'upload/' + file.filename + ')'
        return render_template('imagehost.html', markdownop=markdownop)
    else:
        # 返回上传失败的提示信息
        flash("不支持此文件格式")
        return render_template('failed.html')

# 显示上传成功页面
@app.route('/success')
def success():
    # 获取上传成功页面的文件名参数
    filename = request.args.get('filename')
    # 返回上传成功的提示信息
    return f'{filename}上传成功'


if __name__=='__main__':
    app.run(host='0.0.0.0',port='80',threaded=True)
