from django.http import JsonResponse,HttpResponseForbidden

import logging
from mysite import settings 
from .models import FoodDataCentralAPI

logger = logging.getLogger(__name__)
    
food_api = FoodDataCentralAPI()


def get_foods_from_name(food_name) -> dict:
    """
    Docstring for get_foods_ids_from
    The function get the food name and return the food (fdcId,dataType)
    """
    results = food_api.search_ingredient(food_name)
    if not isinstance(results,list) or len(results) == 0 or not isinstance(results[0],dict):
        return {"dataType":None,"id":None}
    return {"dataType":results[0].get("dataType",""),"id":results[0].get("fdcId",0)}

def get_food_nutrition(info):
    """
    Docstring for get_food_nutrition
    The function receives a info,
    from the info it gets the name of the food and 
    then return its ingredients.
    the function get in the info the parameter 'food'-> the name of the food 
    """
    if not isinstance(info,dict):
        return {"error":"Bad Request","success":False}
     
    food_name = info.get("food")
    if not food_name:
        return {"error":"Bad Request","success":False}
    
    food = get_foods_from_name(food_name)
    if food.get("id") == None:
        return {"error":"The food not found in the system","success":False}  
    
    nutrition_data = food_api.get_food_nutrition(food.get("id"))
    if not nutrition_data:
        return {"error":"The food not found in the system","success":False} 
    
    nutritions = food_api.extract_key_nutrients(nutrition_data)
    if nutritions:
        return {"nutritions":nutritions,"succss":True}
    return {"error":"The food not found in the system","success":False}





def get_multiple_foods(info):
    """
    Docstring for get_multiple_foods
    The function receives a info with a list of foods and it 
    returns the ingredients of all the foods.
    the function get in the info the parameter 'foods'-> list of foods
    """
   
    
    if not isinstance(info,dict):
       return {"error":"Bad Request","success":False}
     
    food_names = info.get("foods")
    if not food_names or not isinstance(food_names,list):
        return {"error":"Bad Request","success":False}
    
    
    foods_id=[]
    for food_name in food_names:
        food = get_foods_from_name(food_name)
        if food.get("id"):
            foods_id.append(food.get("id"))
    
    
    return food_api.get_multiple_foods(foods_id)
    


def calculate_recipe_nutrition(info):
    """
    Docstring for calculate_recipe_nutrition
    The function receives a recipe and returns the summary of the foodNutrients.
    the function get in the info the parameter 'recipe'-> dict in the format:
    {'name':'<name of the reccipe>','foodNutrients':<list of foodNutrients(list of dicts)>} 
    """
 
    
    if not isinstance(info,dict):
       return {"error":"Bad Request","success":False}
    
   
    
    name_recipe = info.get("name")
    foodNutrients = info.get("foodNutrients")
    
    if not isinstance(name_recipe,str) or not isinstance(foodNutrients,list):
        return {"error":"Bad Request","success":False}
    
    
    list_check = [(isinstance(item,dict) and isinstance(item.get("name"),str) and isinstance(item.get("amount_grams"),int)) for item in foodNutrients]
    
    if False in list_check:
       return {"error":"Bad Request","success":False} 

    print("test")
    return food_api.extract_key_nutrients({"name":name_recipe,"foodNutrients":foodNutrients})
    

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


def api_data_view(location,key,info):
    """
    Docstring for api_data_view
    Main dispather of the requests to the API 
    check if the requests is from the application  
    """
    
    if key == settings.INTERNAL_API_SECRET_KEY:
        #get one food's nutritions
        if location == "/api/food/nutritions/":
            data = get_food_nutrition(info)
            return render_response(status=200,res=data)
        
        ##get multiple food's nutritions
        if location == "/api/foods/":
            data = get_multiple_foods(info)
            return render_response(status=200,res=data)
        
        #get recipe's nutritions
        if location == "/api/recipe/nutritions/":
            data = calculate_recipe_nutrition(info)
            return render_response(status=200,res=data)
        
        return render_response(status=404,res={})
        
    else:
        return HttpResponseForbidden("Access denied: Invalid internal key.")