from numpy import double
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config('NZ COVID-19 Vaccine Stats')
st.title('New Zealand COVID-19 Vaccine Stats')

st.subheader('Vaccine stats by Area, Ethnic Group, Age and Gender')

st.caption('Source: [Ministry of Health - Github](https://github.com/minhealthnz/nz-covid-data/)')

moh_github = 'https://raw.githubusercontent.com/minhealthnz/nz-covid-data/main/vaccine-data/latest/'
url = moh_github + 'dhb_residence_uptake.csv'

#read in data
vaccine_data = pd.read_csv(url)

#drop down boxes for x and y axis
x_axis = 'Percent first dose'
x_axis = st.selectbox('X Axis', ('Percent first dose', 'Percent second dose'))

y_axis = 'DHB of residence'
y_axis = st.selectbox('Y Axis', ('DHB of residence', 'Ethnic group', 'Age group', 'Gender'))

highlight_percent = st.slider('Highlight vaccine rate lower than percentage', min_value=0, max_value=100, value=90)

#group data by variable
bar_data = vaccine_data.groupby(f'{y_axis}').sum()
bar_data.reset_index(inplace=True)

#remove categories depending on graph type
if y_axis == 'DHB of residence':
    bar_data = bar_data.drop(bar_data[bar_data['DHB of residence'] == 'Overseas / Unknown'].index)

#add in percentages after variable is created
if x_axis == 'Percent first dose':
    bar_data = bar_data.assign(percent = lambda x: x['First dose administered'] / x['Population'])
else:
    bar_data = bar_data.assign(percent = lambda x: x['Second dose administered'] / x['Population'])

bar_data['percent'] = bar_data['percent'].round(3) * 100
bar_data['percent'] = bar_data['percent'].apply(lambda x: 100 if x > 100 else x)

#create bar graph
base = alt.Chart(bar_data).encode(
    alt.X('percent:Q', title=f'{x_axis}', scale=alt.Scale(domain=[0, 100])),
    y=f'{y_axis}'
)
bars = base.mark_bar().encode(
    color=alt.condition(
        alt.datum.percent > highlight_percent,
        alt.value('#a9a9a9'),
        alt.value('#FF4B4B')
    )
)
text = base.mark_text(
    align='left',
    baseline='middle',
    dx=3,
    color="#31333F"
).encode(
    text='percent:Q'
)

st.altair_chart(bars + text)

