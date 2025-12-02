from django.http import JsonResponse

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

