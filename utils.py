import os
import json
from pathlib import Path
import re
import uuid
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from datetime import datetime
import xlsxwriter
from xlsxwriter.utility import xl_cell_to_rowcol


def filter_dataframe(df: pd.DataFrame, qkey) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # modify = st.checkbox("Add filters")

    # if not modify:
    #     return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()
    print(df.columns)
    with modification_container:
        to_filter_columns = st.multiselect(
            "Filter by:", ["Proteintyp", "Köttyp", "Rätt"], key=f"filter_{qkey}")
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Include {column}:",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Include {column}:",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Include {column}:",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(
                        map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Word to include",
                )
                exclude_input = right.text_input(
                    f"Word to exclude",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]
                if exclude_input:
                    df = df[df[column].str.contains(
                        f"^((?!.*{exclude_input}.*).)*$")]

    return df


def show_df_with_checkboxes(df, column_name, qkey, no_filter=False, allow_delete=False, column_order=None, hide_index=True):
    if "choose" not in df:
        df.insert(0, "choose", [False] * len(df.index), True)
    if "idx_key" not in df and not no_filter:
        df.insert(0, "idx_key", list(df.index), True)
    column_config = {
            "choose": st.column_config.CheckboxColumn(
                column_name,
                help="Select a meal",
                default=False,
                width=60,
                pinned=True,
            ),
            "idx_key": st.column_config.NumberColumn(
                "Global index",
                default=False,
                width=70,
                pinned=False,
            )
        }

    df_upd = st.data_editor(
        df if no_filter else filter_dataframe(df, qkey),
        column_config=column_config,
        column_order=("choose", "Rätt", "Proteintyp",
                      "Köttyp") if not no_filter else column_order,
        hide_index=hide_index,
        num_rows="dynamic" if allow_delete else "fixed",
        key=qkey,
        on_change=lambda: st.session_state.update({"current_tab": qkey})
        )

    return df_upd


def show_editable_df(df, column_name, qkey, no_filter=False, allow_delete=True, column_order=None):
 
    df_upd = st.data_editor(
        df if no_filter else filter_dataframe(df, qkey),
        column_order=column_order,
        hide_index=True,
        num_rows="dynamic" if allow_delete else "fixed",
        key=qkey,
        on_change=check_val,
    )
    return df_upd


def check_val():
    st.session_state["warn_change"] = "Don't forget to save!"


def process_choice(daytime_checked, df, daytime, meal_type, col_name, df_filter_name, no_filter=False):
    print(df.columns)
    df_upd = show_df_with_checkboxes(
        df, f"choose_{meal_type}", df_filter_name, no_filter)
    # if st.session_state[df_filter_name]["edited_rows"]:
    #     st.write(st.session_state[df_filter_name]["edited_rows"])

    if len(df_upd) and df_upd.loc[:, "choose"].max():   # shows true or false
        chosen_one = df_upd.loc[:, "choose"].idxmax()
        if df_upd.loc[:, "choose"].value_counts().get(True) > 1:
            st.error("You selected more than one meal in this list, please unselect one!")
        if no_filter:
            chosen_meal = df_upd.iloc[chosen_one][col_name]
        else:
            chosen_meal = df_upd[df_upd.loc[:, "idx_key"]
                                 == chosen_one].iloc[0][col_name]
        st.write(chosen_meal)
       # st.session_state["tab_dict"][df_filter_name] = True
        st.session_state["tab_dict"][daytime][meal_type][df_filter_name] = True
        if sum([v for k, v in st.session_state["tab_dict"][daytime][meal_type].items()]) > 1:
            st.error("You selected meals in more than one list, please unselect one!")


        if daytime_checked:
            if meal_type not in st.session_state.result_dict["meals"][daytime]:
                st.session_state.result_dict["meals"][daytime][meal_type] = {
                    "food": chosen_meal}
            else:
                st.session_state.result_dict["meals"][daytime][meal_type].update(
                    {"food": chosen_meal})
    else:
        # st.session_state["tab_dict"][df_filter_name] = False
        st.session_state["tab_dict"][daytime][meal_type][df_filter_name] = False
        if not any([v for k, v in st.session_state["tab_dict"][daytime][meal_type].items()]) and daytime_checked:
            st.session_state.result_dict["meals"][daytime][meal_type]["food"] = "[Ingen maträtt vald]"
            #st.warning("STUFF")


def convert_time(time):
    return datetime.strptime(time, '%H:%M:%S')


def input_main_info(daytime_checked, daytime, key_char):
    default_times = {"l": [convert_time('11:00:00'), convert_time('12:00:00')],
                     "m": [convert_time('17:45:00'), convert_time('19:00:00')], }
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        guest_amount = st.number_input(
            "Antal personer:", value=st.session_state[f'guest_amount_{st.session_state["guest_key"]}'], format="%i", step=1,  key=f"guest_amount_{key_char}")
        if daytime_checked:
            st.session_state.result_dict["meals"][daytime].update(
                {"amount_guests": st.session_state[f"guest_amount_{key_char}"]})
    with col2:
        leave_bq = st.time_input(
            "Avg. fr BriQ:", value=default_times[key_char][0], key=f"leave_bq_{key_char}")
    with col3:
        serve_time = st.time_input(
            "Serveringstid:", value=default_times[key_char][1], key=f"serve_time_{key_char}")
        if daytime_checked:
            st.session_state.result_dict["meals"][daytime].update({"leave_bq": st.session_state[f"leave_bq_{key_char}"],
                                                                   "serve_time": st.session_state[f"serve_time_{key_char}"]})


KOST_STRINGS = {"Pescetarian": "Pesc", "Vegetarianer": "Veg", "Vegan": "Vegan"}


def format_allergy_string(allerg, return_str=False):
    # Cut off icon, add minus and abbreviate Veg/Pesc
    if allerg["kost"]:
        s_full, s_mid, s_end = [], [], []
        for i in allerg["kost"]:
            if i[-1] == "🔴":
                k = i[:-1].strip()
                s_end.append(f"-{k}")
            elif i[-1] == "🟢":
                k = i[:-2].strip()
                s_mid.append(f"+{k}")
            else:
                k = i[:-2].strip()
                s_full.append(KOST_STRINGS[k])
            print(" ########################## IMPORTANT", k)
        s_full.extend(sorted(s_mid))
        s_full.extend(sorted(s_end))
        # st.session_state.result_dict["allergies"]["kost_formatted"] = s_front
        # print(st.session_state.result_dict["allergies"]["kost_formatted"])
    else:
        s_full = ""
    if return_str:
        res = ""
        for st in [", ".join(sorted(list(map(lambda x: f"-{x}", allerg["allerg"])))), ", ".join(s_full), allerg["extra"]]:
            if st and not res:
                res = st
            elif st:
                res += ", " + st
        return  res # ", ".join([", ".join(sorted(list(map(lambda x: f"-{x}", allerg["allerg"])))), ", ".join(s_full), allerg["extra"]])
    else:
        return {"Allergier": ", ".join(sorted(list(map(lambda x: f"-{x}", allerg["allerg"])))), "Kostavvikelser": ", ".join(s_full), "Extra": allerg["extra"]}


def input_special(daytime, meal_type, key_char):
    if not st.session_state.result_dict.get("allergies"):
        return

    if not st.session_state.result_dict["meals"][daytime][meal_type].get("amount_special"):
        st.session_state.result_dict["meals"][daytime][meal_type]["amount_special"] = len(
            st.session_state.result_dict["allergies"])

    def update_amount_special(new_spec_amount):
            with new_spec_amount:
                return st.number_input(label=f"Personer med specialkost för {daytime} {meal_type}:", value=st.session_state.result_dict[
                                            "meals"][daytime][meal_type]["amount_special"], key=f"input_amount_special_{key_char}_{st.session_state["sp_amount_key"]}", label_visibility="collapsed")

 #   with st.form(f"{daytime}_{key_char}_specialkost", clear_on_submit=True):
        # if "allergies" in st.session_state.result_dict:
        #     pers_amount = len(st.session_state.result_dict["allergies"])
        # else:
        #     pers_amount = 0
    col_num1, col_num2 = st.columns([0.1, 0.9])
    current_allerg = []
    current_kost = []
    new_df = {}
    st.session_state["summary_allerg"] = {}
    current_avv = ""
    if "allergies" in st.session_state.result_dict:
        for pers, allerg in st.session_state.result_dict["allergies"].items():
            formatted_dict = format_allergy_string(allerg)

            # {"Allergier": ", ".join(sorted(allerg["allerg"])), "Kostavvikelser": ", ".join(
            new_df[pers] = formatted_dict
            # sorted(allerg["kost"])), "Extra": allerg["extra"]}
            current_allerg.extend(allerg["allerg"])
            current_kost.extend(allerg["kost"])
            extra_info = formatted_dict["Extra"]
            current_avv = ""
            for f_str in [formatted_dict["Kostavvikelser"], formatted_dict["Allergier"], extra_info]:
                if not current_avv and f_str:
                    current_avv = f_str
                else:
                    if f_str:
                        current_avv += ", " + f_str
            if current_avv in st.session_state["summary_allerg"]:
                st.session_state["summary_allerg"][current_avv] += 1
            else:
                st.session_state["summary_allerg"][current_avv] = 1
        print("######## Summary :", st.session_state["summary_allerg"])
        '''
        col1, col2, col3 = st.columns([0.2, 0.4, 0.4])
        with col1:
            pers_all = st.number_input(
            "Antal personer med allergier/kostavvikelser:", value=pers_amount, format="%i", step=1,  key=f"pers_amount_{key_char}")
        with col2:
            allerg_multi = st.multiselect("Allergier:", set(sorted(current_allerg)))
        with col3:
            kost_multi = st.multiselect("Kostavvikelser:", set(sorted(current_kost)))
        submit = st.form_submit_button("Add")
        
        if submit:
            st.session_state.result_dict["meals"][daytime]["amount_special"] += pers_all
            if "special" in st.session_state.result_dict["meals"][daytime]:
                next_idx = max(list(st.session_state.result_dict["meals"][daytime]["special"].keys())) + 1
                st.session_state.result_dict["meals"][daytime]["special"].update({next_idx: f"{pers_all} p. {"-" + ", -".join(allerg_multi) + f'{" || " + ", ".join(kost_multi) if kost_multi else ""}'  if allerg_multi else ", ".join(kost_multi)}"})
            else:
                st.session_state.result_dict["meals"][daytime]["special"] = ({0: f"{pers_all} p. {"-" + ", -".join(allerg_multi) + f'{" || " + ", ".join(kost_multi) if kost_multi else ""}' if allerg_multi else ", ".join(kost_multi)}"})
        '''

    col_df_1, col_df_2 = st.columns(2)
    col_df_3, col_df_4 = st.columns(2)

    with col_df_1:
        st.write("Översikt specialkost:")
        
        allerg_df = pd.DataFrame(new_df).astype("str").T
        st.dataframe(allerg_df)
    new_special = col_df_3.info(
        f"Personer med specialkost: **{len(st.session_state.result_dict["allergies"])}**")

    with col_df_2:
        st.write("Sammanfattning:")
        
        allerg_sum_cont = st.empty()

        with allerg_sum_cont:
           # st.session_state["de_key"] = str(uuid.uuid4())
            # if "sum_df_upd" not in st.session_state:
            st.session_state["sum_df_upd"] = show_allerg_summary(
                st.session_state["summary_allerg"], f"{daytime}_{key_char}_{st.session_state["de_key"]}")
            # else:
            #     #st.session_state["de_key"] = str(uuid.uuid4())
            #     st.dataframe(st.session_state["sum_df_upd"])
            #     st.session_state["sum_df_upd"] = show_allerg_summary(st.session_state["summary_allerg"], f"{daytime}_{key_char}_{st.session_state["de_key"]}")
            #     #st.dataframe(st.session_state["sum_df_upd"])
    with col_df_4:
        col_am1, col_am2, _ = st.columns([0.6, 0.3, 0.1])
        col_am1.info(f"Personer med specialkost för {daytime} {meal_type}: ")
        with col_am2:    
            new_spec_amount = st.empty()
            new_special = update_amount_special(new_spec_amount)
        
        _, col_btn_1, col_btn_2 = st.columns([0.3, 0.35, 0.35])
    
        change_warning = st.empty()
        if st.session_state["warn_change"]:
            change_warning.error(st.session_state["warn_change"])
        else:
            change_warning.empty()
        # else:
        #     st.session_state["warn_change"].write("HALLO")

        save_allerg = col_btn_1.button(
            "Spara", key=f"save_special_{daytime}_{key_char}")
        reset_button = col_btn_2.button(
            "Reset", key=f"reset_special_{daytime}_{key_char}")
    if save_allerg:
        st.session_state["warn_change"] = None
        change_warning.empty()

        st.session_state.result_dict["meals"][daytime][meal_type]["amount_special"] = update_allergy_summary(
            daytime, meal_type, new_special, st.session_state["sum_df_upd"])
        new_spec_amount.empty()
        st.session_state["sp_amount_key"] = str(uuid.uuid4())
        new_special = update_amount_special(new_spec_amount)
        if st.session_state["warn_not_saved"]:
            change_warning.error(st.session_state["warn_not_saved"])
        else:
            col_btn_1.success("Sparad!")

    if reset_button:
        st.session_state["de_key"] = str(uuid.uuid4())
        allerg_sum_cont.empty()

        with allerg_sum_cont:
            st.session_state["sum_df_upd"] = show_allerg_summary(
                st.session_state["summary_allerg"], f"{daytime}_{key_char}_{st.session_state["de_key"]}")
        st.session_state.result_dict["meals"][daytime][meal_type]["amount_special"] = update_allergy_summary(
            daytime, meal_type, new_special, st.session_state["sum_df_upd"])
        new_spec_amount.empty()
        st.session_state["sp_amount_key"] = str(uuid.uuid4())
        new_special = update_amount_special(new_spec_amount)
        
    # special_food_list = pd.DataFrame({"entry": [e for e in st.session_state.result_dict["meals"][daytime]["special"].values()]})

    if st.session_state.result_dict["meals"][daytime].get("special"):
        st.write(f"##### Urval specialkost ({daytime} {meal_type}):")

        if not st.session_state.result_dict["meals"][daytime][meal_type].get("special_food"):
            st.session_state.result_dict["meals"][daytime][meal_type]["special_food"] = {
            }

        for x, e in enumerate(st.session_state.result_dict["meals"][daytime]["special"].values()):
            with st.container():
                col_meal_1, col_meal_2, col_meal_3 = st.columns(
                    [0.4, 0.2, 0.4])
                spec_ok = col_meal_2.checkbox(
                    "Klar", key=f'spec_food_ok_{key_char}_{e}')
                if spec_ok:
                    col_meal_1.success(f"-  {e}", icon="✅")
                else:
                    col_meal_1.markdown(
                        f"<div class='special-entry-warning'>⚠️  {e}</div>", unsafe_allow_html=True)
                same_select = []
                same_select.extend(
                    [el for el in st.session_state.result_dict["meals"][daytime]["special"].values() if el != e])
                # if same_select:
                #     col_meal_1.selectbox("Samma kost som:", same_select, key=f'same_as_select_{key_char}_{e}', placeholder="Choose...", index=None)
                if meal_type in st.session_state.result_dict["meals"][daytime]:
                    if st.session_state.result_dict["meals"][daytime][meal_type].get("salads"):
                        salad_str = st.session_state.result_dict["meals"][daytime][meal_type]["salads"]
                    else:
                        salad_str = None
                    if st.session_state.result_dict["meals"][daytime][meal_type].get("cake"):
                        cake_str = f"Lunchkaka"
                    else:
                        cake_str = None
                    if st.session_state.result_dict["meals"][daytime][meal_type].get("bread"):
                        bread_str = "Bröd och smör"
                    else:
                        bread_str = None

                if meal_type == "extras":
                    hint_str = f"{'<br>'.join(pd.Series([salad_str, cake_str, bread_str]).dropna())}"
                else:
                    hint_str = st.session_state.result_dict["meals"][daytime][meal_type].get("food", "[Ingen maträtt vald]")

                col_meal_3.markdown(
                    f"<div class='custom-info'>{hint_str}</div>", unsafe_allow_html=True)

                sf_result = col_meal_2.empty()
            print(st.session_state.get(f"same_as_select_{key_char}_{e}", None))

            # if not st.session_state.result_dict["meals"][daytime][meal_type].get("special_food"):
            #     st.session_state.result_dict["meals"][daytime][meal_type]["special_food"] = {e: []}
            # else:
            if not st.session_state.result_dict["meals"][daytime][meal_type]["special_food"].get(e):
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = [
                ]
           # st.dataframe(show_special_selection(x))
            
            with st.form(key=f"form_special_selection_{key_char}_{e}", clear_on_submit=True):
                col_s1, col_s2, col_s3, col_s4 = st.columns(
                    [0.3, 0.3, 0.3, 0.1])
                with col_s1:
                    hur = " ".join(list(st.multiselect("Maträtt:", st.session_state["alternatives"]["adj"], placeholder="Glutenfri...", key=f'spec_food_select_adj_{key_char}_{e}'))).strip()
                # with col_s2:
                    vad = " ".join(list(st.multiselect("Vad:", st.session_state["alternatives"]["noun"], placeholder="biff...", label_visibility='collapsed', key=f'spec_food_select_noun_{key_char}_{e}'))).strip()
                with col_s2:
                    if same_select:
                        st.selectbox("Samma kost som:", same_select,
                                     key=f'same_as_select_{key_char}_{e}', placeholder="Choose...", index=None)
                        extra_label = 'collapsed'
                    else:
                        extra_label = 'visible'
                    extra = str(st.text_input("Extra:", label_visibility=extra_label,
                                placeholder="Fritext", key=f'spec_food_select_free_{key_char}_{e}')).strip()
                with col_s3:
                    save_special_select_btn = st.form_submit_button("Spara")


            col_sp1, col_sp2 = st.columns([0.6, 0.4])
            with col_sp1:
                chosen_special_cont = st.empty()
                spec_food_result = chosen_special_cont.text_input(f"Vald kost till {e}:", value="; ".join(
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]), key=f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}")
            with col_sp2:
                updd = col_sp2.button(
                    "Uppdatera", key=f"special_food_result_upd_{key_char}_{e}")
                if updd:
                    st.success("Uppdaterad!")
                    if st.session_state[f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}"] == "":
                        st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = [
                        ]
                    else:
                        st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = sorted(list(filter(None, set(str(
                            st.session_state[f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}"]).strip().split("; ")))))
                        # print(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])
                        st.session_state["sp_inp_key"] = str(uuid.uuid4())

                        chosen_special_cont.empty()
                        chosen_special_cont.text_input(
                            f"Vald kost till {e}:", value=f"{'; '.join(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])}", key=f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}")


            if save_special_select_btn:
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e].append(
                    " ".join([hur, vad, extra]).strip())
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = sorted(list(
                        filter(None, set(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]))))
                # st.dataframe(pd.DataFrame(st.session_state["special_food"], index=range(len(st.session_state["special_food"]))).T)
                special_to_copy = st.session_state.get(
                    f"same_as_select_{key_char}_{e}", False)
                same_food = []
                if special_to_copy:
                    same_food = st.session_state.result_dict["meals"][
                        daytime][meal_type]["special_food"][special_to_copy]
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e].extend(
                        same_food)
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = sorted(list(
                        filter(None, set(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]))))
                if st.session_state.get(f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}", False):
                    food_string = "; ".join(sorted(list(set(st.session_state[f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}"].strip(
                    ).split("; ") + st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]))))
                else:
                    food_string = "; ".join(
                        st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])

                st.session_state["sp_inp_key"] = str(uuid.uuid4())
                chosen_special_cont.empty()
                spec_food_result = chosen_special_cont.text_input(
                    f"Vald kost till {e}:", value=food_string, key=f"special_food_result_{key_char}_{e}_{st.session_state['sp_inp_key']}")


#            spec_food_result = st.text_input(f"Vald kost till {e}:", value=f'{"; ".join(food_string)}', key=f"special_food_result_{key_char}_{e}")
            if not spec_food_result:
                sf_result.html(
                    "<span style='color: red;'>... specialkost ej vald ...</span>")
            elif spec_ok:
                sf_result.empty()
            else:
                sf_result.html(
                    "<span style='color: #B9C60B;'>... urval av specialkost påbörjat ...</span>")

            st.divider()


def show_allerg_summary(summary_allerg, qkey):
    sum_df = pd.DataFrame({"entry": [f"{v} p. {k}" for k, v in sorted(
        summary_allerg.items())]}, index=range(0, len(summary_allerg)))
    # sum_df_upd = show_df_with_checkboxes(sum_df, f"choose_allerg", "summary_allerg", True)
    sum_df_upd = show_editable_df(
        sum_df, f"choose_allerg", f"summary_allerg_{qkey}", no_filter=True, allow_delete=True)
    return sum_df_upd


def update_allergy_summary(daytime, meal_type, new_special, sum_df_upd):
    # Check if allergy summary entry exists in special_food and delete those deleted here:
    if st.session_state.result_dict["meals"][daytime][meal_type].get("special_food"):
        for e in list(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"].keys()):
            if e not in list(sum_df_upd.loc[:, "entry"]):
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"].pop(
                    e)
#            for idx, entry in zip(list(sum_df_upd.index), list(sum_df_upd.loc[:, "entry"])):
    st.session_state.result_dict["meals"][daytime]["special"] = {
        idx: entry for idx, entry in zip(list(sum_df_upd.index), list(sum_df_upd.loc[:, "entry"]))}

    # for s in list(sum_df_upd.loc[:, "entry"]):
    #     match = re.match(r"\d+", s)
    #     print(match.group() if match else "No match")
    try:
        calc_sum = sum_df_upd["entry"].str.extract(r"^(\d+)").astype(int).sum()
        st.session_state.result_dict["meals"][daytime][meal_type]["amount_special"] = int(
        calc_sum.iloc[0])
        result = int(calc_sum.iloc[0])
        st.session_state["warn_not_saved"] = None

    except:
        st.session_state["warn_not_saved"] = "Please make sure every entry starts with a number."
        result = 0

    
    return result


def remove_default(allergies_list):
    result = []
    for el in allergies_list:
        if el in ["Nej", "nej", "-", "--", "---", "", "[empty]", "Inga allergier", "inga allergier", "inga", "Inga"]:
            result.append(el)
    return result


def place_minuses(x):
    return "-" if x.lower() in ["ej", "inte", "ingen", "inget"] else f"{x} "


def get_allerg_def(pers_w_allerg, spec_type):
    if spec_type == "extra":
        # key = f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}"
        processed_extra = st.session_state.result_dict["allergies"][pers_w_allerg][spec_type]
        if processed_extra and st.session_state[f"copy_allerg_{pers_w_allerg}"]:
            processed_extra = "".join(
                list(map(place_minuses, processed_extra.split(" ")))).strip()
        return processed_extra
    else:
        key = f"{spec_type}_multiselect_{pers_w_allerg}"
    if key in st.session_state:
        return None
    else:
        return st.session_state.result_dict["allergies"][pers_w_allerg][spec_type]


def read_excel(guest_cont, allerg_select, kostavv_select):

    # TODO: Manual entering of allergy data!
    # TODO: Adjust excel reading if neded!


    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file:
        df_raw = pd.ExcelFile(uploaded_file)

        with st.container(border=True):
            if "raw_file_toggle" not in st.session_state:
                st.session_state["raw_file_toggle"] = False
            col1, col2 = st.columns([0.2, 0.8])
            # hide_file = col2.button("Hide file")
            # show_file = col1.button("Show file")
            toggle_file = col1.toggle("Show source file")
            full_file = st.empty()

            if toggle_file:
                df_full = pd.read_excel(uploaded_file, sheet_name=0, header=None, usecols=list(range(
                    0, df_raw.book['Blad1'].max_column)), skiprows=0, nrows=df_raw.book['Blad1'].max_row)
                full_file.dataframe(df_full)

            else:
                full_file.empty()

        df = pd.read_excel(uploaded_file, sheet_name=0, header=None, usecols=list(range(
            0, df_raw.book['Blad1'].max_column)), skiprows=6, nrows=df_raw.book['Blad1'].max_row - 15)
        df_upd = (df[df.iloc[:, 7].notna()])
        df_upd = df_upd.rename(
            columns={0: "Nr", 7: 'Allergier', 8: 'Extra info'})
        df_upd = df_upd.set_index('Nr')
        guest_cont.empty()
        with guest_cont:
            st.session_state["guest_key"] = str(uuid.uuid4())
            if st.session_state.result_dict["amount_guests"] == 0:
                st.session_state.result_dict["amount_guests"] = int(df_upd.index.max())
            guest_amount = st.number_input(
                "Antal personer:", value=st.session_state.result_dict["amount_guests"], format="%i", step=1,  key=f"guest_amount_{st.session_state["guest_key"]}")

        with st.expander("Allergier:", expanded=True):

            st.markdown("##### Extracted data:")
            extr_amount = st.empty()
            df_upd = show_editable_df(df_upd, f"_raw", f"summary_allerg_raw", no_filter=True,
                             allow_delete=True, column_order=('Nr', '1', '2', 'Allergier', 'Extra info'))
            extr_amount.markdown(
                f'<span style="font-size: 18px; background-color: yellow;"><b>{len(df_upd)}</b> personer med anmärkningar hittad</span>', unsafe_allow_html=True)
            # with st.form("remove entries", clear_on_submit=False):
            st.markdown("##### Sammanställning av allergier")
            allergies_list = list(map(lambda x: x if x != "" else "[empty]", sorted(
                list(set([x.strip() for x in df_upd.loc[:, 'Allergier']])))))
            st.markdown(
                f'<span style="font-size: 16px;">Ta bort följande:</span>', unsafe_allow_html=True)
            del_selection = st.multiselect(
                "Ta bort följande:", allergies_list, default=remove_default(allergies_list), label_visibility="collapsed")
        # del_entries = st.form_submit_button("Ta bort")
            if del_selection:
                del_selection = map(lambda x: x.replace(
                    "[empty]", "",), del_selection)
                df_upd_finished = df_upd[~df_upd['Allergier'].astype(
                    str).str.strip().isin(del_selection)]
            else:
                df_upd_finished = df_upd

            # show_editable_df(df_upd_finished, f"_raw2", f"summary_allerg_result", no_filter=True, allow_delete=True, column_order=('Nr', '1', '2', 'Allergier', 'Extra info'))

                # if "allergies" not in df_upd_finished:
                #     df_upd_finished.insert(0, "allergies", [""] * len(df_upd_finished.index), True)
            st.markdown(
                f'<span style="font-size: 18px; background-color:yellow;"><b>{len(df_upd_finished.index)}</b> personer med kostavvikelser sparad</span>', unsafe_allow_html=True)

            col_df1, col_df2, col_df3, col_df4 = st.columns(
                [0.25, 0.25, 0.25, 0.25])
            col_df1.markdown("##### Person med anmärkning")
            col_df2.markdown("##### Allergier")
            col_df3.markdown("##### Kostavvikelser")
            col_df4.markdown("##### Extra info")

            if "extra_inp_key" not in st.session_state:
                st.session_state["extra_inp_key"] = str(uuid.uuid4())

            if "allergies" not in st.session_state.result_dict:
                st.session_state.result_dict.update({"allergies": {}})

            for pers_w_allerg in df_upd_finished.index:
                if pers_w_allerg not in st.session_state.result_dict["allergies"]:
                    st.session_state.result_dict["allergies"].update(
                        {pers_w_allerg: {"allerg": [], "kost": [], "extra": ""}})

                # if f"extra_info_{pers_w_allerg}" not in st.session_state:
                #     st.session_state[f"extra_info_{pers_w_allerg}"] = ""
                col_df1, col_df2, col_df3, col_df4, col_df5 = st.columns(
                    [0.25, 0.25, 0.25, 0.2, 0.05])
                with col_df1:
                    # df_upd_finished = show_df_with_checkboxes(df_upd_finished, "column_name__", f"summary_allerg_result_2", no_filter=True, allow_delete=False, column_order=('choose', 'Allergier', 'Extra info'), hide_index=False)
                    
                    # TODO: load from json. Maybe save the person strings into json first.
                    st.write(
                        f"{pers_w_allerg} -- {df_upd_finished.loc[pers_w_allerg, 'Allergier']}")
                with col_df2:
                    allerg_selection = st.multiselect("Allergier:", allerg_select, default=get_allerg_def(
                        pers_w_allerg, "allerg"), label_visibility="collapsed", key=f"allerg_multiselect_{pers_w_allerg}")
                    if allerg_selection:
                        st.session_state.result_dict["allergies"][pers_w_allerg].update(
                            {"allerg": allerg_selection})
                    elif allerg_selection == []:
                        st.session_state.result_dict["allergies"][pers_w_allerg].update(
                            {"allerg": []})

                with col_df3:
                    kostavv_selection = st.multiselect("Kostavvikelser:", kostavv_select, default=get_allerg_def(
                        pers_w_allerg, "kost"), label_visibility="collapsed", key=f"kost_multiselect_{pers_w_allerg}")
                    if kostavv_selection:
                        st.session_state.result_dict["allergies"][pers_w_allerg].update(
                            {"kost": kostavv_selection})
                    elif kostavv_selection == []:
                        st.session_state.result_dict["allergies"][pers_w_allerg].update(
                            {"kost": []})
                with col_df4:
                    extra_info_cont = st.empty()
                    extra_info = extra_info_cont.text_input("Extra:", value=get_allerg_def(
                        pers_w_allerg, "extra"), label_visibility="collapsed", key=f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}")
                    if st.session_state[f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}"] == "":
                        st.session_state.result_dict["allergies"][pers_w_allerg].update({
                                                                                        "extra": ""})
                    else:
                        st.session_state.result_dict["allergies"][pers_w_allerg].update(
                            {"extra": st.session_state[f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}"]})

                with col_df5:
                    copy_btn = st.button(
                        "📝", key=f"copy_allerg_{pers_w_allerg}")
                    if copy_btn:
                        st.session_state.result_dict["allergies"][pers_w_allerg].update(
                            {"extra": df_upd_finished.loc[pers_w_allerg, 'Allergier']})
                        extra_info_cont.empty()
                        st.session_state["extra_inp_key"] = str(uuid.uuid4())
                        extra_info = extra_info_cont.text_input("Extra:", value=get_allerg_def(
                            pers_w_allerg, "extra"), label_visibility="collapsed", key=f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}")
                        if st.session_state[f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}"] == "":
                            st.session_state.result_dict["allergies"][pers_w_allerg].update({
                                                                                            "extra": ""})
                        else:
                            st.session_state.result_dict["allergies"][pers_w_allerg].update(
                                {"extra": st.session_state[f"extra_select_{pers_w_allerg}_{st.session_state['extra_inp_key']}"]})

            col_bt1, col_bt2 = st.columns([0.9, 0.1])
            if col_bt2.button("Klar!"):
               # write_excel()
                pers_keys = list(
                    st.session_state.result_dict["allergies"].keys())
                # xl_test = pd.DataFrame({str(k): "Test" for k, v in st.session_state.result_dict["allergies"][18].items()}, index=[0, 1, 2])
                # xl_test.style.apply(lambda x: ['text-align:right']*len(x)).to_excel("TEST.xlsx")
                # xl_test.loc[xl_test.last_valid_index() + 1] = ({str(k): v[0] for k, v in st.session_state.result_dict["allergies"][18].items()})
                # xl_test.to_excel("TEST.xlsx", startcol=5, startrow=5)
                for pers in pers_keys:
                    if pers not in list(df_upd_finished.index):
                        st.session_state.result_dict["allergies"].pop(pers)
                col_bt1.success("Allt är sparad.")

def format_special_string(text, first=False):
    if first:
        max_line = 33
    else:
        max_line = 24
    line = ""
    rest = []

    if len(text) > max_line:
        text_list = text.split(" ")
        rest = text_list[:]
        for e, word in enumerate(text_list):
            if len(line) + len(word.strip()) + 1 < max_line:
                line = f"{line + " " if line else ""}{word.strip()}"
                rest.pop(0)
            else:
                line += "\n"
                if not first:
                    line = " "*8 + line
                print(line)
                break
        return line + format_special_string(" ".join(rest))
    else:
        if not first:
            text = " "*8 + text
        return text
    

def prep_special(data_dict, meal_type, current_row, add_format):
    data_special = []
    food_data = []
    merge_data = []
    special_rows = 0
    new_dict = {}
    extra_lines = 0

    if data_dict[meal_type].get("special_food"):
        for k, v in data_dict[meal_type]['special_food'].items():
            vv = ", ".join(v)
            k_formatted = format_special_string(k, first=True)
            extra_lines = k_formatted.count('\n') + 1
            if vv not in list(new_dict.keys()):
                new_dict[vv] = {"people": k_formatted, "lines": extra_lines}
            else:
                new_dict.update({vv: {"people": f"{new_dict[vv]["people"]},\n{k_formatted}",
                                      "lines": new_dict[vv]["lines"] + extra_lines}})
        for v, k in new_dict.items(): # data_dict[meal_type]['special_food'].items():
            merge_data.append({
                "range": f"A{current_row+special_rows}:B{current_row+special_rows}",
                "values": k["people"],
                "row_height": 15 * k["lines"],
                "format": add_format("special_format", [1, 1, 2, 1])
                      })
            food_data.append({
                "range": f"C{current_row+special_rows}",
                "values": v,
                "format": add_format("special_format", [1, 1, 1, 2])
                      })
            #data_special.append([k, v])
            special_rows += 1

    return special_rows, merge_data, food_data


def prepare_excel_data(wb):

    with open("excel_formats.json", "r", encoding="utf-8") as json_file:
        formats = json.load(json_file)

    def add_format(key, borders=None):
        if borders:
            formats[key].update({"top": borders[0], "bottom": borders[1], "left": borders[2], "right": borders[3],})
        return wb.add_format(formats[key])

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
    cell_names = {"header": "A1:C1",
                "subheader": "A2:C2",
                "start_col": "A",
                "end_col": "C",
                "start_row": 4,
                }
    
    merge_data = [{
                    "range": cell_names["header"],
                    "values": f"{res_dict["customer_name"]} {res_dict["venue"]}, Dag {res_dict["day"]} Grupp {res_dict["group"]}",
                    "format": add_format("header_format"),
                    "row_height": 50,
                  },
                  {"range": cell_names["subheader"],
                   "values": f"Antal pers: {res_dict["amount_guests"]}{" " * 20}Datum: {str(event_date)} - {event_weekday} - v{event_week[0]}",
                   "format": add_format("subheader_format"),
                   "row_height": 30,
                  },

                  ]
    # base_data = [{
    #     "range": cell_names["header"],
    #     "values":
    #     f"{res_dict["customer_name"]} {res_dict["venue"]}, Dag {res_dict["day"]} Grupp {res_dict["group"]}"
    # },
    #     {"range": cell_names["subheader"], "values": f"Antal pers: {res_dict["amount_guests"]}{" " * 20}Datum: {str(event_date)} - {event_weekday} - v{event_week[0]}"},
    # ]
    base_data = []
    row_count = cell_names["start_row"]
    special_rows = 0

    if "lunch" in res_dict["meals"]:
        data_dict = res_dict["meals"]["lunch"]
        
        merge_data.extend([{"range": f'{cell_names["start_col"]}{row_count}:{cell_names["end_col"]}{row_count}',
                "values": 'Lunch',
                "format": add_format("daytime_format"),
                "row_height": 25,
            },
            {
                "range": f'{cell_names["start_col"]}{row_count + 1}:{cell_names["end_col"]}{row_count + 1}',
                "values": f"Antal pers: {data_dict["amount_guests"]}{" " * 25}Avgångstid fr BriQ: {str(data_dict["leave_bq"])[:5]}{" " * 25}Serveringstid: {str(data_dict["serve_time"])[:5]}",
                "format": add_format("daytime_subheader_format"),
                "row_height": 20,
            }
            ])
        row_count += 2

        base_data.extend([
            {
            "range": f'{cell_names["start_col"]}{row_count}',
            "values": "Varmrätt:",
                        "format": add_format("base_format_bold", [1, 1, 2, 0]),
            },
            {
            "range": f'B{row_count}',
            "values": f"{data_dict["amount_guests"] - data_dict["main"].get("amount_special", 0)} pers.",
                        "format": add_format("base_format", [1, 1, 0, 1]),
            },
            {
            "range": f'C{row_count}',
            "values": data_dict["main"]["food"],
                        "format": add_format("base_format", [1, 1, 1, 2]),
            },
            ])
        row_count += 1

        merge_data.extend([{
            "range": f'{cell_names["start_col"]}{row_count}:C{row_count}',
            "values": "Special f. varmrätt:",
                        "format": add_format("special_format_bold", [1, 1, 2, 2]),
                     "row_height": 15,

            },
             ])
        row_count += 1

        special_rows, merge_data_special, food_data  = prep_special(data_dict, "main", row_count, add_format)
        merge_data.extend(merge_data_special)
        base_data.extend(food_data)
        row_count += special_rows
        print(row_count)

        if "extras" in res_dict["meals"]["lunch"]:
            data_dict = res_dict["meals"]["lunch"]["extras"]
            extra_special = False
            
            if "salads" in data_dict and data_dict["salads"] != "---":
                merge_data.append({
                "range": f'{cell_names["start_col"]}{row_count}:B{row_count}',
                "values": "Sallader:",
                "row_height": 15,
                "format": add_format("base_format_bold", [1, 1, 2, 1]),
                })

                base_data.extend([
                {
                "range": f'C{row_count}',
                "values": data_dict["salads"],
                "format": add_format("base_format", [1, 1, 1, 2]),
                },
                ])
                row_count += 1
                print(row_count)
                extra_special = True


            if data_dict["bread"]:
                merge_data.append({
                "range": f'{cell_names["start_col"]}{row_count}:B{row_count}',
                "values": "Bröd och smör:",
                "row_height": 15,
                "format": add_format("base_format_bold", [1, 1, 2, 1]),
                })

                base_data.extend([
                {
                "range": f'C{row_count}',
                "values": "Ja",
                            "format": add_format("base_format", [1, 1, 1, 2]),
                },
                ])
                row_count += 1
                print(row_count)
                extra_special = True

            if data_dict["cake"]:
                merge_data.append({
                "range": f'{cell_names["start_col"]}{row_count}:B{row_count}',
                "values": "Lunchkaka:",
                "row_height": 15,
                "format": add_format("base_format_bold", [1, 1, 2, 1]),
                })

                base_data.extend([
                {
                "range": f'C{row_count}',
                "values": "Ja",
                            "format": add_format("base_format", [1, 1, 1, 2]),
                },
                ])
                row_count += 1
                print(row_count)
                extra_special = True

            merge_data.extend([
                {
                "range": f'{cell_names["start_col"]}{row_count}:C{row_count}',
                "values": "Special:",
                            "format": add_format("special_format_bold", [1, 1, 2, 2]),
                        "row_height": 15,
                },
                ])
            row_count += 1

            if extra_special:
                special_rows, merge_data_special, food_data  = prep_special(res_dict["meals"]["lunch"], "extras", row_count, add_format)
                merge_data.extend(merge_data_special)
                base_data.extend(food_data)
                row_count += special_rows + 1

        # special_row_format.append(f"A7:B{7 + special_rows}")
        # daytime_headers.append("A4")

    if "middag" in res_dict["meals"]:
        data_dict = res_dict["meals"]["middag"]

        merge_data.extend([{"range": f'{cell_names["start_col"]}{row_count}:{cell_names["end_col"]}{row_count}',
                "values": 'Middag',
                "format": add_format("daytime_format"),
                "row_height": 25,
            },
            {
                "range": f'{cell_names["start_col"]}{row_count + 1}:{cell_names["end_col"]}{row_count + 1}',
                "values": f"Antal pers: {data_dict["amount_guests"]}{" " * 25}Avgångstid fr BriQ: {str(data_dict["leave_bq"])[:5]}{" " * 25}Serveringstid: {str(data_dict["serve_time"])[:5]}",
                "format": add_format("daytime_subheader_format"),
                "row_height": 20,
            }
            ])
        row_count += 2



        # current_row = 3 + row_count
        # row_count = current_row
        # base_data.extend([{"range": f'{cell_names["start_col"]}{current_row}', "values": [[f'Middag\n\nAntal pers: {data_dict["amount_guests"]}{" " * 7}Avgångstid fr BriQ: {str(data_dict["leave_bq"])[:5]}       Serveringstid: {str(data_dict["serve_time"])[:5]}']]},])
        # middag_values = []

        if "starter" in data_dict:

            base_data, merge_data, row_count = compile_data({"sv": "Förrätt", "en": "starter"}, add_format, cell_names, merge_data, base_data, row_count, data_dict)


        if "main" in data_dict:
            # data_special, special_rows = prep_special(data_dict, "main")
            # main_data = [[f"Varmrätt: {data_dict["amount_guests"] - data_dict["main"].get("amount_special", 0)} pers.", data_dict["main"]["food"]],
            #             [f"Special:"],
            #             ]
            # row_count += 2
            
            # special_row_format.append(f"A{row_count}:B{row_count + special_rows}")

            # main_data.extend(data_special)
            # middag_values.extend(main_data)

            # row_count += special_rows
            base_data, merge_data, row_count = compile_data({"sv": "Varmrätt", "en": "main"}, add_format, cell_names, merge_data, base_data, row_count, data_dict)

        
        if "dessert" in data_dict:
            # data_special, special_rows = prep_special(data_dict, "dessert")
            # dessert_data = [[f"Dessert: {data_dict["amount_guests"] - data_dict["dessert"].get("amount_special", 0)} pers.", data_dict["dessert"]["food"]],
            #             [f"Special:"],
            #             ]
            # row_count += 2
            
            # special_row_format.append(f"A{row_count}:B{row_count + special_rows}")
            
            # dessert_data.extend(data_special)
            # middag_values.extend(dessert_data)

            # row_count += special_rows
            base_data, merge_data, row_count = compile_data({"sv": "Dessert", "en": "dessert"}, add_format, cell_names, merge_data, base_data, row_count, data_dict)


        # middag_values.extend([["Bröd och smör:", f"{'Ja' if res_dict["meals"]["middag"]["bread"] else '---'}"]])

        # if "salads" in data_dict:
        #     data_special, special_rows = prep_special(data_dict, "salads")

        #     salad_data = [["Sallader:", data_dict["salads"]["food"]],
        #                 [f"Special:"],
        #                 ]
        #     row_count += 3
        #     special_row_format.append(f"A{row_count}:B{row_count + special_rows}")
            
        #     salad_data.extend(data_special)
        #     middag_values.extend(salad_data)

        #     row_count += special_rows

        # base_data.extend([{"range": f'{cell_names["start_col"]}{current_row + 1}:{cell_names["end_col"]}', "values": middag_values}])
        # daytime_headers.append(f'{cell_names["start_col"]}{current_row}')

        # row_count += 2

        if "extras" in res_dict["meals"]["middag"]:
            data_dict = res_dict["meals"]["middag"]["extras"]
            extra_special = False
            
            if "salads" in data_dict and data_dict["salads"] != "---":
                merge_data.append({
                "range": f'{cell_names["start_col"]}{row_count}:B{row_count}',
                "values": "Sallader:",
                "row_height": 15,
                "format": add_format("base_format_bold", [1, 1, 2, 1]),
                })

                base_data.extend([
                {
                "range": f'C{row_count}',
                "values": data_dict["salads"],
                "format": add_format("base_format", [1, 1, 1, 2]),
                },
                ])
                row_count += 1
                print(row_count)
                extra_special = True


            if data_dict["bread"]:
                merge_data.append({
                "range": f'{cell_names["start_col"]}{row_count}:B{row_count}',
                "values": "Bröd och smör:",
                "row_height": 15,
                "format": add_format("base_format_bold", [1, 1, 2, 1]),
                })

                base_data.extend([
                {
                "range": f'C{row_count}',
                "values": "Ja",
                            "format": add_format("base_format", [1, 1, 1, 2]),
                },
                ])
                row_count += 1
                print(row_count)
                extra_special = True


            merge_data.extend([
                {
                "range": f'{cell_names["start_col"]}{row_count}:C{row_count}',
                "values": "Special:",
                            "format": add_format("special_format_bold", [1, 1, 2, 2]),
                        "row_height": 15,
                },
                ])
            row_count += 1

            if extra_special:
                special_rows, merge_data_special, food_data  = prep_special(res_dict["meals"]["middag"], "extras", row_count, add_format)
                merge_data.extend(merge_data_special)
                base_data.extend(food_data)
                row_count += special_rows + 1
    
        row_count += 1
        base_data.extend([{
            "range": f'{cell_names["start_col"]}{row_count}',
            "values": "Anmärkningar:",
            "format": add_format("base_format_bold", [0, 0, 2, 0]),}])
        
        json_path = Path("allergies_formatted.json")

        if json_path.exists():
            row_count += 2
            with open(json_path, "r", encoding="utf-8") as json_file:
                list_data = sorted([f"1 p. {v}" for v in json.load(json_file).values() if v])
                allerg_data = "\n".join(list_data)
                merge_data.extend([{
                    "range": f'{cell_names["start_col"]}{row_count}:C{row_count}',
                    "values": allerg_data,
                    "format": add_format("base_format"),
                    "row_height": len(list_data) * 15
                    }])
                print(allerg_data)
            
        return merge_data, base_data, row_count


def compile_data(meal_type, add_format, cell_names, merge_data, base_data, row_count, data_dict):
    base_data.extend([
                {
                "range": f'{cell_names["start_col"]}{row_count}',
                "values": f"{meal_type["sv"]}:",
                            "format": add_format("base_format_bold", [1, 1, 2, 0]),
                },
                {
                "range": f'B{row_count}',
                "values": f"{data_dict["amount_guests"] - data_dict[meal_type["en"]].get("amount_special", 0)} pers.",
                            "format": add_format("base_format", [1, 1, 0, 1]),
                },
                {
                "range": f'C{row_count}',
                "values": data_dict[meal_type["en"]]["food"],
                            "format": add_format("base_format", [1, 1, 1, 2]),
                },
                ])
    row_count += 1

    merge_data.extend([{
                "range": f'{cell_names["start_col"]}{row_count}:C{row_count}',
                "values": f"Special f. {meal_type["sv"].lower()}:",
                            "format": add_format("special_format_bold", [1, 1, 2, 2]),
                        "row_height": 15,
                },
                ])
    row_count += 1

    special_rows, merge_data_special, food_data  = prep_special(data_dict, meal_type["en"], row_count, add_format)
    merge_data.extend(merge_data_special)
    base_data.extend(food_data)
    row_count += special_rows

    return base_data, merge_data, row_count

    # st.session_state.upd_conn.write_range(
    #     "Resultat", base_data)
    # st.session_state.upd_conn.merge_cells(header_ranges, daytime_headers)
    # print("###BUG??", (header_ranges, daytime_headers, special_row_format))
    # st.session_state.upd_conn.center_text(header_ranges, daytime_headers, special_row_format)


def write_range(ws, item):
    print(item)
    cell_range = item["range"]
    data = item["values"]
    format = item["format"]
    print("### write range", cell_range)
    if ':' in cell_range:
        start_cell, end_cell = cell_range.split(':')
        start_row, start_col = xl_cell_to_rowcol(start_cell)
        end_row, end_col = xl_cell_to_rowcol(end_cell)

        # Determine shape of the range
        n_rows = end_row - start_row + 1
        n_cols = end_col - start_col + 1

        # Handle 1D row or column
        if isinstance(data, list) and all(not isinstance(i, list) for i in data):
            if n_rows == 1:
                ws.write_row(start_row, start_col, data, cell_format=format)
            elif n_cols == 1:
                ws.write_column(start_row, start_col, data, cell_format=format)
            else:
                raise ValueError("1D data can only be written to a single row or single column range.")
        # Handle 2D list
        elif isinstance(data, list) and all(isinstance(i, list) for i in data):
            if len(data) != n_rows or any(len(row) != n_cols for row in data):
                raise ValueError("2D data does not match the size of the target range.")
            for r_idx, row in enumerate(data):
                ws.write_row(start_row + r_idx, start_col, row, cell_format=format)
        else:
            raise TypeError("Unsupported data type for range.")
    else:
        # Single cell
        row, col = xl_cell_to_rowcol(cell_range)
        ws.write(row, col, data, format)


def write_excel():
   
    wb_name = str(datetime.now()).replace(" ", "")
    wb_name = wb_name.replace("-", "")
    wb_name = wb_name.replace(".", "")
    wb_name = wb_name.replace(":", "")
    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook(f'{wb_name}.xlsx')
    st.session_state["workbook"] = workbook

    merge_data, base_data, row_count = prepare_excel_data(workbook)

    worksheet = workbook.add_worksheet(name="Resultat")
    # Increase the cell size of the merged cells to highlight the formatting.
    worksheet.set_column("A:A", 16)
    worksheet.set_column("B:B", 10)
    worksheet.set_column("C:C", 59)

    # worksheet.set_row(0, 50)
    # worksheet.set_row(1, 30)

    #base_format = workbook.add_format({"font_size": 14})
    # Create a format to use in the merged range.
   # help_x = {'A': 0, 'B': 1, 'C': 2}
    # for x in range(0, 20):
    #     worksheet.write_row(0 + x, 'A', ["Test", "Test", "Test"], base_format)
    # col = help_x[data[0]["range"][0]]
    # row = int(data[0]["range"][1:])
    value = merge_data[0]["values"]
    # worksheet.write_row(row, col, value, add_format("header_format"))
    # Merge 3 cells.
    for item in merge_data:                                     # TODO: if special food, access with ["food"] key as set in prep_special
        row_nr = int(item["range"].split(":")[0][1:]) - 1
        print("MERGING ROW ", row_nr)
        worksheet.set_row(row_nr, item["row_height"])
        worksheet.merge_range(item["range"], data=item["values"], cell_format=item["format"])
    #worksheet.merge_range(merge_data[1]["range"], data=merge_data[1]["values"], cell_format=add_format(merge_data[1]["format"]))
    
    for item in base_data:
        write_range(worksheet, item)

    workbook.close()

    fpath = f'"D:\\My Projects\\Coding\\Catering\\{wb_name}.xlsx"'
    os.system(fpath)
    