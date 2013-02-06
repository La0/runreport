from helpers import render


@render('run/index.html')
def index(request):
  return {
    'run' : 'plop',
  }
