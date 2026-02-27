import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard import app as application

def handler(request):
    return application(request.environ, application.start_response)
