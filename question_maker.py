# Takes a folder path that contains a "saved_exam.json" that contains a JSON list of correctly formatted Questions, and
# a list of images that those questions point to. This folder will be copied to UploadedTests
from NYRP.models import Question
import shutil
import sys
import django
import os
import json

os.environ["DJANGO_SETTINGS_MODULE"] = "NYRegentsPrep.settings"
django.setup()


def main():
	if len(sys.argv) != 2:
		print("Exactly 1 argument required, the path to the folder containing the saved exam and diagrams")
		return
	# TODO don't copy everything over, just read the exam file and copy the diagrams to the static location
	local_path = os.path.join(".", "UploadedTests", os.path.basename(sys.argv[1]))

	with open(os.path.join(local_path, "saved_exam.json"), "r") as infile:
		for question in json.load(infile):
			# TODO refactor input file to make these unneeded
			# Form data to fit question model
			question["subject"] = question["subject"].upper()
			del question["number"]
			del question["unit_text"]
			if question["E"] is None:
				question["E"] = ""
			if question["month"] == "Jan":
				question["month"] = "January"
			question["year"] = int(question["year"])
			question["ans"] = {1: "A", 2: "B", 3: "C", 4: "D"}.get(question["ans"])
			if question["diagram"] is not None:
				shutil.copy(os.path.join(sys.argv[1], os.path.basename(question["diagram"])),  os.path.join("staticfiles", "diagrams",  os.path.basename(question["diagram"])))
				question["diagram"] = "diagrams/" + os.path.basename(question["diagram"])
			# Remove any previously generated question, TODO alo match on year/month/subject
			if len(Question.objects.filter(question=question["question"])) > 0:
				Question.objects.filter(question=question["question"]).delete()
			db_question = Question.objects.create(group=None, hint=None, **question)
			try:
				db_question.save()
			except Exception as e:
				print("Could not save question! " + str(e))
	print("Process finished")


if __name__ == "__main__":
	main()
