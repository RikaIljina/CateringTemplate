# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

import streamlit as st

dir_path = Path(__file__).parent


# Note that this needs to be in a method so we can have an e2e playwright test.
def run():

    page = st.navigation(
        [
            st.Page(
                dir_path / "catering.py", title="Inmatning", icon=":material/waving_hand:"
            ),
            # st.Page(
            #     dir_path / "dataframe_demo.py",
            #     title="DataFrame demo",
            #     icon=":material/table:",
            # ),
            # st.Page(
            #     dir_path / "plotting_demo.py",
            #     title="Plotting demo",
            #     icon=":material/show_chart:",
            # ),
            # st.Page(
            #     dir_path / "mapping_demo.py",
            #     title="Mapping demo",
            #     icon=":material/public:",
            # ),
            # st.Page(
            #     dir_path / "animation_demo.py",
            #     title="Animation demo",
            #     icon=":material/animation:",
            # ),
        ]
    )
    page.run()
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#     st.markdown("""
#                 <style>
#                 canvas * {
#     font: 16px Verdana, Arial, sans-serif;
#    }
#    .stExpander details {

#        border: 2px solid green;
#        border-radius: 7px;
#    }
#    .stExpander details summary {
#        background-color: #91CE8F;
#        color: black;
#        border: 2px solid green;
#        border-radius: 5px;
#    }

#    .stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"] {
#    background-color: #e8bcb4;
#    color: #1c1a1a;
#    }

#    .btn-link {
#        background-color: #91CE8F;
#        border-radius: 7px;
#        width: calc(100% + 32px);
#        margin-left: -16px;
#    }

#    .btn-link:hover {
#    background-color: #63AC61;
#    }

#    .streamlit-expanderContent {
#        background-color: white;
#        color: black;
#    }

#    [class*=st-key-SERV] {
#    margin-top: 1rem;
#    }

   
#    [class*=special_food_result] * > input {
#        background: rgba(33, 195, 84, 0.1);
#        font-weight: bold;
#    }
#    [class*=special_food_result] * > label  p {
#        font-weight: bold;
#    }

#    .stExpander details summary * {
#        font-weight: bold;
#        font-size: 1.5rem;
#    }

#    .stExpander details summary:hover {
#        background-color: #63AC61;
#    }
   
#    .stExpander details summary:hover * {
#        color: #F9F7C8;
#    }

#    table * {
#    font-size: 1.5rem !important;
#    }

#    .custom-info {
#        padding: 5px;
#        line-height: 1.6rem;
#        border-radius: 5px;
#        color: #183950;
#        background-color: rgba(186, 217, 240, 0.6);
#    }

#    .center-element {
#        padding: auto;
#        margin: auto;
#    }

#    /* div[class*="stColumn"]:has(button) * {
#    display: flex;
#    align-items: stretch; 
#    } */

#    [class*=input_amount_special] * {
#     font-size: 1.5rem;
#    }

#    .special-entry-warning {
#        color: rgb(110, 89, 24);
#        background-color: rgba(255, 227, 18, 0.1);
#        font-weight: bold;
#        color: rgb(146, 108, 5);
#        padding: 1rem;
#        margin-bottom: 18px;
#    }

#    /*.stFormSubmitButton > button {
#        background-color: rgba(210, 177, 235, 0.5) !important;
#        height: 3rem !important;
#        font-size: 1.2rem;
#    }*/

   

#   /* .stButton > button {
#        background-color: rgba(210, 177, 235, 0.5) !important;
#        height: 3rem !important;
#        font-size: 1.2rem;
#    } */

#    .stElementContainer .stButton button {
#        background-color: rgba(210, 177, 235, 0.5) !important;
#        height: 3rem !important;
#        font-size: 1.2rem;
#        float: right !important;
#    }

#    .stElementContainer .stFormSubmitButton button {
#        background-color: rgba(210, 177, 235, 0.5) !important;
#        height: 3rem !important;
#        font-size: 1.2rem;
#        float: right !important;
#    }

#    .stElementContainer[class*=special_food_result] .stButton button {
#        background-color: rgba(210, 177, 235, 0.5) !important;
#        height: 4rem !important;
#        width: 100px;
#        font-size: 1.2rem;
#        float: left !important;
       
#    }

#    [class*=form_special_selection] .stFormSubmitButton button {
#        background-color: rgba(210, 177, 235, 0.5) !important;
#        height: 6rem !important;
#        width: 100px;
#        font-size: 1.2rem;
#        float: left !important;
#    }

#    button[role="tab"] * {
#        font-weight: bold;
#        font-size: 1.5rem;
#        padding-right: 25px;
#    }

#    .stElementContainer .stFormSubmitButton button:hover,
#    .stElementContainer .stButton button:hover {
#        background-color: grey !important;
#    }

#    button[role="tab"]:hover {
#        background-color: #D8F6EF !important;
#    }

#    button[role="tab"]:hover p {
#        color: black !important;

#    }

#    button[role="tab"]:focus,
#    button[role="tab"]:active  {
#        background-color: #D8F6EF !important;

#    }

#    button[role="tab"]:focus p,
#    button[role="tab"]:active p {
#        color: #203579 !important;

#    }
#    .stElementContainer .stFormSubmitButton button:hover,
#    .stElementContainer .stButton button:hover p {
#        color: rgba(210, 177, 235, 0.5) !important;
#    }

#    .stElementContainer .stFormSubmitButton button:hover,
#    .stElementContainer .stButton button:focus p {
#        color: black !important;
#    }

#                 </style>
    
#                 """, unsafe_allow_html=True)
    # div:has(.st-key-customer_input_container)) {
    #     padding: 0rem;
    # }


if __name__ == "__main__":
    run()
