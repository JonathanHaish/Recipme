from django.http import JsonResponse,HttpResponseForbidden

import logging
from mysite import settings 
from .models import FoodDataCentralAPI

logger = logging.getLogger(__name__)
    
food_api = FoodDataCentralAPI()


def render_response(status,res):
    """
    Docstring for render_response
    The function renser response after the request from the API
    """
   
    data = {
            'status': status,
            'res': res
    }
    return JsonResponse(data)



def get_foods(food_name: str):
    """
    Docstring for get_multiple_foods
    
    :param food_name: name of food for search
    """
    if not isinstance(food_name,str):
        return render_response(502,{"error":"The name of the food is string"})
    list_ingredients = food_api.search_ingredients(food_name)

    return render_response(200,list_ingredients)


def get_food_nutritions(food_id: str):
    """
    Docstring for get_food_nutritions
    
    :param food_id: Description
    :type food_id: str
    """
    if not isinstance(food_id,str):
         return render_response(502,{"error":"The name of the food is string"})   
    if not food_id.isdigit():
        return render_response(502,{"error":"The name of the food is string"})
    food_nutritions = food_api.search_food_nutritions(food_id)
    return render_response(status=200,res=food_nutritions)

def api_data_view(location,key,info):
    """
    Docstring for api_data_view
    Main dispather of the requests to the API 
    check if the requests is from the application  
    """
    
    if key == settings.API_KEY:
        if location == "/api/ingredients/":
            return get_foods(info)
        
        if location == "/api/ingredients/nutritions/":
            return get_food_nutritions(info)
        
        return render_response(status=404,res={})
        
    else:
        return HttpResponseForbidden("Access denied: Invalid internal key.")