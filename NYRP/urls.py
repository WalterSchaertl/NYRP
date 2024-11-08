from django.conf.urls import url

from . import views

# The url patterns for the site
urlpatterns = [
	url(r"^$", views.index, name="index"),											# The base page
	url(r"^set_up/(?P<subject>\w+)/$", views.prep, name="prep"),					# The page to select questions
	url(r"^questions/$", views.question, name="question"),							# The view for each question
	url(r"^results/$", views.view_results, name="view_results"),					# The results of the test
	url(r"^report_question/$", views.question_bug_report, name="report_question"),  # Submitting a bug report
	url(r"^error$", views.custom_error, name="custom_error"),						# Some error happened (bad cookie ext.)
	url(r"^about/$", views.about_site, name="about_site"),							# Info page about the site
	url(r"^feedback/$", views.feedback, name="give_feedback"),						# Get feedback about the site from the users
	url(r"^as_pdf/$", views.as_pdf, name="as_pdf"),									# Allow the user to print the exam
]
