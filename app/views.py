"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2014 Derek Lowes (derek3x)
"""

from flask import render_template, flash, redirect, session, url_for, request, g, request, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, Note_Form, Note_Title, New_Notebook, Rename_Note, Rename_Notebook, Rename_FileCabinet, New_FileCabinet, New_FCNotebook, Move_Notebook, Attach, Merge
from models import User, ROLE_USER, ROLE_ADMIN, Notes, Notebooks, Filecabinets
from datetime import datetime
from flask.ext.sqlalchemy import get_debug_queries
from config import DATABASE_QUERY_TIMEOUT
import re
import os
import urllib
from random import randint
import BeautifulSoup
from BeautifulSoup import Comment
from HTMLParser import HTMLParser
from PIL import Image
import base64
from io import BytesIO
from keyczar import keyczar
from flask import jsonify
import hashlib
from flask_weasyprint import HTML, render_pdf

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 
                          'png', 'jpg', 
                          'jpeg', 'gif', 
                          'zip', 'tar', 
                          'rar', 'tgz', 
                          'png', 'doc', 
                          'odt', 'xls', 
                          'xlsx', 'ppt', 
                          'docx'])
ALLOWED_MIME = set(['image/gif','image/jpg','image/jpeg','image/png'])
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#========================Save to PDF=============================#
@app.route('/<note_title>_<note_id>.pdf')
@login_required
def makePDF(note_title,note_id):
    ids = re.search('[0-9]+',note_id)
    if ids == None:
        flash('Note not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))            
    n = Notes.query.get(int(ids.group(0)))
    if note_check_out(n):
        html = decrypt_it(n.body).decode('utf8', errors='ignore')
        return render_pdf(HTML(string=html))
    else:
        return redirect(url_for('members'))          
    
#========================HTML Stripers and Fixers=============================#
"""
Strips the html down if it has characteristics of a copy and paste from a website.  
If it does not then it will simply pass the text back.  This fixes the bug where 
BeautifulSoup will strip out the text put into the editor by the user.  The textarea
does not put <p> tags on the text.  It also fixes the duplication issue on tables.
"""
def nohtml(doc):
    s = MLStripper()
    s.feed(doc)
    return s.get_data()

def base_fix(doc): 
    fixed = False
    regexp = re.compile(r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')
    soup = BeautifulSoup.BeautifulSoup(doc)
    for tag in soup.findAll('img'):
        pic = tag['src']
        if regexp.search(pic) is not None and pic[:10] == 'data:image':
            data = regexp.search(pic).group(0)
            try:
                im = Image.open(BytesIO(base64.b64decode(data)))
                if pic[:15] == 'data:image/jpeg' or pic[:14] == 'data:image/jpg':
                    filename = filecheck('jpg')
                    filename2 = 'app/static/img/tmp/' + str(g.user.id) + '-' + str(filename) + '.jpg'
                    im.save(filename2, 'JPEG')
                    tag['src'] = "/static/img/tmp/"+ str(g.user.id) + '-' + str(filename)+".jpg"                 
                elif pic[:14] == 'data:image/png':
                    filename = filecheck('png')
                    filename2 = 'app/static/img/tmp/' + str(g.user.id) + '-' + str(filename) + '.png'
                    im.save(filename2, 'PNG')
                    tag['src'] = "/static/img/tmp/"+ str(g.user.id) + '-' + str(filename) + ".png"
                elif pic[:14] == 'data:image/gif':
                    filename = filecheck('fig')
                    filename2 = 'app/static/img/tmp/' + str(g.user.id) + '-' + str(filename) + '.gif'
                    im.save(filename2, 'GIF')
                    tag['src'] = "/static/img/tmp/"+ str(g.user.id) + '-' + str(filename) + ".gif"                    
                else:
                    tag['src'] = pic[:22]                 
                fixed = True
            except IOError:
                pass
        elif pic[:16] != "/static/img/tmp/":
            check = get_content_type(pic)
            if check in ALLOWED_MIME:
                filename = filecheck(check.split('/')[1])
                urllib.urlretrieve(pic,'app/static/img/tmp/' + str(g.user.id) + '-' + str(filename) + '.' + check.split('/')[1])
                tag['src'] = "/static/img/tmp/"+ str(g.user.id) + '-' + str(filename)+"." + check.split('/')[1]
                fixed = True
            else:
                tag['src'] = "/static/img/x.gif"
                fixed = True
    if fixed == True:
        return soup.renderContents().decode('utf8')
    return doc

def get_content_type(url):
    d = urllib.urlopen(url)
    return d.info()['Content-Type']

def filecheck(extension):
    filename = randint(2,99999999999999)
    if os.path.isfile('app/static/tmp/'+ str(g.user.id) + '-' + str(filename)+'.'+str(extension)):
        return filecheck(extension)
    return filename
        
def htmlwork(doc):
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = ['a', 'abbr', 'acronym', 'address', 'area', 'b', 'bdo', 'big', 'blockquote', 'br', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 
                 'dd', 'del', 'dfn', 'div', 'dl', 'dt', 'em', 'font', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'kbd', 'li', 'map', 'ol', 
                 'p', 'pre', 'q', 's', 'samp', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'title', 'tr', 
                 'tt', 'u', 'ul', 'var']
    validAttrs = ['href', 'src', 'width', 'height', 'style', 'WIDTH', 'HEIGHT']
    urlAttrs = 'href src'.split()
    soup = BeautifulSoup.BeautifulSoup(doc)       
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments (ironic comment)
        comment.extract()     
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True            
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                tag.attrs.append((attr, val))
    return soup.renderContents().decode('utf8')                

def strip_extras(doc):
    #doc_stripped = re.sub('[%s]' % ''.join("'"), "\\'", doc) #Escape ' as it will break everything if you don't - Fixed (kept for reference)
    doc_stripped = "".join( doc.splitlines()) # Fixes the end of line issue in the editor on copy and paste from website.  
    return doc_stripped

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):              
        return ''.join(self.fed)
    
#========================Uploads=============================#
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def filecheck_upload(original):
    filename = randint(2,99999999999999)
    extension = original.rsplit('.', 1)[1]
    if os.path.isfile('app/static/uploads/'+str(filename)+'.'+str(extension)):
        return filecheck(original)
    return str(g.user.id) + '-' + str(filename) + '.' + str(extension)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    #if file and file.content_type in ALLOWED_MIME:
    if file and allowed_file(file.filename):
        filename = filecheck_upload(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({
                    'link': '/uploads/' + filename})
    else:
        return jsonify({
                    'link': 'None'})
        
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    if filename.rsplit('-',1)[0] == str(g.user.id):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                filename)
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                '~Data.txt') #fake file for the bots
        
@app.route('/static/uploads/<filename>')
@login_required
def security(filename):
    #This is setup as a warning to people trying to randomly hit others data.
    logout_user()
    return render_template("index.html",
        title = 'Home')    
#==============================Encrypt/Decrypt=============================#    
def encrypt_it(s):
    s = s.encode('utf8', errors='ignore')
    location = 'tmp/kz'
    crypter = keyczar.Crypter.Read(location)
    s_encrypted = crypter.Encrypt(s)
    return s_encrypted

def decrypt_it(s):
    location = 'tmp/kz'
    crypter = keyczar.Crypter.Read(location)
    s_decrypted = crypter.Decrypt(s)
    return s_decrypted
#==============================Landing=============================#
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home')

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])     

@app.route('/old_browser')
def old_browser():
    return app.send_static_file('old_browser.html')
#================================Help===============================#
@app.route('/help')
def helps():
    return render_template("help.html",
        title = 'Help - PryNotes')
#================================Learn More===============================#    
@app.route('/learnmore')
def learnmore():
    return render_template("learnmore.html",
        title = 'PryNotes - Learn PryNotes')
#================================First Run===============================#    
@app.route('/first_run')
@login_required
def first_run():
    return render_template("first_run.html",
        title = 'Welcome to PryNotes')    
    
#==============================Editor Save=============================#
@app.route('/editor', methods = ['POST'])
@login_required
def editor():
    user = g.user
    ids = re.search('[0-9]+',request.form['note'])
    if ids == None:
        flash('Note not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))            
    n = Notes.query.get(int(ids.group(0)))
    if note_check_out(n): 
        if len(request.form['text']) > 524279:
            flash('That note seems kinda big.  Can we make it smaller?', 'danger')
            return redirect(url_for('members'))
        else:
            doc = htmlwork(request.form['text'])
            doc_stripped = strip_extras(doc)
            base = base_fix(doc_stripped)
            encrypted = encrypt_it(base)
            n.body = encrypted
            n.timestamp = datetime.utcnow()
            nbid = request.form['book']
            if nbid == None:
                flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
                return redirect(url_for('members'))         
            nb = Notebooks.query.get(int(nbid))
            if notebook_check_out(nb):
                n.notes_link = nb
                db.session.add(n)
                db.session.commit()
                decrypted = decrypt_it(n.body)
                return jsonify({
                        'text': decrypted,
                        'refresh':request.form['refresh']})

#==============================Select a Note=============================#
@app.route('/select_note', methods = ['POST'])
@login_required
def select_note():        
    user = g.user
    ids = re.search('[0-9]+',request.form['note_id'])
    if ids == None:
        flash('Note not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))            
    n = Notes.query.get(int(ids.group(0)))
    if note_check_out(n):
        if len(n.body) > 2:
            decrypted = decrypt_it(n.body)
        else:
            decrypted = n.body
        time = str(n.timestamp)
        return jsonify({
                'text': decrypted,
                'title' : n.title,
                'stamps' : time})   

#====================Direct Link Shares (read only)=====================#
# Create the shares
@app.route('/create_share/<int:note_id>')
@login_required
def create_share(note_id):
    if note_id == None:
        flash('Note not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))
    n = Notes.query.get(note_id)
    if note_check_out(n):
        key = str(n.id) + str(g.user.id)
        link = hashlib.sha224(str(n.title) + "," + key).hexdigest()
        fluff = randint(2,98)
        link = link + "-" + str(n.id) + "-" + str(fluff)
        flash('www.prynotes.com/shared_note/' + str(link), 'info')
        return redirect(url_for('members'))
    return redirect(url_for('members'))

# Read the shares    
@app.route('/shared_note/<link>')
def shared_note(link):
    note_id = re.search('[0-9]+',link.split('-')[1])
    if note_id == None:
        flash('There seems to be an error here, sorry.  We will check into this', 'danger')
        return redirect(url_for('index'))
    note_id = int(note_id.group(0))
    n = Notes.query.get(note_id)        
    key = str(n.id) + str(n.user_id)
    if link.split('-')[0] == hashlib.sha224(str(n.title) + "," + key).hexdigest():
        note_body = decrypt_it(n.body)
        return render_template("shared_notes.html", 
                                title = 'Shared Notes',
                                link = link,
                                note_title = n.title,
                                note_body = note_body.decode('utf8', errors='ignore'),
                                note_time = n.timestamp
                                )
    flash('There has been an error.  Sorry, we will look into the problem','danger')
    return redirect(url_for('index'))

# Save a shared note to account
@app.route('/save_shared/<link>')
@login_required
def save_shared(link):
    note_id = re.search('[0-9]+',link.split('-')[1])
    if note_id == None:
        flash('There seems to be an error here, sorry.  We will check into this', 'danger')
        return redirect(url_for('index'))
    note_id = int(note_id.group(0))
    n = Notes.query.get(note_id)        
    key = str(n.id) + str(n.user_id)
    if link.split('-')[0] == hashlib.sha224(str(n.title) + "," + key).hexdigest():
        if not g.user.notebooks.filter_by(title = 'Shared Notes').first():
            nb = Notebooks(title="Shared Notes", 
                        timestamp=datetime.utcnow(), 
                        notebook=g.user)
            db.session.add(nb)
        else:
            #User.query.filter_by(nickname = nickname).first()
            nb = g.user.notebooks.filter_by(title = 'Shared Notes').first()
        note_body = decrypt_it(n.body) #this is here due to real server having slightly different encryption (padding)
        nn = Notes(title=n.title,
                   body=encrypt_it(note_body), 
                   timestamp=datetime.utcnow(), 
                   notes_link=nb, 
                   note=g.user)  
        db.session.add(nn)
        db.session.commit()
        return redirect(url_for('members'))
    flash('There has been an error.  Sorry, we will look into the problem','danger')
    return redirect(url_for('index'))    
        
#==============================Members=============================#    
@app.route('/members', methods = ['GET', 'POST'])
@app.route('/members/<int:page>/<int:booked>', methods = ['GET', 'POST'])
@login_required
def members(page=0, booked=0):
    user = g.user
    fc, books, notes = g.user.get_books()
    form = Note_Form()
    form2 = Note_Title()
    form3_new_notebook = New_Notebook()
    form4_new_note_title = Rename_Note()
    form5_new_notebook_title = Rename_Notebook()
    form6_new_fc_title = Rename_FileCabinet()
    form7_new_fc = New_FileCabinet()
    form8_new_fcnotebook = New_FCNotebook()
    form9_move_notebook = Move_Notebook()
    merge = Merge()
    attach = Attach(csrf_enabled=False)
    booked2 = "" # notebook title
    fcd = 0
    note_counter = {}

    # Make sure the notebook is theirs
    if booked > 0:
        if booked == None:
            flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
            return redirect(url_for('members'))     
        nbid = Notebooks.query.get(int(booked))
        if notebook_check_out(nbid):
            booked2 = nbid.title
            fcd = nbid.filecabinet
    
    # Populate the list choices        
    form9_move_notebook.fc_select.choices = [(fcg.id, fcg.title) for fcg in fc]
    merge.nt_select.choices = [(nt.id, nt.title) for nt in notes]
    
    # Count the notes in each book for badges
    for book in books: 
        for note in notes:
            if note.notebooks_id == book.id:
                if book.id in note_counter:
                    note_counter[book.id] += 1
                else:
                    note_counter[book.id] = 1
            elif note.notebooks_id == None:  # delete the orphans (might as well when we are already going through the notebooks)
                    n = Notes.query.get(note.id)
                    db.session.delete(n)
    db.session.commit()  
    
    # Move notebooks to file cabinets
    if form9_move_notebook.validate_on_submit():
        new_fc_id = form9_move_notebook.fc_select.data
        if new_fc_id == None or type(new_fc_id) != int:
            flash('There seems to be a problem. If you think this is in error, please contact us.', 'danger')        
        fc = Filecabinets.query.get(int(new_fc_id))
        if filecabinet_check_out(fc):
            nb_id = re.search('[0-9]+',form9_move_notebook.hidden_nb_id2.data)
            if nb_id == None:
                flash('There seems to be a problem. If you think this is in error, please contact us.', 'danger')
            nb = Notebooks.query.get(int(nb_id.group(0)))
            if notebook_check_out(nb):
                nb.notebook_link=fc
                db.session.add(nb)
                db.session.commit()
                return redirect(url_for('members', page = 0, booked = nb.id))
    
    # New notebook
    if form3_new_notebook.validate_on_submit(): 
        nb_title = nohtml(form3_new_notebook.book_title.data)
        if len(nb_title) > 40:
            flash('Please make the Notebook title shorter', 'danger')
            return redirect(url_for('members'))
        nb = Notebooks(title=nb_title, 
                       timestamp=datetime.utcnow(), 
                       notebook=g.user)
        db.session.add(nb)
        nn_title = nohtml(form3_new_notebook.new_note_title.data)
        if len(nn_title) > 40:
             flash('Please make the Note title shorter', 'danger')           
        nn = Notes(title=nn_title,
                   body=" ", 
                   timestamp=datetime.utcnow(), 
                   notes_link=nb, 
                   note=g.user)
        db.session.add(nn)
        db.session.commit() 
        return redirect(url_for('members', page = nn.id, booked = nb.id))
    
    # New note
    if form2.validate_on_submit():
        nbid = form2.hidden2.data
        if nbid == None:
            flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
            return redirect(url_for('members'))           
        nb = Notebooks.query.get(int(nbid))
        if notebook_check_out(nb):
            tt = nohtml(form2.notetitle.data)
            if len(tt) > 40:
                flash('Can you make it smaller please?', 'danger')
                return redirect(url_for('members'))
            nn = Notes(title=tt, 
                       body=" ", 
                       timestamp=datetime.utcnow(), 
                       notes_link=nb, 
                       note=g.user)
            db.session.add(nn)
            db.session.commit()
            return redirect(url_for('members', page = nn.id, 
                                    booked = int(nbid)))
    
    # Rename note
    if form4_new_note_title.validate_on_submit():
        ids = re.search('[0-9]+',form4_new_note_title.hidden_note_id.data)
        if ids == None:
            flash('Note not found.  If you think this is in error, please contact us.', 'danger')
            return redirect(url_for('members'))         
        n = Notes.query.get(int(ids.group(0)))
        if note_check_out(n):  
            nn_title = nohtml(form4_new_note_title.new_title.data)
            if len(nn_title) > 40:
                flash('Please make the Note title shorter', 'danger')                    
            n.title = nn_title
            db.session.add(n)
            db.session.commit()
            return redirect(url_for('members', page = n.id, 
                                    booked = n.notebooks_id))
    
    # New file cabinet
    if form7_new_fc.validate_on_submit():
        fc_title = nohtml(form7_new_fc.fc_title.data)
        if len(fc_title) > 40:
            flash('Please make the File Cabinet title shorter', 'danger')
            return redirect(url_for('members'))
        nfc = Filecabinets(title=fc_title, filecabinet=g.user)
        db.session.add(nfc)
        nb_title = nohtml(form7_new_fc.nb_title.data)
        if len(nb_title) > 40:
             flash('Please make the Notebook title shorter', 'danger')           
        nb = Notebooks(title=nb_title, 
                       timestamp=datetime.utcnow(), 
                       notebook=g.user, 
                       notebook_link=nfc)
        db.session.add(nb)
        db.session.commit() 
        return redirect(url_for('members', page = 0, 
                                booked = nb.id))        
    
    # Rename notebook
    if form5_new_notebook_title.validate_on_submit():
        nbid = re.search('[0-9]+',form5_new_notebook_title.hidden_book_id.data)
        if nbid == None:
                flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
                return redirect(url_for('members')) 
        nb = Notebooks.query.get(int(nbid.group(0)))
        if notebook_check_out(nb): 
            nb_title = nohtml(form5_new_notebook_title.new_nbtitle.data)
            if len(nb_title) > 40:
                flash('Please make the Notebook title shorter', 'danger')
                return redirect(url_for('members'))            
            nb.title = nb_title
            db.session.add(nb)
            db.session.commit()
            return redirect(url_for('members', page = 0, 
                                    booked = nb.id))
    
    # Rename file cabinet title
    if form6_new_fc_title.validate_on_submit():
        fcid = re.search('[0-9]+',form6_new_fc_title.hidden_fc_id.data)
        if fcid == None:
                flash('File Cabinet not found.  If you think this is in error, please contact us.', 'danger')
                return redirect(url_for('members')) 
        nfc = Filecabinets.query.get(int(fcid.group(0)))
        if filecabinet_check_out(nfc): 
            fc_title = nohtml(form6_new_fc_title.new_fctitle.data)
            if len(fc_title) > 40:
                flash('Please make the File Cabinet title shorter', 'danger')
                return redirect(url_for('members'))            
            nfc.title = fc_title
            db.session.add(nfc)
            db.session.commit()
            return redirect(url_for('members'))      
        
    # New notebook in a file cabinet    
    if form8_new_fcnotebook.validate_on_submit(): 
        fcid = re.search('[0-9]+',form8_new_fcnotebook.hidden_fc_id2.data)
        if fcid == None:
                flash('File Cabinet not found.  If you think this is in error, please contact us.', 'danger')
                return redirect(url_for('members')) 
        nfc = Filecabinets.query.get(int(fcid.group(0)))
        if filecabinet_check_out(nfc):         
            nb_title = nohtml(form8_new_fcnotebook.fcbook_title.data)
            if len(nb_title) > 40:
                flash('Please make the Notebook title shorter', 'danger')
                return redirect(url_for('members'))
            nb = Notebooks(title=nb_title, 
                           timestamp=datetime.utcnow(), 
                           notebook=g.user, 
                           notebook_link=nfc)
            db.session.add(nb)
            nn_title = nohtml(form8_new_fcnotebook.fcnew_note_title.data)
            if len(nn_title) > 40:
                flash('Please make the Note title shorter', 'danger')           
            nn = Notes(title=nn_title, 
                       body=" ", 
                       timestamp=datetime.utcnow(), 
                       notes_link=nb, 
                       note=g.user)
            db.session.add(nn)
            db.session.commit() 
            return redirect(url_for('members', page = nn.id, 
                                    booked = nb.id))  

    # Merge two notes    
    if merge.validate_on_submit(): 
        mergee_id = re.search('[0-9]+',merge.merge_note_id.data)
        if mergee_id == None:
            flash('Note not found.  If you think this is in error, please contact us.', 'danger')
            return redirect(url_for('members'))
        n = Notes.query.get(int(mergee_id.group(0)))
        merger_id = merge.nt_select.data
        if int(mergee_id.group(0)) == int(merger_id):
            flash('You can not merge a Note into itself', 'danger')
            return redirect(url_for('members'))            
        nn = Notes.query.get(int(merger_id))        
        if note_check_out(n) and note_check_out(nn):
            if len(n.body) < 2 or len(nn.body) < 2:
                flash('You can not merge an empty note', 'danger')
                return redirect(url_for('members'))                 
            mergee = decrypt_it(n.body)
            merger = decrypt_it(nn.body)
            new_note = mergee + merger
            if len(new_note) <= 524279:
                n.body = encrypt_it(new_note)
                db.session.add(n)
                db.session.delete(nn)
                db.session.commit()
                return redirect(url_for('members', page=n.id, 
                                        booked=n.notebooks_id))
            
    return render_template("members.html",
                            title = 'Members',
                            user = user,
                            form = form,
                            form2 = form2,
                            form3_new_notebook = form3_new_notebook,
                            form4_new_note_title = form4_new_note_title,
                            form5_new_notebook_title = form5_new_notebook_title,
                            form6_new_fc_title = form6_new_fc_title,
                            form7_new_fc = form7_new_fc,
                            form8_new_fcnotebook = form8_new_fcnotebook,
                            merge = merge,
                            note_counter = note_counter,
                            fc = fc,
                            fcd = fcd,
                            page = page, #reload with right note selected
                            attach = attach,
                            booked = booked, #reload with right notebook selected
                            booked2 = booked2,
                            books = books,
                            form9_move_notebook = form9_move_notebook,
                            notes = notes)

#=======================Log in / Log out code=======================#    
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('members'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In/Sign Up',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])
    
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, 
                    email = resp.email, 
                    role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember = remember_me)
        return redirect(url_for('first_run'))
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('members'))    
    
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))   

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    
@app.route('/logout')
def logout():             
    logout_user()
    return redirect(url_for('index'))     

#==============================Settings=============================#
@app.route('/user/<nickname>', methods = ['GET', 'POST'])
@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.', 'danger')
        return redirect(url_for('members'))
    form = EditForm()    
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('members'))
    else:
        form.nickname.data = g.user.nickname
    return render_template('settings.html',
                            form = form,
                            user = user)   

#===================Error Handlers===================#
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response

#===================Delete Items===================#
#Delete Notes
@app.route('/delete/<int:ids>')
@login_required
def delete(ids):
    note = Notes.query.get(ids)
    if note == None:
        flash('Note not found.', 'danger')
        return redirect(url_for('members'))
    if note.user_id != g.user.id:
        flash('You cannot delete this note.', 'danger')
        return redirect(url_for('members'))
    db.session.delete(note)
    db.session.commit()
    flash('Your note has been deleted.', 'info')
    return redirect(url_for('members'))
#Delete Notebooks
@app.route('/deletenb/<int:ids>')
@login_required
def deletenb(ids):
    noteb = Notebooks.query.get(ids)
    if noteb == None:
        flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))
    if noteb.user_id != g.user.id:
        flash('You cannot delete this notebook.', 'danger')
        return redirect(url_for('members'))
    db.session.delete(noteb)
    db.session.commit()
    flash('Your notebook has been deleted.', 'info')
    return redirect(url_for('members'))
#Delete File Cabinets
@app.route('/deletefc/<int:ids>')
@login_required
def deletefc(ids):
    fc = Filecabinets.query.get(ids)
    if fc == None:
        flash('File Cabinet not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))
    if fc.user_id != g.user.id:
        flash('You cannot delete this File Cabinet.', 'danger')
        return redirect(url_for('members'))
    db.session.delete(fc)
    db.session.commit()
    flash('Your File Cabinet has been deleted.', 'info')
    return redirect(url_for('members'))

@app.route('/removenb/<int:ids>')
@login_required
def removenb(ids):
    noteb = Notebooks.query.get(ids)
    if noteb == None:
        flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
        return redirect(url_for('members'))
    if noteb.user_id != g.user.id:
        flash('You cannot delete this notebook.', 'danger')
        return redirect(url_for('members'))
    noteb.notebook_link=None
    db.session.add(noteb)
    db.session.commit()
    flash('Your notebook has been removed.', 'info')
    return redirect(url_for('members'))

#=====================Delete User=====================#
@app.route('/gobyebye')
@login_required
def gobyebye():
    fc, books, notes = g.user.get_books()
    for f in fc:
        db.session.delete(f)
    for nb in books:
        db.session.delete(nb)
    for n in notes:
        db.session.delete(n)
    db.session.delete(g.user)
    db.session.commit()    
    flash('Your account is gone forever.  Have a good day!', 'danger')
    return redirect(url_for('index'))

#===================Library Checkout===================#
def note_check_out(n):
    if n == None:
        flash('Note not found.  If you think this is in error, please contact us.', 'danger')
        return False
    if n.user_id != g.user.id:
        flash('That note ID does not belong to your account.', 'danger')
        return False
    return True

def notebook_check_out(nb):
    if nb == None:
        flash('Notebook not found.  If you think this is in error, please contact us.', 'danger')
        return False
    if nb.user_id != g.user.id:
        flash('That notebook ID does not belong to your account.', 'danger')
        return False
    return True

def filecabinet_check_out(fc):
    if fc == None:
        flash('File Cabinet not found.  If you think this is in error, please contact us.', 'danger')
        return False
    if fc.user_id != g.user.id:
        flash('That File Cabinet ID does not belong to your account.', 'danger')
        return False
    return True

#=====================Terms and Privacy=====================#
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')