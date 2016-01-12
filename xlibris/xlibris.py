#! /usr/bin/env python
import os
import cmd
import readline
import datetime
from csv import *
from tqdm import tqdm
from tabulate import *
from pyfiglet import Figlet
from isbntools.app import meta
from tinydb import TinyDB, Query
from collections import defaultdict
##########################################################
def _concat(data):
    final = defaultdict(list)
    for d in data:
        for key, value in d.iteritems():
            final[key].append(value)
    return final
def _cleanify(bookMeta):
    if type(bookMeta['Authors']) == list:
        if len(bookMeta['Authors']) > 1:
            bookMeta['Authors'] = bookMeta['Authors'][0]
        else:
            bookMeta['Authors'] = bookMeta['Authors'][0]
    bookMeta['ISBN'] = bookMeta.pop('ISBN-13')
    title = bookMeta['Title']
    title = title.split(":")[0]
    bookMeta['Title'] = title
    auth = bookMeta['Authors']
    auth = auth.split(",")[0]
    auth = auth.split(";")[0]
    auth = auth.split("illustrated", 1)[0]
    auth = auth.split("and", 1)[0]
    auth = auth.split("with", 1)[0]
    bookMeta['Authors'] = auth
    pub = bookMeta['Publisher']
    pub = pub.split(" ")[0]
    bookMeta['Publisher'] = pub
    return bookMeta
def _doesexist(db, isbn):
    ext = Query()
    if db.search(ext.ISBN.matches(isbn)):
        return True
    else:
        return False
def _today():
    dat = datetime.date.today()
    return dat.strftime('%d/%m/%y')
_intro = Figlet(font = 'slant').renderText('xLibris')
############################################################
class xlibris(object):
    def __init__(self, directory = 'xlibris/'):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
    def new(self,dbname):
        '''Creates a new database assigns it to a current database instance to be used by all the other functions
            Usage:-
            new('database name') or new database_name
        '''
        self.db = TinyDB(self.directory + dbname + '.json')
        print 'New database {} created at {}'.format(dbname, self.directory + dbname + '.json' )
    def connect(self,name):
        '''Connect to an existing database for updating/Query
            Usage:-
            connect('name') or connect name
            where 'name' is the name of the existing database'''

        self.db = TinyDB(self.directory + name + '.json')
        print 'Connected to {}'.format(name)
    def display(self):
        try:
            print tabulate(_concat(self.db.all()), headers='keys', tablefmt="simple")
        except AttributeError:
            print 'No database Connected'
    def add(self, ISBN):
        '''Add books to the current working database
            Usage:-
            add(ISBN) or add ISBN'''
        if _doesexist(self.db, ISBN) == False:
            try:
                bookData = meta(ISBN)
                bookData = _cleanify(bookData)
                bookData['Date Added'] = _today()
                self.db.insert(bookData)
                print 'ISBN {} inserted'.format(ISBN)
            except:
                print 'ISBN {} not found. Please add details manually- '.format(ISBN)
                self.madd()
        else:
            print 'Book Already Exists'
    def madd(self):
        bookData = {}
        bookData['Authors'] = raw_input('Authors Name: ')
        bookData['ISBN'] = raw_input('ISBN: ')
        bookData['Language'] = raw_input('Language: ')
        bookData['Publisher'] = raw_input('Publisher: ')
        bookData['Title'] = raw_input('Title: ')
        bookData['Year'] = raw_input('Year: ')
        bookData['Date Added'] = _today()
        self.db.insert(bookData)
    def search(self, keyword):
        NewSearch = Query()
        title = self.db.search(NewSearch.Title == keyword)
        auth = self.db.search(NewSearch.Authors == keyword)
        pub = self.db.search(NewSearch.Publisher == keyword)
        isbn = self.db.search(NewSearch.ISBN == keyword)
        ttable = [title, auth, pub, isbn]

        for i in ttable:
            if i:
                print 'Matches Found for {}'.format(keyword)
                print tabulate(_concat(i), headers='keys', tablefmt="simple")
    def _blkadd(self, ISBNlist):
        with tqdm(ISBNlist) as pbar:
            for i in pbar:
                pbar.set_description("Adding %s "%i)
                self.add(i)
                pbar.update(1/len(ISBNlist)*100)
    def add_from_file(self, filename):
        with open(filename, 'rb') as f:
            raw = reader(f)
            final = list(raw)
        for i in range(len(final)):
            final[i] = str(final[i][0])
        self._blkadd(final)
        print 'Done'
    def change_title(self, isbn):
        tmp = Query()
        def change(field):
            def transform(element):
                element[field] = raw_input('Enter Title ')
            return transform
        title = self.db.search(tmp.ISBN == isbn)[0]
        print 'Change title of :- {}'.format(title['Title'])
        self.db.update(change('Title'), tmp.ISBN == isbn )
        print 'Entry Updated'
    def change_author(self, isbn):
        tmp = Query()
        def change(field):
            def transform(element):
                element[field] = raw_input('Enter Author ')
            return transform
        title = self.db.search(tmp.ISBN == isbn)[0]
        print 'Change author of :- {}'.format(title['Title'])
        self.db.update(change('Authors'), tmp.ISBN == isbn )
        print 'Entry Updated'
    def change_publisher(self, isbn):
        tmp = Query()
        def change(field):
            def transform(element):
                element[field] = raw_input('Enter Publisher ')
            return transform
        title = self.db.search(tmp.ISBN == isbn)[0]
        print 'Change Publisher of :- {}'.format(title['Title'])
        self.db.update(change('Publisher'), tmp.ISBN == isbn )
        print 'Entry Updated'
    def write_to_file(self, filename):
        try:
            data = tabulate(_concat(self.db.all()), headers='keys', tablefmt="simple")
        except AttributeError:
            print 'No database Connected'
        f = open('xlibris/' + filename + '.txt', 'w')
        f.write(data.encode('utf8'))
        f.close()
        print 'Written to {}'.format('xlibris/' + filename + '.txt')
    def purge_current(self):
        self.db.purge()
##############CONSOLE##############################
class xlibris_repl(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'xLibris>> '
        self.intro = _intro + '''A small library management system for your books written in python.
        Connect to a database and then just type the ISBN to add a book.
         Type help to find help
        Author - Shubham Bhushan
        '''
        self.current_db = xlibris()
    def do_hist(self, args):
        '''Prints the list of commands entered recently'''
        print self._hist
    def do_exit(self, args):
        '''Exists from console after you type exit'''
        return -1
    def do_EOF(self, args):
        '''Exit on EOF character'''
        return True
    def do_list_db(self, args):
        '''Lists the databases in the native folder.
        Databases are stored as .json files
        simply type list_db to view available databases'''
        # listdb += [i for i in os.listdir('xlibris/') if i.endswith('.json')]
        for i in os.listdir('xlibris/'):
            if i.endswith('.json'):
                print i
    def do_help(self, args):
        '''Get help on commands.
        type help for a list of available commands
        or help <command> for instructions on a specific command'''
        cmd.Cmd.do_help(self, args)
    def preloop(self):
        cmd.Cmd.preloop(self)
        self._hist    = []
        self._locals  = {}
        self._globals = {}
    def postloop(self):
        cmd.Cmd.postloop(self)
        print 'Exiting xLibris... '
    def precmd(self, args):
        self._hist += [args.split()]
        return args
    def do_new(self, args):
        '''Creates a new database.
        new <name> where <name> is the name of db you wish to create.'''
        self.current_db.new(args)
    def do_connect(self, args):
        '''Connect to an existing database
        connect <name of database without .json>'''
        self.current_db.connect(args)
    def do_add(self, args):
        '''Adds books to the current database.
        add <isbn> to add a book.'''
        self.current_db.add(args)
    def default(self, args):
        '''Adds the book to current database when just ISBN is typed'''
        self.current_db.add(args)
    def do_display(self, args):
        '''Prints the current database to screen'''
        self.current_db.display()
    def do_search(self, args):
        '''Searches the database for given keyword.
        Usage
        search <keyword>
        legal keywords include ISBN, author, Title. '''
        self.current_db.search(args)
    def do_addFromFile(self, args):
        '''Add books from a csv file containing ISBNs.
        type add_from_file <path/filename.csv>'''
        self.current_db.add_from_file(args)
    def do_writeToFile(self, args):
        '''write the current database in a formatted table to a file on the disk
        writeToFile <filename>'''
        self.current_db.write_to_file(args)
    def do_purgeCurrent(self, args):
        '''Purges current database. Beware.
        type purgeCurrent'''
        self.current_db.purge_current()
    def do_changeTitle(self, args):
        '''Helps you change title of the book you have added.
        changeTitle ISBN to change the title of the book'''
        self.current_db.change_title(args)
    def do_changeAuthor(self, args):
        '''Helps you change the Author of the book you have added.
        changeAuthor ISBN to change the author of the book'''
        self.current_db.change_author(args)
    def emptyline(self):
        print '''Create a new database using new or connect to existing database using connect
        or type help to see a list of available commands. You can connect to one of the following
        '''
        self.do_list_db('foo')
    def do_shell(self, args):
        '''Use shell commands by affixing them with ! sign'''
        os.system(args)
if __name__ == '__main__':
    xlibris_repl().cmdloop()
