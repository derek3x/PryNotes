from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, FileField
from wtforms.validators import Required, Length

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
    
class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])  
    
class Note_Form(Form):
    editor1 = TextAreaField('editor1', validators = [Required()])
    hidden = TextField('hidden')
    hidden3 = TextField('hidden3')
    
class Note_Title(Form):
    notetitle = TextField('notetitle', validators = [Required()])
    hidden2 = TextField('hidden2')
    
class New_Notebook(Form):
    book_title = TextField('book_title', validators = [Required()])
    new_note_title = TextField('new_note_title', validators = [Required()])
    
class Rename_Note(Form):
    new_title = TextField('new_title', validators = [Required()])
    hidden_note_id = TextField('hidden_note_id')
    
class Rename_Notebook(Form):
    new_nbtitle = TextField('new_nbtitle', validators = [Required()])
    hidden_book_id = TextField('hidden_book_id')    
    
class Rename_FileCabinet(Form):
    new_fctitle = TextField('new_fctitle', validators = [Required()])
    hidden_fc_id = TextField('hidden_fc_id')    
    
class New_FileCabinet(Form):
    fc_title = TextField('fc_title', validators = [Required()])
    nb_title = TextField('nb_title', validators = [Required()])
    
class New_FCNotebook(Form):
    fcbook_title = TextField('fcbook_title', validators = [Required()])
    fcnew_note_title = TextField('fcnew_note_title', validators = [Required()])
    hidden_fc_id2 = TextField('hidden_fc_id2') 

class Move_Notebook(Form):
    fc_select = SelectField('fc_select', coerce=int,validators = [Required()])
    hidden_nb_id2 = TextField('hidden_nb_id2')
    
class Attach(Form):
    attach_it = FileField('upload')