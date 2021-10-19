import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config('NZ COVID-19 Vaccine Stats')
st.title('New Zealand COVID-19 Vaccine Stats')

st.write('This page visualises the COVID-19 vaccine rollout in New Zealand')
st.write('Data for this page comes from the [Ministry of Health Github Repository](https://github.com/minhealthnz/nz-covid-data/)')

st.write('')
st.write('##### Select minimum vaccine percentage to highlight')

highlight_percent = st.slider('', min_value=0, max_value=100, value=90)

st.subheader('Vaccine stats by Area, Ethnic Group, Age and Gender')

moh_github = 'https://raw.githubusercontent.com/minhealthnz/nz-covid-data/main/vaccine-data/latest/'

#read in data
@st.cache
def read_moh_data(url):
    df = pd.read_csv(url)
    return df

vaccine_data = read_moh_data(moh_github + 'dhb_residence_uptake.csv')

st.write('')
st.write('##### Select x and y axis variables')

#drop down boxes for x and y axis
x_axis = 'Percent first dose'
x_axis = st.selectbox('X Axis', ('Percent first dose', 'Percent second dose'))

y_axis = 'DHB of residence'
y_axis = st.selectbox('Y Axis', ('DHB of residence', 'Ethnic group', 'Age group', 'Gender'))

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
    alt.X('percent:Q', title='', scale=alt.Scale(domain=[0, 100])),
    alt.Y(f'{y_axis}', title='')
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

st.write('')
st.write('##### {} by {}'.format(x_axis, y_axis))
st.altair_chart(bars + text, use_container_width=True)
st.caption('Source: [Ministry of Health](https://github.com/minhealthnz/nz-covid-data/blob/main/vaccine-data/latest/dhb_residence_uptake.csv)')
