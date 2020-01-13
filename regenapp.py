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
from operator import itemgetter
from collections import Counter
from six.moves.urllib.parse import quote
from re import sub




url1 = 'https://raw.githubusercontent.com/walkerdj1995/flying-dog-beers/master/Data%20Sets/esetOct19.csv'
url2 = 'https://raw.githubusercontent.com/walkerdj1995/flying-dog-beers/master/Data%20Sets/evisOct19.csv'
url3 = 'https://raw.githubusercontent.com/walkerdj1995/flying-dog-beers/master/Data%20Sets/SupplierDetails.csv'

e_set = pd.read_csv(url1,na_values=['#VALUE!', '#DIV/0!'])
e_vis = pd.read_csv(url2) 
details = pd.read_csv(url3)

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

evisnames = ['Date_Created','Created_By','Signed_Date','Signed_User','Unit','E_Vis_Ref',
             'Job_Name','Tender_Type_Gr','Tender_Type','Trade','Contractor','County',
             'Post Code','GLO','Payment_Terms','Est_Budget','Order_Cost','Buying_Gain',
             'Pay_Ret','Diff2','Var_Rec','Var_UnRec','Balance']

e_vis.columns = evisnames

e_vis.dropna(subset=['Date_Created', 'Order_Cost','Tender_Type'],inplace = True)

e_vis['County'] = e_vis['County'].astype(str)
e_vis['Plots'] = [0]*len(e_vis)
e_vis['GIFA'] = [0]*len(e_vis)
e_vis['Cost_Plot'] = [0]*len(e_vis)
e_vis['Cost_M2'] = [0]*len(e_vis)
e_vis['Enquiry_Sent'] = [1]*len(e_vis)

a = list(e_set.E_Vis_Ref.unique())
b = list(e_vis.E_Vis_Ref.unique())
c = list(set(a)&set(b))

for item in c:
    plts = e_set.loc[e_set.E_Vis_Ref == item].Plots.iloc[0]
    gifa = e_set.loc[e_set.E_Vis_Ref == item].GIFA.iloc[0]
    e_vis.loc[e_vis.E_Vis_Ref == item,'Plots'] = plts
    e_vis.loc[e_vis.E_Vis_Ref == item,'GIFA'] = gifa
    e_vis.loc[e_vis.E_Vis_Ref == item,'Cost_Plot'] = e_vis.loc[e_vis.E_Vis_Ref == item,'Order_Cost']/plts
    e_vis.loc[e_vis.E_Vis_Ref == item,'Cost_M2'] = e_vis.loc[e_vis.E_Vis_Ref == item,'Order_Cost']/gifa
    
#e_vis['Cost_Plot'] = pd.to_numeric(e_vis['Cost_Plot'])
    

x = 0

details_2 = details[["Name",'Primary Contact Email','Phone No','Mobile No']].drop_duplicates()
details_2[["Name",'Primary Contact Email','Phone No','Mobile No']] = details_2[["Name",'Primary Contact Email','Phone No','Mobile No']].astype(str)
details_2['Phone No'] = details_2['Phone No'].str.replace(" ","")
details_2['Primary Contact Email'] = details_2['Primary Contact Email'].str.replace(" ","")
details_2['Mobile No'] = details_2['Mobile No'].str.replace(" ","")
g = details_2.groupby('Name')['Primary Contact Email','Phone No','Mobile No'].apply(lambda x: list(np.unique(x))).reset_index()
for i in range(0,len(g[0])):
    g[0][i] = [x for x in g[0][i] if str(x) != 'nan']
    
for i in range(0,len(g[0])):
    g[0][i] = ' / '.join(g[0][i])
    
deets = []
cons = list(e_set.Contractor.unique())
for i in range(0,len(cons)):
    if cons[i] in list(g['Name']):
        deets.append(list(g[g["Name"]==cons[i]][0]))
    else:
        deets.append("No Matching Details")

dff = pd.DataFrame({'Contractor':cons,'Details':deets})
    
    
#Create preferred list
    
All = list(e_vis['Contractor'])
cnt = Counter(All)
pref =  [k for k, v in cnt.items() if v > 2]

#%%

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def ScriptMain():
    
    dataTable1 = dt.DataTable(
        id='datatable-interactivity',
        columns=[{'id': c, 'name': c} for c in ["Trade","Quotes","Min Cost/M2(£)","Mean Cost/M2(£)","Max Cost/M2(£)","Min Cost/Plot(£)","Mean Cost/Plot(£)","Max Cost/Plot(£)",'Input Value']],
        #sort_action='native',
        row_selectable="multi",
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
        'height':'70px',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center',
                'font_size':'18px',
                'whiteSpace': 'normal',
                'maxWidth': '165px',
                'height':'70px'},
    )

        
    
    dataTable2 = dt.DataTable(
        id='tab2',
        columns=[{'id': c, 'name': c} for c in ["Trade","Quoted Cost/M2","Quoted Cost/Plot",'Flag Cost/M2','Flag Cost/Plot']],
        #sort_action='native',
        #row_selectable="multi",
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
    
        {   
            'if': {
                'column_id': 'Flag Cost/M2',
                'filter_query': '{Flag Cost/M2} eq "Poor - Low"'
                    },
            'backgroundColor': '#FF4040',
            'color': 'white'
        },
        {   
            'if': {
                'column_id': 'Flag Cost/Plot',
                'filter_query': '{Flag Cost/Plot} eq "Poor - Low"'
                    },
            'backgroundColor': '#FF4040',
            'color': 'white',
        },
                    {   
            'if': {
                'column_id': 'Flag Cost/M2',
                'filter_query': '{Flag Cost/M2} eq "Poor - High"'
                    },
            'backgroundColor': '#FF4040',
            'color': 'white'
        },
        {   
            'if': {
                'column_id': 'Flag Cost/Plot',
                'filter_query': '{Flag Cost/Plot} eq "Poor - High"'
                    },
            'backgroundColor': '#FF4040',
            'color': 'white',
        },
        {   
            'if': {
                'column_id': 'Flag Cost/M2',
                'filter_query': '{Flag Cost/M2} eq "Check - Low"'
                    },
            'backgroundColor': '#ffbf00',
            'color': 'white'
        },
        {   
            'if': {
                'column_id': 'Flag Cost/Plot',
                'filter_query': '{Flag Cost/Plot} eq "Check - Low"'
                    },
            'backgroundColor': '#ffbf00',
            'color': 'white',
        },
        {   
            'if': {
                'column_id': 'Flag Cost/M2',
                'filter_query': '{Flag Cost/M2} eq "Check - High"'
                    },
            'backgroundColor': '#ffbf00',
            'color': 'white'
        },
        {   
            'if': {
                'column_id': 'Flag Cost/Plot',
                'filter_query': '{Flag Cost/Plot} eq "Check - High"'
                    },
            'backgroundColor': '#ffbf00',
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
        'height':'70px',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center',
                'font_size':'18px',
                'whiteSpace': 'normal',
                'maxWidth': '165px',
                'height':'70px'},
    )
    
    dataTable3 = dt.DataTable(
        id='tab3',
        columns=[{'id': c, 'name': c} for c in ['Contractor','Trade','Enquiry_Sent',"Price_Returned","% Return Rate","First","Top_three","% KPI Score","Contact Details"]],
        #fixed_rows={'headers': True, 'data': 0 },
        sort_action='native',
        filter_action="native",
        row_selectable="multi",
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)',
            
        },
                
        {
            'if': {'row_index': 0},
            'backgroundColor': 'rgb(255, 255, 204)',
            
        }
    ],
    style_header={
        'backgroundColor': '#8ebcff',
        'fontWeight': 'bold'
    },
    style_cell={"textAlign":'center',
                'font_size':'18px',
                'whiteSpace': 'normal'},
    
    style_table={
        'maxHeight': '1000px',
        'overflowY': 'scroll'
    },
    )
    
    dataTable4 = dt.DataTable(
        id='tab4',
        columns=[{'id': c, 'name': c} for c in list(e_set.columns)],
        #fixed_rows={'headers': True, 'data': 0 },
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
    style_table={
        'maxHeight': '1000px',
        'overflowY': 'scroll'
    },
    style_cell={"textAlign":'center',
                'font_size':'18px',
                'whiteSpace':'normal'},
    
    )
    
    dataTable5 = dt.DataTable(
    id='tab5',
    #columns=[{'id': c, 'name': c} for c in list(e_set.columns)],
    #fixed_rows={'headers': True, 'data': 0 },
    sort_action='native',
    filter_action="native",
    #row_selectable="multi",
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
    style_table={
        'maxHeight': '1000px',
        'overflowY': 'scroll'
    },
    style_cell={"textAlign":'center',
                'font_size':'18px',
                'whiteSpace':'normal'},
    
    )
    
# =============================================================================
#     dataTable5 = dt.DataTable(
#         id='tab5',
#         columns=[{'id': c, 'name': c} for c in list(e_set.columns)],
#         #fixed_rows={'headers': True, 'data': 0 },
#         sort_action='native',
#         filter_action="native",
#         row_selectable="multi",
#         style_data_conditional=[
#         {
#             'if': {'row_index': 'odd'},
#             'backgroundColor': 'rgb(248, 248, 248)'
#         }
#     ],
#     style_header={
#         'backgroundColor': '#8ebcff',
#         'fontWeight': 'bold'
#     },
#     style_cell={"textAlign":'center',
#                 'font_size':'18px',
#                 'whiteSpace': 'normal'},
#     
#     style_table={
#         'maxHeight': '1000px',
#         'overflowY': 'scroll'
#     },
#     )
# =============================================================================
    
# =============================================================================
#     vistable = dt.DataTable(
#         id='vistab',
#         columns=[{'id': c, 'name': c} for c in ['Job No',"Subcontractor Name","Helped at Tender?"," Estimating Budget"," Order Cost"," Buying Gain"]],
#         sort_action='native',
#         style_data_conditional=[
#         {
#             'if': {'row_index': 'odd'},
#             'backgroundColor': 'rgb(248, 248, 248)'
#         }
#     ],
#     style_header={
#         'backgroundColor': 'rgb(230, 230, 230)',
#         'fontWeight': 'bold'
#     },
#     style_cell={"textAlign":'center'},
#     )
# =============================================================================

    
    tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#8ebcff',
    'color': 'white',
    'padding': '6px'
}



    # Home layout.
    layoutHome = html.Div([
            
            dcc.Store(id = 'memory'),
            dcc.ConfirmDialog(
                            id='confirm',
                            message='Enter GIFA / Plots as integer',
                            ),
            
			# Add dashbaord header/title.            
             dbc.Row([
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'trade choice',
        					options=sorted([
               					{'label': i, 'value': i} for i in list(e_set.Trade.unique()) if i != 0
            						],key=itemgetter('value')),
            					placeholder="Select Other Trades",
        						#value = "***F_LO Brickwork",
                                multi=True
        						),
                    dcc.RadioItems(id='select-all-tr',
                            options=[{'label': 'Same as KPI tab', 'value': 'same'},
                                     {'label': 'Select Key Trades', 'value': 'keytr'},
                                     {'label': 'Reset', 'value': 'settr'}],
                            value = 'same')],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'OU',
            					options=sorted([
               							 {'label': i, 'value': i} for i in list(e_set.Unit.unique()) if i != 0
            							],key=itemgetter('value')),
            					placeholder="All Selected",
        						#value = "OU1",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-OU',
                            options=[{'label': 'Same as KPI tab', 'value': 'same'},
                                     {'label': 'Select All', 'value': 'allOU'},
                                     {'label': 'Reset', 'value': 'setOU'}],
                            value = 'same')],
                    align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Market"),
        			dcc.Dropdown(id = 'Market',
            					options=sorted([
               							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique()) if i != 0
            							],key=itemgetter('value')),
            					placeholder="All Selected",
        						#value = "NB - Housing",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-ma',
                            options=[{'label': 'Same as KPI tab', 'value': 'same'},
                                     {'label': 'Select All', 'value': 'allma'},
                                     {'label': 'Reset', 'value': 'setma'}],
                            value = 'same')],
                    align = "center",
                    
                    width={"size": 4}),
                    
                    ],
                    justify = 'around',
                    style = {'padding':30}),
                    
            dbc.Row([
                    dbc.Col([
                            
                    html.Label("Position"),
                    dcc.Dropdown(id = 'pos',
        					options=sorted([
               					{'label': i, 'value': i} for i in list(e_set.Position.unique()) if i != 0
            						],key=itemgetter('value')),
            					placeholder="All Selected",
        						#value = "1",
                                multi=True
        						),
                    dcc.RadioItems(id='select-all-po',
                            options=[{'label': 'Same as KPI tab', 'value': 'same'},
                                     {'label': 'Select All', 'value': 'allpo'},
                                     {'label': 'Reset', 'value': 'setpo'}],
                            value = 'same')],
                     align = "center",
                    
                    width = {'size':3}),
                    
                    dbc.Col([
                    html.Label("County"),
                    dcc.Dropdown(id = 'cou',
            					options=sorted([
               							 {'label': i, 'value': i} for i in list(e_set.County.unique()) if i != 0
            							],key=itemgetter('value')),
            					placeholder="All Selected",
        						#value = "West Yorkshire",
                                multi = True
        						),
                    dcc.RadioItems(id='select-all-co',
                            options=[{'label': 'Same as KPI tab', 'value': 'same'},
                                     {'label': 'Select All', 'value': 'allco'},
                                     {'label': 'Reset', 'value': 'setco'}],
                            value = 'same')],
                    align = "center",
                    
                    width = {'size':3}),
                    
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
                    
                    width={"size": 2}),
                            
                    dbc.Col([
                    html.Label("Data Set"),
        			dcc.Slider(
                            id = 'ds',
                            min=0,
                            max=2,
                            step=None,
                            marks={
                                    0 : 'CONQUEST',
                                    1 : 'BOTH',
                                    2 : 'EVISION'},
                            value=0,
                            disabled = True
                        )],
                    align = "center",
                    
                    width={"size": 2}),        
                    ],
                    justify = 'around',
                    style = {'padding':30}),
                           
                            
             dbc.Row([
                    dbc.Col([html.Label('GIFA'),dcc.Input(id = 'gifa',type='number',placeholder = 'Input GIFA')],width=3),
                    dbc.Col([html.Label('Plots'),dcc.Input(id = 'plots',type='number',placeholder = 'Input number of plots')],width=3),
                    dbc.Col([html.Button(['Update'],id='btn')],width = 3, align = 'start'),
                    ],
                    
                    justify = "around",
                    style = {'padding':30}
                            ),
                     
             dbc.Row([
                    dbc.Col([html.H2("Summary of Costs",style={'textAlign':'center'}),
                             html.A('Download Data',id='download-link1',download="rawdata.csv",href="",target="_blank"),
                             dataTable1],width=7),
             
                    dbc.Col([html.H2("Comparison Table",style={'textAlign':'center'}),
                             html.A('a',id='null',download="rawdata.csv",href="",target="_blank"),
                             dataTable2],width=5) 
                    
                    ],
             
                    
                    align = 'start',
                    justify = 'around',
                    style = {'padding':30}
                            ),
             dcc.Store(id='intermediate-value'),
             dcc.Store(id='hidden-value'),
                     
                     
# =============================================================================
#             dbc.Row([
#                     dbc.Col([html.H2("Comparison Table",style={'textAlign':'center'}),dataTable2],width=8)],
#                     justify = "end",
#                     style = {'padding':30}
#                     ),
# =============================================================================
            dbc.Row([
                     dbc.Col([html.H2('Anomaly Detection/Removal',style={'textAlign':'center'}),
                              dcc.RadioItems(id = 'Rem',
                                             options=[{'label': 'Remove Outliers', 'value': 'rem'},
                                                      {'label': 'Keep All', 'value': 'kee'}],
                                             value = 'kee'),
                            dcc.Graph(id = 'jobplot')
                              ],width=12)]
            ),
                              
            dbc.Row([
                     dbc.Col([html.H2('Financial Source Data',style={'textAlign':'center'}),
                               html.A('Download Data',id='download-link4',download="sourcedata.csv",href="",target="_blank"),
                              dataTable5],width=12)]
            )
                     
                    
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
            ]
        )
            
             
    layoutPerf = html.Div([
            
			# Add dashbaord header/title.            
             dbc.Row([
                    dbc.Col([
                            
                    html.Label("Trade"),
                    dcc.Dropdown(id = 'trade choicep',
        					options=sorted([
               					{'label': i, 'value': i} for i in list(e_set.Trade.unique()) if i != 0
            						],key=itemgetter('value')),
            					placeholder="Select Other Trades",
        						value = "***F_LO Brickwork",
                                multi=True
        						),
                                        
                    dcc.RadioItems(id='select-all-trp',
                            options=[{'label': 'Select Key Trades', 'value': 'keytrp'},
                                     {'label': 'Reset', 'value': 'settrp'}])],
                     align = "center",
                    
                    width = {'size':4}),
                    
                    dbc.Col([
                    html.Label("Ops Unit"),
                    dcc.Dropdown(id = 'OUp',
            					options=sorted([
               							 {'label': i, 'value': i} for i in list(e_set.Unit.unique()) if i != 0
            							],key=itemgetter('value')),
            					placeholder="All Selected",
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
            					options=sorted([
               							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique()) if i != 0
            							],key=itemgetter('value')),
            					placeholder="All Selected",
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
        					options=sorted([
               					{'label': i, 'value': i} for i in list(e_set.Position.unique()) if i != 0
            						],key=itemgetter('value')),
            					placeholder="All Selected",
        						#value = "1",
                                multi=True
        						)],
                     align = "center",
                    
                    width = {'size':3}),
                    
                    dbc.Col([
                    html.Label("County"),
                    dcc.Dropdown(id = 'coup',
            					options=sorted([
               							 {'label': i, 'value': i} for i in list(e_set.County.unique()) if i != 0
            							],key=itemgetter('value')),
            					placeholder="All Selected",
        						#value = "West Yorkshire",
                                multi = True
        						)],
                    align = "center",
                    
                    width = {'size':3}),
                    
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
                    
                    width={"size": 3}),
                    
                                        dbc.Col([
                    html.Label("Preferred Only?"),
        			dcc.Slider(
                            id = 'pre',
                            min=0,
                            max=1,
                            step=None,
                            marks={
                                    0 : 'Preferred',
                                    1 : 'All'},
                            value=1
                        )],
                    align = "center",
                    
                    width={"size": 2})],
                    justify = 'around',
                    style = {'padding':30}),
                            
            dbc.Row([
                    dbc.Col([
                            dcc.RadioItems(id='select-all-posp',
                            options=[{'label': 'Select All', 'value': 'allposp'},
                                     {'label': 'Reset', 'value': 'setposp'}])
                            ],width=4),

                    dbc.Col([
                            dcc.RadioItems(id='select-all-coup',
                            options=[{'label': 'Select All', 'value': 'allcoup'},
                                     {'label': 'Reset', 'value': 'setcoup'}])
                            ],width=4)

                    ],justify = 'start'),
                    
           dbc.Row([
                    dbc.Col([html.H2("Subcontractor List",style={'textAlign':'center'}),
                             html.A(
                                    'Download Data',
                                    id='download-link2',
                                    download="rawdata.csv",
                                    href="",
                                    target="_blank"),
                            dataTable3,
                            html.H2("Source Data",style={'textAlign':'center'}),
                            html.A(
                                    'Download Source Data',
                                    id='download-link3',
                                    download="sourcedata.csv",
                                    href="",
                                    target="_blank"),
                            dataTable4],
                    width=10,align="center"),
                    ],
                    
                    justify = "center",
                            )
           ])
                
        
# =============================================================================
#     layoutMap = html.Div([
#             dbc.Row([
#                      dbc.Col(html.H3("E-Set Filters",style={'textAlign':'center'}),width = {'size':6}),
#                      dbc.Col(html.H3("E-Vision Filters",style={'textAlign':'center'}),width = {'size':6})]),
# 			# Add dashbaord header/title.            
#             dbc.Row([
#                     dbc.Col([
#                             
#                     html.Label("Trade"),
#                     dcc.Dropdown(id = 'trade choice2',
#         					options=[
#                					{'label': i, 'value': i} for i in list(e_set.Trade.unique())
#             						],
#             					placeholder="Select a Trade",
#         						value = "***F_LO Brickwork"
#         						)],
#                      align = "center",
#                     
#                     width = {'size':2}),
#                     
#                     dbc.Col([
#                     html.Label("Ops Unit"),
#                     dcc.Dropdown(id = 'OU2',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set.Unit.unique())
#             							],
#             					placeholder="Select Ops Unit",
#         						value = "OU1"
#         						)],
#                     align = "center",
#                     
#                     width = {'size':2}),
#                     
#                     dbc.Col([
#                     html.Label("Market"),
#         			dcc.Dropdown(id = 'Market2',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set.Tender_Type.unique())
#             							],
#             					placeholder="Select Market",
#         						value = "NB - Housing"
#         						)],
#                     align = "center",
#                     
#                     width={"size": 2}),
#                     
#                     dbc.Col([
#                             
#                     html.Label("Trade"),
#                     dcc.Dropdown(id = 'vistrade2',
#         					options=[
#                					{'label': i, 'value': i} for i in list(e_vis.Trade.unique())
#             						],
#             					placeholder="Select a Trade",
#         						value = "Brickwork"
#         						)],
#                      align = "center",
#                     
#                     width = {'size':2}),
#                     
#                     dbc.Col([
#                     html.Label("Ops Unit"),
#                     dcc.Dropdown(id = 'visops2',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_vis.Division.unique())
#             							],
#             					placeholder="Select Ops Unit",
#         						value = "Central OU1"
#         						)],
#                     align = "center",
#                     
#                     width = {'size':2}),
#                     
#                     dbc.Col([
#                     html.Label("Market"),
#         			dcc.Dropdown(id = 'vismark2',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_vis['Level 1 & 2'].unique())
#             							],
#             					placeholder="Select Market",
#         						value = "New Build - Housing"
#         						)],
#                     align = "center",
#                     
#                     width={"size": 2}),
#                     ],
#                     justify = 'around',
#                     style = {'padding':30}),
#                     
#             dbc.Row([
#                     #dbc.Col([dataTable2], width={"size": 6, "offset": 0},align="center"),
#                             
#                     dbc.Col([html.H2("Subcontractor Summary",style={'textAlign':'center'}),dcc.Graph(id = "enq")], width={"size": 12, "offset": 0},align="center")
#                     ],
#                     
#                     justify = "around"
#                             ),
#              dbc.Row([
#                     dbc.Col([html.H3("Subcontractors That Are Pricing",style={'textAlign':'center'}),dcc.Graph(id = 'price')], width={"size": 6, "offset": 0},align="center"),
#                             
#                     dbc.Col([html.H3("Subcontractors Receiving Work",style={'textAlign':'center'}),dcc.Graph(id = "work")], width={"size": 6, "offset": 0},align="center")
#                     ],
#                     
#                     justify = "around"
#                             )
#             ]
#         )
# =============================================================================
             
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
           
# =============================================================================
#     layoutVis = html.Div([
#             
# 			# Add dashbaord header/title.            
#              dbc.Row([
#                     dbc.Col([
#                             
#                     html.Label("Trade"),
#                     dcc.Dropdown(id = 'evistrade',
#         					options=[
#                					{'label': i, 'value': i} for i in list(e_vis.Trade.unique())
#             						],
#             					placeholder="Select a Trade",
#         						value = "Brickwork",
#                                 multi=True
#         						)],
#                      align = "center",
#                     
#                     width = {'size':3}),
#                     
#                     dbc.Col([
#                     html.Label("Ops Unit"),
#                     dcc.Dropdown(id = 'evisops',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_vis.Division.unique())
#             							],
#             					placeholder="Select Ops Unit",
#         						#value = "OU1",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width = {'size':3}),
#                     
#                     dbc.Col([
#                     html.Label("Market"),
#         			dcc.Dropdown(id = 'evisMarket',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_vis["Market Sector"].unique())
#             							],
#             					placeholder="Select Market",
#         						#value = "NB - Housing",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width={"size": 3}),
#                     
#                     dbc.Col([
#                     html.Label("E_Set Trade"),
#         			dcc.Dropdown(id = 'esettrade',
#             					options=[
#                							 {'label': i, 'value': i} for i in list(e_set["Trade"].unique())
#             							],
#             					placeholder="Select Trade",
#         						value = "***F_LO Brickwork",
#                                 multi = True
#         						)],
#                     align = "center",
#                     
#                     width={"size": 3}),
# 
#                     ],
#                     justify = 'around',
#                     style = {'padding':30}),
#              
#             dbc.Row([
#                     dbc.Col([html.H2("Tender versus Order",style={'textAlign':'center'}),vistable],width=6,align="center"),
#                     dbc.Col([html.H3(id = "mean")],width=3),
#                     dbc.Col([html.H2("% Helped at Tender"),dcc.Graph(id='helpdonut')],width=3)
#                     
#                     ],align='center')
#             ]
#         )
# =============================================================================
    
             
    
                    
    app.layout = html.Div(children=[
            dcc.Tabs(
                    id='tabs',
                    value = 'tabsLayoutHome',
                    children = [
                            dcc.Tab(label = 'KPI Scores', value = 'tabsLayoutKPI', children = layoutPerf,selected_style=tab_selected_style),
                            dcc.Tab(label = 'Financial Benchmarking', value = 'tabsLayoutFin', children = layoutHome,selected_style=tab_selected_style),
                            #dcc.Tab(label = 'Tender vs Order', value = 'tabsLayouttvo', children = layoutVis),
                            #dcc.Tab(label = 'Financial Graphs', value = 'tabsLayoutFing', children = layoutFinGraphs),
                            #dcc.Tab(label = 'KPI Graphs', value = 'tabsLayoutKPIg', children = layoutMap)
                            ])
    ])
        
    @app.callback(
    [Output('memory', 'data'),Output('hidden-value','data')],
    [Input('trade choice','value'),
     Input('OU','value'),
     Input('Market','value'),
     Input('pos','value'),
     Input('cou','value'),
     Input('yq','value'),
     Input('jobplot', "selectedData"),
     Input('Rem','value'),
     Input('ds','value')],
     [State('datatable-interactivity','data')])

    def update_memory(trade,OU,market,pos,cou,yq,rows,rem,ds,inp):#,derived_virtual_selected_rows,data):
        
        ################################ Get Correct Data Set#####################################
        if ds == 0:
            data = e_set
        elif ds == 1:
            data = e_set
        else:
            data = e_vis
        
        if type(trade) == str:
            trade = [trade]
        elif trade is None or trade == []:
             trade = list(data.Trade.unique())
        else:
            trade = trade
        
        if type(OU) == str:
            OU = [OU]
        elif OU is None or OU == []:
             OU = list(data.Unit.unique())
        else:
            OU = OU
            
        if type(market) == str:
            market = [market]
        elif market is None or market ==[]:
             market = list(data.Tender_Type.unique())
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
             cou = list(data.County.unique())
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
            rows={'points':[]}
             
        df = data[data.Trade.isin(trade)]
        #df = e_set[e_set.Trade.isin(trade)]
        df = df[df.Unit.isin(OU)]
        df = df[df.Tender_Type.isin(market)]
        df = df[df.County.isin(cou)]
        
        if ds == 0 or ds == 1:
            df = df[df.YQ.isin(m)]
            df = df[df.Position.isin(pos)]
        else:
            df = df
        
        df = df.reset_index(drop=True)
        
        #############################################################################################
        
        ############################### Remove Outliers #############################################
        
        def q1(x):
            return x.quantile(0.25)

        def q2(x):
            return x.quantile(0.75)
        
        if rem == 'rem':
            df_rem = df.copy()
            f = {'Cost_M2': [q1,q2]}
            df1 = df.groupby('Trade',as_index=False).agg(f)
            df1.columns = ['Trade','Q1','Q3']
            df1['Diff'] = df1['Q3']-df1['Q1']
            inds = []
            
            for i in range(0,len(df_rem)):
                tr = df_rem['Trade'][i]
                low = float(df1[df1['Trade'] == tr]['Q1']-((df1[df1['Trade'] == tr]['Diff'])*1.5))
                high = float(df1[df1['Trade'] == tr]['Q3']+((df1[df1['Trade'] == tr]['Diff'])*1.5))
                
                if float(df_rem['Cost_M2'][i]) > high:
                    inds.append(i)
                    
                if float(df_rem['Cost_M2'][i]) < low:
                    inds.append(i)
                    
            df_fin = df_rem.drop(inds)
            
        else:
            df_fin = df
            
        #print(df_fin)
        
        p = []
        x = rows.get('points')
        for item in x:
            z = item.get('y')
            p.append(z)
            
        for item in p:
            df_fin = df_fin[df_fin["Cost_M2"] != item]
            
        ##############################################################################################
        #df2 = pd.concat([df,u]).drop_duplicates(keep=False)
        
# =============================================================================
#         if derived_virtual_selected_rows == []: 
#             df2 = df
#             
#         else:
#             jobs = u.iloc[derived_virtual_selected_rows,0]
#             df2 = df[~df['E_Vis_Ref'].isin(jobs)]
# =============================================================================
        ####################################### Group and Summarise #################################
        
        df_fin = df_fin.loc[df_fin['Cost_M2'] != 0]
        df_source = df_fin.copy()
        df2 = df_fin.groupby("Trade",as_index=False).agg({'Enquiry_Sent':'count','Cost_M2': {"Minimum":'min','Average':'mean','Maximum':'max'},'Cost_Plot':{"Minimum":'min','Average':'mean','Maximum':'max'}})
        if inp is None:
            vals = [0]*len(df2)
        else:
            cur = pd.DataFrame(inp)
            vals = [0]*len(df2)
            for i in range(0,len(df2)):
                tr = str(df2.Trade[i])
                val = list(cur.loc[cur.Trade == tr]['Input Value'])
                if len(val)==0:
                    val = [0]
                    
                vals[i] = val[0] #float(sub(r'[^\d.]', '',val[0]))

            
        df2["Input Value"] = vals
        df2.columns  = ["Trade","Quotes","Min Cost/M2(£)","Mean Cost/M2(£)","Max Cost/M2(£)","Min Cost/Plot(£)","Mean Cost/Plot(£)","Max Cost/Plot(£)",'Input Value']
        #df2 = df2.round(0)  
        dat = df2.to_dict('records')
        sourcedat = df_source.to_dict('records')
        
        return([dat,sourcedat])
        
       ################################################################################################
        
    @app.callback(
    Output('datatable-interactivity', 'data'),
    [Input('memory', 'data')])

    def update_table(data):
        if data is None:
            raise PreventUpdate
            
        t = pd.DataFrame(data)
        for i in range(0,len(t)):
            if pd.isnull(t["Input Value"][i]):
                t["Input Value"][i] = 0
        
        t['Min Cost/M2(£)'] = ["£{:0,.2f}".format(x) for x in list(t['Min Cost/M2(£)'])]
        t['Mean Cost/M2(£)'] = ["£{:0,.2f}".format(x) for x in list(t['Mean Cost/M2(£)'])]
        t['Max Cost/M2(£)'] = ["£{:0,.2f}".format(x) for x in list(t['Max Cost/M2(£)'])]
        t['Min Cost/Plot(£)'] = ["£{:0,.0f}".format(x) for x in list(t['Min Cost/Plot(£)'])]
        t['Mean Cost/Plot(£)'] = ["£{:0,.0f}".format(x) for x in list(t['Mean Cost/Plot(£)'])]
        t['Max Cost/Plot(£)'] = ["£{:0,.0f}".format(x) for x in list(t['Max Cost/Plot(£)'])]
        #t['Input Value'] = ["£{:0,.0f}".format(x) for x in list(t['Input Value'])]
        
                
        dat = t.to_dict('records')
        
        return dat
    
    @app.callback(
    [Output('tab2', 'data'),
     Output('intermediate-value','data')],
     [Input('datatable-interactivity', 'data_timestamp'),
     Input('gifa','value'),
     Input('plots','value'),
     Input('btn','n_clicks')],
    [State('datatable-interactivity', 'data'),
     State('intermediate-value','data')])

    def update_table_2(timestamp,gifa,plots,n_clicks,rows,x):
        
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
                
        df['Min Cost/M2(£)'] = [float(sub(r'[^\d.]', '',x)) for x in list(df['Min Cost/M2(£)'])]
        df['Mean Cost/M2(£)'] = [float(sub(r'[^\d.]', '',x)) for x in list(df['Mean Cost/M2(£)'])]
        df['Max Cost/M2(£)'] = [float(sub(r'[^\d.]', '',x)) for x in list(df['Max Cost/M2(£)'])]
        df['Min Cost/Plot(£)'] = [float(sub(r'[^\d.]', '',x)) for x in list(df['Min Cost/Plot(£)'])]
        df['Mean Cost/Plot(£)'] = [float(sub(r'[^\d.]', '',x)) for x in list(df['Mean Cost/Plot(£)'])]
        df['Max Cost/Plot(£)'] = [float(sub(r'[^\d.]', '',x)) for x in list(df['Max Cost/Plot(£)'])]
        
        
        qm = [float(item)/(gifa) for item in list(df['Input Value'])]
        qp = [float(item)/(plots) for item in list(df['Input Value'])]
        
        
        
        df1 = pd.DataFrame({'Trade':df.Trade,'Quoted Cost/M2':qm,'Quoted Cost/Plot':qp,'Flag Cost/M2':[0]*len(df),'Flag Cost/Plot':[0]*len(df)})
        
        flag = []
        dev = [0]*len(df1)
        for i in range(0,len(df1)):
            dev[i] = ((float(df1['Quoted Cost/M2'][i]) - float(df["Mean Cost/M2(£)"][i]))/(float(df["Mean Cost/M2(£)"][i])))
            if dev[i] <= -0.25:
                flag.append("Poor - Low")
            elif dev[i] > -0.25 and dev[i] <= -0.1:
                flag.append("Check - Low")
            elif dev[i]>0.1 and dev[i] <=0.25:
                flag.append("Check - High")
            elif dev[i]>0.25:
                flag.append("Poor - High")
            else:
                flag.append("OK")
            
        
        flag2 = []
        dev2 = [0]*len(df1)
        for j in range(0,len(df1)):
            dev2[j] = ((float(df1['Quoted Cost/Plot'][j]) - float(df["Mean Cost/Plot(£)"][j]))/(float(df["Mean Cost/Plot(£)"][j])))
            if dev2[j] <= -0.25:
                flag2.append("Poor - Low")
            elif dev2[j] > -0.25 and dev2[i] <= -0.1:
                flag2.append("Check - Low")
            elif dev2[j]>0.1 and dev2[i] <=0.25:
                flag2.append("Check - High")
            elif dev2[j]>0.25:
                flag2.append("Poor - High")
            else:
                flag2.append("OK")
                
        df1['Flag Cost/M2'] = flag
        
        df1['Flag Cost/Plot'] = flag2
                
        df1['Quoted Cost/Plot'] = ["£{:0,.0f}".format(x) for x in list(df1['Quoted Cost/Plot'])]
        df1['Quoted Cost/M2'] = ["£{:0,.2f}".format(x) for x in list(df1['Quoted Cost/M2'])]
        
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
        
# =============================================================================
#     @app.callback(
#     Output('enq', 'figure'),
#     [Input('trade choice2', 'value'),
#      Input('OU2','value'),
#      Input('Market2','value')])
#                 
#     
#     def update_enq(trade,OU,market):
#         
#         df = e_set[e_set.Trade == trade]
#         df = df[df.Unit == OU]
#         df = df[df.Tender_Type == market]
#         df = df.groupby("Contractor",as_index=False).agg({'Enquiry_Sent': "count","Price_Returned":"sum","First":"sum","Top_three":"sum"})
#         
#         fig = go.Figure()
#         fig.add_trace(go.Bar(x=df["Contractor"],
#         y=df["Enquiry_Sent"],
#         name='Enquiry_Sent',
#         marker_color='rgb(178,34,34)'
#         ))
#         fig.add_trace(go.Bar(x=df["Contractor"],
#         y=df["Price_Returned"],
#         name='Price_Returned',
#         marker_color='rgb(26, 118, 255)'
#         ))
#         fig.add_trace(go.Bar(x=df["Contractor"],
#         y=df["Top_three"],
#         name='Top 3',
#         marker_color='rgb(0,255,0)'
#         ))
#         
#         return(fig) 
# =============================================================================
        
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
        
# =============================================================================
#     @app.callback(
#     Output('price', 'figure'),
#     [Input('trade choice2', 'value'),
#      Input('OU2','value'),
#      Input('Market2','value')])
#                 
#     
#     def update_price(trade,OU,market):
#         
#         df = e_set[e_set.Trade == trade]
#         df = df[df.Unit == OU]
#         df = df[df.Tender_Type == market]
#         df = df[df.Price_Returned != 0]
#         
#         df = df.groupby("Contractor",as_index=False).agg({'Price_Returned':"sum"})
#         
#         labels = list(df.Contractor)
#         values = list(df["Price_Returned"])
# 
#         # Use `hole` to create a donut-like pie chart
#         fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
#         
#         return(fig) 
# =============================================================================
        
# =============================================================================
#     @app.callback(
#     Output('work', 'figure'),
#     [Input('vistrade2', 'value'),
#      Input('visops2','value'),
#      Input('vismark2','value')])
#                 
#     
#     def update_work(trade,OU,market):
#         
#         df = e_vis[e_vis.Trade == trade]
#         df = df[df.Division == OU]
#         df = df[df['Level 1 & 2'] == market]
#         
#         df = df.groupby("Subcontractor Name",as_index=False).agg({'Job No':"count"})
#         
#         labels = list(df["Subcontractor Name"])
#         values = list(df["Job No"])
#         
#         fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
#         
#         return(fig) 
# =============================================================================
        
    @app.callback(
    Output('tab3', 'data'),
    [Input('trade choicep', 'value'),
     Input('OUp','value'),
     Input('Marketp','value'),
     Input('posp','value'),
     Input('coup','value'),
     Input('yqp','value'),
     Input('pre','value')])
                
    
    def update_tab3(trade,OU,market,pos,cou,yq,pre):
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
            
        df = e_set[e_set.Trade.isin(trade)]
        df = df[df.Unit.isin(OU)]
        df = df[df.Tender_Type.isin(market)]
        df = df[df.Position.isin(pos)]
        df = df[df.County.isin(cou)]
        df = df[df.YQ.isin(m)]
        
        conts = list(df.Contractor.unique())
        
        if pre == 1:
            conts_final = conts
        else:
            conts_final = [x for x in conts if x in pref]
            
        df2 = e_set[e_set.Contractor.isin(conts_final)]
        
        df2 = df2.groupby(["Contractor","Trade"],as_index=False).agg({'Enquiry_Sent': "count","Price_Returned":"sum","First":"sum","Top_three":"sum"})
        df2["% Return Rate"] = round((df2['Price_Returned']/df2['Enquiry_Sent'])*100,0)
        df2["% KPI Score"] = round(((df2["% Return Rate"]*0.67) + ((df2["First"]/df2["Price_Returned"])*0.198) + ((df2["Top_three"]/df2["Price_Returned"])*0.122))/(0.868),0)
        Totals = pd.DataFrame({'Contractor':'Total','Trade':'NA','Enquiry_Sent':sum(df2['Enquiry_Sent']),'Price_Returned':sum(df2['Price_Returned']),'% Return Rate':round((sum(df2['Price_Returned'])/sum(df2['Enquiry_Sent']))*100,0),'First':sum(df2['First']),'Top_three':sum(df2['Top_three']),'% KPI Score':0},index=[0])
        Totals["% KPI Score"] = round(((Totals["% Return Rate"]*0.67) + ((Totals["First"]/Totals["Price_Returned"])*0.198) + ((Totals["Top_three"]/Totals["Price_Returned"])*0.122))/(0.868),0)
        df2 = Totals.append(df2, ignore_index = True)
        df2['% Return Rate'] = ["{:.0%}".format((x/100)) for x in list(df2['% Return Rate'])]
        df2['% KPI Score'] = ["{:.0%}".format(x/100) for x in list(df2['% KPI Score'])]
        df2['Contact Details'] = ''
        for i in range(0,len(df2)):
            df2['Contact Details'][i] = dff.loc[dff['Contractor']==df2['Contractor'][i],'Details']
        
        data = df2.to_dict('records')
        
        return data
    
# =============================================================================
#     @app.callback(
#     Output('vistab', 'data'),
#     [Input('evistrade', 'value'),
#      Input('evisops','value'),
#      Input('evisMarket','value'),
#      Input('esettrade','value')])
#                 
#     
#     def update_vistab(trade,OU,market,trade2):
#         
#         if type(trade) == str:
#             trade = [trade]
#         elif trade is None:
#              trade = list(e_vis.Trade.unique())
#         else:
#             trade = trade
#         
#         if type(OU) == str:
#             OU = [OU]
#         elif OU is None:
#              OU = list(e_vis.Division.unique())
#         else:
#             OU = OU
#             
#         if type(market) == str:
#             market = [market]
#         elif market is None:
#              market = list(e_vis['Market Sector'].unique())
#         else:
#             market = market
#             
#         df = e_vis[e_vis.Trade.isin(trade)]
#         df = df[df.Division.isin(OU)]
#         df = df[df['Market Sector'].isin(market)]
#         
#         helped = []
#         
#         for index, row in df.iterrows():
#             temp = e_set.loc[e_set["E_Vis_Ref"]==row["Job No"]]
#             priced = list(temp.loc[temp.Price_Returned == 1].Contractor)
#             if(row["Subcontractor Name"] in priced):
#                 helped.append(1)
#             else:
#                 helped.append(0)
#                 
#         df["Helped at Tender?"] = helped
#         df = df.round(0)
#         
#         data = df.to_dict('records')
#         
#         return data
# =============================================================================
    
# =============================================================================
#     @app.callback(
#     Output('mean', 'children'),
#     [Input('vistab', 'data'),
#      Input('vistab', 'columns')])
#         
#     def display_mean(rows, columns):
#         
#         if rows is None:
#             raise PreventUpdate
# 
#             
#         df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
#         
#         x = df[" Buying Gain"].astype(float)
#         z = df[" Estimating Budget"].astype(float)
#         y = sum(x)/sum(z)
#         y = round(y,5)
#         
#         return('The Total Buying gain is: %{}'.format(y))
# =============================================================================
        
# =============================================================================
#     @app.callback(
#     Output('helpdonut', 'figure'),
#     [Input('vistab', 'data'),
#      Input('vistab', 'columns')])
#         
#     def display_help(rows, columns):
#         
#         if rows is None:
#             raise PreventUpdate
#             
#         df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
#     
#         values = [sum(df["Helped at Tender?"]),len(df) - sum(df["Helped at Tender?"])]
#         labels = ["Yes","No"]
#         
#         fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
#         
#         return(fig)
# =============================================================================
        
    @app.callback(
    Output('OU', 'value'),
    [Input('select-all-OU', 'value'),
     Input('OUp','value')],
     [State('OU', 'value')])

    def test(selected, copy, values):
            
        if selected == 'same':
            return copy
        
        if selected == 'allOU':
            return list(e_set.Unit.unique())
        
        elif selected == 'setOU':
            return ['OU1']
        
        else:
            return values
        
    @app.callback(
    Output('Market', 'value'),
    [Input('select-all-ma', 'value'),
     Input('Marketp','value')],
     [State('Market', 'value')])

    def sma(selected, copy, values):
        
        if selected is None:
            raise PreventUpdate
            
        if selected == 'same':
            return copy
        
        if selected == 'allma':
            return list(e_set['Tender_Type'].unique())
        
        elif selected == 'setma':
            return ['NB - Housing']
        
        else:
            return values
        
    @app.callback(
    Output('pos', 'value'),
    [Input('select-all-po', 'value'),
     Input('posp','value')],
     [State('pos', 'value')])

    def smp(selected, copy, values):
        
        if selected is None:
            raise PreventUpdate
            
        if selected == 'same':
            return copy
        
        if selected == 'allpo':
            return list(e_set.Position.unique())
        
        elif selected == 'setpo':
            return ['1','2','3']
        
        else:
            return values
        
    @app.callback(
    Output('cou', 'value'),
    [Input('select-all-co', 'value'),
     Input('coup','value')],
     [State('cou', 'value')])

    def smc(selected, copy, values):
        
        if selected is None:
            raise PreventUpdate
            
        if selected == 'same':
            return copy
        
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
    Output('trade choice', 'value'),
    [Input('select-all-tr', 'value'),
     Input('trade choicep', 'value')],
     [State('trade choice', 'value')])

    def select_key_trades(selected, copy, values):
        
        if selected is None:
            raise PreventUpdate
            
        elif selected == 'same':
            return copy
        
        elif selected == 'keytr':
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
    Output('trade choicep', 'value'),
    [Input('select-all-trp', 'value')],
    [State('trade choicep', 'value')])

    def select_key_tradesp(selected, values):
        
        if selected is None:
            raise PreventUpdate
            
        elif selected == 'keytrp':
            return ['***D_SC Bulk Excavation','***D_SC Groundworker','***E_SC PCC Floors',
                    'G_SC Structural Steelwork','***M_SC Screeding','***F_LO Brickwork',
                    '***G_QM Timber Upper Floors','***G_LO Joinery','***L_QM Stairs-Timber',
                    '***G_QM Roof Trusses','***H_SC Roofing Slate & Tile','***P_SC Insulation',
                    '***L_SC PVC Windows','***R_SC Plumbing','***Y_SC Electrical',
                    '***M_SC Plastering','***M_SC Painting&Decorating','***Q_SC Landscaping',
                    '***Q_SC Fencing (Timber)','***Q_SC Fencing (Metal)']
        
        elif selected == 'settrp':
            return ['***F_LO Brickwork']
        
        else:
            return values
        
        
    @app.callback(
    Output('jobplot', 'figure'),
    [Input('trade choice','value'),
     Input('OU','value'),
     Input('Market','value'),
     Input('pos','value'),
     Input('cou','value'),
     Input('yq','value'),
     Input('Rem','value')])
    
    def update_joblist(trade,OU,market,pos,cou,yq,rem):
        
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
        df = df.reset_index(drop=True)
        
        # If remove outliers is T, group by trade, work out q1&3 and diff, times diff by 1.5 and remove any values 
        def q1(x):
            return x.quantile(0.25)

        def q2(x):
            return x.quantile(0.75)
        
        if rem == 'rem':
            df_rem = df.copy()
            f = {'Cost_M2': [q1,q2]}
            df1 = df.groupby('Trade',as_index=False).agg(f)
            df1.columns = ['Trade','Q1','Q3']
            df1['Diff'] = df1['Q3']-df1['Q1']
            inds = []
            
            for i in range(0,len(df_rem)):
                tr = df_rem['Trade'][i]
                low = float(df1[df1['Trade'] == tr]['Q1']-((df1[df1['Trade'] == tr]['Diff'])*1.5))
                high = float(df1[df1['Trade'] == tr]['Q3']+((df1[df1['Trade'] == tr]['Diff'])*1.5))
                
                if float(df_rem['Cost_M2'][i]) > high:
                    inds.append(i)
                    
                if float(df_rem['Cost_M2'][i]) < low:
                    inds.append(i)
                    
            df_fin = df_rem.drop(inds)
            fig = px.box(df_fin,y="Cost_M2",color="Trade",points=False)
            fig.layout.clickmode = "event+select"
            
        else:
            df_fin = df
                
            #df = df[df.Position != 0]
            fig = px.box(df_fin,y="Cost_M2",color="Trade")
            fig.layout.clickmode = "event+select"
                
        return(fig)
        
    @app.callback(
    dash.dependencies.Output('download-link2', 'href'),
    [dash.dependencies.Input('tab3', 'data')])
    
    def update_download_link(data):
        dff = pd.DataFrame(data)
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)
    
        return csv_string

    @app.callback(
    dash.dependencies.Output('download-link1', 'href'),
    [dash.dependencies.Input('datatable-interactivity', 'data'),
     dash.dependencies.Input('tab2', 'data')])
    
    def update_download_link2(data,comp_data):
        df1 = pd.DataFrame(data)
        df2 = pd.DataFrame(comp_data)
        
        if len(df1) != len(df2):
            raise PreventUpdate
            
        dff = pd.merge(df1,df2,on='Trade')
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)
    
        return csv_string
    
    @app.callback(
    dash.dependencies.Output('download-link3', 'href'),
    [dash.dependencies.Input('tab4', 'data')])
    
    def download_kpisource_link(data):
        dff = pd.DataFrame(data)
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)
    
        return csv_string
    
    @app.callback(
    dash.dependencies.Output('download-link4', 'href'),
    [dash.dependencies.Input('tab5', 'data')])
    
    def download_fin_source_link(data):
        dff = pd.DataFrame(data)
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(csv_string)
    
        return csv_string
    
    @app.callback(
    Output('tab4', 'data'),
    [Input('tab3', "derived_virtual_data"),
     Input('tab3', "derived_virtual_selected_rows")])
    
    def kpi_source_data(rows, derived_virtual_selected_rows):
        
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []
            
        if rows is None:
            rows = []
            
        df = pd.DataFrame(rows)
        dff = df.iloc[derived_virtual_selected_rows,:]
        
        if len(dff)==0:
            Conts = []
        else:
            Conts = list(dff['Contractor'].unique())
         
        df_fin = e_set.loc[e_set.Contractor.isin(Conts)]
        
        data = df_fin.to_dict('records')

    
        return(data)
        
        
    @app.callback(
    [Output('trade choice','options'),
     Output('OU','options'),
     Output('Market','options'),
     Output('pos','options'),
     Output('cou','options')],
    [Input('ds','value')])

    def update_filter_vals(dataset):
        if dataset == 0:
            return([sorted([{'label': i, 'value': i} for i in list(e_set.Trade.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.Unit.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.Tender_Type.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.Position.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.County.unique()) if i != 0],key=itemgetter('value')),
                    ])
        if dataset == 1:
            return([sorted([{'label': i, 'value': i} for i in list(e_set.Trade.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.Unit.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.Tender_Type.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.Position.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_set.County.unique()) if i != 0],key=itemgetter('value')),
                    ])
        if dataset == 2:
            return([sorted([{'label': i, 'value': i} for i in list(e_vis.Trade.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_vis.Unit.unique()) if i != 0],key=itemgetter('value')),
                    sorted([{'label': i, 'value': i} for i in list(e_vis.Tender_Type.unique()) if i != 0],key=itemgetter('value')),
                    [{'label': i, 'value': i,'disabled':True} for i in ['0']],
                    [{'label': i, 'value': i,'disabled':True} for i in ['0']]
                    ])
        
    @app.callback(
    Output('confirm', 'displayed'),
    [Input('btn', 'n_clicks')],
    [State('gifa','value'),
     State('plots','value')])
    
    
    def display_confirm(n_clicks,gifa,plots):
        if not n_clicks:
            raise PreventUpdate
            
        if gifa == 0 or gifa is None:
            return True
        
        elif plots == 0 or plots is None:
            return True
        
        return False
    
    @app.callback(
    [Output('tab5', 'data'),
     Output('tab5', 'columns')],
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows"),
     Input('ds','value'),
     Input('hidden-value','data')])
    
    def fin_source_data(rows, derived_virtual_selected_rows,dataset,mem):
        
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []
            
        if rows is None:
            rows = []
            
        if len(derived_virtual_selected_rows) == 0:
            raise PreventUpdate
            
        if dataset == 2:
            cols = [{'id': c, 'name': c} for c in list(e_vis.columns)]
            
        else:
            cols = [{'id': c, 'name': c} for c in list(e_set.columns)]
            
        df_mem = pd.DataFrame(mem)
        
        df = pd.DataFrame(rows)
        
        dff = df.iloc[derived_virtual_selected_rows,:]
        trds = list(dff.Trade.unique())
        
        print(trds)
        
        df_fin = df_mem.loc[df_mem.Trade.isin(trds)]
            
        return([df_fin.to_dict('records'),cols])
            
            
    if __name__ == '__main__':
        app.run_server(debug=True)
      
    
ScriptMain()