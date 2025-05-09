from PyQt6.QtWidgets import *
from PyQt6.QtCore import QRegularExpression, QTimer
from PyQt6.QtGui import QRegularExpressionValidator
from grade_app import *
import csv
import os


class Logic(QMainWindow, Ui_MainWindow):
    """
        Logic class for managing the grade application.

        This class inherits from QMainWindow and Ui_MainWindow. It handles user interactions, checks input validity, calculates
        statistics like the average, highest, and lowest scores, saves data to a CSV file, shows results in a table,
        and clears the input fields.

       Attributes:
           csv_file (str): The name of the CSV file where data is saved.
           error_message_color (str): CSS style for error messages.
           success_message_color (str): CSS style for success messages.
       """
    csv_file: str = 'grades.csv'
    error_message_color: str = "color: red;"
    success_message_color: str = "color: green;"

    def __init__(self) -> None:
        """
            Initializes the Logic class, sets up the UI, and connects buttons.

            This method sets up the user interface, make a list of score_inputs & labels, hide fields until number of
            attempts is entered and connects button click events to their respective methods.
        """
        super().__init__()
        self.setupUi(self)

        self.score_inputs: list = [self.score_one_input, self.score_two_input, self.score_three_input, self.score_four_input]
        self.score_labels: list = [self.score_one_label, self.score_two_label, self.score_three_label, self.score_four_label]

        self.hide_fields()
        self.set_validator()
        self.connect_buttons()

    def set_validator(self) -> None:
        """
            Sets input validators for the name, attempts, and score fields.

            This method applies regular expression validators to ensure that the user inputs are the valid ones.
        """
        names_validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z'-]+"))
        self.first_name_input.setValidator(names_validator)
        self.last_name_input.setValidator(names_validator)

        attempts_input_validator = QRegularExpressionValidator(QRegularExpression("[1-4]"))
        self.attempts_input.setValidator(attempts_input_validator)

        score_input_validator = QRegularExpressionValidator(QRegularExpression("[0-9]+"))
        for score_input in self.score_inputs:
            score_input.setValidator(score_input_validator)
            score_input.setMaxLength(3)

    def connect_buttons(self) -> None:
        """
            Connects button click events to their respective methods.

            This function links the UI buttons to their corresponding functions to handle user interactions. It also
            clears the message_label if user changes the input.
        """
        self.save_button.clicked.connect(self.save_to_csv)
        self.output_button.clicked.connect(self.output_current_data)
        self.attempts_input.textChanged.connect(self.update_attempt_fields)
        self.clear_button.clicked.connect(self.clear_form)

        self.first_name_input.textChanged.connect(self.clear_message)
        self.last_name_input.textChanged.connect(self.clear_message)
        self.attempts_input.textChanged.connect(self.clear_message)
        for score_input in self.score_inputs:
            score_input.textChanged.connect(self.clear_message)

    def hide_fields(self) -> None:
        """
            Hides score input fields and labels.

            This method is used to clear and hide score labels and fields hidden until the number of attempts is updated
            or when the form is cleared.
        """
        for score_input in self.score_inputs:
            score_input.clear()
            score_input.hide()
        for label in self.score_labels:
            label.hide()

    def update_attempt_fields(self) -> None:
        """
            Updates the visibility of score input fields based on the number of attempts.

            This method shows or hides the score input fields and labels according to the number of attempts specified
            by the user.
        """
        try:
            num_attempts = int(self.attempts_input.text())
            if not 1 <= num_attempts <= 4:
                raise ValueError
        except ValueError:
            self.hide_fields()
            return

        for i in range(4):
            if i < num_attempts:
                self.score_inputs[i].show()
                self.score_labels[i].show()
            else:
                self.score_inputs[i].hide()
                self.score_labels[i].hide()

    def validate_inputs(self) -> tuple[str | None, str | None, int | None, list[int] | None]:
        """
            Validates user inputs for first name, last name, attempts, and scores.

            Returns:
                tuple: A tuple containing the first name, last name, number of attempts, and a list of scores.
                If any input is invalid, returns None.
        """
        first_name = self.first_name_input.text()
        if not first_name:
            self.show_message("Please provide the first name", self.error_message_color)
            return None, None, None, None

        last_name = self.last_name_input.text()
        if not last_name:
            self.show_message("Please provide the last name", self.error_message_color)
            return None, None, None, None

        num_attempts = self.attempts_input.text()
        if not num_attempts:
            self.show_message("Please enter the number of attempts", self.error_message_color)
            return None, None, None, None

        num_attempts = int(self.attempts_input.text())

        scores = []
        for i in range(num_attempts):
            score_text = self.score_inputs[i].text()
            if not score_text:
                self.show_message(f"Please enter a score for attempt {i + 1}", self.error_message_color)
                return None, None, None, None

            try:
                score = int(score_text)
                if not (0 <= score <= 100):
                    self.show_message(f"Invalid score for attempt {i + 1}. Score must be between 0 and 100.", self.error_message_color)
                    return None, None, None, None
                scores.append(score)

            except ValueError:
                self.show_message(f"Invalid score for attempt {i + 1}. Please enter a valid number.", self.error_message_color)
                return None, None, None, None

        return first_name, last_name, num_attempts, scores

    def scores_summary(self) -> tuple[str, str, str] | None:
        """
            Calculates and returns the average, best, and lowest scores.

            Returns:
                tuple: A tuple containing the average score, best score, and lowest score as strings. Returns
                None if input validation fails.
        """
        first_name, last_name, num_attempts, scores = self.validate_inputs()
        if scores is None:
            return

        average = sum(scores) / len(scores)
        avg_score = f"{average:.2f}"
        best_score = str(max(scores))
        low_score = str(min(scores))

        return avg_score, best_score, low_score

    def save_to_csv(self) -> None:
        """
            Saves the validated input data to a CSV file.

            This method writes the first name, last name, scores, and calculated statistics (best, average, low)
            to a CSV file. If the file does not exist, it creates it and writes the headers.
        """
        first_name, last_name, num_attempts, scores = self.validate_inputs()

        if first_name is None or last_name is None or num_attempts is None or scores is None:
            return

        headers = ['First Name', 'Last Name', 'Attempt 1', 'Attempt 2', 'Attempt 3',
                   'Attempt 4', 'Best', 'Average', 'Low']

        avg_score, best_score, low_score = self.scores_summary()

        attempts_filled = scores + ['NA'] * (4 - num_attempts)
        row = [first_name, last_name] + attempts_filled + [best_score, avg_score, low_score]

        try:
            if not os.path.exists(self.csv_file):
                with open(self.csv_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)

            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

            self.clear_form()

            self.show_message(f"Data saved to grades.csv!", self.success_message_color)
            QTimer.singleShot(5000, self.message_label.clear)

        except Exception as e:
            QMessageBox.warning(self, " Save Error", f"Failed to save: {e}")

    def output_current_data(self) -> None:
        """
            Outputs the current data to a table widget.

            This method retrieves the validated input data, calculates grades based on scores, and displays the results
            in a table format within the UI.
        """
        first_name, last_name, num_attempts, scores = self.validate_inputs()

        if first_name is None or last_name is None or num_attempts is None or scores is None:
            return

        avg_score, best_score, low_score = self.scores_summary()

        grades = []
        for score in scores:
            if score >= 90:
                grades.append('A')
            elif score >= 80:
                grades.append('B')
            elif score >= 70:
                grades.append('C')
            elif score >= 60:
                grades.append('D')
            else:
                grades.append('F')

        self.table_widget_to_output.setRowCount(0)
        self.table_widget_to_output.setColumnCount(6)
        self.table_widget_to_output.setHorizontalHeaderLabels(['Attempt', 'Score', 'Grade', 'Best', 'Average', 'Low'])

        for i in range(num_attempts):
            row_position = self.table_widget_to_output.rowCount()
            self.table_widget_to_output.insertRow(row_position)
            self.table_widget_to_output.setItem(row_position, 0, QTableWidgetItem(f"Attempt {i + 1}"))
            self.table_widget_to_output.setItem(row_position, 1, QTableWidgetItem(str(scores[i])))
            self.table_widget_to_output.setItem(row_position, 2, QTableWidgetItem(grades[i]))

        row_position = self.table_widget_to_output.rowCount()
        self.table_widget_to_output.insertRow(row_position)
        self.table_widget_to_output.setItem(row_position, 3, QTableWidgetItem(best_score))
        self.table_widget_to_output.setItem(row_position, 4, QTableWidgetItem(avg_score))
        self.table_widget_to_output.setItem(row_position, 5, QTableWidgetItem(low_score))

    def show_message(self, text: str, color: str) -> None:
        """
            Displays a message in the message label with the specified style.

            Args:
                text (str): The message text to display.
                color (str): The color to apply to the message label.
        """
        self.message_label.setText(text)
        self.message_label.setStyleSheet(color)

    def clear_message(self) -> None:
        """
            Clears the message label text.

            This method is called to reset the message label when the user starts typing in the input fields.
        """
        self.message_label.clear()

    def clear_form(self) -> None:
        """
            Clears all input fields and resets the table widget.

            This method is called to reset the form, clearing all inputs and hiding any displayed scores or labels.
        """
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.attempts_input.clear()
        self.clear_message()

        self.hide_fields()

        self.table_widget_to_output.setRowCount(0)
        self.table_widget_to_output.setColumnCount(0)

        self.first_name_input.setFocus()
