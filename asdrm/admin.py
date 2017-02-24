from django.contrib import admin

from .models import Auth
from .models import TestCase
from .models import TestParameter
from .models import TestStatus
from .models import TestSuite
from .models import TestAnalysis

# Register your models here.
admin.site.register(Auth)
admin.site.register(TestCase)
admin.site.register(TestParameter)
admin.site.register(TestStatus)
admin.site.register(TestSuite)
admin.site.register(TestAnalysis)