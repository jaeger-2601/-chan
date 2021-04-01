'''
/board/<>?sort_by=<> - for seeing threads related to a specific board

/board/<>/thread/<>?sort_by=<> - for seeing posts related to a thread

/board/<>/thread/<>/modify - for modifying or deleting a thread

/board/<>/thread/<>/post/<> - for seeing a specific post in a thread

/board/<>/thread/<>/post/<>/modify - for modifying or deleting a post

/user/<> - for seeing user related info

/user/<>/modify - modifying user info or deleting user info'''

from flask import Blueprint, redirect, render_template, request, flash, current_app, url_for, session
from .models import Users, Boards, Threads, Posts
from .forms import ThreadForm, PostForm
from uuid import uuid4
from os.path import join as path_join
import bleach

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/board/<board_url>/<int:page_no>')
def threads(board_url, page_no):

    sort_by = request.args.get('sort_by')

    #set default sorting method
    if sort_by not in ['replies', 'upvotes']:
        sort_by = 'replies'

    bid = Boards.get(
        attributes=('BID',),
        condition='URL = %s',
        condition_vars=(board_url,),
    )
    
    if bid == []:
        flash('Board does not exist!')
        return redirect('/')
    
    bid = bid[0][0]

    threads = Threads.filter_by_board_url(
        board_url=board_url,
        sort_by=sort_by,
        offset=current_app.config['MAX_THREADS_PER_PAGE'] * (page_no-1),
        rows_no=current_app.config['MAX_THREADS_PER_PAGE']
    )

    return str(threads)

@forum_bp.route('/board/<board_url>/thread/<thread_url>')
def posts(board_url, thread_url):

    bid = Boards.get(
        attributes=('BID',),
        condition='URL = %s',
        condition_vars=(board_url,),
    )
    
    if bid == []:
        flash('Board does not exist!')
        return redirect('/')
    
    bid = bid[0][0]

    tid = Threads.get(
        attributes=('TID',),
        condition='URL = %s',
        condition_vars=(thread_url,),
    )
    
    if tid == []:
        flash('Thread does not exist!')
        return redirect('/')

    posts = Posts.filter_by_thread_url(thread_url=thread_url)
    return str(posts)

@forum_bp.route('/board/<board_url>/thread/<thread_url>/post/<post_url>')
def post(board_url, thread_url, post_url):
    
    bid = Boards.get(
        attributes=('BID',),
        condition='URL = %s',
        condition_vars=(board_url,),
    )
    
    if bid == []:
        flash('Board does not exist!')
        return redirect('/')
    
    bid = bid[0][0]

    tid = Threads.get(
        attributes=('TID',),
        condition='URL = %s',
        condition_vars=(thread_url,),
    )
    
    if tid == []:
        flash('Thread does not exist!')
        return redirect('/')
    
    post = Posts.filter_by(
        condition='URL = %s',
        condition_vars=(post_url,)
    )

    return str(post)
    
@forum_bp.route('/board/<board_url>/create_thread', methods=['GET', 'POST'])
def make_thread(board_url):
    
    form = ThreadForm()

    bid = Boards.get(
                attributes=('BID',),
                condition='URL = %s',
                condition_vars=(board_url,),
            )
    
    if bid == []:
        flash('Board does not exist!')
        return redirect('/')
    
    bid = bid[0][0]

    if form.validate_on_submit():

        filename = None
        

        if form.pic.data != None:
            ext =  form.pic.data.filename.rsplit('.', 1)[1].lower()
            filename = path_join(
                current_app.config['IMG_UPLOADS_DIR'], 
                'thread', 
                f'{str(uuid4())}.{ext}'
            )

            #save the image 
            form.pic.data.save(path_join('app', filename))
        
        Threads.add(
            URL=str(uuid4()),
            TITLE=bleach.clean(form.title.data),
            DESCRIPTION=bleach.clean(form.description.data),
            PIC= filename,
            BID=bid,

            UID=session.get('user', None)['uid']
        )

        flash('Thread created successfully!')
        return redirect(url_for('forum.posts'), board_url=board_url, thread_url=thread_url)
        

    return render_template('make_thread.html', form=form)

@forum_bp.route('/board/<board_url>/thread/<thread_url>/create_post', methods=['GET', 'POST'])
def make_post(board_url, thread_url):

    form = PostForm()

    bid = Boards.get(
                attributes=('BID',),
                condition='URL = %s',
                condition_vars=(board_url,),
            )
    
    if bid == []:
        flash('Board does not exist!')
        return redirect('/')
    
    bid = bid[0][0]

    tid = Threads.get(
                attributes=('TID',),
                condition='URL = %s',
                condition_vars=(thread_url,),
            )
    
    if tid == []:
        flash('Thread does not exist!')
        return redirect('/')
    
    tid = tid[0][0]


    if form.validate_on_submit():

        filename = None

        if form.pic.data != None:
            ext =  form.pic.data.filename.rsplit('.', 1)[1].lower()
            filename = path_join(
                current_app.config['IMG_UPLOADS_DIR'], 
                'post', 
                f'{str(uuid4())}.{ext}'
            )

            #save the image 
            form.pic.data.save(path_join('app', filename))


        Posts.add(
            URL=str(uuid4()),
            TEXT=bleach.clean(bleach.linkify(form.text.data)),
            PIC= filename,
            TID=tid,
            UID=session.get('user', None)['uid']
        )

        flash('Post created successfully!')
        return redirect(url_for('forum.posts', board_url=board_url, thread_url=thread_url))

    return render_template('make_post.html', form=form)