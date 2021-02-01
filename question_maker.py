# Takes a .txt semi-edited version of an exam and creates questions from it
# Inputs:
# 	A .txt version of the exam (requires some pre-possessing)
# 	A .txt version of the answers (question # question answer, 1 per line)
#   A path of the folder of images that go with the question, named as subject_year_month_question#.JPG
# 	The subject (must be an option from NYRegentsPrep/settings.py SUBJECTS)
# 	The exams year
# 	The exams month
# TODO: use https://apiv2.online-convert.com/ to auto convert, take in pdf as input
# TODO: preprocess to strip whitespace ext
# TODO: break up into multiple stages?
import sys
import re
import os
from shutil import copy

os.environ["DJANGO_SETTINGS_MODULE"] = "NYRegentsPrep.settings"
import django
django.setup()

from NYRP.models import Question


def main():
	if len(sys.argv) != 7:
		print("Requires five parameters: the questions text file, the answers text file, the subject, the Year of the"
				" exam, the month of the exam.")
		print("ex) python3 question_maker.py questions.txt answers.txt . CHEM 2020 August")
		return

	ans_map = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
	answers = dict()
	questions = dict()
	questions_file = sys.argv[1]
	answers_file = sys.argv[2]
	picture_dir = sys.argv[3]
	subject = sys.argv[4]
	year = sys.argv[5]
	month = sys.argv[6]

	# Read in the correct answers
	with open(answers_file) as f:
		for line in f.readlines():
			q, a = line.split()
			answers[int(q)] = int(a)

	# Part 1: Read in and parse the exam
	with open(questions_file) as f:
		lines = f.readlines()

	for i in range(len(lines)):
		# Search for the start of a question
		match = re.compile(r"^\d* ").match(lines[i])
		if match is not None and int(match.group(0)) <= 50:
			# Start of a question and answers (trim its number) and don't end until the next question
			# is found or the end of the file
			question_block = lines[i][len(match.group(0)):]
			i += 1
			while i < len(lines) and re.compile(r"^\d{1,2} ").match(lines[i]) is None:
				question_block += lines[i]
				i += 1
			i -= 1

			# Parse through the text of answers looking for (1), (2), (3), and (4)
			# These are not guaranteed to be in any particular order
			opts = {1: "", 2: "", 3: "", 4: ""}
			indexes = sorted([question_block.index("(" + str(i) + ")") for i in range(1, 5)])
			question = question_block[:indexes[0]].replace("\n", " ").strip()
			for j in range(4):
				answer_num = int(question_block[int(indexes[j] + 1)])
				start = indexes[j]
				end = indexes[j + 1] if j + 1 < 4 else -1
				opts[answer_num] = question_block[start:end].replace("\n", " ").strip()[4:]
			questions[int(match.group(0))] = {
				"question": question, "A": opts[1], "B": opts[2], "C": opts[3], "D": opts[4], "E": "",
			}

			# print(match.group(0) + ": " + question)
			# print("\t A: '" + answers[1] + "'")
			# print("\t B: '" + answers[2] + "'")
			# print("\t C: '" + answers[3] + "'")
			# print("\t D: '" + answers[4] + "'\n")

	# Part 2: All questions created, go through and assign topics for each and write to file
	start = int(input("Start at question: "))
	temp_file = sys.argv[1][:sys.argv[1].index(".txt")] + "_formatted_questions.txt"
	with open(temp_file, "a") as outf:
		for question_num in sorted(questions.keys()):
			if question_num < start:
				continue
			v = questions[question_num]
			diagram = ""
			diagram_name = subject + "_" + year + "_" + month + "_" + str(question_num) + ".JPG"
			if os.path.isfile(os.path.join(picture_dir, diagram_name)):
				src = os.path.join(picture_dir, diagram_name)
				diagram = os.path.join("diagrams", diagram_name)
				copy(src, os.path.join("NYRP", "static", "diagrams/", diagram_name))

			print(str(question_num) + ": " + v["question"])
			print("\tA: '" + v["A"] + "'")
			print("\tB: '" + v["B"] + "'")
			print("\tC: '" + v["C"] + "'")
			print("\tD: '" + v["D"] + "'")
			print("\tE: '" + v["E"] + "'")
			print("\tAnswer: " + ans_map[answers[question_num]])
			print("\tDiagram: " + diagram)

			unit = input("Unit: ")
			outf.write(v["question"] + "\n")
			outf.write(v["A"] + "\n")
			outf.write(v["B"] + "\n")
			outf.write(v["C"] + "\n")
			outf.write(v["D"] + "\n")
			outf.write(v["E"] + "\n")
			outf.write(ans_map[answers[question_num]] + "\n")
			outf.write(subject + "\n")
			outf.write(month + "\n")
			outf.write(year + "\n")
			outf.write(unit + "\n")
			outf.write(diagram + "\n")

			if input("Stop? ") in ["Y", "y", "yes", "Yes", "YES"]:
				break
	print("Intermediate results stored in " + temp_file)
	print("Check and edit that file and then save it.")
	if input("Continue? [Y/N] ") not in ["Y", "y", "yes", "Yes", "YES"]:
		return

	# Part 3: Manual edits to the file if required

	# Part 4: Read the file and create the db question objects
	i = 0
	with open(temp_file, "r") as inf:
		while i < 50:
			i += 1
			try:
				q = inf.readline().strip()
				a = inf.readline().strip()
				b = inf.readline().strip()
				c = inf.readline().strip()
				d = inf.readline().strip()
				e = inf.readline().strip()
				ans = inf.readline().strip()
				subject = inf.readline().strip()
				month = inf.readline().strip()
				year = int(inf.readline())
				unit = int(inf.readline())
				diagram = inf.readline().strip()
				question = Question.objects.create(question=q, A=a, B=b, C=c, D=d, E=e, ans=ans, subject=subject, month=month,
												   year=year, unit=unit, group=None, hint=None, diagram=diagram)
				try:
					question.save()
				except Exception as e:
					print("Could not save question! " + str(e))
				print("question saved: " + str(question))
			except IOError:
				pass
	print("All questions ingested")

if __name__ == "__main__":
	main()
