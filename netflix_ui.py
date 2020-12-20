import netflix as nf
import streamlit as st


@st.cache
def load_data():
    """Load the Netflix viewing data."""
    return nf.load_viewing_activity(nf.view_activity_path)


@st.cache
def select_data_for_year(data, year):
    """Get the dataframe for the given year."""
    return data.loc[data['Month Begin'].dt.year == year]


@st.cache
def get_monthly_usage_for_year(data_for_year):
    """This hangs for some reason with streamlit 0.71.0."""
    return nf.plot_monthly_usage_by_device(data_for_year)


def get_monthly_usage_for_year_cached(data_for_year):
    """Manually cache the plot used by this function."""
    _id = id(data_for_year)
    FCN_KEY = 'get-monthly-usage-for-year-manual-cache'
    cache = st.caching._mem_caches.get_cache(FCN_KEY, None, None)
    if _id in cache:
        return cache[_id]
    plot = nf.plot_monthly_usage_by_device(data_for_year)
    cache[_id] = plot
    return plot


@st.cache
def get_show_watch_count_for_year(data_for_year):
    """Get the number of times each show watched for the year."""
    return nf.count_show_watches(data_for_year)


data = load_data()

st.title('Netflix Usage')
year = st.sidebar.selectbox('Pick a year', data['Month Begin'].dt.year.unique())

data_for_year = select_data_for_year(data, year)

if st.checkbox('Show Monthly Usage'):
    # This one hangs trying to use the cache.
    # st.write(get_monthly_usage_for_year(data_for_year))
    st.write(get_monthly_usage_for_year_cached(data_for_year))

if st.checkbox('Show watches by show'):
    counts = get_show_watch_count_for_year(data_for_year)
    st.write(counts)
