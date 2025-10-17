from flask import Flask, send_file, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
import time
import traceback

from edt_IG1 import scrape_and_generate, ICS_DEFAULT, JSON_DEFAULT

app = Flask(__name__)

LAST_STATS = None
LAST_RUN = None


def job_scrape():
    global LAST_STATS, LAST_RUN
    try:
        print("[job] Lancement du scraping...")
        json_path, ics_path, stats = scrape_and_generate(output_json=JSON_DEFAULT, output_ics=ICS_DEFAULT)
        LAST_STATS = stats
        LAST_RUN = time.time()
        print(f"[job] Terminé: {stats}")
    except Exception:
        print("[job] Erreur lors du scraping:")
        traceback.print_exc()


@app.route("/calendar.ics")
def calendar():
    # Serve the latest ICS file if present, otherwise return 503
    if os.path.exists(ICS_DEFAULT):
        # use minimal send_file signature for maximum compatibility with Flask 2.x and 3.x
        return send_file(ICS_DEFAULT, mimetype="text/calendar", as_attachment=False)
    return ("ICS not generated yet", 503)


@app.route('/ical')
def ical():
    """Parametric ICS endpoint for calendar subscription.

    Query params supported (for compatibility with typical iCal provider URLs):
      - class: class name to scrape (default IG1)
      - nbWeeks: number of weeks (ignored by scraper but accepted)
      - force=1 to force regeneration
      - token=... optional token to protect the endpoint (compare with ICAL_TOKEN env var)

    Behavior: if an existing ICS file is present and younger than 50 minutes and force is not set,
    it is returned directly. Otherwise the scraper is invoked to regenerate the ICS, then returned.
    """
    class_name = request.args.get('class', 'IG1')
    nb_weeks = request.args.get('nbWeeks')
    force = request.args.get('force') == '1'
    token = request.args.get('token')

    # simple token protection (optional)
    env_token = os.environ.get('ICAL_TOKEN')
    if env_token:
        if not token or token != env_token:
            return ("Forbidden", 403)

    # If recent ICS exists and not forcing, return it
    max_age = 50 * 60  # seconds
    try:
        if not force and os.path.exists(ICS_DEFAULT) and (time.time() - os.path.getmtime(ICS_DEFAULT) < max_age):
            return send_file(ICS_DEFAULT, mimetype='text/calendar', as_attachment=False)
    except Exception:
        pass

    # Otherwise regenerate (synchronous). This may be slow; subscription clients usually poll infrequently.
    try:
        print(f"[ical] Regenerating ICS for class={class_name} (nbWeeks={nb_weeks})")
        scrape_and_generate(output_json=JSON_DEFAULT, output_ics=ICS_DEFAULT, class_name=class_name)
    except Exception:
        import traceback
        traceback.print_exc()
        return ("Error generating ICS", 500)

    if os.path.exists(ICS_DEFAULT):
        return send_file(ICS_DEFAULT, mimetype='text/calendar', as_attachment=False)
    return ("ICS not generated", 500)


@app.route("/status")
def status():
    return jsonify({
        "last_run": LAST_RUN,
        "last_stats": LAST_STATS,
        "ics_path": ICS_DEFAULT,
    })


def run_server(host="0.0.0.0", port=5000):
    scheduler = BackgroundScheduler()
    # Cron trigger: minute 0 every hour between 6 and 20 inclusive
    scheduler.add_job(job_scrape, CronTrigger(minute=0, hour="6-20"), id="hp_scrape")
    scheduler.start()

    # Run an initial scrape on startup (non-blocking)
    try:
        job_scrape()
    except Exception:
        pass

    app.run(host=host, port=port)


if __name__ == '__main__':
    run_server()
