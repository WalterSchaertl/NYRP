from django.contrib import admin
from . import models


# Registers the models to the admin site
admin.site.register(models.Question)
admin.site.register(models.Hint)
admin.site.register(models.Group)
admin.site.register(models.Selector)
admin.site.register(models.QuestionBug)
admin.site.register(models.Feedback)
