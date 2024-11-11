from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import QuestionBug, Feedback


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
		self.fields["disallow_retry"] = forms.BooleanField(required=False)
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


class FeedbackForm(forms.Form):
	"""
	This isn't a ModelForm, as it needs to accept more inputs than correspond to fields on the model.
	Rolls future feature votes into a JSON object.
	"""
	UNIMPLEMENTED_SUBJECTS = [("PHYS", "Physics"), ("GEOM", "Geometry"), ("LIVE", "Living Environment")]
	IMPLEMENTED_SUBJECTS = [("ANY_", "ANY"), ("CHEM", "Chemistry"), ("USHG", "US History And Government"),
							("ALG1", "Algebra I"), ("ALG2", "Algebra II Common Core"),
							("GHG2", "Global History And Geography II"), ("ESCI", "Earth Science")]
	PRIORITIES = (("0", "---"), ("1", "1"), ("2", "2"), ("3", "3"))
	FEATURE_CHOICES = [
		{
			"name": "more_subjects", "pretty_name": "Adding more subjects",
			"add_on_type": forms.ChoiceField, "choices": UNIMPLEMENTED_SUBJECTS,
			"help_text": "Please select which subject you'd like to see added"
		}, {
			"name": "more_exams", "pretty_name": "Adding more exams for current subjects",
			"add_on_type": forms.ChoiceField, "choices": IMPLEMENTED_SUBJECTS,
			"help_text": "Please select which subject you'd like to see more exams for"
		}, {
			"name": "extended_response", "pretty_name": "Add extended response questions",
			"add_on_type": forms.ChoiceField, "choices": IMPLEMENTED_SUBJECTS,
			"help_text": "Please select which subject you'd like to extended response questions added for"
		}, {
			"name": "more_customization", "pretty_name": "More customization when selecting questions",
			"add_on_type": forms.CharField,
			"help_text": "Please add details about the type of customization you'd like to see"
		}, {
			"name": "better_UI", "pretty_name": "UI/UX improvements", "add_on_type": forms.CharField,
			"help_text": "Please add details about the type of UI improvements you'd like to see"
		}, {
			"name": "other", "pretty_name": "Other feature",
			"add_on_type": forms.CharField, "help_text": "Please add details"
		}
	]

	def __init__(self, *args, **kwargs):
		self.req = kwargs.pop("req")
		super(FeedbackForm, self).__init__(*args, **kwargs)
		self.fields["misc_feedback"] = forms.CharField(required=False)
		for feature_request in self.FEATURE_CHOICES:
			self.fields["priority_" + feature_request["name"]] = forms.ChoiceField(choices=self.PRIORITIES)
			field_name = "text_" + feature_request["name"]
			if feature_request.get("choices", None) is None:
				self.fields[field_name] = feature_request["add_on_type"](required=False)
			else:
				self.fields[field_name] = feature_request["add_on_type"](choices=feature_request["choices"], required=False)

	def clean(self):
		clean_data = super().clean()
		feature_requests = list()
		for feature_choice in self.FEATURE_CHOICES:
			# If not set by user, drop the default values that come back
			rank = clean_data["priority_" + feature_choice["name"]]
			if rank == "0":
				del clean_data["priority_" + feature_choice["name"]]
				del clean_data["text_" + feature_choice["name"]]
			# If priority set, but the user somehow avoided the html required, validate here too
			elif clean_data.get("text_" + feature_choice["name"], None) in [None, ""]:
				self.add_error("text_" + feature_choice["name"], "If picking a priority for '"
							   + feature_choice["pretty_name"] + "', then the details must be filled in as well.")
			else:
				# The whole reason to use this Form instead of a ModelForm, so that the answers can be rolled up and
				# stored in the data base as a JSON list with ranking.
				comment = clean_data["text_" + feature_choice["name"]]
				feature_requests.append({"rank": int(rank), "name": feature_choice["name"], "comment": comment})
		if len(clean_data["misc_feedback"].strip()) == 0 and len(clean_data) == 1:
			self.add_error("misc_feedback", "If you want to leave feedback, please enter a comment or rank some features you'd like to see.")
		clean_data["new_feature_requests"] = feature_requests
