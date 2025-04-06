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

import uuid
import streamlit as st
import json
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from streamlit_javascript import st_javascript
from datetime import date, datetime
from datetime import time
from streamlit_gsheets import GSheetsConnection
from db_con import CatSheet, UpdSheet
from utils import filter_dataframe, show_df_with_checkboxes, process_choice, input_main_info, input_special, read_excel  # upd_results


st.set_page_config(page_title="Hello", page_icon=":material/waving_hand:",
                   layout="wide", initial_sidebar_state="auto", menu_items=None)


st.title("Welcome to Catering! 👋")
st.write(
    """
    Here, you can prefill your catering template.
    """
)

ws_names = {"all": "Data_AllaRätter", "kvs25": "Data_KvällSommar25", "kvh24": "Data_KvällHöst24",
                   "ls25": "Data_LunchSommar25", "lh24": "Data_LunchHöst24", "allerg": "Data_Allergier",
                   "fe": "Data_FörEftermiddag", "customers": "Data_Kunder", "salads": "Data_Sallader", }

# Create a connection object.

# conn = st.connection("gsheets", type=GSheetsConnection)

# df = conn.read(worksheet="Resultat", usecols=[0,1,2])
# if st.button("Update worksheet"):
# print(st.session_state)
if "df" not in st.session_state:
    st.session_state.df = CatSheet()
    print("CONNECTED GSHEETS")
if "upd_conn" not in st.session_state:
    print("CONNECTING GSPREAD")
    st.session_state.upd_conn = UpdSheet()

if "result_dict" not in st.session_state:

    st.session_state.result_dict = {
        "venue": "",
        "customer_name": "",
        "amount_guests": 0,
        "date": "",
        "meals": {},
    }

if "customer_list" not in st.session_state:
    st.session_state.customer_list = st.session_state.df.read(
        ws_names["customers"], 1)
cont_border = False
info_col1, info_col2, info_col3, info_col4 = st.columns([1, 1, 1, 1])
with info_col1:
    with st.container(border=True, key="venue_input_container"):
        venue = st.selectbox("Ort", ["Mariestad", "Sätra"])
        st.session_state.result_dict.update({"venue": venue})
with info_col2:
    with st.container(border=True, key="customer_input_container"):
        customer_name = st.selectbox(
            "Kund:", st.session_state.customer_list, key="customer_name")
        if customer_name == "Ny ...":
            cont_border = True
            st.text_input("Ny kund:", key="new_customer_name")
            st.session_state.result_dict.update(
                {"customer_name": st.session_state.new_customer_name})
            if st.button("Add to list", key="update_clicked"):
                st.session_state.upd_conn.write(
                    ws_names["customers"], st.session_state.new_customer_name, len(st.session_state.customer_list))
                st.session_state.customer_list = st.session_state.df.read(
                    ws_names["customers"], 1)

                # st.session_state.update_clicked = False
            # print(st.cache_data())
                st.cache_data.clear()
                st.rerun()
        else:
            st.session_state.result_dict.update(
                {"customer_name": st.session_state.customer_name})
            cont_border = False
# if st.session_state.recon_clicked:
#     df = CatSheet()
#     upd_customers()
#     st.session_state.recon_clicked = False
# else:
#     st.write("Old connection")

if "guest_key" not in st.session_state:
    st.session_state["guest_key"] = str(uuid.uuid4())

with info_col3:
    with st.container(border=True, key="guest_input_container"):
        guest_cont = st.empty()
        with guest_cont:
            guest_amount = st.number_input(
                "Antal personer:", value=st.session_state.result_dict["amount_guests"], format="%i", step=1,  key=f"guest_amount_{st.session_state["guest_key"] }")

with info_col4:
    with st.container(border=True, key="date_input_container"):
        event_date = st.date_input(
            "Datum:",   key="event_date")
    # Get input for date and amount of guests
# st.write(st.session_state.guest_amount)
st.session_state.result_dict.update(
    {"amount_guests": st.session_state[f'guest_amount_{st.session_state["guest_key"]}']})
# st.write(event_date)

st.session_state.result_dict.update(
    {"date": st.session_state.event_date})
# st.write(st.session_state.result_dict)
# st.write(st.session_state.result_dict["date"])

# lunch = df.read(ws_names["all"])
# st.write(lunch.columns.to_list())

# Reference the list for förmiddag here
if "morning" not in st.session_state:
    st.session_state.morning = st.session_state.df.read(ws_names["fe"], 1)
if "efterm" not in st.session_state:
    st.session_state.efterm = st.session_state.morning.copy()
if "all_dishes" not in st.session_state:
    st.session_state.all_dishes = st.session_state.df.read(ws_names["all"], 3)
if "lunch24" not in st.session_state:
    st.session_state.lunch24 = st.session_state.df.read(ws_names["lh24"], 2)
if "lunch25" not in st.session_state:
    st.session_state.lunch25 = st.session_state.df.read(ws_names["ls25"], 2)
if "kvs25" not in st.session_state:
    st.session_state.kvs25 = st.session_state.df.read(ws_names["kvs25"], 4)
if "kvh24" not in st.session_state:
    st.session_state.kvh24 = st.session_state.df.read(ws_names["kvh24"], 4)
if "allerg" not in st.session_state:
    st.session_state.allerg = st.session_state.df.read(ws_names["allerg"], 2)
if "salads" not in st.session_state:
    st.session_state.salads = st.session_state.df.read(ws_names["salads"], 1)

if "de_key" not in st.session_state:
    st.session_state["de_key"] = str(uuid.uuid4())

if "sp_inp_key" not in st.session_state:
    st.session_state["sp_inp_key"] = str(uuid.uuid4())

if "special_food" not in st.session_state:
    st.session_state["special_food"] = {}


res_cont = st.empty()

read_excel(guest_cont, st.session_state.allerg.iloc[:, 0], st.session_state.allerg[st.session_state.allerg.loc[:, "Kostavvikelser"].notna()].iloc[:, 1])


    # allerg_form = st.form("allerg_names", clear_on_submit=True)
    # with allerg_form:
    #     col1, col2, col3, col4 = st.columns([0.1, 0.3, 0.3, 0.3])
    #     with col1:
    #         pers_w_allerg = st.text_input(
    #             "Name: ", value=chosen_idx)
    #         name_warning = st.empty()

    #     with col2:
    #         allerg_selection = st.multiselect(
    #             "Allergier:", st.session_state.allerg.iloc[:, 0])

    #     with col3:
    #         kostavv_selection = st.multiselect(
    #             "Kostavvikelser:", st.session_state.allerg[st.session_state.allerg.loc[:, "Kostavvikelser"].notna()].iloc[:, 1])
            
    #     with col4:
    #         free_selection = st.text_input("Annat:", chosen_allergy)

    #     submit = st.form_submit_button("Add")

    #     if submit:
    #         if pers_w_allerg == "":
    #             with name_warning:
    #                 st.warning("Name missing!")
    #         else:
    #             # st.write(allerg_selection)
    #             # st.write(kostavv_selection)

    #             if "allergies" not in st.session_state.result_dict:
    #                 st.session_state.result_dict.update({"allergies": {}})
    #                 # st.write(st.session_state.result_dict)

    #             if pers_w_allerg not in st.session_state.result_dict["allergies"]:
    #                 st.session_state.result_dict["allergies"].update(
    #                     {pers_w_allerg: {"allerg": "", "kost": ""}})

    #             if allerg_selection:
    #                 st.session_state.result_dict["allergies"][pers_w_allerg].update(
    #                     {"allerg": allerg_selection})

    #             if kostavv_selection:

    #                 st.session_state.result_dict["allergies"][pers_w_allerg].update(
    #                     {"kost":  kostavv_selection})

if "expander_state_m" not in st.session_state:
    st.session_state["expander_state_m"] = False

if "expander_state_l" not in st.session_state:
    st.session_state["expander_state_l"] = False


st.markdown('<div id="lunch-top" style="color:white;">Lunch top</div>', unsafe_allow_html=True)

# x = st_javascript("(function() {window.parent.document.getElementById('top-of-expander-lunch').scrollIntoView({behavior: 'smooth'})})()")
# print(x)
with st.expander("LUNCH", expanded=st.session_state["expander_state_l"]):
    yes_lunch = st.checkbox("Servera lunch", key="SERV")
    if yes_lunch:
        st.session_state["expander_state_l"] = True
        st.success("Lunch kommer att serveras.")
        if "lunch" not in st.session_state.result_dict["meals"]:
            st.session_state.result_dict["meals"].update(
                {"lunch": {"main": {}}})
    else:
        st.error("Lunch kommer INTE att serveras.")
        st.session_state.result_dict["meals"].pop("lunch", None)


    input_main_info(yes_lunch, "lunch", "l")


    col0, col1, col2, col3 = st.columns([0.1, 0.33, 0.33, 0.33])
    tab_l1, tab_l2, tab_l3, tab_l4 = st.tabs(
        ["Lunch Sommar 2025", "Lunch Höst 2024", "Visa stora listan", "Sallad"])
    with tab_l1:
        # if col1.checkbox("Lunch Sommar 2025", key="lunch_chk1"):
        process_choice(yes_lunch, st.session_state.lunch25, "lunch",
                       "main", "Rätt", "lunch25_table", no_filter=True)


    with tab_l2:
        process_choice(yes_lunch, st.session_state.lunch24, "lunch",
                       "main", "Rätt", "lunch24_table", no_filter=True)

    with tab_l3:
        # Special index retrieval for filtered lists!!!
        process_choice(yes_lunch, st.session_state.all_dishes, "lunch",
                       "main", "Rätt", "alldishes_table", no_filter=False)

    with tab_l4:
        if st.checkbox("Sallad", key="lunch_salad"):
            salad_choices = st.multiselect(
                "Sallader:", st.session_state.salads)
            salad_mod = st.text_input("Salladurval:", ", ".join(salad_choices))
            if yes_lunch:
                if salad_choices:
                    st.session_state.result_dict["meals"]["lunch"]["salads"] = salad_mod
                else:
                    st.session_state.result_dict["meals"]["lunch"]["salads"] = "---"
                print(salad_mod)

        else:
            if yes_lunch and "salads" in st.session_state.result_dict["meals"]["lunch"]:
                st.session_state.result_dict["meals"]["lunch"].pop("salads")

        # st.form_submit_button("Spara lunch")

       # with st.expander("Specialkost lunch:", expanded=False):

    if yes_lunch:
        input_special("lunch", "main", "l")

        lunch_summary = st.form(key="lunch_summary", clear_on_submit=False)

        with lunch_summary:
            lunch_mod = st.text_area(
                "Vald lunchrätt:", value=st.session_state.result_dict["meals"]["lunch"]["main"].get("food", "---"))
            salad_mod = st.text_area("Vald sallad:", value=st.session_state.result_dict["meals"]["lunch"].get(
                "salads", "---"))
            save_btn = st.form_submit_button("Spara")
            if save_btn:
                st.session_state.result_dict["meals"]["lunch"]["main"]["food"] = lunch_mod
                st.session_state.result_dict["meals"]["lunch"]["main"]["salads"] = salad_mod

    st.markdown("<div class='btn-link'><a href='#lunch-top' target='_self' style='display: inline-block; width: 100%; text-decoration: none; text-align: center; color: black; font-weight: bold;'> ⏫ UP ⏫ </a></div>", unsafe_allow_html=True)


##################
# TODO : connect save_btn!!!
##################

# TODO: Add process_choice to middag!!!

st.markdown('<div id="middag-top" style="color:white;">Middag top</div>', unsafe_allow_html=True)

with st.expander("MIDDAG", expanded=st.session_state["expander_state_m"]):
    yes_middag = st.checkbox("Servera middag", key="SERV_M")
    if yes_middag:
        st.session_state["expander_state_m"] = True
        st.success("Middag kommer att serveras.")
        if "middag" not in st.session_state.result_dict["meals"]:
            st.session_state.result_dict["meals"].update({"middag": {}})
    else:
        st.error("Middag kommer INTE att serveras.")
        st.session_state.result_dict["meals"].pop("middag", None)

    input_main_info(yes_middag, "middag", "m")

    tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs(
        ["Förrätt", "Varmrätt", "Dessert", "Sallad + Bröd"])
    
    with tab_m1:
        if st.checkbox("Förrätt"):
            if yes_middag and "starter" not in st.session_state.result_dict["meals"]["middag"]:
                st.session_state.result_dict["meals"]["middag"]["starter"] = {}

            col0, col1, col2, col3 = st.columns([0.1, 0.33, 0.33, 0.33])

            if col1.checkbox("Kväll Sommar 2025", key="kvs25_f"):
                process_choice(yes_middag, st.session_state.kvs25.iloc[:]["Förrätt"].to_frame(), "middag", "starter", "Förrätt", "kvs25_f_f", no_filter=True)


            if col2.checkbox("Kväll Höst 2024", key="kvh24_f"):
                process_choice(yes_middag, st.session_state.kvh24.iloc[:]["Förrätt"].to_frame(), "middag", "starter", "Förrätt", "kvh24_f_f", no_filter=True)


            if yes_middag:
                input_special("middag", "starter", "ms")

        else:
            if yes_middag and "starter" in st.session_state.result_dict["meals"]["middag"]:
                st.session_state.result_dict["meals"]["middag"].pop(
                    "starter")

    with tab_m2:
        if st.checkbox("Varmrätt"):
            if yes_middag and "main" not in st.session_state.result_dict["meals"]["middag"]:
                st.session_state.result_dict["meals"]["middag"]["main"] = {}

            col0, col1, col2, col3 = st.columns([0.1, 0.33, 0.33, 0.33])

            if col1.checkbox("Kväll Sommar 2025", key="kvs25_v"):
                process_choice(yes_middag, st.session_state.kvs25.iloc[:]["Varmrätt"].to_frame(
                ), "middag", "main", "Varmrätt", "kvs25_v_f", no_filter=True)

            if col2.checkbox("Kväll Höst 2024", key="kvh24_v"):
                process_choice(yes_middag, st.session_state.kvh24.iloc[:]["Varmrätt"].to_frame(
                ), "middag", "main", "Varmrätt", "kvh24_v_f", no_filter=True)

            if yes_middag:
                input_special("middag", "main", "mm")

        else:
            if yes_middag and "main" in st.session_state.result_dict["meals"]["middag"]:
                st.session_state.result_dict["meals"]["middag"].pop("main")

    with tab_m3:
        if st.checkbox("Dessert"):
            if yes_middag and "dessert" not in st.session_state.result_dict["meals"]["middag"]:
                st.session_state.result_dict["meals"]["middag"]["dessert"] = {}
            col0, col1, col2 = st.columns([0.1, 0.45, 0.45])

            if col1.checkbox("Kväll Sommar 2025", key="kvs25_d"):
                process_choice(yes_middag, st.session_state.kvs25.iloc[:]["Dessert"].to_frame(
                ), "middag", "dessert", "Dessert", "kvs25_d_f", no_filter=True)
            # st.dataframe(kvs25.iloc[:, 3].to_frame())
            # st.dataframe(filter_dataframe(kvs25))

            if col2.checkbox("Kväll Höst 2024", key="kvh24_d"):
                process_choice(yes_middag, st.session_state.kvh24.iloc[:]["Dessert"].to_frame(
                ), "middag", "dessert", "Dessert", "kvh24_d_f", no_filter=True)
            # st.dataframe(kvh24.iloc[:, 3].to_frame())

            # with st.expander("Specialkost middag dessert:", expanded=False):
            if yes_middag:
                input_special("middag", "dessert", "md")

        else:
            if yes_middag and "dessert" in st.session_state.result_dict["meals"]["middag"]:
                st.session_state.result_dict["meals"]["middag"].pop(
                    "dessert")

    with tab_m4:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            yes_middag_salads = st.checkbox("Sallad", key="dinner_salad")
            if yes_middag_salads:
                salad_choices = st.multiselect(
                    "Sallader:", st.session_state.salads, key="dinner_salad_selection")
                salad_mod = st.text_input("Salladurval:", ", ".join( 
                    salad_choices), key="dinner_salad_selection_updated")
                if yes_middag:
                    if salad_choices:
                        if "salads" not in st.session_state.result_dict["meals"]["middag"]:
                            st.session_state.result_dict["meals"]["middag"]["salads"] = {"food": salad_mod}
                        else:
                            st.session_state.result_dict["meals"]["middag"]["salads"].update({"food": salad_mod})
                    # st.session_state.result_dict["meals"]["middag"]["salads"] = salad_mod
                    else:
                        st.session_state.result_dict["meals"]["middag"]["salads"] = {"food": "---"}

            else:
                if yes_middag and "salads" in st.session_state.result_dict["meals"]["middag"]:
                    st.session_state.result_dict["meals"]["middag"].pop("salads")

        with col_s2:
            bread_choice = st.checkbox("Bröd och smör")
            if bread_choice and yes_middag:
                st.write("Bröd och smör behövs.")
                st.session_state.result_dict["meals"]["middag"]["bread"] = True
            else:
                st.write("Bröd och smör behövs inte.")
                if yes_middag:
                    st.session_state.result_dict["meals"]["middag"]["bread"] = False

        if yes_middag and yes_middag_salads:
            input_special("middag", "salads", "msal")

    #st.link_button("[Middag top]", url='#middag-top', )
    st.markdown("<div class='btn-link'><a href='#middag-top' target='_self' style='display: inline-block; width: 100%; text-decoration: none; text-align: center; color: black; font-weight: bold;'> ⏫ UP ⏫ </a></div>", unsafe_allow_html=True)
    

    # if st.button("Scroll up", key="scroll_up_m"):
    #     # Inject JS to scroll to anchor
    #     st.session_state["scroll_to_expander_m"] = True
    #     # if "expander_state" not in st.session_state:
    #     st.session_state["expander_state_m"] = True

        #st.rerun()

    # if st.session_state.scroll_to_expander_m:
    #    # js_test = st_javascript("window.parent.document.getElementById('top-of-expander-middag').scrollIntoView({behavior: 'smooth'});")
    #     #st.markdown({js_test})
    #     st.session_state.scroll_to_expander_m = False  # reset it so it only scrolls once


# st.write(st.session_state.result_dict)
# print(st.session_state.result_dict)

# https://docs.gspread.org/en/latest/api/models/worksheet.html#gspread.worksheet.Worksheet.merge_cells

# if st.checkbox("Merge"):
#     st.session_state.upd_conn.merge_cells("A9:B9")



def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (time)):
        return obj.strftime("%H:%M:%S")
    return str(obj)
    # raise TypeError ("Type %s not serializable" % type(obj))


if st.button("To JSON"):
    with open("result.json", "w", encoding="utf-8") as json_file:
        json.dump(st.session_state.result_dict, json_file,
                  indent=4, default=json_serial, ensure_ascii=False)

if st.button("From JSON"):
    with open("result.json", "r", encoding="utf-8") as json_file:
        st.session_state["result_dict_loaded"] = json.load(json_file)
        st.write(st.session_state.result_dict_loaded)

if st.button("Delete JSON"):
    st.session_state.pop("result_dict_loaded")


def prep_special(data_dict, meal_type):
    data_special = []
    special_rows = 0
    new_dict = {}

    if data_dict[meal_type].get("special_food"):
        for k, v in data_dict[meal_type]['special_food'].items():
            vv = ", ".join(v)
            if vv not in list(new_dict.keys()):
                new_dict[vv] = k
            else:
                new_dict.update({vv: f"{new_dict[vv]}, {k}"})
        print(" #  # #  special ", new_dict)
        for v, k in new_dict.items(): # data_dict[meal_type]['special_food'].items():
            data_special.append([k, v])
            special_rows += 1
    return data_special, special_rows


if st.button("Write to sheet"):
   # st.dataframe(st.session_state.upd_conn.read())
    # st.session_state.upd_conn.write("Inmatning", [result, result, result], 1)
    if "result_dict_loaded" in st.session_state:
        res_dict = st.session_state["result_dict_loaded"]
    else:
        res_dict = st.session_state.result_dict
    weekdays = {0: "Måndag", 1: "Tisdag", 2: "Onsdag",
                3: "Torsdag", 4: "Fredag", 5: "Lördag", 6: "Söndag"}
    event_date = pd.Timestamp(
        res_dict["date"]).to_pydatetime().date()
    event_weekday = weekdays[pd.Timestamp(
        res_dict["date"]).to_pydatetime().weekday()]
    event_week = pd.to_datetime(
        pd.Series(res_dict["date"])).dt.isocalendar().week
    print(event_week)
    cell_names = {"header": "A1",
                  "amount_and_date": "A2",
                  "slot_header": "A3",
                  "start_col": "A",
                  "end_col": "B",
                  "start_row": 5,
                  }
    base_data = [{
        "range": cell_names["header"],
        "values":
        [[f"{res_dict["venue"]} {res_dict["customer_name"]}"]]
    },
        {"range": cell_names["amount_and_date"], "values": [
            [f"Antal pers: {res_dict["amount_guests"]}{" " * 20}Datum: {str(event_date)} - {event_weekday} - v{event_week[0]}"]]},
    ]
    row_count = 0
    special_rows = 0
    header_ranges = ['A1', 'A2']
    daytime_headers = []
    special_row_format = []

    # if "förmiddag" in res_dict["meals"]:
    #     data_dict = res_dict["meals"]["förmiddag"]
    #     base_data.extend([{"range": "A3", "values": [[f'Förmiddag\n\nAntal pers: {data_dict["amount_guests"]}       Avgångstid fr BriQ: {str(data_dict["leave_bq"])[:5]}       Serveringstid: {str(data_dict["serve_time"])[:5]}\n']]},
    #                       {"range": f'{cell_names["start_col"]}{cell_names["start_row"]}', "values": [
    #                           [f"Fika: {data_dict["amount_guests"] - data_dict.get("amount_special", 0)} pers.", data_dict["food"]],
    #                           [f"Special:\n{'\n'.join([i for i in data_dict['special'].values()]) if data_dict.get('special') else '---'}"]]},
    #                       ])
    #     row_count += 4
    #     header_ranges.append("A3")
    print(" DICT: ", res_dict)
    if "lunch" in res_dict["meals"]:
        data_dict = res_dict["meals"]["lunch"]
        data_special, special_rows = prep_special(data_dict, "main")

        base_data.extend([{"range": "A4", "values": [[f'Lunch\n\nAntal pers: {data_dict["amount_guests"]}{" " * 7}Avgångstid fr BriQ: {str(data_dict["leave_bq"])[:5]}       Serveringstid: {str(data_dict["serve_time"])[:5]}\n']]},
                          {"range": f'{cell_names["start_col"]}{cell_names["start_row"] + row_count}', "values": [
                              [f"Varmrätt: {data_dict["amount_guests"] - data_dict["main"].get("amount_special", 0)} pers.", data_dict["main"]["food"]],
                              ["Sallader:", data_dict.get("salads", "---")],
                              [f"Special:"]]}, #\n{'\n'.join([i for i in data_dict['main']['special_food'].keys()]) if data_dict['main'].get('special_food') else '---'}", data_special],], },

                          {"range": "A8:B", "values": data_special},

                          ])
        special_row_format.append(f"A7:B{7 + special_rows}")
        daytime_headers.append("A4")
        row_count += 6 + special_rows

    if "middag" in res_dict["meals"]:
        data_dict = res_dict["meals"]["middag"]
        current_row = 3 + row_count
        row_count = current_row
        base_data.extend([{"range": f'{cell_names["start_col"]}{current_row}', "values": [[f'Middag\n\nAntal pers: {data_dict["amount_guests"]}{" " * 7}Avgångstid fr BriQ: {str(data_dict["leave_bq"])[:5]}       Serveringstid: {str(data_dict["serve_time"])[:5]}\n']]},])
        middag_values = []

        if "starter" in data_dict:
            data_special, special_rows = prep_special(data_dict, "starter")
            starter_data = [[f"Förrätt: {data_dict["amount_guests"] - data_dict['starter'].get("amount_special", 0)} pers.", data_dict["starter"]["food"]],
                            [f"Special:"],
                            ]
            row_count += 2
            special_row_format.append(f"A{row_count}:B{row_count + special_rows}")
            starter_data.extend(data_special)
            middag_values.extend(starter_data)

            row_count += special_rows

        if "main" in data_dict:
            data_special, special_rows = prep_special(data_dict, "main")
            main_data = [[f"Varmrätt: {data_dict["amount_guests"] - data_dict["main"].get("amount_special", 0)} pers.", data_dict["main"]["food"]],
                         [f"Special:"],
                         ]
            row_count += 2
            
            special_row_format.append(f"A{row_count}:B{row_count + special_rows}")

            main_data.extend(data_special)
            middag_values.extend(main_data)

            row_count += special_rows
        
        if "dessert" in data_dict:
            data_special, special_rows = prep_special(data_dict, "dessert")
            dessert_data = [[f"Dessert: {data_dict["amount_guests"] - data_dict["dessert"].get("amount_special", 0)} pers.", data_dict["dessert"]["food"]],
                         [f"Special:"],
                         ]
            row_count += 2
            
            special_row_format.append(f"A{row_count}:B{row_count + special_rows}")
            
            dessert_data.extend(data_special)
            middag_values.extend(dessert_data)

            row_count += special_rows

        middag_values.extend([["Bröd och smör:", f"{'Ja' if res_dict["meals"]["middag"]["bread"] else '---'}"]])

        if "salads" in data_dict:
            data_special, special_rows = prep_special(data_dict, "salads")

            salad_data = [["Sallader:", data_dict["salads"]["food"]],
                         [f"Special:"],
                         ]
            row_count += 3
            special_row_format.append(f"A{row_count}:B{row_count + special_rows}")
            
            salad_data.extend(data_special)
            middag_values.extend(salad_data)

            row_count += special_rows

        base_data.extend([{"range": f'{cell_names["start_col"]}{current_row + 1}:{cell_names["end_col"]}', "values": middag_values}])
        daytime_headers.append(f'{cell_names["start_col"]}{current_row}')

        row_count += 2

    st.session_state.upd_conn.write_range(
        "Resultat", base_data)
    st.session_state.upd_conn.merge_cells(header_ranges, daytime_headers)
    st.session_state.upd_conn.center_text(header_ranges, daytime_headers, special_row_format)

   # st.dataframe(st.session_state.upd_conn.read())

   # st.dataframe(st.session_state.df.read("Resultat", 10))

    # st.cache_data.clear()
    # st.rerun()
# st.dataframe(res_dict["meals"])
