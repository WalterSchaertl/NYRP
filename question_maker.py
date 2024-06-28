# Takes a folder path that contains a "saved_exam.json" that contains a JSON list of correctly formatted Questions, and
# a list of images that those questions point to. This folder will be copied to UploadedTests
import shutil
import sys
import django
import os
import json

os.environ["DJANGO_SETTINGS_MODULE"] = "NYRegentsPrep.settings"
django.setup()
from NYRP.models import Question


def main():
	if len(sys.argv) != 2:
		print("Exactly 1 argument required, the path to the saved exam.")
		return
	with open(sys.argv[1], "r") as infile:
		for question in json.load(infile):
			if question["diagram"] is not None:
				# Diagram path for serving in production
				new_diagram_path = "diagrams/" + os.path.basename(question["diagram"])
				# Copy the diagram path to NYRP/static/diagrams/{diagram_name} for development
				shutil.copy(question["diagram"], "NYRP/static/" + new_diagram_path)
				# Set the diagram name to the production expected location (stataicfiles/diagrams/{diagram_name})
				question["diagram"] = new_diagram_path
			# Remove any previously generated question, TODO alo match on year/month/subject
			if len(Question.objects.filter(question=question["question"])) > 0:
				print("This question already exists, deleting and recreating.")
				Question.objects.filter(question=question["question"]).delete()
			db_question = Question.objects.create(group=None, hint=None, **question)
			try:
				db_question.save()
			except Exception as e:
				print("Could not save question! " + str(e))
	print("Process finished")


if __name__ == "__main__":
	main()
