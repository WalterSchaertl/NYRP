from django import forms
from django.forms import ModelForm
from .models import QuestionBug


# These constants define the units for each topic, as well as
# which exams there are to select from. Chemistry has a small
# populated database, United States History and Government is
# just here as a proof of concept

# Chemistry
CHEM_UNITS = (
	("1", "1: The Atom"),
	("2", "2: Formulas and Equations"),
	("3", "3: The Mathematics of Formulas and Equations"),
	("4", "4: Physical Behavior of Matter"),
	("5", "5: The Periodic Table"),
	("6", "6: Bonding"),
	("7", "7: Properties of Solutions"),
	("8", "8: Kinetics and Equilibrium"),
	("9", "9: Oxidation-Reduction"),
	("10", "10: Acids, Bases, and Salts"),
	("11", "11: Organic Chemistry"),
	("12", "12: Nuclear Chemistry"),
)
CHEM_EXAMS = (
	("August 2024", "August 2024"),
	# TODO June 2024 Chem
	("January 2024", "January 2024"),
	("August 2023", "August 2023"),
	("June 2023", "June 2023"),
	("January 2023", "January 2023"),
	("August 2022", "August 2022"),
	("June 2022", "June 2022"),
	("June 2017", "June 2017"),
	("January 2017", "January 2017"),
	# ("August 2017", "August 2017"),
	# ("January 2016", "January 2016"),
	# ("June 2016", "June 2016"),
	("August 2016", "August 2016"),
)

# United States History and Government
USHG_UNITS = (
	("1", "Period 1: 1491–1607"),
	("2", "Period 2: 1607–1754"),
	("3", "Period 3: 1754–1800"),
	("4", "Period 4: 1800–1848"),
	("5", "Period 5: 1844–1877"),
	("6", "Period 6: 1865–1898"),
	("7", "Period 7: 1890–1945"),
	("8", "Period 8: 1945–1980"),
	("9", "Period 9: 1980–Present"),

)
USHG_EXAMS = (
	("August 2024", "August 2024"),
	("June 2024", "June 2024"),
	("January 2024", "January 2024"),
	("August 2023", "August 2023"),
	("June 2023", "June 2023"),
	("January 2020", "January 2020"),
	("August 2017", "August 2017"),
)


# Algebra I, Algebra 2, Global History and Geography,
# and Physics are not implemented yet.
# TODO add the ALG1 reference sheet: https://www.nysed.gov/sites/default/files/programs/state-assessment/public-facing-reference-sheet.pdf
# and https://www.nysed.gov/sites/default/files/programs/state-assessment/a1-next-gen-reference-sheet.pdf starting June 2024
# and update the reference table button to point to them
ALG1_UNITS = (
	("1", "1: The Real Number System"),
	("2", "2: Quantities"),
	("3", "3: Structure in Expressions"),
	("4", "4: Arithmetic with Polynomials nd Rational Expressions"),
	("5", "5: Creating Equations"),
	("6", "6: Reasoning with Questions and Inequalities"),
	("7", "7: Interpreting Functions"),
	("8", "8: Building Functions"),
	("9", "9: Linear, Quadratic, and Exponential Models"),
	("10", "10: Interpreting Categorical and Quantitative Data")
)
ALG1_EXAMS = (
	("June 2024", "June 2024"),
	("January 2024", "January 2024"),
)


ALG2_UNITS = (("", ""),)
ALG2_EXAMS = (("", ""),)
GHGE_UNITS = (("", ""),)
GHGE_EXAMS = (("", ""),)
PHYS_UNITS = (("", ""),)
PHYS_EXAMS = (("", ""),)
ERRO_UNITS = (("", ""),)
ERRO_EXAMS = (("", ""),)


class SelectorForm(forms.Form):
	"""
	This is the form that the user submits to get questions. The user can
	either select questions based from a particular exam, or pick questions based on their topic.

	Fields:
	units - A multiple choice selection for picking questions based on their unit
	exams - A multiple choice selection for picking questions based on which exam they appeared on
	"""

	# Both of these fields are overwritten in __init__
	units = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CHEM_UNITS, required=False)
	exams = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CHEM_EXAMS, required=False)
	# This could possibly be implemented in the future to act as a cap so
	# the user doesn't get a ridiculous amount of questions they don't want
	# num_qs= forms.IntegerField(widget=forms.NumberInput, min_value=1)

	# Initialization of the the form
	def __init__(self, *args, **kwargs):
		# The request with which the form was submitted
		self.req = kwargs.pop("req")
		# The subject they user has selected
		self.subject = kwargs.pop("subject")
		super(SelectorForm, self).__init__(*args, **kwargs)
		# Picking the correct exam/units based on the subject
		self.fields["units"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
														 choices=eval(self.subject + "_UNITS"), required=False)
		self.fields["exams"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
														 choices=eval(self.subject + "_EXAMS"), required=False)

	# Checking the form for errors
	def clean(self):
		cleaned_data = super(SelectorForm, self).clean()
		units = cleaned_data.get("units")
		exams = cleaned_data.get("exams")
		# Adding errors to the form if the user wanted to get questions
		# by the unit and didn't select a unit, or if they wanted to get
		# questions by the exam and didn't select the exam button.
		if "by_unit" in self.req:
			if len(units) < 1:
				self.add_error("units", "unit")
		elif "by_exam" in self.req:
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
