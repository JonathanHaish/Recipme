from django.http import JsonResponse
from django.http import JsonResponse,Http404
from mysite import settings
from api_management.views import api_data_view
import json

def call_internal_api_view(location,info):
    """
    Docstring for call_internal_api_view
    The function get:
        location - option how to use in the API
        info - the request parameters as dict

    the options are:
    Location:
       1) /api/food/nutritions/ -> Getting the ingredients of food 
       2) /api/foods/ -> Getting the ingredients of multiple foods
       3) /api/recipe/nutritions/ -> Getting the nutritions of recipe
    Info format according the location option:
        1 -> {'food':<str name of the food>}
        2 -> {'foods':<List of strings(names of the food)>}
        3 -> {'name':<str name of the recipe>,'foodNutrients':<List of Dicts -> list of {'name':'<name of food>','amount_grams':<number>}
    """
    key = settings.INTERNAL_API_SECRET_KEY
    return api_data_view(location,key,info)
    




def testAPI(request):
    
    info = request.GET if request.method == 'GET' else request.POST
    location = info.get("path")
    data = json.loads(info.get("data"))
    return call_internal_api_view(location,data)




def root_view(request):
    """Root API endpoint"""
    return JsonResponse({
        'message': 'Welcome to Recipme API',
        'status': 'success',
        'endpoints': {
            'example': '/example/',
            'admin': '/admin/'
        }
    })

def example_view(request):
    """Example API endpoint that returns some example text"""
    return JsonResponse({
        'message': 'Hello from Django! This is an example API endpoint.',
        'status': 'success'
    })






