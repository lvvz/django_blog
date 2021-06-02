from django.contrib import admin
from . import models as M
# Register your models here.

admin.site.register(M.BlogUser)
admin.site.register(M.BlogPost)
admin.site.register(M.Comment)
admin.site.register(M.Vote)
