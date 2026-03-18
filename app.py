from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_database, init_database

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-production"

# Initialise the database
with app.app_context():
    init_database()



# Timeline routes

@app.route("/")
def index():
    with get_database() as conn:
        timelines = conn.execute("""
            SELECT t.*, COUNT(e.id) as event_count
            FROM timelines t
            LEFT JOIN events e ON t.id = e.timeline_id
            GROUP BY t.id
        """).fetchall()
    return render_template("index.html", timelines=timelines)

@app.route("/timeline/new", methods=["GET", "POST"])
def new_timeline():
    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        with get_database() as conn:
            conn.execute(
                "INSERT INTO timelines (title, description) VALUES (?, ?)",
                (title, description)
            )
        flash("Timeline created!", "success")
        return redirect(url_for("index"))
    return render_template("edit_timeline.html", timeline=None)

@app.route("/timeline/<int:timeline_id>")
def view_timeline(timeline_id):
    with get_database() as conn:
        timeline = conn.execute(
            "SELECT * FROM timelines WHERE id = ?", (timeline_id,)
        ).fetchone()
        if not timeline:
            flash("Timeline not found.", "error")
            return redirect(url_for("index"))
        events = conn.execute(
            "SELECT * FROM events WHERE timeline_id = ? ORDER BY event_date ASC",
            (timeline_id,)
        ).fetchall()
    return render_template("timeline.html", timeline=timeline, events=events)

@app.route("/timeline/<int:timeline_id>/edit", methods=["GET", "POST"])
def edit_timeline(timeline_id):
    with get_database() as conn:
        timeline = conn.execute(
            "SELECT * FROM timelines WHERE id = ?", (timeline_id,)
        ).fetchone()
        if not timeline:
            flash("Timeline not found.", "error")
            return redirect(url_for("index"))
        if request.method == "POST":
            title = request.form["title"].strip()
            description = request.form["description"].strip()
            conn.execute(
                "UPDATE timelines SET title = ?, description = ? WHERE id = ?",
                (title, description, timeline_id)
            )
            flash("Timeline updated!", "success")
            return redirect(url_for("view_timeline", timeline_id=timeline_id))
    return render_template("edit_timeline.html", timeline=timeline)

@app.route("/timeline/<int:timeline_id>/delete", methods=["POST"])
def delete_timeline(timeline_id):
    with get_database() as conn:
        conn.execute("DELETE FROM timelines WHERE id = ?", (timeline_id,))
    flash("Timeline deleted.", "success")
    return redirect(url_for("index"))



# Event routes

@app.route("/timeline/<int:timeline_id>/events/new", methods=["GET", "POST"])
def new_event(timeline_id):
    with get_database() as conn:
        timeline = conn.execute(
            "SELECT * FROM timelines WHERE id = ?", (timeline_id,)
        ).fetchone()
        if not timeline:
            flash("Timeline not found.", "error")
            return redirect(url_for("index"))
        if request.method == "POST":
            title = request.form["title"].strip()
            description = request.form["description"].strip()
            event_date = request.form["event_date"]
            conn.execute(
                "INSERT INTO events (timeline_id, title, description, event_date) VALUES (?, ?, ?, ?)",
                (timeline_id, title, description, event_date)
            )
            flash("Event added!", "success")
            return redirect(url_for("view_timeline", timeline_id=timeline_id))
    return render_template("edit_event.html", timeline=timeline, event=event)

@app.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id):
    with get_database() as conn:
        event = conn.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ).fetchone()
        if not event:
            flash("Event not found.", "error")
            return redirect(url_for("index"))
        timeline = conn.execute(
            "SELECT * FROM timelines WHERE id = ?", (event["timeline_id"],)
        ).fetchone()
        if request.method == "POST":
            title = request.form["title"].strip()
            description = request.form["description"].strip()
            event_date = request.form["event_date"]
            conn.execute(
                "UPDATE events SET title = ?, description = ?, event_date = ? WHERE id = ?",
                (title, description, event_date, event_id)
            )
            flash("Event updated!", "success")
            return redirect(url_for("view_timeline", timeline_id=event["timeline_id"]))
    return render_template("edit_event.html", timeline=timeline, event=event)

@app.route("/events/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id):
    with get_database() as conn:
        event = conn.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ).fetchone()
        if event:
            timeline_id = event["timeline_id"]
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            flash("Event deleted.", "success")
            return redirect(url_for("view_timeline", timeline_id=timeline_id))
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run()