
def make_dict(**args):  # Used to create a dictionary of the current state
    return args

def update_state(request):
    project, text, sentence, token
    request.session['query'] = request.POST.get('query', None)
    request.session['project'] = request.POST.get('project', None)
    request.session['text'] = request.POST.get('text', None)
    request.session['sentence'] = request.POST.get('sentence', None)
    request.session['token'] = request.POST.get('token', None)
    
def get_state(request):
    query = request.session.get('query')
    people = request.session.get('project')
    places = request.session.get('text')
    keywords = request.session.get('sentence')
    start_year = request.session.get('token')

    state = make_dict(*args)
    return state