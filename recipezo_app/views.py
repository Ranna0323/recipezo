from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def post_view(request):
    return render(request, 'post.html')


def get_post(request):
    if request.method == 'GET':
        ingredient = request.GET['ingredient']
        data = {
            'data': ingredient,
        }
        return render(request, 'parameter.html', data)

    elif request.method == 'POST':
        ingredient = request.POST['ingredient']
        data = {
            'ingredient': ingredient,
        }

        print(data["ingredient"])

        return render(request, 'parameter.html', data)