from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

OUTREACH_STATUS_CHOICES = [
    ("new", "Neu"),
    ("contacted", "Kontaktiert"),
    ("follow_up_1", "Follow-up 1"),
    ("follow_up_2", "Follow-up 2"),
    ("follow_up_3", "Follow-up 3"),
    ("replied", "Geantwortet"),
    ("qualified", "Qualifiziert"),
    ("meeting_booked", "Termin gebucht"),
    ("won", "Gewonnen"),
    ("lost", "Verloren"),
]

OUTREACH_STATUS_LABELS = dict(OUTREACH_STATUS_CHOICES)


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
        choices=OUTREACH_STATUS_CHOICES,
        validators=[DataRequired()],
    )
    submit = SubmitField("Status speichern")
