from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from service import PlayerService
from models import PlayerModel
from schema import Schema
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd

app = Flask(__name__)

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    return response

############################################################################################################################################################################

@app.route("/")
def home():
    return render_template("home.html")

############################################################################################################################################################################

# GET and POST for managing players
@app.route("/players", methods=["GET", "POST"])
def players():
    if request.method == "POST":
        player_data = {
            "name": request.form["name"],
            "home_runs": int(request.form["home_runs"]),
            "ops_plus": int(request.form["ops_plus"]),
            "war": float(request.form["war"]),
            "owar": float(request.form["owar"]),
            "dwar": float(request.form["dwar"]),
            "drs": int(request.form["drs"])
        }
        PlayerService().create(player_data)
        return redirect(url_for("players"))

    return render_template("players.html", players=PlayerService().list())

############################################################################################################################################################################

# GET, PUT, DELETE operations for a single player by ID
@app.route("/player/<int:player_id>", methods=["GET", "PUT", "DELETE"])
def manage_player(player_id):
    player_service = PlayerService()

    # Handle GET request - Fetch a single player
    if request.method == "GET":
        player = player_service.get_by_id(player_id)
        if player is None:
            abort(404)  # Player not found
        return jsonify(player)

    # Handle PUT request - Update player details
    elif request.method == "PUT":
        player_data = request.get_json()
        updated_player = player_service.update(player_id, player_data)
        if updated_player is None:
            abort(404)  # Player not found
        return jsonify(updated_player)

    # Handle DELETE request - Remove player
    elif request.method == "DELETE":
        success = player_service.delete(player_id)
        if not success:
            abort(404)  # Player not found
        return jsonify({"message": "Player deleted successfully"})

############################################################################################################################################################################


@app.route("/player/<int:player_id>/update", methods=["GET", "POST"])
def update_player(player_id):
    player_model = PlayerModel()
    
    if request.method == "POST":
        # Get updated player data from form
        updated_data = {
            "id": player_id,
            "name": request.form["name"],
            "home_runs": int(request.form["home_runs"]),
            "ops_plus": int(request.form["ops_plus"]),
            "war": float(request.form["war"]),
            "owar": float(request.form["owar"]),
            "dwar": float(request.form["dwar"]),
            "drs": int(request.form["drs"])
        }
        
        # Call update method from PlayerModel
        player_model.update(updated_data)
        return redirect(url_for("players"))  # Redirect back to players list after update

    # If GET request, retrieve current player data for pre-filling the form
    player = player_model.get_by_id(player_id)
    if player is None:
        abort(404)  # Handle player not found

    return render_template("update_player.html", player=player)


############################################################################################################################################################################

@app.route("/player/<int:player_id>/delete", methods=["POST"])
def delete_player(player_id):
    PlayerService().delete(player_id)
    return redirect(url_for("players"))


############################################################################################################################################################################

@app.route("/player/<int:player_id>/stats", methods=["GET"])
def player_stats(player_id):
    player_model = PlayerModel()
    player = player_model.get_by_id(player_id)

    if player is None:
        abort(404)  # Handle player not found

    all_players = player_model.get_all()
    all_players_data = pd.DataFrame([{
        'home_runs': p['home_runs'],
        'ops_plus': p['ops_plus'],
        'war': p['war'],
        'owar': p['owar'],
        'dwar': p['dwar'],
        'drs': p['drs']
    } for p in all_players])

    league_averages = {
        "home_runs": all_players_data['home_runs'].mean(),
        "ops_plus": all_players_data['ops_plus'].mean(),
        "war": all_players_data['war'].mean(),
        "owar": all_players_data['owar'].mean(),
        "dwar": all_players_data['dwar'].mean(),
        "drs": all_players_data['drs'].mean()
    }

    metrics = ["home_runs", "ops_plus", "war", "owar", "dwar", "drs"]
    plots_html = {}

    for metric in metrics:
        player_value = player[metric]
        league_value = league_averages[metric]

        fig = go.Figure(data=[
            go.Bar(name=player['name'], x=[metric], y=[player_value], marker_color='blue'),
            go.Bar(name='League Average', x=[metric], y=[league_value], marker_color='orange')
        ])

        fig.update_layout(
            title=f"{metric.capitalize()} for {player['name']}",
            barmode='group',
            xaxis_title='Metric',
            yaxis_title='Value'
        )

        plots_html[metric] = fig.to_html(full_html=False)

    return render_template('player_stats.html', player=player, plots_html=plots_html)

############################################################################################################################################################################

if __name__ == "__main__":
    Schema()
    app.run(debug=True, host='0.0.0.0', port=5000)
