from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited
import json
import pprint
from rest_framework import status

# This is necessary to handle the "Ratelimited" exception that django-ratelimit raises.
# The purpose of this middleware is to allow the django-ratelimit package & @ratelimit decorator
# to be able to rate limit functions and not just view functions.
# if a ratelimited function is called insideof a view function the provided tools
# cannot catch the "Ratelimited" (403 error) which the django-ratelimit raises. 
# As a workaround if wrs_api returns a generic 403,
# this middleware will convert it to a 429 response.
# Note: this means other 403s will need to have text different from the below check:
class Custom403to429Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Custom Middleware: 403 to 429 check.")

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        # print(response.content)
        # print(type(response.content))
        # Code to be executed for each request/response after
        # the view is called.
        if response.status_code == 403:

            error_message = json.dumps(response.data)
            default_403_message = '{"detail": "You do not have permission to perform this action."}'
            if error_message == default_403_message:
                print("403 converted to 429")

                error_429 = {
                            "status": 
                                {
                                    "status_code": 429,
                                    "message": f"Too many requests sent to Riot servers. Please Retry in 20 seconds",
                                    "retry_after": int(20)
                                },
                            "meta": "WR.GG enforced."
                        }

                print("403 converted to 429")
                return JsonResponse(error_429, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
        return response
        

