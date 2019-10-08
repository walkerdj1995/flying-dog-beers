# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 09:32:06 2019

@author: GR5842
"""

import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import datetime


url1 = 'https://raw.githubusercontent.com/walkerdj1995/flying-dog-beers/master/eset.csv'
url2 = 'https://raw.githubusercontent.com/walkerdj1995/flying-dog-beers/master/EVis.csv'

e_set = pd.read_csv(url1,na_values=['#VALUE!', '#DIV/0!'])
e_vis = pd.read_csv(url2) 

# ----------------- Pre-Processing----------------------------------------------------------
# Change colnames
names = ["Source","ID","E_Vis_Ref","Tender_Type","Description","Client",\
          "Tender_Status","Plots","GIFA","Unit","County","Order_Date","Estimator",\
          "Trade","Contractor","Value","Position","Cost_Plot","Cost_M2",\
          "Value_Calc","Enquiry_Sent","Price_Returned","First","Second","Third","Top_three",\
          "Preferred","Year","Quarter","YQ","Space_Check"]

e_set.columns = names

# Replace nans with 0 and make whole column floats
e_set = e_set.fillna(0)
e_set["Cost_M2"] = pd.to_numeric(e_set["Cost_M2"])
e_set.replace('SWREG','OU4',inplace=True)

e_set['YQ'] = e_set['YQ'].str.replace('Q','')
e_set['YQ'] = e_set['YQ'].astype(str)
e_set['YQ'] = e_set['YQ'].replace('nan', '2000 - 1')

e_vis['Date Created'] = pd.to_datetime(e_vis['Date Created'])
e_vis.dropna(subset=['Date Created', ' Order Cost','Level 1 & 2'],inplace = True)

x = 0


#%%

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def ScriptMain():
    
    dataTable1 = dt.DataTable(
        id='datatable-interactivity',
        columns=[{'id': c, 'name': c} for c in ["Trade","Number of Quotes","Min Cost/M2(£)","Mean Cost/M2(£)","Max Cost/M2(£)","Min Cost/Plot(£)","Mean Cost/Plot(£)","Max Cost/Plot(£)",'Input Value']],
        sort_action='native',
        editable = True,
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
        {   
            'if': {
                'column_id': 'Min Cost/M2(£)',
                    },
            'backgroundColor': '#FAEBD7'
        },
        {   
            'if': {
                'column_id': 'Mean Cost/M2(£)',
                    },
            'backgroundColor': '#FAEBD7'
        },
        {   
            'if': {
                'column_id': 'Max Cost/M2(£)',
                    },
            'backgroundColor': '#FAEBD7'
        },
                    {   
            'if': {
                'column_id': 'Min Cost/Plot(£)',
                    },
            'backgroundColor': '#97FFFF'
        },
        {   
            'if': {
                'column_id': 'Mean Cost/Plot(£)',
                    },
            'backgroundColor': '#97FFFF'
        },
        {   
            'if': {
                'column_id': 'Max Cost/Plot(£)',
                    },
            'backgroundColor': '#97FFFF'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center'},
    )

        
    
    dataTable2 = dt.DataTable(
        id='tab2',
        columns=[{'id': c, 'name': c} for c in ["Trade","Quoted Cost/M2","Quoted Cost/Plot",'Flag Cost/M2','Flag Cost/Plot']],
        sort_action='native',
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
    
        {   
            'if': {
                'column_id': 'Flag Cost/M2',
                'filter_query': '{Flag Cost/M2} eq "Out of Range"'
                    },
            'backgroundColor': '#FF4040',
            'color': 'white'
        },
        {   
            'if': {
                'column_id': 'Flag Cost/Plot',
                'filter_query': '{Flag Cost/Plot} eq "Out of Range"'
                    },
            'backgroundColor': '#FF4040',
            'color': 'white',
        },
        {   
            'if': {
                'column_id': 'Flag Cost/Plot',
                'filter_query': '{Flag Cost/Plot} eq "OK"'
                    },
            'backgroundColor': '#7FFF00'
        },
        {   
            'if': {
                'column_id': 'Flag Cost/M2',
                'filter_query': '{Flag Cost/M2} eq "OK"'
                    },
            'backgroundColor': '#7FFF00'
        },
         {   
            'if': {
                'column_id': 'Quoted Cost/M2',
                    },
            'backgroundColor': '#FAEBD7'
        },
        {   
            'if': {
                'column_id': 'Quoted Cost/Plot',
                    },
            'backgroundColor': '#97FFFF'
        },
        
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center'},
    )
    
    dataTable3 = dt.DataTable(
        id='tab3',
        columns=[{'id': c, 'name': c} for c in ['Contractor','Enquiry_Sent',"Price_Returned","% Return Rate","First","Top_three"]],
        sort_action='native',
        filter_action="native",
        row_selectable="multi",
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': '#8ebcff',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center'},
    )
    
    vistable = dt.DataTable(
        id='vistab',
        columns=[{'id': c, 'name': c} for c in ['Job No',"Subcontractor Name","Helped at Tender?"," Estimating Budget"," Order Cost"," Buying Gain"]],
        sort_action='native',
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center'},
    )
    
    dataTable4 = dt.DataTable(
        id='contact',
        columns=[{'id': c, 'name': c} for c in ["Contractor","email","tel"]],
        style_header={
        'backgroundColor': '#8ebcff',
        'fontWeight': 'bold'
    },
    )
    
    dataTable5 = dt.DataTable(
        id='joblist',
        columns=[{'id': c, 'name': c} for c in ["E_Vis_Ref","Estimator"]],
        row_selectable="multi",
        style_header={
        'backgroundColor': '#8ebcff',
        'fontWeight': 'bold'
    },
    )

    # Home layout.
    layoutHome = html.Div([
            
            dcc.Store(id = 'memory'),
            
			# Add dashbaord header/title.            
             dbc.Row([
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'trade choice',
        					options=[
               					{'label': i, 'value': i} for i in list(e_set.Trade.unique())
            						],
            					placeholder="Select a Trade",
        						value = "***F_LO Brickwork",
                                multi=True
        						),
                    dcc.RadioItems(id='select-all-tr',
                            options=[{'label': 'Select Key Trades', 'value': 'keytr'},
                                     {'label': 'Reset', 'value': 'settr'}])],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'OU',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.Unit.unique())
            							],
            					placeholder="Select Ops Unit",
        						#value = "OU1",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-OU',
                            options=[{'label': 'Select All', 'value': 'allOU'},
                                     {'label': 'Reset', 'value': 'setOU'}])],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Market"),
        			dcc.Dropdown(id = 'Market',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique())
            							],
            					placeholder="Select Market",
        						#value = "NB - Housing",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-ma',
                            options=[{'label': 'Select All', 'value': 'allma'},
                                     {'label': 'Reset', 'value': 'setma'}])],
                    align = "center",
                    
                    width={"size": 4}),
                    
                    ],
                    justify = 'around',
                    style = {'padding':30}),
                    
            dbc.Row([
                    dbc.Col([
                            
                    html.Label("Position"),
                    dcc.Dropdown(id = 'pos',
        					options=[
               					{'label': i, 'value': i} for i in list(e_set.Position.unique())
            						],
            					placeholder="Choose Position",
        						#value = "1",
                                multi=True
        						),
                    dcc.RadioItems(id='select-all-po',
                            options=[{'label': 'Select All', 'value': 'allpo'},
                                     {'label': 'Reset', 'value': 'setpo'}])],
                     align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("County"),
                    dcc.Dropdown(id = 'cou',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.County.unique())
            							],
            					placeholder="Select County",
        						#value = "West Yorkshire",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-co',
                            options=[{'label': 'Select All', 'value': 'allco'},
                                     {'label': 'Reset', 'value': 'setco'}])],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Year-Quarter"),
        			dcc.Slider(
                            id = 'yq',
                            min=0,
                            max=2,
                            step=None,
                            marks={
                                    0 : 'All',
                                    1 : 'Last 12 Months',
                                    2 : 'Last 24 Months'},
                            value=0
                        )],
                    align = "center",
                    
                    width={"size": 4})],
                    justify = 'around',
                    style = {'padding':30}),
                    
             dbc.Row([
                    dbc.Col([html.H2("Summary of Costs",style={'textAlign':'center'}),dataTable1],width=8,align='end'),
                      
                    #dbc.Col([html.H2("Budget Cost vs Actual Cost by Subcontractor",style={'textAlign':'center'}),dcc.Graph(id = 'timeseries')],width={"size": 6, "offset": 0},align="center")
                    
                    ],
                    
                    justify = "end",
                    style = {'padding':30}
                            ),
             dcc.Store(id='intermediate-value'),
                     
             dbc.Row([
                    dbc.Col([html.Label('GIFA'),dcc.Input(id = 'gifa',type='number',placeholder = 'Input GIFA')],width=2),
                    dbc.Col([html.Label('Plots'),dcc.Input(id = 'plots',type='number',placeholder = 'Input number of plots')],width=3),
                    dbc.Col([html.Button(['Update'],id='btn')],width = 2, align = 'right'),
                    ],
                    
                    justify = "end",
                    style = {'padding':30}
                            ),
                     
            dbc.Row([
                    dbc.Col([html.H2("Comparison Table",style={'textAlign':'center'}),dataTable2],width=8)],
                    justify = "end",
                    style = {'padding':30}
                    ),
                     
                    
# =============================================================================
#             dbc.Row([
#                     dbc.Col([dataTable1], width={"size": 4, "offset": 0},align="center"),
#                             
#                     dbc.Col([html.H2("Cost Per M2 Coloured By Status",style={'textAlign':'center'}),dcc.Graph(id = "sca")], width={"size": 6, "offset": 0},align="center"),
#                     
#                     dbc.Col([html.H2("Cost Per M2 By Position",style={'textAlign':'center'}),dcc.Graph(id = "vio")], width={"size": 6, "offset": 0},align="center")
#                     ],
#                     
#                     justify = "around"
#                             )
# =============================================================================
            html.Div([
                    dataTable5])
            ]
        )
            
             
    layoutPerf = html.Div([
            
			# Add dashbaord header/title.            
             dbc.Row([
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'trade choicep',
        					options=[
               					{'label': i, 'value': i} for i in list(e_set.Trade.unique())
            						],
            					placeholder="Select a Trade",
        						value = "***F_LO Brickwork",
                                multi=True
        						)],
                     align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'OUp',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.Unit.unique())
            							],
            					placeholder="Select Ops Unit",
        						#value = "OU1",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-OUp',
                            options=[{'label': 'Select All', 'value': 'allOUp'},
                                     {'label': 'Reset', 'value': 'setOUp'}])],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Market"),
        			dcc.Dropdown(id = 'Marketp',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique())
            							],
            					placeholder="Select Market",
        						#value = "NB - Housing",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-map',
                            options=[{'label': 'Select All', 'value': 'allmap'},
                                     {'label': 'Reset', 'value': 'setmap'}])],
                    align = "center",
                    
                    width={"size": 4}),
                    
                    ],
                    justify = 'around',
                    style = {'padding':30}),
                    
            dbc.Row([
                    dbc.Col([
                            
                    html.Label("Position"),
                    dcc.Dropdown(id = 'posp',
        					options=[
               					{'label': i, 'value': i} for i in list(e_set.Position.unique())
            						],
            					placeholder="Choose Position",
        						#value = "1",
                                multi=True
        						),
                    dcc.RadioItems(id='select-all-posp',
                            options=[{'label': 'Select All', 'value': 'allposp'},
                                     {'label': 'Reset', 'value': 'setposp'}])],
                     align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("County"),
                    dcc.Dropdown(id = 'coup',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.County.unique())
            							],
            					placeholder="Select County",
        						#value = "West Yorkshire",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-coup',
                            options=[{'label': 'Select All', 'value': 'allcoup'},
                                     {'label': 'Reset', 'value': 'setcoup'}])],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Year-Quarter"),
        			dcc.Slider(
                            id = 'yqp',
                            min=0,
                            max=2,
                            step=None,
                            marks={
                                    0 : 'All',
                                    1 : 'Last 12 Months',
                                    2 : 'Last 24 Months'},
                            value=0
                        )],
                    align = "center",
                    
                    width={"size": 4})],
                    justify = 'around',
                    style = {'padding':30}),
                    
           dbc.Row([
                    dbc.Col([html.H2("Subcontractor List",style={'textAlign':'center'}),dataTable3],width=6,align="center"),
                    dbc.Col([html.H2('Contact Details',style={'textAlign':'center'}),dataTable4],width=4,align='start'),
                    ],
                    
                    justify = "center",
                            )
           ])
                
        
    layoutMap = html.Div([
            dbc.Row([
                     dbc.Col(html.H3("E-Set Filters",style={'textAlign':'center'}),width = {'size':6}),
                     dbc.Col(html.H3("E-Vision Filters",style={'textAlign':'center'}),width = {'size':6})]),
			# Add dashbaord header/title.            
            dbc.Row([
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'trade choice2',
        					options=[
               					{'label': i, 'value': i} for i in list(e_set.Trade.unique())
            						],
            					placeholder="Select a Trade",
        						value = "***F_LO Brickwork"
        						)],
                     align = "center",
                    
                    width = {'size':2}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'OU2',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.Unit.unique())
            							],
            					placeholder="Select Ops Unit",
        						value = "OU1"
        						)],
                    align = "center",
                    
                    width = {'size':2}),
                    
                    dbc.Col([
                    html.Label("Market"),
        			dcc.Dropdown(id = 'Market2',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique())
            							],
            					placeholder="Select Market",
        						value = "NB - Housing"
        						)],
                    align = "center",
                    
                    width={"size": 2}),
                    
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'vistrade2',
        					options=[
               					{'label': i, 'value': i} for i in list(e_vis.Trade.unique())
            						],
            					placeholder="Select a Trade",
        						value = "Brickwork"
        						)],
                     align = "center",
                    
                    width = {'size':2}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'visops2',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_vis.Division.unique())
            							],
            					placeholder="Select Ops Unit",
        						value = "Central OU1"
        						)],
                    align = "center",
                    
                    width = {'size':2}),
                    
                    dbc.Col([
                    html.Label("Market"),
        			dcc.Dropdown(id = 'vismark2',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_vis['Level 1 & 2'].unique())
            							],
            					placeholder="Select Market",
        						value = "New Build - Housing"
        						)],
                    align = "center",
                    
                    width={"size": 2}),
                    ],
                    justify = 'around',
                    style = {'padding':30}),
                    
            dbc.Row([
                    #dbc.Col([dataTable2], width={"size": 6, "offset": 0},align="center"),
                            
                    dbc.Col([html.H2("Subcontractor Summary",style={'textAlign':'center'}),dcc.Graph(id = "enq")], width={"size": 12, "offset": 0},align="center")
                    ],
                    
                    justify = "around"
                            ),
             dbc.Row([
                    dbc.Col([html.H3("Subcontractors That Are Pricing",style={'textAlign':'center'}),dcc.Graph(id = 'price')], width={"size": 6, "offset": 0},align="center"),
                            
                    dbc.Col([html.H3("Subcontractors Receiving Work",style={'textAlign':'center'}),dcc.Graph(id = "work")], width={"size": 6, "offset": 0},align="center")
                    ],
                    
                    justify = "around"
                            )
            ]
        )
             
# =============================================================================
#     layoutFinGraphs = html.Div([
#             
# 			# Add dashbaord header/title.            
#              dbc.Row([
#                     dbc.Col([
#                             
#                     html.Label("Trade"),
#                     dcc.Dropdown(id = 'trade choiceg',
#         					options=[
#                					{'label': i, 'value': i} for i in list(e_set.Trade.unique())
#             						],
#             					placeholder="Select a Trade",
#         						value = "***F_LO Brickwork",
#                                 multi=True
#         						)],
#                      align = "center",
#                     
#                     width = {'size':4}),
#                     
#                     dbc.Col([
#                     html.Label("Ops Unit"),
#                     dcc.Dropdown(id = 'OUg',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set.Unit.unique())
#             							],
#             					placeholder="Select Ops Unit",
#         						#value = "OU1",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width = {'size':4}),
#                     
#                     dbc.Col([
#                     html.Label("Market"),
#         			dcc.Dropdown(id = 'Marketg',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique())
#             							],
#             					placeholder="Select Market",
#         						#value = "NB - Housing",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width={"size": 4}),
#                     
# 
#                     ],
#                     justify = 'around',
#                     style = {'padding':30}),
#                     
#             dbc.Row([
#                     dbc.Col([
#                             
#                     html.Label("Position"),
#                     dcc.Dropdown(id = 'posg',
#         					options=[
#                					{'label': i, 'value': i} for i in list(e_set.Position.unique())
#             						],
#             					placeholder="Choose Position",
#         						#value = "1",
#                                 multi=True
#         						)],
#                      align = "center",
#                     
#                     width = {'size':4}),
#                     
#                     dbc.Col([
#                     html.Label("County"),
#                     dcc.Dropdown(id = 'coug',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set.County.unique())
#             							],
#             					placeholder="Select County",
#         						#value = "West Yorkshire",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width = {'size':4}),
#                     
#                     dbc.Col([
#                     html.Label("Year-Quarter"),
#         			dcc.Dropdown(id = 'yqg',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set.YQ.unique())
#             							],
#             					placeholder="Select Quarter",
#         						#value = "2019 - Q1",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width={"size": 4})],
#                     justify = 'around',
#                     style = {'padding':30}),
#                     
#                     
#             dbc.Row([
#                     #dbc.Col([dataTable1], width={"size": 4, "offset": 0},align="center"),
#                             
#                     dbc.Col([html.H2("Cost Per M2 Coloured By Status",style={'textAlign':'center'}),dcc.Graph(id = "sca")], width={"size": 6, "offset": 0},align="center"),
#                     
#                     dbc.Col([html.H2("Cost Per M2 By Position",style={'textAlign':'center'}),dcc.Graph(id = "vio")], width={"size": 6, "offset": 0},align="center")
#                     ],
#                     
#                     justify = "around"
#                             )
#             ]
#         )
# =============================================================================
           
    layoutVis = html.Div([
            
			# Add dashbaord header/title.            
             dbc.Row([
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'evistrade',
        					options=[
               					{'label': i, 'value': i} for i in list(e_vis.Trade.unique())
            						],
            					placeholder="Select a Trade",
        						value = "Brickwork",
                                multi=True
        						)],
                     align = "center",
                    
                    width = {'size':3}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'evisops',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_vis.Division.unique())
            							],
            					placeholder="Select Ops Unit",
        						#value = "OU1",
                                multi = True
        						)],
                    align = "center",
                    
                    width = {'size':3}),
                    
                    dbc.Col([
                    html.Label("Market"),
        			dcc.Dropdown(id = 'evisMarket',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_vis["Market Sector"].unique())
            							],
            					placeholder="Select Market",
        						#value = "NB - Housing",
                                multi = True
        						)],
                    align = "center",
                    
                    width={"size": 3}),
                    
                    dbc.Col([
                    html.Label("E_Set Trade"),
        			dcc.Dropdown(id = 'esettrade',
            					options=[
               							 {'label': i, 'value': i} for i in list(e_set["Trade"].unique())
            							],
            					placeholder="Select Trade",
        						value = "***F_LO Brickwork",
                                multi = True
        						)],
                    align = "center",
                    
                    width={"size": 3}),

                    ],
                    justify = 'around',
                    style = {'padding':30}),
             
            dbc.Row([
                    dbc.Col([html.H2("Tender versus Order",style={'textAlign':'center'}),vistable],width=6,align="center"),
                    dbc.Col([html.H3(id = "mean")],width=3),
                    dbc.Col([html.H2("% Helped at Tender"),dcc.Graph(id='helpdonut')],width=3)
                    
                    ],align='center')
            ]
        )
    
             
    
                    
    app.layout = html.Div(children=[
            dcc.Tabs(
                    id='tabs',
                    value = 'tabsLayoutHome',
                    children = [
                            dcc.Tab(label = 'KPI Scores', value = 'tabsLayoutKPI', children = layoutPerf),
                            dcc.Tab(label = 'Financial Benchmarking', value = 'tabsLayoutFin', children = layoutHome),
                            dcc.Tab(label = 'Tender vs Order', value = 'tabsLayouttvo', children = layoutVis),
                            #dcc.Tab(label = 'Financial Graphs', value = 'tabsLayoutFing', children = layoutFinGraphs),
                            dcc.Tab(label = 'KPI Graphs', value = 'tabsLayoutKPIg', children = layoutMap)
                            ])
    ])
        
    @app.callback(
    Output('memory', 'data'),
    [Input('trade choice','value'),
     Input('OU','value'),
     Input('Market','value'),
     Input('pos','value'),
     Input('cou','value'),
     Input('yq','value'),
     Input('joblist', "derived_virtual_data"),
     Input('joblist', "derived_virtual_selected_rows")],
     [State('joblist', 'data')])
    
    def update_memory(trade,OU,market,pos,cou,yq,rows,derived_virtual_selected_rows,data):
        
        if type(trade) == str:
            trade = [trade]
        elif trade is None or trade == []:
             trade = list(e_set.Trade.unique())
        else:
            trade = trade
        
        if type(OU) == str:
            OU = [OU]
        elif OU is None or OU == []:
             OU = list(e_set.Unit.unique())
        else:
            OU = OU
            
        if type(market) == str:
            market = [market]
        elif market is None or market ==[]:
             market = list(e_set.Tender_Type.unique())
        else:
            market = market
            
        if type(pos) == str:
            pos = [pos]
        elif pos is None or pos == []:
             pos = list(e_set.Position.unique())
        else:
            pos = pos
            
        if type(cou) == str:
            cou = [cou]
        elif cou is None or cou == []:
             cou = list(e_set.County.unique())
        else:
            cou = cou
            
        srtd = sorted(e_set['YQ'].unique(), key=lambda x: datetime.datetime.strptime(x, '%Y - %m'))
        
        if yq == 0:
            m = srtd
        elif yq == 1:
            m = srtd[-4:]
        else:
            m = srtd[-8:]
            
        if rows is None:
            rows=[]
            
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []
            
        if data is None:
            data = []
            
        u = pd.DataFrame(rows)
            
        df = e_set[e_set.Trade.isin(trade)]
        df = df[df.Unit.isin(OU)]
        df = df[df.Tender_Type.isin(market)]
        df = df[df.Position.isin(pos)]
        df = df[df.County.isin(cou)]
        df = df[df.YQ.isin(m)]
        
        if derived_virtual_selected_rows == []: 
            df2 = df
            
        else:
            jobs = u.iloc[derived_virtual_selected_rows,0]
            df2 = df[~df['E_Vis_Ref'].isin(jobs)]

        #df = df[df.Position != 0]
        df2 = df2.groupby("Trade",as_index=False).agg({'Enquiry_Sent':'count','Cost_M2': {"Minimum":'min','Average':'mean','Maximum':'max'},'Cost_Plot':{"Minimum":'min','Average':'mean','Maximum':'max'}})
        df2["Input Value"] = [0]*len(df2)
        df2.columns  = ["Trade","Number of Quotes","Min Cost/M2(£)","Mean Cost/M2(£)","Max Cost/M2(£)","Min Cost/Plot(£)","Mean Cost/Plot(£)","Max Cost/Plot(£)",'Input Value']
        df2 = df2.round(0)  
        
        dat = df2.to_dict('records')
        return(dat)
        
       
        
    @app.callback(
    Output('datatable-interactivity', 'data'),
    [Input('memory', 'data')])

    def update_table(data):
        
        return data
    
    @app.callback(
    [Output('tab2', 'data'),
     Output('intermediate-value','data')],
    [Input('memory', 'data'),
     Input('datatable-interactivity', 'data_timestamp'),
     Input('gifa','value'),
     Input('plots','value'),
     Input('btn','n_clicks')],
    [State('datatable-interactivity', 'data'),
     State('intermediate-value','data')])

    def update_table_2(mem,timestamp,gifa,plots,n_clicks,rows,x):
        
        if rows is None:
            raise PreventUpdate
        
        if not n_clicks:
            raise PreventUpdate
        
        if x is None:
            x = 0
            
        if gifa == 0 or gifa is None:
            raise PreventUpdate
            
        if plots == 0 or plots is None:
            raise PreventUpdate
        
        df = pd.DataFrame(rows)
        
        for i in range(0,len(df)):
            if df['Input Value'][i] == "":
                raise PreventUpdate
        
        qm = [float(item)/(gifa) for item in list(df['Input Value'])]
        qp = [float(item)/(plots) for item in list(df['Input Value'])]
        
        df1 = pd.DataFrame({'Trade':df.Trade,'Quoted Cost/M2':qm,'Quoted Cost/Plot':qp,'Flag Cost/M2':[0]*len(df),'Flag Cost/Plot':[0]*len(df)})
        
        flag = []
        for i in range(0,len(df1)):
            if (float(df1['Quoted Cost/M2'][i]) < float(df["Min Cost/M2(£)"][i]) or float(df1['Quoted Cost/M2'][i]) > float(df["Max Cost/M2(£)"][i])):
                flag.append("Out of Range")
            else:
                flag.append("OK")
        
        flag2 = []
        for j in range(0,len(df1)):
            if (float(df1['Quoted Cost/Plot'][j]) < float(df["Min Cost/Plot(£)"][j]) or float(df1['Quoted Cost/Plot'][j]) > float(df["Max Cost/Plot(£)"][j])):
                flag2.append("Out of Range")
            else:
                flag2.append("OK")
                
        df1['Flag Cost/M2'] = flag
        
        df1['Flag Cost/Plot'] = flag2
        
        data = df1.to_dict('records')
        
        x = x+1

        return data,x
        
    
            
        
# =============================================================================
#     @app.callback(
#     Output('sca', 'figure'),
#     [Input('trade choiceg','value'),
#      Input('OUg','value'),
#      Input('Marketg','value'),
#      Input('posg','value'),
#      Input('coug','value'),
#      Input('yqg','value')])
#             
#     def update_scatter(trade,OU,market,pos,cou,yq):
#         
#         if type(trade) == str:
#             trade = [trade]
#         elif trade is None or trade == []:
#              trade = list(e_set.Trade.unique())
#         else:
#             trade = trade
#         
#         if type(OU) == str:
#             OU = [OU]
#         elif OU is None or OU == []:
#              OU = list(e_set.Unit.unique())
#         else:
#             OU = OU
#             
#         if type(market) == str:
#             market = [market]
#         elif market is None or market == []:
#              market = list(e_set.Tender_Type.unique())
#         else:
#             market = market
#             
#         if type(pos) == str:
#             pos = [pos]
#         elif pos is None or pos == []:
#              pos = list(e_set.Position.unique())
#         else:
#             pos = pos
#             
#         if type(cou) == str:
#             cou = [cou]
#         elif cou is None or cou == []:
#              cou = list(e_set.County.unique())
#         else:
#             cou = cou
#             
#         
#             
#         df = e_set[e_set.Trade.isin(trade)]
#         df = df[df.Unit.isin(OU)]
#         df = df[df.Tender_Type.isin(market)]
#         df = df[df.Position.isin(pos)]
#         df = df[df.County.isin(cou)]
#         df = df[df.YQ.isin(yq)]
#         df.round(0)
#         
#         fig = px.scatter(df, x="Cost_Plot",y='Cost_M2',color='Tender_Status',marginal_y="rug")
#         
#         return(fig)
#         
#     @app.callback(
#     Output('vio', 'figure'),
#     [Input('trade choiceg','value'),
#      Input('OUg','value'),
#      Input('Marketg','value'),
#      Input('posg','value'),
#      Input('coug','value'),
#      Input('yqg','value')])
#             
#     def update_violin(trade,OU,market,pos,cou,yq):
#         
#         if type(trade) == str:
#             trade = [trade]
#         elif trade is None or trade == []:
#              trade = list(e_set.Trade.unique())
#         else:
#             trade = trade
#         
#         if type(OU) == str:
#             OU = [OU]
#         elif OU is None or OU == []:
#              OU = list(e_set.Unit.unique())
#         else:
#             OU = OU
#             
#         if type(market) == str:
#             market = [market]
#         elif market is None or market == []:
#              market = list(e_set.Tender_Type.unique())
#         else:
#             market = market
#             
#         if type(pos) == str:
#             pos = [pos]
#         elif pos is None or pos == []:
#              pos = list(e_set.Position.unique())
#         else:
#             pos = pos
#             
#         if type(cou) == str:
#             cou = [cou]
#         elif cou is None or cou == []:
#              cou = list(e_set.County.unique())
#         else:
#             cou = cou
#             
#         if type(yq) == str:
#             yq = [yq]
#         elif yq is None or yq == []:
#              yq = list(e_set.YQ.unique())
#         else:
#             yq = yq
#             
#         df = e_set[e_set.Trade.isin(trade)]
#         df = df[df.Unit.isin(OU)]
#         df = df[df.Tender_Type.isin(market)]
#         df = df[df.Position.isin(pos)]
#         df = df[df.County.isin(cou)]
#         df = df[df.YQ.isin(yq)]
#         df=df.round(0)
#         
#         fig = px.violin(df, x="Position",y='Cost_M2',box=True,points='all')
#         
#         return(fig)
# =============================================================================
        
# =============================================================================
#     @app.callback(
#     Output('interactive_table2', 'data'),
#     [Input('trade choice2', 'value'),
#      Input('OU2','value'),
#      Input('Market2','value')])
#         
#     def update_kpitab(trade,OU,market):
#         
#         df = e_set[e_set.Trade == trade]
#         df = df[df.Unit == OU]
#         df = df[df.Tender_Type == market]
#         df = df.groupby("Contractor",as_index=False).agg({'Enquiry_Sent': "count","Price_Returned":"sum","First":"sum","Top_three":"sum"})
#         dat = df.to_dict('records')
#         
#         return(dat)
# =============================================================================
        
    @app.callback(
    Output('enq', 'figure'),
    [Input('trade choice2', 'value'),
     Input('OU2','value'),
     Input('Market2','value')])
                
    
    def update_enq(trade,OU,market):
        
        df = e_set[e_set.Trade == trade]
        df = df[df.Unit == OU]
        df = df[df.Tender_Type == market]
        df = df.groupby("Contractor",as_index=False).agg({'Enquiry_Sent': "count","Price_Returned":"sum","First":"sum","Top_three":"sum"})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Contractor"],
        y=df["Enquiry_Sent"],
        name='Enquiry_Sent',
        marker_color='rgb(178,34,34)'
        ))
        fig.add_trace(go.Bar(x=df["Contractor"],
        y=df["Price_Returned"],
        name='Price_Returned',
        marker_color='rgb(26, 118, 255)'
        ))
        fig.add_trace(go.Bar(x=df["Contractor"],
        y=df["Top_three"],
        name='Top 3',
        marker_color='rgb(0,255,0)'
        ))
        
        return(fig) 
        
# =============================================================================
#     @app.callback(
#     Output('timeseries', 'figure'),
#     [Input('vistrade', 'value'),
#      Input('visops','value'),
#      Input('vismark','value')])
#                 
#     
#     def update_ts(trade,OU,market):
#         
#         df = e_vis[e_vis.Trade == trade]
#         df = df[df.Division == OU]
#         df = df[df['Level 1 & 2'] == market]
#         
#         fig = go.Figure()
#         fig.add_trace(go.Bar(x=df["Subcontractor Name"],
#         y=df[" Estimating Budget"],
#         name='Budget',
#         marker_color='rgb(178,34,34)'
#         ))
#         fig.add_trace(go.Bar(x=df["Subcontractor Name"],
#         y=df[" Order Cost"],
#         name='Order Cost',
#         marker_color='rgb(26, 118, 255)'
#         ))
#         
#         return(fig) 
# =============================================================================
        
    @app.callback(
    Output('price', 'figure'),
    [Input('trade choice2', 'value'),
     Input('OU2','value'),
     Input('Market2','value')])
                
    
    def update_price(trade,OU,market):
        
        df = e_set[e_set.Trade == trade]
        df = df[df.Unit == OU]
        df = df[df.Tender_Type == market]
        df = df[df.Price_Returned != 0]
        
        df = df.groupby("Contractor",as_index=False).agg({'Price_Returned':"sum"})
        
        labels = list(df.Contractor)
        values = list(df["Price_Returned"])

        # Use `hole` to create a donut-like pie chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        
        return(fig) 
        
    @app.callback(
    Output('work', 'figure'),
    [Input('vistrade2', 'value'),
     Input('visops2','value'),
     Input('vismark2','value')])
                
    
    def update_work(trade,OU,market):
        
        df = e_vis[e_vis.Trade == trade]
        df = df[df.Division == OU]
        df = df[df['Level 1 & 2'] == market]
        
        df = df.groupby("Subcontractor Name",as_index=False).agg({'Job No':"count"})
        
        labels = list(df["Subcontractor Name"])
        values = list(df["Job No"])
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        
        return(fig) 
        
    @app.callback(
    Output('tab3', 'data'),
    [Input('trade choicep', 'value'),
     Input('OUp','value'),
     Input('Marketp','value'),
     Input('posp','value'),
     Input('coup','value'),
     Input('yqp','value')])
                
    
    def update_tab3(trade,OU,market,pos,cou,yq):
        if pos ==[]:
            raise PreventUpdate
            
        if trade == []:
            raise PreventUpdate
            
        if OU == []:
            raise PreventUpdate
            
        if cou == []:
            raise PreventUpdate
            
        if market == []:
            raise PreventUpdate
        
        if type(trade) == str:
            trade = [trade]
        elif trade is None:
             trade = list(e_set.Trade.unique())
        else:
            trade = trade
        
        if type(OU) == str:
            OU = [OU]
        elif OU is None:
             OU = list(e_set.Unit.unique())
        else:
            OU = OU
            
        if type(market) == str:
            market = [market]
        elif market is None:
             market = list(e_set.Tender_Type.unique())
        else:
            market = market
            
        if type(pos) == str:
            pos = [pos]
        elif pos is None:
             pos = list(e_set.Position.unique())
        else:
            pos = pos
            
        if type(cou) == str:
            cou = [cou]
        elif cou is None:
             cou = list(e_set.County.unique())
        else:
            cou = cou
            
        srtd = sorted(e_set['YQ'].unique(), key=lambda x: datetime.datetime.strptime(x, '%Y - %m'))
            
        if yq == 0:
            m = srtd
        elif yq == 1:
            m = srtd[-4:]
        else:
            m = srtd[-8:]
            
        print(m)
            
        df = e_set[e_set.Trade.isin(trade)]
        df = df[df.Unit.isin(OU)]
        df = df[df.Tender_Type.isin(market)]
        df = df[df.Position.isin(pos)]
        df = df[df.County.isin(cou)]
        df = df[df.YQ.isin(m)]
        df=df.round(0)
        
        df = df.groupby("Contractor",as_index=False).agg({'Enquiry_Sent': "count","Price_Returned":"sum","First":"sum","Top_three":"sum"})
        df["% Return Rate"] = round((df['Price_Returned']/df['Enquiry_Sent'])*100,0)
        data = df.to_dict('records')
        
        return data
    
    @app.callback(
    Output('vistab', 'data'),
    [Input('evistrade', 'value'),
     Input('evisops','value'),
     Input('evisMarket','value'),
     Input('esettrade','value')])
                
    
    def update_vistab(trade,OU,market,trade2):
        
        if type(trade) == str:
            trade = [trade]
        elif trade is None:
             trade = list(e_vis.Trade.unique())
        else:
            trade = trade
        
        if type(OU) == str:
            OU = [OU]
        elif OU is None:
             OU = list(e_vis.Division.unique())
        else:
            OU = OU
            
        if type(market) == str:
            market = [market]
        elif market is None:
             market = list(e_vis['Market Sector'].unique())
        else:
            market = market
            
        df = e_vis[e_vis.Trade.isin(trade)]
        df = df[df.Division.isin(OU)]
        df = df[df['Market Sector'].isin(market)]
        
        helped = []
        
        for index, row in df.iterrows():
            temp = e_set.loc[e_set["E_Vis_Ref"]==row["Job No"]]
            priced = list(temp.loc[temp.Price_Returned == 1].Contractor)
            if(row["Subcontractor Name"] in priced):
                helped.append(1)
            else:
                helped.append(0)
                
        df["Helped at Tender?"] = helped
        df = df.round(0)
        
        data = df.to_dict('records')
        
        return data
    
    @app.callback(
    Output('mean', 'children'),
    [Input('vistab', 'data'),
     Input('vistab', 'columns')])
        
    def display_mean(rows, columns):
        
        if rows is None:
            raise PreventUpdate

            
        df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        
        x = df[" Buying Gain"].astype(float)
        z = df[" Estimating Budget"].astype(float)
        y = sum(x)/sum(z)
        y = round(y,5)
        
        return('The Total Buying gain is: %{}'.format(y))
        
    @app.callback(
    Output('helpdonut', 'figure'),
    [Input('vistab', 'data'),
     Input('vistab', 'columns')])
        
    def display_help(rows, columns):
        
        if rows is None:
            raise PreventUpdate
            
        df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    
        values = [sum(df["Helped at Tender?"]),len(df) - sum(df["Helped at Tender?"])]
        labels = ["Yes","No"]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        
        return(fig)
        
    @app.callback(
    Output('OU', 'value'),
    [Input('select-all-OU', 'value')],
     [State('OU', 'value')])

    def test(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allOU':
            return list(e_set.Unit.unique())
        
        elif selected == 'setOU':
            return ['OU1']
        
        else:
            return values
        
    @app.callback(
    Output('Market', 'value'),
    [Input('select-all-ma', 'value')],
     [State('Market', 'value')])

    def sma(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allma':
            return list(e_set['Tender_Type'].unique())
        
        elif selected == 'setma':
            return ['NB - Housing']
        
        else:
            return values
        
    @app.callback(
    Output('pos', 'value'),
    [Input('select-all-po', 'value')],
     [State('pos', 'value')])

    def smp(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allpo':
            return list(e_set.Position.unique())
        
        elif selected == 'setpo':
            return ['1','2','3']
        
        else:
            return values
        
    @app.callback(
    Output('cou', 'value'),
    [Input('select-all-co', 'value')],
     [State('cou', 'value')])

    def smc(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allco':
            return list(e_set.County.unique())
        
        elif selected == 'setco':
            return ['West Yorkshire']
        
        else:
            return values
        
    @app.callback(
    Output('OUp', 'value'),
    [Input('select-all-OUp', 'value')],
     [State('OUp', 'value')])

    def smoup(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allOUp':
            return list(e_set.Unit.unique())
        
        elif selected == 'setOUp':
            return ['OU1']
        
        else:
            return values
        
    @app.callback(
    Output('Marketp', 'value'),
    [Input('select-all-map', 'value')],
     [State('Marketp', 'value')])

    def smmap(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allmap':
            return list(e_set['Tender_Type'].unique())
        
        elif selected == 'setmap':
            return ['NB - Housing']
        
        else:
            return values
        
    @app.callback(
    Output('posp', 'value'),
    [Input('select-all-posp', 'value')],
     [State('posp', 'value')])

    def smposp(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allposp':
            return list(e_set.Position.unique())
        
        elif selected == 'setposp':
            return ['1','2','3']
        
        else:
            return values
        
    @app.callback(
    Output('coup', 'value'),
    [Input('select-all-coup', 'value')],
     [State('coup', 'value')])

    def smcoup(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'allcoup':
            return list(e_set.County.unique())
        
        elif selected == 'setcoup':
            return ['West Yorkshire']
        
        else:
            return values
        
    @app.callback(
    Output('contact', 'data'),
    [Input('tab3', "derived_virtual_data"),
     Input('tab3', "derived_virtual_selected_rows")],
     [State('tab3', 'data')])
    
    def contact_details(rows,derived_virtual_selected_rows,data):
        
        if rows is None:
            raise PreventUpdate
            
        if derived_virtual_selected_rows is None:
            raise PreventUpdate
            
        if data is None:
            raise PreventUpdate
            
        df = pd.DataFrame(rows)
        
        if len(df) < 1:
            raise PreventUpdate
            
        cons = list(df.iloc[derived_virtual_selected_rows,1])
        ems = [item+'@gmail.com' for item in cons]
        tels = ['01234 567 890']*len(cons)
        
        dff = pd.DataFrame({'Contractor':cons,'email':ems,'tel':tels})
                
        return(dff.to_dict('records'))
        
    @app.callback(
    Output('trade choice', 'value'),
    [Input('select-all-tr', 'value')],
     [State('trade choice', 'value')])

    def select_key_trades(selected, values):
        
        if selected is None:
            raise PreventUpdate
        
        if selected == 'keytr':
            return ['***D_SC Bulk Excavation','***D_SC Groundworker','***E_SC PCC Floors',
                    'G_SC Structural Steelwork','***M_SC Screeding','***F_LO Brickwork',
                    '***G_QM Timber Upper Floors','***G_LO Joinery','***L_QM Stairs-Timber',
                    '***G_QM Roof Trusses','***H_SC Roofing Slate & Tile','***P_SC Insulation',
                    '***L_SC PVC Windows','***R_SC Plumbing','***Y_SC Electrical',
                    '***M_SC Plastering','***M_SC Painting&Decorating','***Q_SC Landscaping',
                    '***Q_SC Fencing (Timber)','***Q_SC Fencing (Metal)']
        
        elif selected == 'settr':
            return ['***F_LO Brickwork']
        
        else:
            return values
        
        
    @app.callback(
    Output('joblist', 'data'),
    [Input('trade choice','value'),
     Input('OU','value'),
     Input('Market','value'),
     Input('pos','value'),
     Input('cou','value'),
     Input('yq','value')])
    
    def update_joblist(trade,OU,market,pos,cou,yq):
        
        if type(trade) == str:
            trade = [trade]
        elif trade is None or trade == []:
             trade = list(e_set.Trade.unique())
        else:
            trade = trade
        
        if type(OU) == str:
            OU = [OU]
        elif OU is None or OU == []:
             OU = list(e_set.Unit.unique())
        else:
            OU = OU
            
        if type(market) == str:
            market = [market]
        elif market is None or market ==[]:
             market = list(e_set.Tender_Type.unique())
        else:
            market = market
            
        if type(pos) == str:
            pos = [pos]
        elif pos is None or pos == []:
             pos = list(e_set.Position.unique())
        else:
            pos = pos
            
        if type(cou) == str:
            cou = [cou]
        elif cou is None or cou == []:
             cou = list(e_set.County.unique())
        else:
            cou = cou
            
        srtd = sorted(e_set['YQ'].unique(), key=lambda x: datetime.datetime.strptime(x, '%Y - %m'))
        
        if yq == 0:
            m = srtd
        elif yq == 1:
            m = srtd[-4:]
        else:
            m = srtd[-8:]
            
        print(m)
            
        df = e_set[e_set.Trade.isin(trade)]
        df = df[df.Unit.isin(OU)]
        df = df[df.Tender_Type.isin(market)]
        df = df[df.Position.isin(pos)]
        df = df[df.County.isin(cou)]
        df = df[df.YQ.isin(m)]
        #df = df[df.Position != 0]
        x = df.loc[:,["E_Vis_Ref","Estimator"]]
        x = x.drop_duplicates(['E_Vis_Ref'])
        dat = x.to_dict('records')
            
        return(dat)
        
            
    if __name__ == '__main__':
        app.run_server(debug=True)
      
    
ScriptMain()
