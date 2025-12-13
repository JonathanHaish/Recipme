from django.http import JsonResponse,HttpResponseForbidden

import logging
from mysite import settings 
from .models import FoodDataCentralAPI

logger = logging.getLogger(__name__)
    
        

def get_food_nutrition(request):
    """
    Docstring for get_food_nutrition
    The function receives a request,
    from the request it gets the name of the food and 
    then returns its ingredients.
    the function get in the request.GET the parameter 'food'-> the name of the food 
    """
   
    
    if request.method != 'GET':
       return {"error":"Bad Request","success":False}
     
    food_name = request.GET.get("food")
    if not food_name:
        return {"error":"Bad Request","success":False}
    
    food = FoodDataCentralAPI()
    nutrition = food.get_food_nutrition(food_name)
    if nutrition:
        return {"nutrition":nutrition,"succss":True}
    return {"error":"The food not found in the system","success":False}





def get_multiple_foods(request):
    """
    Docstring for get_multiple_foods
    The function receives a request with a list of foods and it 
    returns the ingredients of all the foods.
    the function get in the request.GET the parameter 'foods'-> list of foods
    """
   
    
    if request.method != 'GET':
       return {"error":"Bad Request","success":False}
     
    food_names = request.GET.get("foods")
    if not food_names or not isinstance(food_names,list):
        return {"error":"Bad Request","success":False}
    
    return FoodDataCentralAPI().get_multiple_foods(food_names)
    


def calculate_recipe_nutrition(request):
    """
    Docstring for calculate_recipe_nutrition
    The function receives a recipe and returns the summary of the foodNutrients.
    the function get in the request.GET the parameter 'recipe'-> dict in the format:
    {'name':'<name of the reccipe>','foodNutrients':<list of foodNutrients(list of strings)>} 
    """
 
    
    if request.method != 'GET':
       return {"error":"Bad Request","success":False}
    
    recipe = request.GET.get("recipe")
    if not recipe or not isinstance(recipe,dict):
        return {"error":"Bad Request","success":False}
    
    name_recipe = recipe.get("name")
    foodNutrients = recipe.get("foodNutrients")
    if not isinstance(name_recipe,str) or not isinstance(foodNutrients,list):
        return {"error":"Bad Request","success":False}
    
    return FoodDataCentralAPI().extract_key_nutrients({"name":name_recipe,"foodNutrients":[item if isinstance(item,str) else "" for item in foodNutrients]})
    

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


def api_data_view(request):
    """
    Docstring for api_data_view
    Main dispather of the requests to the API 
    check if the requests is from the application  
    """
    
    secret_key = request.META.get("HTTP_X_MY_APP_SECRET_KEY")
    if secret_key == settings.INTERNAL_API_SECRET_KEY:

        #get one food's nutritions
        if request.path == "/api/food/":
            data = get_food_nutrition(request)
            return render_response(status=200,res=data)
        
        ##get multiple food's nutritions
        if request.path == "/api/foods/":
            data = get_multiple_foods(request)
            return render_response(status=200,res=data)
        
        #get recipe's nutritions
        if request.path == "/api/recipe/nutrition/":
            data = calculate_recipe_nutrition(request)
            return render_response(status=200,res=data)
        
        return render_response(status=404,res={"success":False})
        
    else:
        return HttpResponseForbidden("Access denied: Invalid internal key.")