# from django.http import JsonResponse,HttpResponseForbidden

# import logging
# from mysite import settings 
# from .models import FoodDataCentralAPI

# logger = logging.getLogger(__name__)
    
# food_api = FoodDataCentralAPI()


# def render_response(status,res):
#     """
#     Docstring for render_response
#     The function renser response after the request from the API
#     """
   
#     data = {
#             'status': status,
#             'res': res
#     }
#     return JsonResponse(data)



# def get_foods(food_name: str):
#     """
#     Docstring for get_multiple_foods
    
#     :param food_name: name of food for search
#     """
#     if not isinstance(food_name,str):
#         return render_response(502,{"error":"The name of the food is string"})
#     list_ingredients = food_api.search_ingredients(food_name)

#     return render_response(200,list_ingredients)


# def get_food_nutritions(food_id: str):
#     """
#     Docstring for get_food_nutritions
    
#     :param food_id: food id
    
#     """
#     if not isinstance(food_id,str):
#          return render_response(502,{"error":"The name of the food is string"})   
#     if not food_id.isdigit():
#         return render_response(502,{"error":"The name of the food is string"})
#     food_nutritions = food_api.search_food_nutritions(food_id)
#     return render_response(status=200,res=food_nutritions)

# def api_data_view(location,key,info):
#     """
#     Docstring for api_data_view
#     Main dispather of the requests to the API 
#     check if the requests is from the application  
#     """
    
#     if key == settings.API_KEY:
#         if location == "/api/ingredients/":
#             return get_foods(info)
        
#         if location == "/api/ingredients/nutritions/":
#             return get_food_nutritions(info)
        
#         return render_response(status=404,res={})
        
#     else:
#         return HttpResponseForbidden("Access denied: Invalid internal key.")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import FoodDataCentralAPI
from .serializers import  IngredientSearchResponseSerializer
from .premissions import IsInternalApp

food_api = FoodDataCentralAPI(api_key=settings.API_KEY)

class FoodIngredientView(APIView):
    permission_classes = [IsInternalApp] 
    def get(self, request):
        location = request.query_params.get('location')
        info = request.query_params.get('info')

        # בדיקה בסיסית של פרמטרים
        if not info:
            return Response({
                "status": 400,
                "success": False,
                "error": "Missing info parameter"
            }, status=status.HTTP_400_BAD_REQUEST)

        # לוגיקת חיפוש רכיבים
        if location == "/api/ingredients/":
            results = food_api.search_ingredients(info)
            
            # בניית האובייקט עבור הסריליאזר העוטף
            response_data = {
                'status': 200,
                'success': True,
                'res': results  # רשימת ה-taglines מה-API שלך
            }
            
            serializer = IngredientSearchResponseSerializer(response_data)
            return Response(serializer.data)

        # לוגיקת ערכים תזונתיים
        elif location == "/api/ingredients/nutritions/":
            if not info.isdigit():
                return Response({
                    "status": 400, "success": False, "error": "Invalid ID"
                }, status=400)
            
            nutritions = food_api.search_food_nutritions(info)
            return Response({
                "status": 200,
                "success": True,
                "res": nutritions # כאן res יהיה אובייקט תזונה ולא רשימת מוצרים
            })

        return Response({
            "status": 404, "success": False, "error": "Location not found"
        }, status=404)