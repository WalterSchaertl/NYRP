from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .forms import SelectorForm, QuestionBugForm
from django.conf import settings
from .models import Question, Selector
from django.contrib import messages

'''
The view for the index with different subjects to pick from
'''
def index(request):
	return render(request, 'NYRP/index.html')

'''
The view for selecting questions
Subject:	The subject the user wants, specified by the url
'''
def prep(request, subject):
	# Changing URL friendly parameter to database parameter and template title
	bd_subject = "ERRO"		# If none of the subjects match it, there was an error
	# Match the subject up with what the database uses
	for i in range(0, len(settings.SUBJECTS)):
		if subject.replace("_", " ").lower() == settings.SUBJECTS[i][1].lower():
			bd_subject = settings.SUBJECTS[i][0]
			# print("Title " + settings.SUBJECTS[i][1] + " with subject " + bd_subject)

	# If the user submitted the form
	if request.method == 'POST':
		# Create the form based on the request and subject (see forms.py)
		form = SelectorForm(request.POST, req=request.POST, subject=bd_subject)
		# If the form is valid and filled out correctly
		if form.is_valid():
			# Creates a selector object to get questions by
			select = Selector.objects.create(index = 0, subject=bd_subject)
			# Populates the questions based on the user form and how it was submitted
			select.populate_questions(form.cleaned_data.get('units'), form.cleaned_data.get('exams'), "by_unit" in request.POST)
			# Store the primary key for the selector in the session cookies
			request.session['sel_pk'] = select.pk
			# Alerts the user if there arn't any questions for what they selected and retry
			if select.questions.count() < 1:
				messages.error(request, "Oops! They're arn't any questions with those criteria!  Go try out Chemistry!")
				form = SelectorForm(request.POST, req=request.POST, subject=bd_subject)
				return render(request, 'NYRP/prep.html', {'form': form, 'title':subject.replace("_", " ")})
			# If everything was a success, start displaying the questions
			return redirect('question')
	# Otherwise, show them a form
	else:
		form = SelectorForm(req=request.POST, subject=bd_subject)
	#Adding the form and the title to the context
	return render(request, 'NYRP/prep.html', {'form':form, 'title':subject.replace("_", " ")})

'''
The view that handles the questions
'''
def question(request):
	# Get the selector from the cookies
	select = Selector.objects.get(pk=request.session.get('sel_pk'))
	# Get the next question
	question = select.get_question()
	# Get the total questions
	total_q = select.questions.count()
	# If there are no more questions, go to results
	if question is None:
		return redirect('view_results')

	# If the user is submitting a quesion
	if request.method == "POST":
		# Answered correctly previously, and the user has the option to move on
		if "continue" == request.POST.get('answer'):
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
			return redirect('view_results')
		# User answer the question correctly (Will now be given the option to continue and remove skip)
		elif question.ans.lower() == request.POST.get('answer'):
			# Adds a record for the question's pk, if it was skipped, and the sequence of answers entered
			select.choice_history += request.POST.get('answer')
			select.save()
			select.record += "" + str(question.pk) + " False " + select.choice_history + ", "
			select.correct = True
			select.save()
		# Answerd incorrectly
		elif request.POST.get('answer') != "":
			select.choice_history += request.POST.get('answer')
			select.correct = False
			select.save()
		return redirect('question')

	# Context used for the template
	context = {"question"	: question,									# The question
				"total"		: total_q,									# The total number of questions
				"index"		: select.index + 1,							# Where the user is in that list
				"correct"	: select.correct,							# If they're previous answer was correct
				"prev_ans"	: select.choice_history,						# What they answered previously
				"percent"	: int(round(select.index / total_q * 100))}	# What percent they've done

	return render(request, "NYRP/question.html", context)

'''
The view to see the results of the tests
'''
def view_results(request):
	# Getting the selector
	select = Selector.objects.get(pk=request.session.get('sel_pk'))
	record = [x.strip(' ') for x in select.record[:len(select.record) - 2 ].split(',')]
	total = len(record)		# The total number of questions
	total_missed = 0		# Total questions missed
	trys = [0, 0, 0, 0]		# Holds the data of number or questions answered on the 1st, 2ed, 3rd, and 4th try
	num_skipped = 0			# The number of questions skipped

	unit_total			= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]		# Total number of questions per unit
	num_miss_by_unit 	= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]		# Total number of questions missed by unit
	num_skiped_by_unit	= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]		# Total number of questions skipped by unit

	# For each question history in the records, provided at least one exists, compute the statistics
	if str(record[0]) != "":
		for x in record:
			data = x.split(' ')
			q_pk = data[0]												# The question
			skipped = data[1]											# If it was skipped
			if skipped != "True":										# If it wasn't skipped
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
				if skipped == 'True':
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

'''
#For debugging only, makes question models in large groups
'''
def make_qs(request):
	for i in range(0,20):
		question = Question.objects.create(subject="CHEM", month="January", year=2017, unit=12)
		question.save()
	return HttpResponse("made.")

'''
View for submitting a bug report
'''
def question_bug_report(request):
	if request.method == "POST":
		form = QuestionBugForm(request.POST)
		if form.is_valid():
			bug = form.save(commit=False)
			bug.question = Selector.objects.get(pk=request.session.get('sel_pk')).get_question()
			bug.save()
			return redirect('question')
	else:
		form = QuestionBugForm()
	return render(request, "NYRP/question_problem.html", {"form":form})
