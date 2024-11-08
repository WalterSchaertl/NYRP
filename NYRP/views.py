from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import *
from .models import Question, Selector
import random


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
	:return: A HTTPResponse object, the rendering of the prep.html page with the question selection form, or a pdf if
	they want to see a pdf.
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
									  "by_unit" in request.POST or "by_unit_pdf" in request.POST,
									  form.cleaned_data.get("max_qs"),
									  form.cleaned_data.get("diagram_qs")
									  )
			# Store the primary key for the selector in the session cookies
			request.session["sel_pk"] = select.pk
			# Alerts the user if there aren't any questions for what they selected and retry
			if select.questions.count() < 1:
				messages.error(request, "Oops! They're aren't any questions with those criteria!")
				form = SelectorForm(request.POST, req=request.POST, subject=bd_subject)
				return render(request, "NYRP/prep.html", {"form": form, "title": subject.replace("_", " ")})
			# If everything was a success, and the user wants a pdf, display that
			if form.is_pdf:
				# TODO should this be part of the selector?
				request.session["with_answer"] = form.cleaned_data.get("with_answer")
				request.session["exam_with_version"] = form.cleaned_data.get("exam_with_version")
				request.session["fill_in_key"] = form.cleaned_data.get("fill_in_key")
				request.session["max_img_height"] = form.cleaned_data.get("max_img_height")
				return redirect("as_pdf")
			# Else start displaying the questions
			request.session["disallow_retry"] = form.cleaned_data.get("disallow_retry")
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
			select.record += "" + str(question.pk) + " True False " + select.choice_history + ", "
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
			select.record += "" + str(question.pk) + " False True " + select.choice_history + ", "
			select.correct = True
			select.save()
			# move on to the next question
			if request.session["disallow_retry"]:
				select.index += 1
				select.choice_history = ""
				select.correct = False
				select.save()
		# Answered incorrectly
		elif request.POST.get("answer") != "":
			select.choice_history += request.POST.get("answer")
			select.correct = False
			select.save()
			# move on to the next question
			if request.session["disallow_retry"]:
				select.record += "" + str(question.pk) + " False False " + select.choice_history + ", "
				select.index += 1
				select.choice_history = ""
				select.correct = False
				select.save()
		return redirect("question")

	ref_table = question.subject + "Ref.pdf" if question.subject in settings.REQUIRES_REF_TABLE else None
	# This is atypical, but the question diagrams are stored as static files, not under media
	# However, they will never change and are only 'uploaded' by a admin, and should only happen
	# once, so they are more like static than dynamic, but are associated to questions.

	# Context used for the template
	context = {"question"	: question,									 # The question
				"total"		: total_q,									 # The total number of questions
				"index"		: select.index + 1,							 # Where the user is in that list
				"correct"	: select.correct,							 # If they're previous answer was correct
				"prev_ans"	: select.choice_history,					 # What they answered previously
				"percent"	: int(round(select.index / total_q * 100)),	 # What percent they've done
				"static_url": question.diagram.url[1:] if question.diagram else "",  # The questions diagram
				"ref_table" : ref_table}								 # The reference table (if required)

	return render(request, "NYRP/question.html", context)


def as_pdf(request):
	"""
	Displays the selected questions as a pdf file
	"""
	# Get the selector from the cookies
	try:
		select = Selector.objects.get(pk=request.session.get("sel_pk"))
	except ObjectDoesNotExist:
		return redirect("custom_error")
	human_readable_subject = select.subject
	for tuple in settings.SUBJECTS:
		if tuple[0] == select.subject:
			human_readable_subject = tuple[1]
	context = {
		"questions": select.questions.all().order_by('?'),
		"subject": human_readable_subject,
		"midpoint": (int)(len(select.questions.all()) / 2),
		"with_answer": request.session["with_answer"],
		"fill_in_key": request.session["fill_in_key"],
		"max_img_height": request.session["max_img_height"]
	}
	if request.session["exam_with_version"]:
		context["exam_with_version"] = "{:04d}".format(random.randrange(0, 1000))
	return render(request, "NYRP/print_view.html", context=context)

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
	units = settings.SUPPORTED_TOPICS[select.subject][settings.UNITS]
	total = len(record)		# The total number of questions
	total_missed = 0		# Total questions missed
	total_correct = 0
	trys = [0, 0, 0, 0]		# Holds the data of number or questions answered on the 1st, 2ed, 3rd, and 4th try
	num_skipped = 0			# The number of questions skipped

	unit_total			= [0 for _ in units]  # Total number of questions per unit
	num_miss_by_unit 	= [0 for _ in units]  # Total number of questions missed by unit
	num_skiped_by_unit	= [0 for _ in units]  # Total number of questions skipped by unit
	incorrect_question_pks = []
	incorrect_answer_history = []

	# For each question history in the records, provided at least one exists, compute the statistics
	if str(record[0]) != "":
		for x in record:
			data = x.split(" ")
			q_pk = data[0]												# The question
			skipped = data[1]											# If it was skipped
			was_correct = data[2]										# If the user got it right
			answers = data[3] if len(data) > 3 else list()				# What the user answered
			unit_total[Question.objects.get(pk=q_pk).unit - 1] += 1		# Tracking questions by unit

			# If the question wasn't skipped
			if skipped == "False":
				# Track the number of attempts for each attempt
				trys[len(answers) - 1] += 1
				# If it was also incorrect
				if was_correct == "False":
					incorrect_question_pks.append(q_pk)
					incorrect_answer_history.append(answers)
				else:
					total_correct += 1
			else:
				num_skipped += 1

			# If got one wrong or skipped it, register that the unit was in err
			if skipped == "True" or was_correct == "False":
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

	# Questions and answers zipped together because Django doesn't allow variable indexing, this allows iterating both at once
	context = {	"missed_questions"	: zip(Question.objects.filter(pk__in=incorrect_question_pks).order_by("unit"), incorrect_answer_history),
				"units"				: units,
				"total"				: total,
				"total_missed"		: total_missed,
				"total_correct"		: total_correct,
				"percent_correct"	: int(total_correct / total * 100),
				"disallow_retry"	: request.session["disallow_retry"],
				"miss_by_unit"		: num_miss_by_unit,
				"trys"				: trys,
				"total_skipped"		: num_skipped,
				"num_skiped_by_unit": num_skiped_by_unit}
	return render(request, "NYRP/result.html", context)


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


def about_site(request):
	"""
	The about page for information about the website and author

	:param request: A HTTPRequest object for the client about page
	:return: A HTTPResponse object, the rendering of the about.htm
	"""
	return render(request, "NYRP/about.html")


def feedback(request):
	"""
	Get feedback from the user
	"""
	return render(request, "NYRP/feedback.html")
