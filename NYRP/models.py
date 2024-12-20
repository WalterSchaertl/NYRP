from django.utils.timezone import now
from django.db import models
from django.utils import timezone
from django.conf import settings

# A constant the defines the different choices the user has when submitting a bug
QUESTION_BUG_CHOICES = (("1", "This question doesn't belong in this topic."),
						("2", "This question doesn't belong in this unit."),
						("3", "The given answer is incorrect."),
						("4", "There is a formatting/typo error in the question."),
						("5", "Other (please specify below)."))


class Question(models.Model):
	"""
	The model for a question object, a Question object has:
	Question: 			Text: A string that is the question
	Answers Choices: 	Text: 5 different options to answer (A-E)
	Ans					Text: The correct answer to the question
	Subject: 			Text: The subject it belongs to
	Month:				Text: The Month is was published
	Year:				Int:  The year it was published
	Unit:				Int:  The unit number of the quesion
	Group				Foreign Key: If this question belongs to a set, the questions will all share a group
	Hint				Foreign Key: A relation to a hint for the question
	Diagram:			File: A PNG file that goes with the question
	Group, Hint, and Diagram are not applicable to all questions
	"""

	question = models.CharField(max_length=500, blank=True)
	A   	 = models.CharField(max_length=200, blank=True)
	B		 = models.CharField(max_length=200, blank=True)
	C		 = models.CharField(max_length=200, blank=True)
	D		 = models.CharField(max_length=200, blank=True)
	E		 = models.CharField(max_length=200, blank=True)
	ans 	 = models.CharField(max_length=1, default="z")
	subject  = models.CharField(choices=settings.SUBJECTS, max_length=4, default="ERRO")
	month  	 = models.CharField(max_length=200, blank=True)
	year 	 = models.IntegerField(blank=True, null=True)
	unit 	 = models.IntegerField(blank=True, null=True)
	group 	 = models.ForeignKey("Group", blank=True, null=True, on_delete=models.SET_NULL)
	hint 	 = models.ForeignKey("Hint",  blank=True, null=True, on_delete=models.SET_NULL)
	diagram  = models.FileField(default=None, blank=True, null=True, upload_to="diagrams")

	# How the question is shown in the admin view
	def __str__(self):
		return str(self.subject) + " : " + str(self.unit) + " : " + str(self.year) + " : " +\
			   str(self.month)[0:3] + " : " + str(self.question)


class Hint(models.Model):
	"""
	A Hint object that can go with questions
	"""

	hint1 = models.CharField(max_length=200, default="")
	hint2 = models.CharField(max_length=200, default="")
	hint3 = models.CharField(max_length=200, default="")

	def __str___(self):
		return "Hints for " + str(Question.objects.get(hint=self))
		

class Group(models.Model):
	"""
	An model that is related to a set of questions
	Name:	Text: The name of the group
	"""

	name = models.CharField(max_length=200, default="")

	def __str__(self):
		return "This group contains questions " + str(Question.objects.filter(group=self))


class Selector(models.Model):
	"""
	Object used to create a list of questions that pertain to the users selection
	"""

	# Used to select the questions and keep track of the current one
	subject = models.CharField(max_length=100, default="ERRO")		# The subject the user chose
	index = models.IntegerField(default=0)							# Used to iterate through the questions
	questions = models.ManyToManyField(Question)					# All the questions matching the user's criteria
	pri_keys = models.CharField(max_length=1000, default="")		# A list of the primary keys in questions
	created_on = models.DateTimeField(auto_now_add=True)			# way to age out selectors

	# Used to track the user's record
	correct = models.BooleanField(default=False)		# If the user answer the current question correctly
	choice_history = models.TextField(default="")		# What their previous answers were
	# A list of how the user did on questions in the form of [question's pk, if_skipped, if_correct, sequence of answers entered]
	# Stored as a string, but can be cast to a list of [int, boolean, string]
	record = models.TextField(default="")

	# TODO extra form validation so by_unit isn't needed
	def populate_questions(self, units, exams, by_unit, question_limit, include_diagrams):
		"""
		Creates relationships to the appropriate questions. The parameter by_unit is included because the user may have
		selected some exams, but changed their mind and selected questions by unit. The form will say the user
		selected both units and exams, so by_unit is included to check which submission button they clicked.

		:param units: the units the user wants to take
		:param exams: the exams the user wants to take
		:param by_unit: if the user choose to get questions by unit or not
		:param question_limit: upper limit of the number of questions to return
		:param include_diagrams: if to allow questions that have diagrams
		"""

		# If the user choose to get questions by unit, filter by unit
		if by_unit:
			self.questions.set(Question.objects.filter(subject=self.subject).filter(unit__in=units))
		else:
			# Exams are a list of Month Year pairings
			for exam in exams:
				month = exam[0:exam.index(" ")]
				year = exam[exam.index(" ") + 1:]
				# Adding each question that matches both the year and the month for each exam
				# TODO refactor this
				self.questions.set(self.questions.all() | Question.objects.filter(subject=self.subject).filter(year=year, month=month))

		# Add filter to excluse diagram questions (if given)
		if not include_diagrams:
			self.questions.set(self.questions.filter(diagram=""))
		# Filter down the total number of questions
		if self.questions.count() > question_limit:
			self.questions.set(self.questions.all().order_by("?")[:question_limit])

		# Randomizing the Queryset and storing that random order in pri_keys
		for q in self.questions.all():
			self.pri_keys += str(q.pk) + ","
		self.pri_keys = self.pri_keys[0:len(self.pri_keys) - 1]		# Removing trailing ","
		self.save()			# Saving it

	# Returns the question with the primary key at the index of index
	def get_question(self):
		# Used to tell there are more questions or not
		if self.questions is None or self.index is None or self.index >= self.questions.count():
			return None
		index_list = self.pri_keys.split(",")
		return self.questions.get(pk=index_list[self.index])

	# How the selector will show up in the admin view
	def __str__(self):
		return "Selector: " + str(self.pk)


class QuestionBug(models.Model):
	"""
	Used for users to submit bug reports on the questions.
	Question:		The question the user finds fault with
	Bug Choices:	Options for errors with the question
	Description:	A description of the fault
	Time:			When the error occurred
	"""
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	bug_choices = models.CharField(max_length=1, choices=QUESTION_BUG_CHOICES, default="5")
	description = models.TextField(blank=True)
	time = models.DateTimeField(default=timezone.now, blank=True)

	# How the bug report will show up in the admin view
	def __str__(self):
		return "Bug: " + str(self.pk) + " with question " + str(self.question.pk) + \
			   ": " + str(self.get_bug_choices_display())


class Feedback(models.Model):
	"""
	Used for user feedback about misc bugs and the desired future state of the project
	"""
	created_on = models.DateTimeField(auto_now_add=True)
	new_feature_requests = models.JSONField(default=list, blank=True)
	misc_feedback = models.TextField(blank=True, max_length=500)

	def __str__(self):
		ret = str(self.created_on.date())
		if self.new_feature_requests is not None and len(self.new_feature_requests) > 0:
			ret += " | " + str([feature["name"] for feature in sorted(self.new_feature_requests, key=lambda item: item["rank"])])
		print(self.misc_feedback)
		if self.misc_feedback is not None and len(self.misc_feedback) > 0:
			ret += " | " + self.misc_feedback[0:50]
		return ret

	def set_data(self, new_features: list, misc_feedback: str) -> None:
		self.new_feature_requests = new_features
		self.misc_feedback = misc_feedback
		self.save()
