use_gl = True

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from bokeh.plotting import Figure
from bokeh.models import Range1d, ColumnDataSource, HoverTool
from bokeh.embed import components
from bokeh.models.widgets import HBox, Slider, VBoxForm, Select, TextInput
from bokeh.io import curdoc

if use_gl:
    import graphlab as gl
    #model = gl.load_model('model/gl_model')
    model = gl.load_model('model/model_12ft_lr0.01_iter1000')

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
        DATABASE_URL = 'postgres://xsguljepueowms:IR7-TicHebWDkYr0WGZngcVsa5@ec2-23-21-157-223.compute-1.amazonaws.com:5432/d95o8es4f7241o'
        engine = create_engine(DATABASE_URL)
        filtered_games = pd.read_sql_query(qb, engine)

        return filtered_games

    except:
        _, ex, _ = sys.exc_info()
        log.error(ex.message)
        return pd.DataFrame #defaults to empty dataframe

@app.route('/_fetch_ratings_game')
def fetch_ratings_game():

    global rated_games

    logging.basicConfig(level=logging.INFO)
    # get the logger for the current Python module
    log = logging.getLogger(__name__)

    game_name = request.args.get('name', '', type = unicode)
    print rated_games['name'].values
    if game_name in rated_games['name'].values:
        return jsonify(flag = 1)
    else:

        query = r"SELECT objectid as objectid, name as name, thumbnail as thumbnail FROM games WHERE name = '" + game_name + r"'"
        print game_name
        print query
        try:
            log.info('querying database...')
            DATABASE_URL = 'postgres://xsguljepueowms:IR7-TicHebWDkYr0WGZngcVsa5@ec2-23-21-157-223.compute-1.amazonaws.com:5432/d95o8es4f7241o'
            engine = create_engine(DATABASE_URL)
            selected_game = pd.read_sql_query(query, engine)
            selected_game['rating'] = 3 # default rating
            rated_games = rated_games.append(selected_game, ignore_index=True)
            print rated_games

            recs_html = render_template('game_rating_div.html',
                                        name = selected_game['name'].iloc[0],
                                        img = 'http:'+selected_game['thumbnail'].iloc[0],
                                        objectid = selected_game['objectid'].iloc[0])

            return jsonify(recs_html = recs_html, flag=0 )

        except:
            _, ex, _ = sys.exc_info()
            log.error(ex.message)
            return jsonify( flag=-1 )



@app.route('/_recommend')
def recommend():

    global rated_games

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
    if request.args.get('usernamecheck', type=str) == 'off' and (len(rated_games) == 0 or
                                                                 request.args.get('ignoreratings', type=str) == 'on' or
                                                                 use_gl==False): # recommend by popularity
        rec_games = filtered_games
    else: #use ratings to recommend
        if request.args.get('usernamecheck', type=str) == 'on':
            rec_username = request.args.get('username', type=str)
        else:
            rec_username = 'gg_web_user_dummy'
        filtered_games_SFrame = gl.SFrame(filtered_games[['objectid']])
        filtered_games_SFrame.rename({'objectid':'item_id'}) # recommender system needs this format
        if request.args.get('ignoreratings', type=str) == 'on':
            new_obs_data = gl.SFrame({'user_name' : [],
                                      'item_id' : [],
                                      'rating' : []})
        else:
            new_obs_data = gl.SFrame({'user_name' : [rec_username]*len(rated_games),
                                      'item_id' : [int(o) for o in rated_games['objectid']],
                                      'rating' : [2*rating for rating in rated_games['rating']]}) # bgg scores are 1-10

        recommendations_SFrame = model.recommend([rec_username],
                                          new_observation_data = new_obs_data, k=27,
                                          diversity = 0,
                                          items=gl.SFrame(filtered_games_SFrame))
        recommendations_SFrame.rename({'item_id': 'objectid'})
        recommendations_df = recommendations_SFrame.to_dataframe()
        rec_games = pd.merge(recommendations_df, filtered_games, how='inner', on=['objectid'])


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


@app.route('/')
def main():
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/recommend')
def rec():
    global rated_games
    rated_games = pd.DataFrame(columns=['objectid', 'name', 'thumbnail', 'rating'])
    return render_template('recommender.html')

@app.route('/_add_rating')
def add_rating():
    global rated_games
    objectid = request.args.get('objectid', type=int)
    rating = request.args.get('rating', type=float)
    rated_games.loc[rated_games['objectid'] == objectid, 'rating']=rating
    print rated_games
    return jsonify(msg = 'Rating: {}'.format(int(rating)))


@app.route('/explore')
def explorer_page():
    return render_template('game_ratings.html')

@app.route('/_explore')
def update_explorer():
    #query = "SELECT * FROM games WHERE rank <= 100 LIMIT 100"
    #DATABASE_URL = 'postgres://xsguljepueowms:IR7-TicHebWDkYr0WGZngcVsa5@ec2-23-21-157-223.compute-1.amazonaws.com:5432/d95o8es4f7241o'
    #engine = create_engine(DATABASE_URL)
    #games = pd.read_sql_query(query, engine)
    games = pd.read_csv('static/games_full.csv')

    games["color"] = "blue"
    games.fillna(0, inplace=True)

    axis_map = {
        "Year Published": "yearpublished",
        "Average Rating": "bayes_avg_rating",
        "Boardgamegeek Rank": "rank",
        "Min Players": "minplayers",
        "Max Players": "maxplayers",
        "Min Playtime": "minplaytime",
        "Max Playtime": "maxplaytime",
        "Min Age": "minage"
    }
    ordered_keys = [
        "Year Published",
        "Average boardgamegeek Rating",
        "Rank",
        "Min Players",
        "Max Players",
        "Min Playtime",
        "Max Playtime",
        "Min Age"
    ]

    # Create Column Data Source that will be used by the plot
    source = ColumnDataSource(data=dict(x=[], y=[], color=[], name=[], year=[], thumbnail=[]))

    hover = HoverTool(
        tooltips="""
            <section style="width:350px; float:left; padding:10px;">
                    <img src="@img" height="42" alt="@name" width="42" style="float: left; margin: 0px 15px 15px 0px;" border="2"></img>
                    <span style="font-size: 17px; font-weight: bold;">@name (@year)</span>
            </section>
            """)

    #name = TextInput(title="Name contains")
    x_axis = Select(title="X Axis", options=ordered_keys, value="Year Published")
    y_axis = Select(title="Y Axis", options=ordered_keys, value="Average boardgamegeek Rating")

    filter = {}
    filter['minplayers'] = request.args.get('minplayers', type=int)
    filter['maxplayers'] = request.args.get('maxplayers', type=int)
    filter['minplaytime'] = request.args.get('minplaytime', type=int)
    filter['maxplaytime'] = request.args.get('maxplaytime', type=int)
    filter['minyear'] = request.args.get("minyear", type=int)
    filter['maxyear'] = request.args.get("maxyear", type=int)
    filter['minage'] = request.args.get("minage", type=int)
    filter['rank'] = request.args.get("rank", type=int)
    x_axis = request.args.get("xaxis")
    y_axis = request.args.get("yaxis")

    p = Figure(plot_height=600, plot_width=800, title="", toolbar_location=None, tools=[hover])
    p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha=0.25)

    def select_games():
        selected = games[
            #(games["yearpublished"] >= year.value) &
            (games["maxplayers"] <= filter['maxplayers']) &
            (games["minplayers"] >= filter['minplayers']) &
            (games["maxplaytime"] <= filter['maxplaytime']) &
            (games["minplaytime"] >= filter['minplaytime']) &
            (games["yearpublished"] >= filter['minyear']) &
            (games["yearpublished"] <= filter['maxyear']) &
            (games["minage"] >= filter['minage']) &
            (games["rank"] <= filter['rank'])
            ]
        #name_val = name.value.strip()
        #if (name_val != ""):
        #    selected = selected[selected.name.str.contains(name_val) == True]
        return selected

    def update(attrname, old, new):
        df = select_games()

        x_name = axis_map[x_axis]
        y_name = axis_map[y_axis]

        p.xaxis.axis_label = x_axis
        p.yaxis.axis_label = y_axis
        p.title = "%d games selected" % len(df)
        source.data = dict(
            x=df[x_name],
            y=df[y_name],
            color=df["color"],
            name=df["name"],
            year=df["yearpublished"],
            img=df['thumbnail'].apply(lambda s: 'http:'+str(s))
        )

    update(None, None, None)  # initial view

    script, div = components(p)
    return jsonify(plot=render_template('tmp.html',script=script, div=div), flag = 0)

if __name__ == '__main__':
    app.run(port=33507)
