from django.http import JsonResponse
from django.http import JsonResponse,Http404,HttpResponseForbidden
from mysite import settings
from api_management.views import api_data_view
import json

def call_internal_api_view(location,info):
    """
    Docstring for call_internal_api_view
    The function get:
        location - option how to use in the API
        info - the parameters

    the options are:
    Location:
        1) api/ingredients/ ->  get list of options(types) of the food: [{"id":fdc_id,"name":description,"category":category,"description":brand,"fat_str":fat_str}...]
        2) api/ingredients/nutritions/ -> get the nutritions of the food:
        {
            "Protein": "protein",
            "Total lipid (fat)": "fat",
            "Carbohydrate, by difference": "carbohydrates",
            "Energy": "calories",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugars"
        }
    info:
    1 -> string of name of the food
    2 -> ID of the food according the fdc.nal.usda.gov 
      
    """
    key = settings.API_KEY
    return api_data_view(location,key,info)
    




def callAPI(request):
    info = request.GET if request.method == 'GET' else request.POST
    location = request.path
    data = info.get("data")
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






