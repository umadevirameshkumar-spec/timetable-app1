import random
import json
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SETTINGS_FILE = "school_data.json"


def save_data(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)


def load_data():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}


class SchoolTimeTableApp(App):

    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        header = Label(text="🏫 CLASH-FREE SCHOOL TIMETABLE",
                       font_size=22,
                       size_hint_y=None,
                       height=40)
        root.add_widget(header)

        self.data = load_data()

        self.class_input = TextInput(
            hint_text="Enter Class Name (Example: 6A)",
            size_hint_y=None, height=40)
        root.add_widget(self.class_input)

        self.start_input = TextInput(
            hint_text="Start Time (HH:MM)",
            text="09:00",
            size_hint_y=None, height=40)
        root.add_widget(self.start_input)

        self.period_input = TextInput(
            hint_text="Period Duration (minutes)",
            text="45",
            size_hint_y=None, height=40)
        root.add_widget(self.period_input)

        self.period_count_input = TextInput(
            hint_text="Total Periods Per Day",
            text="8",
            size_hint_y=None, height=40)
        root.add_widget(self.period_count_input)

        self.subject_input = TextInput(
            hint_text="Subject Name",
            size_hint_y=None, height=40)
        root.add_widget(self.subject_input)

        self.teacher_input = TextInput(
            hint_text="Teacher Name",
            size_hint_y=None, height=40)
        root.add_widget(self.teacher_input)

        self.priority_input = TextInput(
            hint_text="Priority (1-5)",
            text="1",
            size_hint_y=None, height=40)
        root.add_widget(self.priority_input)

        add_btn = Button(text="Add Subject",
                         size_hint_y=None, height=40)
        add_btn.bind(on_press=self.add_subject)
        root.add_widget(add_btn)

        generate_btn = Button(text="Generate All Class Timetable",
                              size_hint_y=None, height=50)
        generate_btn.bind(on_press=self.generate_all)
        root.add_widget(generate_btn)

        scroll = ScrollView()
        self.output = Label(size_hint_y=None)
        self.output.bind(texture_size=self.output.setter('size'))
        scroll.add_widget(self.output)
        root.add_widget(scroll)

        return root

    # ===============================
    # Add Subject to Class
    # ===============================
    def add_subject(self, instance):
        class_name = self.class_input.text.strip()
        subject = self.subject_input.text.strip()
        teacher = self.teacher_input.text.strip()
        priority = int(self.priority_input.text)

        if not class_name:
            return

        if class_name not in self.data:
            self.data[class_name] = []

        self.data[class_name].append({
            "subject": subject,
            "teacher": teacher,
            "priority": priority
        })

        save_data(self.data)

        self.subject_input.text = ""
        self.teacher_input.text = ""
        self.priority_input.text = "1"

    # ===============================
    # Generate All Timetables (No Clash)
    # ===============================
    def generate_all(self, instance):

        if not self.data:
            self.output.text = "No classes added."
            return

        start_time = self.start_input.text
        period_minutes = int(self.period_input.text)
        total_periods = int(self.period_count_input.text)

        text = ""

        # teacher schedule tracker
        # structure: schedule[day][period] = list of teachers used
        schedule = {}

        for day in days:
            schedule[day] = {}
            for p in range(1, total_periods + 1):
                schedule[day][p] = []

        # generate timetable
        for class_name in self.data:

            text += f"\n🏫 Class: {class_name}\n"

            subjects = self.data[class_name]

            weighted_subjects = []
            for s in subjects:
                weighted_subjects.extend([s] * s["priority"])

            for day in days:

                text += f"\n📅 {day}\n"
                current_time = datetime.strptime(start_time, "%H:%M")

                lunch_position = total_periods // 2

                for p in range(1, total_periods + 1):

                    random.shuffle(weighted_subjects)

                    assigned = False

                    for subject_data in weighted_subjects:

                        teacher = subject_data["teacher"]

                        # Check clash
                        if teacher not in schedule[day][p]:
                            schedule[day][p].append(teacher)
                            subject_name = subject_data["subject"]
                            assigned = True
                            break

                    if not assigned:
                        subject_name = "FREE"
                        teacher = "-"

                    end_time = current_time + timedelta(minutes=period_minutes)

                    text += f"Period {p}: {subject_name} ({teacher}) "
                    text += f"{current_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n"

                    current_time = end_time

                    # Fixed Lunch
                    if p == lunch_position:
                        lunch_end = current_time + timedelta(minutes=30)
                        text += f"🍽 LUNCH {current_time.strftime('%H:%M')} - {lunch_end.strftime('%H:%M')}\n"
                        current_time = lunch_end

                text += "\n"

        self.output.text = text


if __name__ == "__main__":
    SchoolTimeTableApp().run()