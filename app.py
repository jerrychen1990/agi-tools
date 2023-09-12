import base64
import logging

import streamlit as st
from streamlit.components.v1 import html

from views import batch_llm, similarity, test_llm_api

st.set_page_config(layout="wide", page_title='AI工具集合')
st.set_option('deprecation.showPyplotGlobalUse', False)


NAVBAR_PATHS = {
    '文本相似度': 'similarity',
    'api测试': 'test_llm_api',
    "批量测试": 'batch_llm'

}
_view_map = {
    "similarity": similarity,
    "test_llm_api": test_llm_api,
    "batch_llm": batch_llm
}


SETTINGS = {
    'OPTIONS': 'options',
    'CONFIGURATION': 'configuration'
}


def inject_custom_css():
    with open('assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def get_current_route():
    try:
        return st.experimental_get_query_params()['nav'][0]
    except:
        return None


def navbar_component():
    with open("assets/images/settings.png", "rb") as image_file:
        image_as_base64 = base64.b64encode(image_file.read())

    navbar_items = ''
    for key, value in NAVBAR_PATHS.items():
        navbar_items += (f'<a class="navitem" href="/?nav={value}">{key}</a>')

    settings_items = ''
    for key, value in SETTINGS.items():
        settings_items += (
            f'<a href="/?nav={value}" class="settingsNav">{key}</a>')

    component = rf'''
            <nav class="container navbar" id="navbar">
                <ul class="navlist">
                {navbar_items}
                </ul>
                <div class="dropdown" id="settingsDropDown">
                    <img class="dropbtn" src="data:image/png;base64, {image_as_base64.decode("utf-8")}"/>
                    <div id="myDropdown" class="dropdown-content">
                        {settings_items}
                    </div>
                </div>
            </nav>
            '''
    st.markdown(component, unsafe_allow_html=True)
    js = '''
    <script>
        // navbar elements
        var navigationTabs = window.parent.document.getElementsByClassName("navitem");
        var cleanNavbar = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }

        for (var i = 0; i < navigationTabs.length; i++) {
            cleanNavbar(navigationTabs[i]);
        }
        '''


logging.getLogger().setLevel(logging.INFO)


inject_custom_css()
navbar_component()


def navigation():
    route = get_current_route()
    logging.info(f"{route=}")
    view = _view_map.get(route, similarity)
    view.load_view()


navigation()
