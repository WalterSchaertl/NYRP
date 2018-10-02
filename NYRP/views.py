from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import *
from .models import Question, Selector


def index(request):
	"""
	The view for the index with different subjects to pick from.

	:param request: A HTTPRequest object for the landing page
	:return: A HTTPResponse object, the rendering of the index.html page
	"""
	return render(request, "NYRP/index.html")


def prep(request, subject):
	"""
	The view for selecting questions

	:param request: A HTTPRequest object for the page to select questions
	:param subject: The subject the user wants, specified by the url
	:return: A HTTPResponse object, the rendering of the prep.html page with the question selection form
	"""

	# Changing URL friendly parameter to database parameter and template title
	bd_subject = "ERRO"		# If none of the subjects match it, there was an error

	# Match the subject up with what the database uses
	for i in range(0, len(settings.SUBJECTS)):
		if subject.replace("_", " ").lower() == settings.SUBJECTS[i][1].lower():
			bd_subject = settings.SUBJECTS[i][0]
			# print("Title " + settings.SUBJECTS[i][1] + " with subject " + bd_subject)

	# If the user submitted the form
	if request.method == "POST":
		# Create the form based on the request and subject (see forms.py)
		form = SelectorForm(request.POST, req=request.POST, subject=bd_subject)

		# If the form is valid and filled out correctly
		if form.is_valid():
			# Creates a selector object to get questions by
			select = Selector.objects.create(index=0, subject=bd_subject)
			# Populates the questions based on the user form and how it was submitted
			select.populate_questions(form.cleaned_data.get("units"),
									  form.cleaned_data.get("exams"),
									  "by_unit" in request.POST)
			# Store the primary key for the selector in the session cookies
			request.session["sel_pk"] = select.pk
			# Alerts the user if there aren't any questions for what they selected and retry
			if select.questions.count() < 1:
				messages.error(request, "Oops! They're aren't any questions with those criteria!")
				form = SelectorForm(request.POST, req=request.POST, subject=bd_subject)
				return render(request, "NYRP/prep.html", {"form": form, "title": subject.replace("_", " ")})
			# If everything was a success, start displaying the questions
			return redirect("question")
		else:
			errors = form.errors.as_data()
			if errors.get("exams") is not None:
				messages.error(request, "If you pick questions by exam, you must select at least one exam.")
			if errors.get("units") is not None:
				messages.error(request, "If you pick questions by unit, you must select at least one unit.")
	# Otherwise, show them a form
	else:
		form = SelectorForm(req=request.POST, subject=bd_subject)
	# Adding the form and the title to the context
	return render(request, "NYRP/prep.html", {"form": form, "title": subject.replace("_", " ")})


def question(request):
	"""
	The view that handles the questions.

	:param request: A HTTPRequest object for the question view
	:return: A HTTPResponse object, the rendering of the question.html page for each question
	"""

	# Get the selector from the cookies
	try:
		select = Selector.objects.get(pk=request.session.get("sel_pk"))
	except ObjectDoesNotExist:
		return redirect("custom_error")
	# Get the next question
	question = select.get_question()
	# Get the total questions
	total_q = select.questions.count()
	# If there are no more questions, go to results
	if question is None:
		return redirect("view_results")

	# If the user is submitting a question
	if request.method == "POST":
		# Answered correctly previously, and the user has the option to move on
		if "continue" == request.POST.get("answer"):
			select.index += 1
			select.choice_history = ""
			select.correct = False
			select.save()
		# If user wants to skip the question instead of submitting
		elif "skip" in request.POST:
			select.index += 1
			# Add that the user skipped the question
			select.record += "" + str(question.pk) + " True " + select.choice_history + ", "
			select.choice_history = ""
			select.correct = False
			select.save()
		# User ended the practice early
		elif "end" in request.POST:
			return redirect("view_results")
		# User answer the question correctly (Will now be given the option to continue and remove skip)
		elif question.ans.lower() == request.POST.get("answer"):
			# Adds a record for the question's pk, if it was skipped, and the sequence of answers entered
			select.choice_history += request.POST.get("answer")
			select.save()
			select.record += "" + str(question.pk) + " False " + select.choice_history + ", "
			select.correct = True
			select.save()
		# Answered incorrectly
		elif request.POST.get("answer") != "":
			select.choice_history += request.POST.get("answer")
			select.correct = False
			select.save()
		return redirect("question")

	# Context used for the template
	context = {"question"	: question,									 # The question
				"total"		: total_q,									 # The total number of questions
				"index"		: select.index + 1,							 # Where the user is in that list
				"correct"	: select.correct,							 # If they're previous answer was correct
				"prev_ans"	: select.choice_history,					 # What they answered previously
				"percent"	: int(round(select.index / total_q * 100))}	 # What percent they've done

	return render(request, "NYRP/question.html", context)


# TODO convert lists to dictionaries to improve readability
def view_results(request):
	"""
	The view to see the results, questions answered/skipped, percent correct, and missed by unit.

	:param request: A HTTPRequest object for the results view
	:return: A HTTPResponse object, the rendering of the result.html page with the results
	"""

	# Getting the selector
	try:
		select = Selector.objects.get(pk=request.session.get("sel_pk"))
	except ObjectDoesNotExist:
		return redirect("custom_error")

	record = [x.strip(" ") for x in select.record[:len(select.record) - 2].split(",")]
	num_units = len(eval(select.subject + "_UNITS"))
	total = len(record)		# The total number of questions
	total_missed = 0		# Total questions missed
	trys = [0, 0, 0, 0]		# Holds the data of number or questions answered on the 1st, 2ed, 3rd, and 4th try
	num_skipped = 0			# The number of questions skipped

	unit_total			= [0 for x in range(num_units)]  # Total number of questions per unit
	num_miss_by_unit 	= [0 for x in range(num_units)]  # Total number of questions missed by unit
	num_skiped_by_unit	= [0 for x in range(num_units)]  # Total number of questions skipped by unit

	# For each question history in the records, provided at least one exists, compute the statistics
	if str(record[0]) != "":
		for x in record:
			data = x.split(" ")
			q_pk = data[0]												# The question
			skipped = data[1]											# If it was skipped
			if skipped == "False":										# If it wasn't skipped
				answers = data[2]										# How it was answered
			unit_total[Question.objects.get(pk=q_pk).unit - 1] += 1		# Tracking questions by unit

			# If the question wasn't skipped
			if skipped == "False":
				# Track the number of attempts for each attempt
				trys[len(answers) - 1] += 1
			else:
				num_skipped += 1

			# If got one wrong or skipped it, register that the unit was in err
			if skipped == "True" or len(answers) > 1:
				total_missed += 1
				unit = Question.objects.get(pk=q_pk).unit
				num_miss_by_unit[unit - 1] += 1
				if skipped == "True":
					num_skiped_by_unit[unit - 1] += 1

	# Printing the Statistics for debugging
	# print("The record:                          " + str(record))
	# print("Total questions by unit:             " + str(unit_total))
	# print("Total questions missed by unit:      " + str(num_miss_by_unit))
	# print("Total questions skiped by unit:      " + str(num_skiped_by_unit))
	# print("Number of 1st, 2ed, 3rd, 4th tries:  " + str(trys))
	# print("Total number of questions skipped:   " + str(num_skipped))
	# print("Percent correct:                     " + str(trys[0] / total * 100))
	context = {"total"				: total,
				"total_missed"		: total_missed,
				"percent_correct"	: int(trys[0] / total * 100),
				"miss_by_unit"		: num_miss_by_unit,
				"trys"				: trys,
				"total_skipped"		: num_skipped,
				"num_skiped_by_unit": num_skiped_by_unit}
	return render(request, "NYRP/result.html", context)


def make_qs(request):
	"""
	For ease of database population, makes question models in large batches\
	"""

	for i in range(0, 20):
		question = Question.objects.create(subject="CHEM", month="January", year=2017, unit=12)
		question.save()
	return HttpResponse("made.")


def question_bug_report(request):
	"""
	View for submitting a bug report.

	:param request: A HTTPRequest object for the results view
	:return: A HTTPResponse object, the rendering of the question_problem.html page with the results
	"""

	if request.method == "POST":
		# Getting the selector
		try:
			select = Selector.objects.get(pk=request.session.get("sel_pk"))
		except ObjectDoesNotExist:
			return redirect("custom_error")

		form = QuestionBugForm(request.POST)
		if form.is_valid():
			bug = form.save(commit=False)
			bug.question = select.get_question()
			bug.save()
			messages.error(request, "Bug Report submitted successfully, thank you!")
			return redirect("question")
	else:
		form = QuestionBugForm()
	return render(request, "NYRP/question_problem.html", {"form": form})


def custom_error(request):
	"""
	Django is currently handling the generic errors (500, 404). This is a custom error in the case that
	a required cookie was not allowed, deleted, or malformed.

	:param request: A HTTPRequest object for the client error view
	:return: A HTTPResponse object, the rendering of the custom_error.html page with an error message
	"""

	if "sel_pk" not in request.session.keys():
		error_message = "The session ID could not be obtained from the cookies. Make sure cookies are allowed " \
						" and try selecting questions again."
	elif type(request.session.get("sel_pk")) is not int:
		error_message = "The session ID is malformed, please try selecting questions again."
	else:
		try:
			Selector.objects.get(pk=request.session.get("sel_pk"))
			error_message = "An unknown error has occurred."
		except ObjectDoesNotExist:
			error_message = "No data could be found for your session, please try selecting questions again."

	return render(request, "NYRP/custom_error.html", {"code": 400, "message": error_message})
