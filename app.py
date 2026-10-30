
import os
import requests
from urllib.parse import quote
from flask import Flask, render_template, jsonify

app = Flask(__name__)

JENKINS_URL = os.getenv(
    "JENKINS_URL", "http://127.0.0.1:8080"
).rstrip("/")

JENKINS_JOB = os.getenv("JENKINS_JOB", "DeployEase-Pipeline")
JENKINS_USER = os.getenv("JENKINS_USER", "")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "")

JOB_PATH = "/job/" + quote(JENKINS_JOB, safe="")


def jenkins_request(method, path):
    if not JENKINS_USER or not JENKINS_TOKEN:
        raise RuntimeError("Jenkins username or API token is missing")

    response = requests.request(
        method,
        JENKINS_URL + path,
        auth=(JENKINS_USER, JENKINS_TOKEN),
        timeout=30,
        allow_redirects=False
    )

    response.raise_for_status()
    return response


@app.route("/")
def home():
    return render_template("index.html")


# Trigger Jenkins deployment
@app.route("/api/deploy", methods=["POST"])
def deploy():
    try:
        response = jenkins_request(
            "POST",
            JOB_PATH + "/build"
        )

        if response.status_code not in (200, 201, 202):
            return jsonify({
                "success": False,
                "message": "Unexpected Jenkins response"
            }), 502

        return jsonify({
            "success": True,
            "message": "Deployment triggered successfully!"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# Latest Jenkins build status
@app.route("/api/status")
def status():
    try:
        response = jenkins_request(
            "GET",
            JOB_PATH + "/lastBuild/api/json"
        )

        build = response.json()

        return jsonify({
            "success": True,
            "number": build.get("number"),
            "building": build.get("building", False),
            "result": (
                "IN PROGRESS"
                if build.get("building")
                else build.get("result", "UNKNOWN")
            ),
            "url": build.get("url")
        })

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return jsonify({
                "success": True,
                "number": None,
                "building": False,
                "result": "NO BUILDS YET"
            })

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# Previous Jenkins builds
@app.route("/api/builds")
def builds():
    try:
        response = jenkins_request(
            "GET",
            JOB_PATH +
            "/api/json?tree=builds[number,result,building,timestamp,duration,url]{0,10}"
        )

        return jsonify({
            "success": True,
            "builds": response.json().get("builds", [])
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# Latest Jenkins console logs
@app.route("/api/logs")
def logs():
    try:
        response = jenkins_request(
            "GET",
            JOB_PATH + "/lastBuild/consoleText"
        )

        return jsonify({
            "success": True,
            "logs": response.text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
