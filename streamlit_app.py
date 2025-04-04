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
    st.markdown("""
                <style>
                canvas * {
                 font: 16px Verdana, Arial, sans-serif;
                }
                .stExpander details {

                    border: 2px solid green;
                    border-radius: 5px;
                }
                .stExpander details summary {
                    background-color: #9cf06e;
                    color: black; # Adjust this for expander header color
                    border: 2px solid green;
                    border-radius: 5px;
                
                }
                .streamlit-expanderContent {
                    background-color: white;
                    color: black; # Expander content color
                }

                [class*=st-key-SERV] {
                margin-top: 1rem;
                }

                
                [class*=special_food_result] * > input {
                background: rgba(33, 195, 84, 0.1);
                font-weight: bold;}
                [class*=special_food_result] * > label  p {
                font-weight: bold;}

                summary * {
                font-weight: bold;
                }

                table * {
                font-size: 1.5rem !important;
                }

                .custom-info {
                padding: 5px;
                line-height: 1.6rem;
                border-radius: 5px;
                color: #183950;
                background-color: rgba(186, 217, 240, 0.6);
                }

                .center-element {
                padding: auto;
                margin: auto;
                }

               /* div:has(> [class*=input_amount_special])  {
                 margin: auto;
                } */

                [class*=input_amount_special] * {
                 font-size: 1.5rem;
                }

                .special-entry-warning {
                color: rgb(110, 89, 24);
                background-color: rgba(255, 227, 18, 0.1);
                font-weight: bold;
                color: rgb(146, 108, 5);
                padding: 1rem;
                margin-bottom: 18px;
                }

                .stFormSubmitButton > button,
                .stButton > button {
                background-color: rgba(199, 199, 236, 0.3) !important;
                }

                </style>
                """, unsafe_allow_html=True)
                    # div:has(.st-key-customer_input_container)) {
                #     padding: 0rem;
                # }

if __name__ == "__main__":
    run()
