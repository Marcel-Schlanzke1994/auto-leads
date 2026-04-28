from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class SearchForm(FlaskForm):
    keyword = StringField("Suchbegriff", validators=[DataRequired(), Length(max=120)])
    cities = StringField("Städte", validators=[DataRequired(), Length(max=500)])
    target_count = IntegerField(
        "Zielanzahl", default=1000, validators=[NumberRange(min=1)]
    )
    submit = SubmitField("Suche starten")


class StatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("new", "Neu"),
            ("qualified", "Qualifiziert"),
            ("contacted", "Kontaktiert"),
            ("replied", "Geantwortet"),
            ("won", "Gewonnen"),
            ("lost", "Verloren"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Status speichern")
