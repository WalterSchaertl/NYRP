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

# TODO, update units to align with key ideas in https://www.nysed.gov/sites/default/files/programs/standards-instruction/framework-9-12-with-2017-updates.pdf
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
	("August 2024", "August 2024"),
	("June 2024", "June 2024"),
	("January 2024", "January 2024"),
	("August 2023", "August 2023"),
	("June 2023", "June 2023")
)


ALG2_UNITS = (
	("1", "1: The Real Number System"),
	("2", "2: Quantities"),
	("3", "3: The Complex Number System"),
	("4", "4: Seeing Structure in Expressions"),
	("5", "5: Arithmetic with Polynomials and Rational Expressions"),
	("6", "6: Creating Equations"),
	("7", "7: Reasoning with Equations and Inequalities"),
	("8", "8: Expressing Geometric Properties with Equations"),
	("9", "9: Interpreting Functions"),
	("10", "10: Building Functions"),
	("11", "11: Linear, Quadratic, and Exponential Models "),
	("12", "12: Trigonometric Functions "),
	("13", "13: Interpreting categorical and quantitative data "),
	("14", "14: Making Inferences and Justifying Conclusions"),
	("15", "15: Conditional Probability and the Rules of Probability ")
)
ALG2_EXAMS = (
	("August 2024", "August 2024"),
	("June 2024", "June 2024"),
	("January 2024", "January 2024"),
	("August 2023", "August 2023"),
	("June 2023", "June 2023")
)

GHG1_UNITS = (  # This was discontinued in 2018
	("1", "1: Development of Civilization"),  # 9.1: 10000 BCE to 630 CE
	("2", "2: The Rise and Impact of Belief Systems"),  # 9.2: 10000 BCE to 630 CE
	("3", "3: Expansion, Achievement, and Decline of Classical Civilizations"),  # 9.3: 600 BCE to 900 CE
	("4", "4: Rise of Transregional Trade Networks"),  # 9.4: 500 CD to 1500 CE
	("5", "5: Political Powers and Achievements"),  # 9.5: 500 CD to 1500 C
	("6", "6: Social and Cultural Growth and Conflict"),  # 9.5: 500 CD to 1500 C
	("7", "7: Ottoman Empire and Ming Dynasty Pre-1600"),  # 9.7 1400 CE to 1600 CE
	("8", "8: Africa and the Americas Pre-1600"),  # 9.8 1325 CE to 1600 CE
	("9", "9: Transformations of Western Europe and Russia"),  # 9.9 1400 CE to 1750 CE
	("10", "10: Interactions nad Disruptions")  # 9.10 1400 CE to 1750 CE
)
GHG1_EXAMS = (("", ""),)

GHG2_UNITS = (
	("1", "1: The World in 1750"),  # 10.1
	("2", "2: Enlightenment, Revolution, and Nationalism (1750-1914)"),  # 10.2 (1750-1914)
	("3", "3: Causes and Effects of the Industrial Revolution (1750-1914)"),  # 10.3 (1750-1914)
	("4", "4: Imperialism (1750-1914)"),  # 10.4 (1750-1914)
	("5", "5: Unresolved Global Conflict (1914-1945)"),  # 10.5 (1914-1945)
	("6", "6: Unresolved Global Conflict (1945-1991)"),  # 10.5 (1945-1991)
	("7", "7: Decolonization and Nationalism (1900-2000)"),  # 10.7 (1900-2000)
	("8", "8: Tensions Between Traditional Cultures and Modernization (1945-present)"),  # 10.8 (1945-present)
	("9", "9: Globalization and a Changing Global Environment (1945-present)"),  # 10.9 (1990-present)
	("10", "10: Human Rights Violations (1933-present)")  # 10.10 (1948-present)
)
GHG2_EXAMS = (
	("August 2024", "August 2024"),
	("June 2024", "June 2024"),
	("January 2024", "January 2024"),
	("August 2023", "August 2023"),
	("June 2023", "June 2023")
)

ESCI_UNITS = (
	("1", "1: Introduction to Earth's Changing Environment"),
	("2", "2: Measuring Earth"),
	("3", "3: Earth in the Universe"),
	("4", "4: Motion of Earth, Moon, and Sun"),
	("5", "5: Energy in Earth Processes"),
	("6", "6: Insolation and the Seasons"),
	("7", "7: Weather"),
	("8", "8: Water and Climate"),
	("9", "9: Weathering and Erosion"),
	("10", "10: Deposition"),
	("11", "11: Earth Materials-Minerals, Rocks, and Mineral Resources"),
	("12", "12: Earth's Dynamic Crust and Interior"),
	("13", "13: Interpreting Geologic History"),
	("14", "14: Landscape Development and Environmental Change"),
)
ESCI_EXAMS = (
	("August 2024", "August 2024"),
)

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
