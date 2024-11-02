from django import forms
from django.conf import settings
from django.forms import ModelForm
from .models import QuestionBug


class SelectorForm(forms.Form):
	"""
	This is the form that the user submits to get questions. The user can
	either select questions based from a particular exam, or pick questions based on their topic.

	Fields:
	units - A multiple choice selection for picking questions based on their unit
	exams - A multiple choice selection for picking questions based on which exam they appeared on
	"""

	# Initialization of the the form
	def __init__(self, *args, **kwargs):
		# The request with which the form was submitted
		self.req = kwargs.pop("req")
		# The subject they user has selected
		self.subject = kwargs.pop("subject")
		super(SelectorForm, self).__init__(*args, **kwargs)

		# Picking the correct exam/units based on the subject
		self.fields["units"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
														 choices=settings.SUPPORTED_TOPICS[self.subject][settings.UNITS], required=False)
		self.fields["exams"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
														 choices=settings.SUPPORTED_TOPICS[self.subject][settings.EXAMS], required=False)
		self.fields["max_qs"] = forms.IntegerField(widget=forms.NumberInput, min_value=1, required=False)
		self.fields["diagram_qs"] = forms.BooleanField(required=False)
		self.fields["with_answer"] = forms.BooleanField(required=False)
		self.fields["exam_with_version"] = forms.BooleanField(required=False)
		self.fields["fill_in_key"] = forms.BooleanField(required=False)
		self.fields["max_img_height"] = forms.IntegerField(required=False)
		self.is_pdf = any("pdf" in key for key in self.req.dict().keys())

	def clean(self):
		"""
		Checking the form for errors
		"""
		cleaned_data = super(SelectorForm, self).clean()
		units = cleaned_data.get("units")
		exams = cleaned_data.get("exams")
		# Adding errors to the form if the user wanted to get questions
		# by the unit and didn't select a unit, or if they wanted to get
		# questions by the exam and didn't select the exam button.
		if "by_unit" in self.req or "by_unit_pdf" in self.req:
			if len(units) < 1:
				self.add_error("units", "unit")
		elif "by_exam" in self.req or "by_unit_pdf" in self.req:
			if len(exams) < 1:
				self.add_error("exams", "exam")
		return self.cleaned_data		# Returning the cleaned data


class QuestionBugForm(ModelForm):
	"""
	Model for used to get user bug reports on the questions
	"""

	class Meta:
		model = QuestionBug
		fields = ["bug_choices", "description"]

	def clean(self):
		"""
		Adds validation to the form. If the user gives "other" as a problem, they must
		also provide a reason.

		"""

		cleaned_data = super(QuestionBugForm, self).clean()
		description = cleaned_data.get("description")
		bug_choice = cleaned_data.get("bug_choices")

		if int(bug_choice) == 5 and description in [None, "", " "]:
			self.add_error("description", "If selecting \"other\" as an option, please provide a description.")
