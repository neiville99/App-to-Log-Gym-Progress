import os
import customtkinter as ctk
import pyodbc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Data.WeightAnalytics import create_weight_plot
from MachineLearning.WeightPredictor import predict_days_to_target
from Data.WorkoutAnalytics import mood_change_by_hour_plot
from Data.ExerciseAnalytics import most_popular_exercise_plot, max_weight_plot, progress_plot, get_exercise_names

from dotenv import load_dotenv

load_dotenv()

server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")

# SQL Server connection
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('SQL_SERVER')};"
    f"DATABASE={os.getenv('SQL_DATABASE')};"
    f"Trusted_Connection=yes;"
)

cursor = conn.cursor()
print("Connected Succesfully")
# Main App Window
class GymApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gym Tracker")

        # Full screen windpw
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda  e: self.attributes("-fullscreen", False))

        ctk.set_appearance_mode("dark")

        self.large_font = ctk.CTkFont(size=18)
        self.exercise_data = []
        self.workout_aims = ["Strength", "Hypertrophy", "Endurance", "Cardio", "Mobility"]

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Tab options
        self.exercise_tab = self.tabview.add("Add Exercise")
        self.workout_tab = self.tabview.add("Log Workout")
        self.weight_tab = self.tabview.add("Log Weight")
        self.analytics_tab = self.tabview.add("Analytics")

        self.create_exercise_form() # create exercise form

        # Vertical  scroll abr
        self.workout_scroll = ctk.CTkScrollableFrame(self.workout_tab, width=800, height=700)
        self.workout_scroll.pack(expand=True, pady=10)
        self.create_workout_form(self.workout_scroll) # create workout form with scroll

        self.create_weight_log(self.weight_tab) # Create weight view

        self.create_analytics_view(self.analytics_tab) # Create analytics view



    def get_dropdown_values(self, column):
        cursor.execute(f"SELECT DISTINCT {column} FROM GymExercises WHERE {column} IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]

    def get_muscle_groups(self):
        cursor.execute("SELECT DISTINCT MuscleGroup FROM GymExercises WHERE MuscleGroup IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]

    def get_exercises_by_muscle(self, muscle_group):
        cursor.execute("SELECT Name FROM GymExercises WHERE MuscleGroup = ?", (muscle_group,))
        return [row[0] for row in cursor.fetchall()]

    # Exercise form
    def create_exercise_form(self):
        ctk.CTkLabel(self.exercise_tab, text="Exercise Name", font=self.large_font).pack(pady=10)
        self.exercise_name = ctk.CTkEntry(self.exercise_tab, font=self.large_font, width=400, height=40)
        self.exercise_name.pack(pady=5)

        ctk.CTkLabel(self.exercise_tab, text="Muscle Group", font=self.large_font).pack(pady=10)
        self.muscle_group_values = self.get_dropdown_values("MuscleGroup")
        self.muscle_group = ctk.CTkComboBox(self.exercise_tab, values=self.muscle_group_values, font=self.large_font,
                                            width=400, height=40)
        self.muscle_group.set("Select or Type Muscle Group")
        self.muscle_group.pack(pady=5)

        ctk.CTkLabel(self.exercise_tab, text="Type", font=self.large_font).pack(pady=10)
        self.exercise_type_values = self.get_dropdown_values("Type")
        self.exercise_type = ctk.CTkComboBox(self.exercise_tab, values=self.exercise_type_values, font=self.large_font,
                                             width=400, height=40)
        self.exercise_type.set("Select or Type Exercise Type")
        self.exercise_type.pack(pady=5)

        ctk.CTkLabel(self.exercise_tab, text="Description", font=self.large_font).pack(pady=10)
        self.exercise_description = ctk.CTkEntry(self.exercise_tab, font=self.large_font, width=400, height=40)
        self.exercise_description.pack(pady=5)

        ctk.CTkLabel(self.exercise_tab, text="Limb Type", font=self.large_font).pack(pady=10)
        self.limb_type = ctk.CTkComboBox(self.exercise_tab, values=["uni-lateral", "bi-lateral"], font=self.large_font,
                                         width=400, height=40)
        self.limb_type.set("Select Limb Type")
        self.limb_type.pack(pady=5)

        ctk.CTkLabel(self.exercise_tab, text="Is Machine?", font=self.large_font).pack(pady=10)
        self.is_machine = ctk.CTkComboBox(self.exercise_tab, values=["Yes", "No"], font=self.large_font, width=400,
                                          height=40)
        self.is_machine.set("Yes or No")
        self.is_machine.pack(pady=5)

        ctk.CTkButton(self.exercise_tab, text="Save Exercise", command=self.save_exercise, font=self.large_font).pack(
            pady=20)

    def save_exercise(self):
        name = self.exercise_name.get()
        muscle = self.muscle_group.get()
        etype = self.exercise_type.get()
        description = self.exercise_description.get()
        limb = self.limb_type.get()
        is_machine = 1 if self.is_machine.get() == "Yes" else 0

        cursor.execute(
            "INSERT INTO GymExercises (Name, MuscleGroup, Type, Description, LimbType, IsMachine) VALUES (?, ?, ?, ?, ?, ?)",
            (name, muscle, etype, description, limb, is_machine)
        )
        conn.commit()

        if muscle not in self.muscle_group_values:
            self.muscle_group_values.append(muscle)
            self.muscle_group.configure(values=self.muscle_group_values)

        if etype not in self.exercise_type_values:
            self.exercise_type_values.append(etype)
            self.exercise_type.configure(values=self.exercise_type_values)

        ctk.CTkLabel(self.exercise_tab, text="Exercise Saved!", font=self.large_font, text_color="green").pack(pady=5)

    def create_workout_form(self, parent):
        ctk.CTkLabel(parent, text="Workout Name", font=self.large_font).pack(pady=10)
        self.workout_name = ctk.CTkEntry(parent, font=self.large_font, width=400, height=40)
        self.workout_name.pack(pady=5)

        ctk.CTkLabel(parent, text="Workout Aim", font=self.large_font).pack(pady=10)
        self.workout_aim = ctk.CTkComboBox(parent, values=self.workout_aims, font=self.large_font, width=400, height=40)
        self.workout_aim.set("Select or Type Aim")
        self.workout_aim.pack(pady=5)

        ctk.CTkLabel(parent, text="Pre Workout Mood (1–5)", font=self.large_font).pack(pady=10)
        self.pre_mood = ctk.CTkEntry(parent, font=self.large_font, width=400, height=40)
        self.pre_mood.pack(pady=5)

        ctk.CTkLabel(parent, text="Post Workout Mood (1–5)", font=self.large_font).pack(pady=10)
        self.post_mood = ctk.CTkEntry(parent, font=self.large_font, width=400, height=40)
        self.post_mood.pack(pady=5)

        ctk.CTkLabel(parent, text="Comment", font=self.large_font).pack(pady=10)
        self.comment = ctk.CTkEntry(parent, font=self.large_font, width=400, height=40)
        self.comment.pack(pady=5)

        ctk.CTkLabel(parent, text="Muscle Group", font=self.large_font).pack(pady=10)
        self.exercise_muscle_group = ctk.CTkComboBox(parent, values=self.get_muscle_groups(), font=self.large_font, width=400, height=40)
        self.exercise_muscle_group.set("Select Muscle Group")
        self.exercise_muscle_group.pack(pady=5)
        self.exercise_muscle_group.bind("<<ComboboxSelected>>", self.filter_exercises_by_muscle)

        ctk.CTkLabel(parent, text="Select Exercise", font=self.large_font).pack(pady=10)
        self.exercise_picker = ctk.CTkComboBox(parent, values=[], font=self.large_font, width=400, height=40)
        self.exercise_picker.set("Select Exercise")
        self.exercise_picker.pack(pady=5)

        self.weight_entry = ctk.CTkEntry(parent, placeholder_text="Weight (kg)", font=self.large_font)
        self.weight_entry.pack(pady=5)

        self.reps_entry = ctk.CTkEntry(parent, placeholder_text="Reps", font=self.large_font, width=400, height=40)
        self.reps_entry.pack(pady=5)

        ctk.CTkButton(parent, text="Add Exercise Entry", command=self.add_exercise_to_workout, font=self.large_font).pack(pady=10)

        self.exercise_log = ctk.CTkTextbox(parent, height=150, font=self.large_font)
        self.exercise_log.pack(pady=10)

        ctk.CTkButton(parent, text="Submit Workout", command=self.save_workout, font=self.large_font,
                      fg_color="#1f6aa5", hover_color="#144e75").pack(pady=20)

    def filter_exercises_by_muscle(self, event=None):
        group = self.exercise_muscle_group.get()
        if group:
            cursor.execute("SELECT Name FROM GymExercises WHERE MuscleGroup = ?", (group,))
            exercises = [row[0] for row in cursor.fetchall()]
            self.exercise_picker.configure(values=exercises)

    def add_exercise_to_workout(self):
        name = self.exercise_picker.get()
        weight = self.weight_entry.get()
        reps = self.reps_entry.get()
        if name and weight and reps:
            self.exercise_data.append((name, float(weight), int(reps)))
            self.exercise_log.insert("end", f"{name} - {weight}kg x {reps} reps\n")

    def save_workout(self):
        try:
            name = self.workout_name.get()
            aim = self.workout_aim.get()
            if aim not in self.workout_aims:
                self.workout_aims.append(aim)
                self.workout_aim.configure(values=self.workout_aims)

            pre = int(self.pre_mood.get())
            post = int(self.post_mood.get())
            comment = self.comment.get()

            self.exercise_log.delete("0.0", "end")

            cursor.execute(
                """
                INSERT INTO Workouts (WorkoutName, WorkoutAim, PreMood, PostMood, Comment)
                OUTPUT INSERTED.WorkoutID
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, aim, pre, post, comment)
            )
            row = cursor.fetchone()
            workout_id = row[0] if row else None

            if workout_id is None:
                self.exercise_log.insert("end", "Workout ID not captured.\n")
                return

            self.exercise_log.insert("end", f"Workout ID: {workout_id}\n")

            for name, weight, reps in self.exercise_data:
                cursor.execute("SELECT ExerciseID FROM GymExercises WHERE Name = ?", (name,))
                result = cursor.fetchone()
                if result is None:
                    self.exercise_log.insert("end", f"Exercise '{name}' not found.\n")
                    continue

                exercise_id = result[0]
                cursor.execute(
                    "INSERT INTO WorkoutEntries (WorkoutID, ExerciseID, Weight, Reps) VALUES (?, ?, ?, ?)",
                    (workout_id, exercise_id, weight, reps)
                )

            conn.commit()
            self.exercise_log.insert("end", "Workout saved!\n")
            self.exercise_data.clear()

            self.workout_name.delete(0, "end")
            self.workout_aim.set("Select or Type Aim")
            self.pre_mood.delete(0, "end")
            self.post_mood.delete(0, "end")
            self.comment.delete(0, "end")

        except Exception as e:
            self.exercise_log.insert("end", f"Error: {e}\n")

    def create_weight_log(self, parent):
        ctk.CTkLabel(parent, text="Log Current Weight", font=self.large_font).pack(pady=10)
        self.current_weight = ctk.CTkEntry(parent, font=self.large_font, width=400, height=40)
        self.current_weight.pack(pady=5)
        ctk.CTkButton(parent, text="Submit", command=self.submit_weight, font=self.large_font).pack(pady=10) # Submit button

        # Target weight entry
        ctk.CTkLabel(parent, text="Enter Target Weight", font=self.large_font).pack(pady=10)
        self.target_weight_entry = ctk.CTkEntry(parent, font=self.large_font, width=400, height=40)
        self.target_weight_entry.pack(pady=5)
        ctk.CTkButton(parent, text="Predict Time to Target", command=self.show_target_prediction, font=self.large_font).pack(pady=10) # Predict Button

        self.prediction_label = ctk.CTkLabel(parent, text="", font=self.large_font)
        self.prediction_label.pack(pady=10)

        # Display plot of weight over time
        try:
            fig = create_weight_plot()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            ctk.CTkLabel(parent, text=f"Plot error: {e}", text_color="red", font=self.large_font).pack(pady=10)

    def submit_weight(self):
        try:
            weight = float(self.current_weight.get())
            cursor.execute("INSERT INTO WeightLogs (Weight_kg) VALUES (?)", (weight,))
            conn.commit()
            self.current_weight.delete(0, "end")
            print("Weight logged succesfully!")
        except Exception as e:
            print(f"error logging weight: {e}")

    def show_target_prediction(self):
        try:
            target = float(self.target_weight_entry.get())
            days = predict_days_to_target(target)
            if days is not None:
                self.prediction_label.configure(
                    text=f"With your current progress, you will reach your target weight in {days} days."
                )
            else:
                self.prediction_label.configure(
                    text="Target weight not reachable within 5 years at your current pace.", text_color="orange"
                )
        except Exception as e:
            self.prediction_label.configure(
                text=f"Error: {e}", text_color="red"
            )

    def create_analytics_view(self, parent):
        ctk.CTkLabel(parent, text="Analytics Dashboard", font=self.large_font).pack(pady=10)

        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Split layout into two side-by-side frames
        left_frame = ctk.CTkScrollableFrame(container, width=850)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_frame = ctk.CTkFrame(container, width=400)
        right_frame.pack(side="left", fill="y")

        def show_plot(plot_func, target_frame):
            fig = plot_func()
            canvas = FigureCanvasTkAgg(fig, master=target_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

        try:
            show_plot(create_weight_plot, left_frame)
            show_plot(mood_change_by_hour_plot, left_frame)
            show_plot(most_popular_exercise_plot, left_frame)
            show_plot(max_weight_plot, left_frame)
        except Exception as e:
            ctk.CTkLabel(left_frame, text=f"Error loading plots: {e}", text_color="red").pack()

        ctk.CTkLabel(right_frame, text="Select Exercise to View Progress:", font=self.large_font).pack(pady=10)
        self.exercise_names = get_exercise_names()
        self.exercise_dropdown = ctk.CTkComboBox(right_frame, values=self.exercise_names, font=self.large_font)
        self.exercise_dropdown.pack(pady=5)

        ctk.CTkButton(right_frame, text="Show Progress Chart", command=self.display_progress_plot,
                      font=self.large_font).pack(pady=10)

        self.progress_canvas_frame = ctk.CTkFrame(right_frame)
        self.progress_canvas_frame.pack(fill="both", expand=True, pady=10)

    def display_progress_plot(self):
        for widget in self.progress_canvas_frame.winfo_children():
            widget.destroy()

        try:
            selected_exercise = self.exercise_dropdown.get()
            fig = progress_plot(selected_exercise)
            canvas = FigureCanvasTkAgg(fig, master=self.progress_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        except Exception as e:
            ctk.CTkLabel(self.progress_canvas_frame, text=f"Error: {e}", text_color="red").pack(pady=5)


if __name__ == "__main__":
    app = GymApp()
    app.mainloop()
