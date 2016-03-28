from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.embed import components

def parse_players(players_df):
    min_players = players_df['minplayers'].astype(str)
    max_players = players_df['maxplayers'].astype(str)
    players_str = min_players + "-" + max_players + ' players'
    return players_str

def parse_playtime(players_df):
    min_playtime = players_df['minplaytime'].astype(str)
    max_playtime = players_df['maxplaytime'].astype(str)
    playtime_str = min_playtime + "-" + max_playtime + ' minutes'
    return playtime_str

def create_recs_page(recs_df, show_page=True):
    
    #display variables
    margin = 0.05
    text_margin = 0.1
    size = 1-2*margin
    N=6
    
    #get data from dataframe
    game_imgs = recs_df['thumbnail'].apply(lambda s: 'http:'+s)
    game_names = recs_df['name'].apply(lambda s: s.decode('utf-8'))
    numplayers = parse_players(recs_df)
    playtimes = parse_playtime(recs_df)

    #prepare html page and bokeh "plot"
    html_filename = 'recs/recommendations.html'
    output_file(html_filename, title = "Your Games Recommendations")

    p = figure(x_range=(0-margin,5+margin), y_range=(0-margin,N+margin), height = 200*N, width = 1000,tools=[],title="Game recommendations") 
    x_locs = [margin]*N
    y_locs = [N-margin-ctr for ctr in range(0,N)]

    p.axis.visible = None
    p.grid.grid_line_color = None
    p.logo = None
    p.toolbar_location = None

    p.image_url(url = game_imgs, x = x_locs, y = y_locs, w = size, h = size) 
    p.text(x=np.array(x_locs) + size + margin*2, y=np.array(y_locs)-size/2+text_margin, text=game_names, text_baseline = 'middle', text_font_style = 'bold') #game names/years
    p.text(x=np.array(x_locs) + size + margin*2, y=np.array(y_locs)-size/2, text=numplayers, text_baseline = 'middle') #game player limits
    p.text(x=np.array(x_locs) + size + margin*2, y=np.array(y_locs)-size/2-text_margin, text=playtimes, text_baseline = 'middle') #game playtimes

    if show_page:
        show(p)
    
    script, div = components(p)
    
    return script, div
