import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config('NZ COVID-19 Vaccine Stats')
st.title('New Zealand COVID-19 Vaccine Stats')

st.write('This page visualises the COVID-19 vaccine rollout in New Zealand')
st.write('Data for this page comes from the [Ministry of Health Github Repository](https://github.com/minhealthnz/nz-covid-data/)')

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
st.write('##### Select x and y axis variables and optional filter variable')

#drop down boxes for x and y axis
x_axis = 'Percent first dose'
x_axis = st.selectbox('X Axis', ('Percent first dose', 'Percent second dose'))

y_axis_list = ['', 'DHB of residence', 'Ethnic group', 'Age group', 'Gender']

y_axis = 'DHB of residence'
y_axis = st.selectbox('Y Axis', (list(filter(lambda x: x != '', y_axis_list))))

st.markdown("""---""")

#add a optional filter for the data
filter_category_list = list(filter(lambda x: x != y_axis, y_axis_list))

filter_category = st.selectbox('Filter by', (filter_category_list))

if filter_category != '':
    filter_value_list = vaccine_data[filter_category].drop_duplicates()
    filter_value = st.selectbox('Filter value', (filter_value_list))
else: 
    filter_value = ''

def create_graph_dataset(df, x_axis, y_axis, filter_category, filter_value, filter_type='include'):
    #filter for category
    if filter_category != '':
        if filter_type == 'include':
            df = df[df[filter_category]==filter_value]
        elif filter_type == 'exclude':
            df = df[df[filter_category]!=filter_value]

    #group data by variable
    df = df.groupby(f'{y_axis}').sum()
    df.reset_index(inplace=True)

    #remove categories depending on graph type
    if y_axis == 'DHB of residence':
        df = df.drop(df[df['DHB of residence'] == 'Overseas / Unknown'].index)
        df = df.drop(df[df['DHB of residence'] == 'Various'].index)

    #add in percentages after variable is created
    if x_axis == 'Percent first dose':
        df = df.assign(percent = lambda x: x['First dose administered'] / x['Population'])
    else:
        df = df.assign(percent = lambda x: x['Second dose administered'] / x['Population'])

    df['percent'] = df['percent'].round(3) * 100
    df['percent'] = df['percent'].apply(lambda x: 100 if x > 100 else x)

    return df

#create bar graph
bar_data = create_graph_dataset(vaccine_data, x_axis, y_axis, filter_category, filter_value, 'include')

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

st.markdown("""---""")
st.write('##### {} by {}'.format(x_axis, y_axis))
st.altair_chart(bars + text, use_container_width=True)
st.caption('Source: [Ministry of Health](https://github.com/minhealthnz/nz-covid-data/blob/main/vaccine-data/latest/dhb_residence_uptake.csv)')

if filter_category != '':
    category_data = bar_data[[y_axis, 'percent']]
    category_data.rename(columns = {y_axis: 'y'}, inplace = True)
    category_data['colour'] = '#191970'

    other_data = create_graph_dataset(vaccine_data, x_axis, y_axis, filter_category, filter_value, 'exclude')
    other_data = other_data[[y_axis, 'percent']]
    other_data['colour'] = '#a9a9a9'
    other_data.rename(columns = {y_axis: 'y'}, inplace = True)

    dumbbell_data = category_data.append(other_data, ignore_index=True)

    dumbbell = alt.Chart(dumbbell_data).mark_circle().encode(
        alt.X(
            'percent:Q',
            scale=alt.Scale(zero=False, domain=[0, 100]),
            axis=alt.Axis(grid=False),
            title=""
        ),
        alt.Y(
            'y',
            title="",
            axis=alt.Axis(grid=True)
        ),
        color=alt.Color('colour', scale=None, legend=alt.Legend(title="")),
        tooltip=[alt.Tooltip('percent', title=x_axis)]
    )

    vline = alt.Chart(pd.DataFrame({
        'percent': [highlight_percent],
        'color': ['#FF4B4B']
        })).mark_rule().encode(
        x='percent:Q',
        color=alt.Color('color:N', scale=None)
    )

    dumbbell_chart = alt.layer(vline, dumbbell).properties(
        height=alt.Step(20)
    ).configure_view(stroke="transparent"
    ).configure_circle(size=200)

    st.write('##### {} by {}'.format(x_axis, y_axis))
    st.markdown('<b style="color:#191970;">{} {}</b> compared to the <b style="color:#a9a9a9;">Other {}s</b>'.format(filter_value, filter_category, filter_category), unsafe_allow_html=True)
    st.altair_chart(dumbbell_chart,use_container_width=True)
    st.caption('Source: [Ministry of Health](https://github.com/minhealthnz/nz-covid-data/blob/main/vaccine-data/latest/dhb_residence_uptake.csv)')
