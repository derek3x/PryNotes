from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(120), unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    filecabinets = db.relationship('Filecabinets', backref = 'filecabinet', lazy = 'dynamic')
    notebooks = db.relationship('Notebooks', backref = 'notebook', lazy = 'dynamic')
    notes = db.relationship('Notes', backref = 'note', lazy = 'dynamic')
    last_seen = db.Column(db.DateTime)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    
    def get_books(self):
        u = User.query.get(self.id)
        fc = sorted(u.filecabinets.all(), key=lambda FileCabinets: FileCabinets.title)
        nb = sorted(u.notebooks.all(), key=lambda Notebooks: Notebooks.title)
        nt = sorted(u.notes.all(), key=lambda Notes: Notes.title)
        return fc, nb, nt

    def __repr__(self):
        return '<User %r>' % (self.nickname)
        
    """ def shared_nbs(self):
        return Notebooks.query.join(shares, (shares.c.shared_from_user_id == Notebooks.user_id)).filter(shares.c.shared_to_user_id == self.id).filter(shares.c.shared_noteboook_id == Notebooks.id).order_by(Notebooks.title) """
    
    
class Filecabinets(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notebook_link = db.relationship('Notebooks', backref = 'notebook_link', lazy = 'dynamic')

class Notebooks(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes_link = db.relationship('Notes', backref = 'notes_link', lazy = 'dynamic')
    filecabinet = db.Column(db.Integer, db.ForeignKey('filecabinets.id'))

    def __repr__(self):
        return '<NoteBooks %r>' % (self.title)   

class Notes(db.Model):    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    body = db.Column(db.String(524280))
    timestamp = db.Column(db.DateTime)
    notebooks_id = db.Column(db.Integer, db.ForeignKey('notebooks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def get_note(self, ids):
        n = Notes.query.get(ids)
        return n

    def __repr__(self):
        return '<Notes %r>' % (self.body)
 