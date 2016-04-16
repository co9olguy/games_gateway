DEMO = False

import numpy as np
import pandas as pd
rated_games = pd.DataFrame( columns = ['objectid','name','thumbnail','rating'])

if DEMO:
    import graphlab as gl
    model = gl.load_model('model/gl_model')

from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.embed import components

import logging
import sys

from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

def create_recs_page(recs_df, show_page=True):
    # display variables
    margin = 0.05
    text_margin = 0.1
    size = 1 - 2 * margin
    N = max(min(len(recs_df),6),2)

    # get data from dataframe
    game_imgs = recs_df['thumbnail'].apply(lambda s: 'http:' + s)
    game_names = recs_df['name']  # .apply(lambda s: s.decode('utf-8'))
    numplayers = parse_players(recs_df)
    playtimes = parse_playtime(recs_df)

    # prepare html page and bokeh "plot"
    html_filename = 'recs/recommendations.html'
    output_file(html_filename, title="Your Games Recommendations")

    p = figure(x_range=(0 - margin, 5 + margin), y_range=(0 - margin, N + margin), height=200 * N, width=800, tools=[],
               title="Your game recommendations")
    x_locs = [margin] * N
    y_locs = [N - margin - ctr for ctr in range(0, N)]

    p.axis.visible = None
    p.grid.grid_line_color = None
    p.logo = None
    p.toolbar_location = None

    p.image_url(url=game_imgs, x=x_locs, y=y_locs, w=size, h=size)
    p.text(x=np.array(x_locs) + size + margin * 2, y=np.array(y_locs) - size / 2 + text_margin, text=game_names,
           text_baseline='middle', text_font_style='bold')  # game names/years
    p.text(x=np.array(x_locs) + size + margin * 2, y=np.array(y_locs) - size / 2, text=numplayers,
           text_baseline='middle')  # game player limits
    p.text(x=np.array(x_locs) + size + margin * 2, y=np.array(y_locs) - size / 2 - text_margin, text=playtimes,
           text_baseline='middle')  # game playtimes

    # if show_page:
    #    show(p)

    script, div = components(p)

    return script, div

def parse_players(players_df):
    min_players = players_df['minplayers'].astype(str)
    max_players = players_df['maxplayers'].astype(str)
    players_str = min_players + "-" + max_players + ' players'
    return players_str

def parse_playtime(players_df, minmax=False):
    min_playtime = players_df['minplaytime'].astype(str)
    max_playtime = players_df['maxplaytime'].astype(str)
    if minmax:
        playtime_str = min_playtime + "-" + max_playtime + ' minutes'
    else:
        playtime_str = max_playtime + ' minutes'
    return playtime_str

def get_filtered_games(filter_dict):

    # Defaults to stdout
    logging.basicConfig(level=logging.INFO)
    # get the logger for the current Python module
    log = logging.getLogger(__name__)

    q1b_list = ["""SELECT games.objectid as objectid, games.name as name, games.thumbnail as thumbnail, games.minplayers as minplayers, games.maxplayers as maxplayers, games.minplaytime as minplaytime, games.maxplaytime as maxplaytime FROM games"""]
    q2b_list = []

    q1 = "SELECT * FROM games " #note: on remote db, ranks table has already been joined and limited to top 2500
    if 'minplayers' in filter_dict:
        q2b_list.append("minplayers <= {}".format(filter_dict['minplayers']))
    if 'maxplayers' in filter_dict:
        q2b_list.append("maxplayers >= {}".format(filter_dict['maxplayers']))
    if 'minplaytime' in filter_dict:
        q2b_list.append("minplaytime >= {}".format(filter_dict['minplaytime']))
    if 'maxplaytime' in filter_dict:
        q2b_list.append("maxplaytime <= {}".format(filter_dict['maxplaytime']))
    if 'minage' in filter_dict:
        q2b_list.append("minage >= {}".format(filter_dict['minage']))

    if 'category' in filter_dict:
        #fix postgresql quote issues
        cat = filter_dict['category']
        if cat.find("'") != -1:
            cat = cat.replace("'","''")

        q1b_list.append("boardgamecategory ON games.objectid = boardgamecategory.objectid")
        q2b_list.append("""boardgamecategory = '{}'""".format(cat))

    if 'family' in filter_dict:
        fam = filter_dict['family']
        if fam.find("'") != -1:
            fam = fam.replace("'","''")

        q1b_list.append("boardgamefamily ON games.objectid = boardgamefamily.objectid")
        q2b_list.append("boardgamefamily = '{}'".format(fam))

    q1b = " JOIN ".join(q1b_list)
    q2b = " AND ".join(q2b_list)
    if len(q2b) > 0:
        qb = q1b + " WHERE " + q2b
    else:
        qb = q1b

    qb += ' ORDER BY games.rank'
    print qb

    try:
        log.info('querying database...')
        from sqlalchemy import create_engine
        DATABASE_URL = 'postgres://xsguljepueowms:IR7-TicHebWDkYr0WGZngcVsa5@ec2-23-21-157-223.compute-1.amazonaws.com:5432/d95o8es4f7241o'
        engine = create_engine(DATABASE_URL)
        filtered_games = pd.read_sql_query(qb, engine)

        return filtered_games

    except:
        _, ex, _ = sys.exc_info()
        log.error(ex.message)
        return pd.DataFrame #defaults to empty dataframe

@app.route('/')
def main():
    return redirect('/index')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/recommend')
def rec():
    global session_game_cntr
    session_game_cntr = 0
    return render_template('recommender.html')

@app.route('/_fetch_ratings_game')
def fetch_ratings_game():

    global session_game_cntr

    logging.basicConfig(level=logging.INFO)
    # get the logger for the current Python module
    log = logging.getLogger(__name__)

    game_name = request.args.get('name', type = str)
    query = r"SELECT objectid as objectid, name as name, thumbnail as thumbnail FROM games WHERE name = '" + game_name + r"'"
    print game_name
    print query
    try:
        log.info('querying database...')
        from sqlalchemy import create_engine
        DATABASE_URL = 'postgres://xsguljepueowms:IR7-TicHebWDkYr0WGZngcVsa5@ec2-23-21-157-223.compute-1.amazonaws.com:5432/d95o8es4f7241o'
        engine = create_engine(DATABASE_URL)
        selected_game = pd.read_sql_query(query, engine)
        selected_game['rating'] = np.nan
#        rated_games.append(selected_game, inplace=True)
    except:
        _, ex, _ = sys.exc_info()
        log.error(ex.message)
        return pd.DataFrame  # defaults to empty dataframe

    session_game_cntr += 1
    recs_html = render_template('game_rating_div.html',
                                session_game_number = session_game_cntr,
                                name = selected_game['name'].iloc[0],
                                img = 'http:'+selected_game['thumbnail'].iloc[0],
                                objectid = selected_game['objectid'].iloc[0])
    return jsonify(recs_html = recs_html, flag=0 )

@app.route('/_recommend')
def recommend():
    # apply filters based on user selections
    filter = {}
    if request.args.get('useplayers', type=str) == 'on':
        filter['minplayers'] = request.args.get('minplayers', type=int)
        filter['maxplayers'] = request.args.get('maxplayers', type=int)
    if request.args.get('useplaytime', type=str) == 'on':
        filter['minplaytime'] = request.args.get('minplaytime', type=int)
        filter['maxplaytime'] = request.args.get('maxplaytime', type=int)
    if request.args.get('useage', type=str) == 'on':
        filter['minage'] = request.args.get("minage", type=int)
    if request.args.get('usecategory', type=str) == 'on':
        category_args = request.args.get('category', None, type=str)
        if category_args is not None and category_args != '':
            filter['category'] = request.args.get('category', None, type=str)
    if request.args.get('usefamily', type=str) == 'on':
        family_args = request.args.get('family', None, type=str)
        if family_args is not None and family_args != '':
            filter['family'] = family_args
    filtered_games = get_filtered_games(filter)

    # recommender logic goes here...
    if DEMO:
        filtered_games_SFrame = gl.SFrame(filtered_games[['objectid']])
        filtered_games_SFrame.rename({'objectid':'item_id'}) # recommender system needs this format
        new_obs_data = gl.SFrame({'user_name' : ['web_user']*3,
                                  'item_id' : [234, 243, 91],
                                  'rating' : [10]*3})
        recommendations_SFrame = model.recommend(['web_user'],
                                          new_observation_data = new_obs_data, k=27,
                                          items=gl.SFrame(filtered_games_SFrame))
        recommendations_SFrame.rename({'item_id': 'objectid'})
        recommendations_df = recommendations_SFrame.to_dataframe()
        rec_games = pd.merge(recommendations_df, filtered_games, how='inner', on=['objectid'])
    else:
        rec_games = filtered_games

    CUTOFF = min(9, len(rec_games.index))
    rec_games = rec_games[0:CUTOFF]
    rec_games['link'] = rec_games['objectid'].apply(lambda objectid: 'http://boardgamegeek.com/boardgame/{}'.format(objectid))
    rec_games['img'] = rec_games['thumbnail'].apply(lambda thumbnail: 'http:{}'.format(thumbnail))

    # display results
    if rec_games.empty:
        return jsonify(result='Nothing here', return_string='Sorry, no games found matching your criteria. Try a less restrictive search', flag=-1)

    else:

        recs_html = render_template('game_rec_div.html', recs_dict = rec_games[['link','img','name','minplayers','maxplayers','minplaytime','maxplaytime']].to_dict(orient='split'))


        return jsonify(recs_html =  recs_html, flag=0 )


@app.route('/figure1')
def figure1():
    return render_template('figure1.html', script=script1, div=div1)


@app.route('/figure2')
def figure2():
    #  return render_template('figure1.html', script=script2, div=div2)
    # return url_for('static', filename='figure2.html')
    return render_template('figure2b.html')


@app.route('/explore')
def game_ratings():
    return render_template('game_ratings.html')


# @app.route('/rec_demo1')
# def rec_demo1():
#     return render_template('recommendation_demo_Core Eurogamer_top1000.html')
#
#
# @app.route('/rec_demo2')
# def rec_demo2():
#     return render_template('recommendation_demo_Family_starwars_trivia.html')


@app.route('/rec_demo3')
def rec_demo3():
    return render_template('recommendation_demo_War Gamer_.html')


# @app.route('/rec_demo4')
# def rec_demo4():
#     return render_template('recommendation_demo_Family Eurogamer_kickstarter.html')
#
#
# @app.route('/rec_demo5')
# def rec_demo5():
#     return render_template('recommendation_demo_Family Eurogamer_dinosaurs.html')
#
#
# @app.route('/rec_demo6')
# def rec_demo6():
#     return render_template('recommendation_demo_Family Eurogamer_sherlock_holmes.html')
#
#
# @app.route('/rec_demo7')
# def rec_demo7():
#     return render_template('recommendation_demo_Joke Game Fan_.html')


if __name__ == '__main__':
    app.run(port=33507)
