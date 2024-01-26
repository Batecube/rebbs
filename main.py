'''
本次变动：
1.fix bug
2. add webname set
'''
from flask import Flask,render_template,session,redirect,url_for,flash,send_from_directory,request
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from werkzeug.exceptions import HTTPException, BadRequest
from wtforms.validators import DataRequired
from markdown import markdown
import bleach
import time
import os
import uuid
#模块
app = Flask(__name__)#主bbs系统
appguide = Flask(__name__)#向导
app.config['SECRET_KEY']='Kingwho123!'#表单密钥,请填自己的
appguide.config['SECRET_KEY']='Kingwho123!'
app.config['FONT_PATH'] = '/static/fonts/YouYuan.ttf'#字体
app.config['BOOTSTRAP_SERVE_LOCAL'] = False #cdn资源离线化，建议关闭
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #最大上传大小
app.config['UPLOAD_FOLDER'] = './upload'#上传目录
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} #设置允许上传的文件后缀名
bootstrap = Bootstrap(app)
bootstrap = Bootstrap(appguide)
cwd = os.getcwd().replace("\\", "/")


#markdown过滤并转换html


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def markdowned(inputcon):#看看行不行
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',  
                    'em', 'i', 'li', 'ol', 'pre', 'strong',  
                    'ul','h1', 'h2', 'h3', 'p', 'img']  
    attrs = {  
        'a': ['href'],  # 允许a标签的href属性  
        'img': ['src', 'alt']  
    }  
    markdown_result = bleach.linkify(bleach.clean(markdown(inputcon,output_format='html'),tags=allowed_tags,attributes=attrs,strip=True))
    return markdown_result

#答辩遍历article（by FGO）

def tryread(file_name):
    file = str(file_name)
    file = open(file,'r',encoding="utf-8-sig")
    file1 = file.read()
    file1 = file1
    file1 = eval(file1)[0]
    file.close()
    return file1

#写入文章(by FGO)

def trywrite(file_name,atr):
    file = str(file_name)
    file = open(file,'w',encoding="utf-8-sig")
    file.write(atr)
    file.close()

#bbs论坛渲染文章（逻辑）

def tryfinding():
    finalcontent=[]
    num=0
    getartcont=open("config.txt","r",encoding="utf-8-sig")
    trygetcont=getartcont.read()
    trygetcont=eval(trygetcont)
    cont=trygetcont['cont']
    getartcont.close()
    for i in range(int(cont)):
        readlib="{}/article/{}.txt".format(cwd,i)
        con = tryread(readlib)
        finalcontent.append(con)
    finalcontent.reverse()
    for markcon in finalcontent:
        markcon['content']=markdowned(markcon['content'])
    return finalcontent

#新建文章（主逻辑）

def newaricle():

    getartcont=open("config.txt","r",encoding="utf-8-sig")
    trygetcont=getartcont.read()
    trygetcont=eval(trygetcont)
    cont=trygetcont['cont']
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
        trygetcont['cont']=recont
        getartcont.write(str(trygetcont))
        getartcont.close()

class POSTForm(FlaskForm):
    name = StringField('昵称',validators=[DataRequired()])  #昵称form
    body = TextAreaField('内容',validators=[DataRequired()])  #内容form
    submit = SubmitField('确认')

class CONFIGForm(FlaskForm):
    setname = StringField('设置站点昵称',validators=[DataRequired()])
    seturl = StringField('本站URL（对外访问的地址，如http://example.com/）',validators=[DataRequired()])
    setlocal = StringField('本地IP地址',validators=[DataRequired()])
    setport = StringField('监听端口',validators=[DataRequired()])
    settoken = StringField('确认token（在服务端命令行显示）',validators=[DataRequired()])
    submit = SubmitField('保存并应用')

#（你应该看得懂）

def getwhen():
    now = datetime.now()
 
    if now.hour < 12:
        return "☀️早上好"
    elif now.hour >= 12 and now.hour < 18:
        return "☕下午好"
    else:
        return "🌙晚上好"

##处理错误页面

@app.errorhandler(413)
def file_out_of_size(e):
    return render_template('413.html',webname=webname), 413    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',webname=webname), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',webname=webname), 500

#主页

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
    return render_template('index.html',whattime=getwhen(),form=form,name=hisname,rescont=tryfinding(),webname=webname)
#index 变量解释：whattime:反馈早中晚，form:表单，name:名字,rescont:文章全局

#文章详情
@app.route('/article/<artid>',methods=['GET','POST'])
def article(artid):
    getartcont=open("config.txt","r",encoding="utf-8-sig")
    trygetcont=getartcont.read()
    trygetcont=eval(trygetcont)
    cont=trygetcont['cont']
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

            return redirect(url_for('article',artid=artid,webname=webname))
        artall = open("{}/article/{}.txt".format(cwd, artid), 'r', encoding="utf-8-sig")
        artcm = artall.read()
        artcm = eval(artcm)
        del artcm[0]

        artcm = artcm[::-1]
        artall.close()

        return render_template('article.html', wz=wz,form=form,name=hisname,comments=artcm,webname=webname)
    else:
        return render_template('404.html'), 404
    #except:
        #return render_template('404.html'), 404

#图床

@app.route('/imagehost',methods=['GET','POST'])
def imagehost():
    return render_template('imagehost.html',webname=webname)

#上传图片

@app.route('/upload/<filename>/',methods=['GET','POST'])
def upload(filename):
    return send_from_directory(cwd+'/upload',filename,webname=webname)

#上传图片后所发生的事件

@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    # 从请求中获取上传的文件
    file = request.files['file']

    # 如果文件已经存在，就提示该文件存在
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)):
        #os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))# 如果文件已经存在，就删除
        flash("呜呜，已存在该文件")
        return render_template('failed.html',webname=webname)
    # 检查文件类型是否允许上传
    if file and allowed_file(file.filename):
        # 保存文件到指定路径
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        # 重定向到上传成功页面，并传递文件名参数
        flash("恭喜！已成功上传，以下将会出现一条Markdown代码。注意，这将只会出现一次，请妥善保存")
        markdownop = '![' + file.filename + '](' + urled + 'upload/' + file.filename + ')'
        return render_template('imagehost.html', markdownop=markdownop,webname=webname)
    else:
        # 返回上传失败的提示信息
        flash("不支持此文件格式")
        return render_template('failed.html',webname=webname)

# 显示上传成功页面
@app.route('/success')
def success():
    # 获取上传成功页面的文件名参数
    filename = request.args.get('filename')
    # 返回上传成功的提示信息
    return f'{filename}上传成功'



@appguide.route('/',methods=['GET','POST'])
def index():
    if session.get('settoken') == token:
        writeconfig=open("config.txt","w",encoding="utf-8-sig")
        writedict={'name':'','url':'','localip':'','port':'','cont':''}
        writedict['name'] = session.get('setname')
        writedict['url'] = session.get('seturl')
        writedict['localip']=session.get('setlocal')
        writedict['port'] = session.get('setport')
        
        folder_path = "{}/article".format(cwd) 
        file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
        writedict['cont'] = file_count
        writeconfig.write(str(writedict))
        writeconfig.close()
        flash("已完成设置，可安全退出。(自行重新开启实例)")
        session['settoken']= None
    elif not session.get('settoken') == None:
        flash("请检查token是否正确")
    session['settoken']= None
    form = CONFIGForm()
    if form.validate_on_submit():
        session['setname'] = form.setname.data
        session['seturl'] = form.seturl.data
        session['setlocal'] = form.setlocal.data
        session['setport'] = form.setport.data
        session['settoken'] = form.settoken.data
        return redirect(url_for('index')) 
    
    return render_template('guide.html',form=form)

def check_file_exists(file_path):  
    if os.path.isfile(file_path):  
        return True  
    else:  
        return False

#main入口
if __name__=='__main__':
    file_path = "{}/config.txt".format(cwd) 
    if not check_file_exists(file_path):  
        print("您可能是第一次使用本程序，现已启动向导")
        token = str(uuid.uuid4())
        print("本次token为")
        print(token)
        appguide.run(host='0.0.0.0',port='51111',threaded=True)
    else:
        getartcont=open("config.txt","r",encoding="utf-8-sig")
        trygetcont=getartcont.read()
        trygetcont=eval(trygetcont)
        webname=trygetcont['name']
        cont=trygetcont['url']
        ip=trygetcont['localip']
        pt=trygetcont['port']
        getartcont.close()
        urled=cont #域名，事关upload
        app.run(host=ip,port=pt,threaded=True)
