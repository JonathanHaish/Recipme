from django.http import JsonResponse
from django.http import JsonResponse,Http404
from mysite import settings
import requests




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





def call_internal_api_view(request):
    """
    Docstring for call_internal_api_view

    """
    api_url = "internal-api-service.local" 

    headers = {
        'X-My-App-Secret-Key': settings.INTERNAL_API_SECRET_KEY
    }

    try:

        if request.method == 'GET':
            response = requests.get(api_url, headers=headers,params=request.GET)
            response.raise_for_status() 
            return response
        
        elif request.method == 'post':
            response = requests.get(api_url, headers=headers,params=request.POST)
            response.raise_for_status() 
            return response
        return Http404(f"Error:{e}")

    except requests.exceptions.RequestException as e:
        return Http404(f"Error:{e}")