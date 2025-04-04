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
        to_filter_columns = st.multiselect("Filter by:", ["Proteintyp", "Köttyp", "Rätt"], key=f"filter_{qkey}")
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

def show_df_with_checkboxes(df, column_name, qkey, no_filter=False, allow_delete=False):
    if "choose" not in df:
        df.insert(0, "choose", [False] * len(df.index), True)
    if "idx_key" not in df and not no_filter:
        df.insert(0, "idx_key", list(df.index), True)
    # else:
    #     df["choose"] = [False] * len(df.index)
    print(qkey)
    print(st.session_state.get(qkey))
    df_upd = st.data_editor(
        df if no_filter else filter_dataframe(df, qkey),
        column_config={
            "choose": st.column_config.CheckboxColumn(
                column_name,
                help="Select a meal",
                default=False,
                width="small",
                pinned=True,
            ),
            "idx_key": st.column_config.NumberColumn(
                "Global index",
                default=False,
                width="small",
                pinned=False,                
            )
        },
        column_order=("choose", "Rätt", "Proteintyp", "Köttyp") if not no_filter else None,
        # disabled=["Rätt"],
        hide_index=True,
        num_rows="dynamic" if allow_delete else "fixed",
        key=qkey,

        # on_change=check_val,
    )

    return df_upd

def show_editable_df(df, column_name, qkey, no_filter=False, allow_delete=True):
    # if "choose" not in df:
    #     df.insert(0, "choose", [False] * len(df.index), True)
    # else:
    #     df["choose"] = [False] * len(df.index)
    print(qkey)
    print(st.session_state.get(qkey))
    df_upd = st.data_editor(
        df if no_filter else filter_dataframe(df, qkey),

        hide_index=True,
        num_rows="dynamic" if allow_delete else "fixed",
        key=qkey,
        # on_change=check_val,
    )
    return df_upd

def upd_results():
    pass


# def process_choice(df, df_type, df_filter_name, no_filter=False):
#     df_upd = show_df_with_checkboxes(
#         df, f"choose_{df_type}", df_filter_name, no_filter)
#     chosen_one = df_upd.loc[:, "choose"].idxmax()
#    # st.write(chosen_one)
#     if df_upd.loc[:, "choose"].max():   # shows true or false
#         if df_upd.loc[:, "choose"].value_counts().get(True) > 1:
#             st.write("unselect one!")
#         st.write(df_upd.iloc[chosen_one, 1])
#         st.session_state.result_dict["meals"]["middag"].update(
#             {df_type: df_upd.iloc[chosen_one, 1]})

def process_choice(daytime_checked, df, daytime, meal_type, col_name, df_filter_name, no_filter=False):
    df_upd = show_df_with_checkboxes(
        df, f"choose_{meal_type}", df_filter_name, no_filter)
   # st.write(chosen_one)
    if len(df_upd) and df_upd.loc[:, "choose"].max():   # shows true or false
        chosen_one = df_upd.loc[:, "choose"].idxmax()
        if df_upd.loc[:, "choose"].value_counts().get(True) > 1:
            st.write("unselect one!")
        if no_filter:
            chosen_meal = df_upd.iloc[chosen_one][col_name]
        else:
            chosen_meal = df_upd[df_upd.loc[:, "idx_key"] == chosen_one].iloc[0][col_name]
        st.write(chosen_meal)
        if daytime_checked:    
            if meal_type not in st.session_state.result_dict["meals"][daytime]:
                st.session_state.result_dict["meals"][daytime][meal_type] = {"food": chosen_meal}
            else:
                st.session_state.result_dict["meals"][daytime][meal_type].update({"food": chosen_meal})

def convert_time(time):
    return datetime.strptime(time, '%H:%M:%S')

def input_main_info(daytime_checked, daytime, key_char):
    default_times = {"l": [convert_time('11:00:00'), convert_time('12:00:00')],
                     "m": [convert_time('17:45:00'), convert_time('19:00:00')],}
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        guest_amount = st.number_input(
        "Antal personer:", value=st.session_state.guest_amount, format="%i", step=1,  key=f"guest_amount_{key_char}")
        if daytime_checked:
            st.session_state.result_dict["meals"][daytime].update(
                {"amount_guests": st.session_state[f"guest_amount_{key_char}"]})
    with col2:
        leave_bq = st.time_input("Avg. fr BriQ:", value=default_times[key_char][0], key=f"leave_bq_{key_char}")
    with col3:
        serve_time = st.time_input("Serveringstid:", value=default_times[key_char][1], key=f"serve_time_{key_char}")
        if daytime_checked:
                st.session_state.result_dict["meals"][daytime].update({"leave_bq": st.session_state[f"leave_bq_{key_char}"],
                                                               "serve_time": st.session_state[f"serve_time_{key_char}"]})


# TODO: Delete special entry from result dict if deleted from dataframe by user!!!

def input_special(daytime, meal_type, key_char):
    if not st.session_state.result_dict.get("allergies"):
        return

    if not st.session_state.result_dict["meals"][daytime][meal_type].get("amount_special"):
        st.session_state.result_dict["meals"][daytime][meal_type]["amount_special"] = len(st.session_state.result_dict["allergies"])

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
            new_df[pers] = {"Allergier": ", ".join(sorted(allerg["allerg"])), "Kostavvikelser": ", ".join(sorted(allerg["kost"]))}
            current_allerg.extend(allerg["allerg"])
            current_kost.extend(allerg["kost"])
            current_avv = f"{"-" + ", -".join(sorted(allerg["allerg"])) + f'{" || " + ", ".join(sorted(allerg["kost"])) if allerg["kost"] else ""}' if allerg["allerg"] else ", ".join(sorted(allerg["kost"]))}"
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
    with col_df_1:
        st.write("Översikt specialkost:")
        new_special = st.info(f"Personer med specialkost: **{len(st.session_state.result_dict["allergies"])}**")
        allerg_df = pd.DataFrame(new_df).astype("str").T
        st.dataframe(allerg_df)

    with col_df_2:
        st.write("Sammanfattning:")
        col_am1, col_am2, _ = st.columns([0.6, 0.3, 0.1])
        col_am1.info(f"Personer med specialkost för {daytime} {meal_type}: ")
        with col_am2:
            new_special = st.number_input(label=f"Personer med specialkost för {daytime} {meal_type}:", value=len(st.session_state.result_dict["allergies"]), key=f"input_amount_special_{key_char}", label_visibility="collapsed")

        allerg_sum_cont = st.empty()
        with allerg_sum_cont:
           # st.session_state["de_key"] = str(uuid.uuid4())
            # if "sum_df_upd" not in st.session_state:
            st.session_state["sum_df_upd"] = show_allerg_summary(st.session_state["summary_allerg"], f"{daytime}_{key_char}_{st.session_state["de_key"]}")
            # else:
            #     #st.session_state["de_key"] = str(uuid.uuid4())
            #     st.dataframe(st.session_state["sum_df_upd"])
            #     st.session_state["sum_df_upd"] = show_allerg_summary(st.session_state["summary_allerg"], f"{daytime}_{key_char}_{st.session_state["de_key"]}")
            #     #st.dataframe(st.session_state["sum_df_upd"])

        col_btn_1, col_btn_2, _ = st.columns([0.2, 0.2, 0.6])
        save_allerg = col_btn_1.button("Spara", key=f"save_special_{daytime}_{key_char}")
        reset_button = col_btn_2.button("Reset", key=f"reset_special_{daytime}_{key_char}")
    if save_allerg:
        update_allergy_summary(daytime, meal_type, new_special, st.session_state["sum_df_upd"])
        col_btn_1.success("Sparad!")

    if reset_button:
        st.session_state["de_key"] = str(uuid.uuid4())
        allerg_sum_cont.empty()
        with allerg_sum_cont:
            st.session_state["sum_df_upd"] = show_allerg_summary(st.session_state["summary_allerg"], f"{daytime}_{key_char}_{st.session_state["de_key"]}")
            update_allergy_summary(daytime, meal_type, new_special, st.session_state["sum_df_upd"])
    #special_food_list = pd.DataFrame({"entry": [e for e in st.session_state.result_dict["meals"][daytime]["special"].values()]})
    
    if st.session_state.result_dict["meals"][daytime].get("special"):
        st.write(f"##### Urval specialkost ({daytime} {meal_type}):")

        if not st.session_state.result_dict["meals"][daytime][meal_type].get("special_food"):
            st.session_state.result_dict["meals"][daytime][meal_type]["special_food"] = {}

        for x, e in enumerate(st.session_state.result_dict["meals"][daytime]["special"].values()):
            with st.container():
                col_meal_1, col_meal_2, col_meal_3 = st.columns([0.4, 0.1, 0.5])
                spec_ok = col_meal_2.checkbox("Klar", key=f'spec_food_ok_{key_char}_{x}')
                if spec_ok:
                    col_meal_1.success(f"-  {e}", icon="✅")
                else:
                    col_meal_1.markdown(f"<div class='special-entry-warning'>⚠️  {e}</div>", unsafe_allow_html=True)
                same_select = []
                same_select.extend([el for el in st.session_state.result_dict["meals"][daytime]["special"].values() if el != e])
                # if same_select:
                #     col_meal_1.selectbox("Samma kost som:", same_select, key=f'same_as_select_{key_char}_{x}', placeholder="Choose...", index=None)
                if meal_type in st.session_state.result_dict["meals"][daytime]:
                    if daytime == "lunch" and "salads" in st.session_state.result_dict["meals"][daytime]:
                        salad_str = f"<br>{st.session_state.result_dict["meals"][daytime]["salads"]}"
                    else:
                        salad_str = ""
                    if daytime == "middag" and meal_type == "salads" and st.session_state.result_dict["meals"]["middag"].get("bread"):
                        bread_str = "<br>Bröd och smör"
                    else:
                        bread_str = ""
                    
                    col_meal_3.markdown(f"<div class='custom-info'>{st.session_state.result_dict["meals"][daytime][meal_type].get("food", "[Ingen maträtt vald]")}{salad_str}{bread_str}</div>", unsafe_allow_html=True)


                sf_result = st.empty()
            print(st.session_state.get(f"same_as_select_{key_char}_{x}", None))


            # if not st.session_state.result_dict["meals"][daytime][meal_type].get("special_food"):
            #     st.session_state.result_dict["meals"][daytime][meal_type]["special_food"] = {e: []}
            # else:
            if not st.session_state.result_dict["meals"][daytime][meal_type]["special_food"].get(e):
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = []
           # st.dataframe(show_special_selection(x))
            with st.form(key=f"form_special_selection_{key_char}_{x}", clear_on_submit=True):
                col_s1, col_s2, col_s3, col_s4 = st.columns([0.3, 0.3, .3, 0.1])
                with col_s1:
                    hur = " ".join(list(st.multiselect("Maträtt:",  ['glutenfri', 'laktosfri', 'vegan'], placeholder="Glutenfri...", key=f'spec_food_select_adj_{key_char}_{x}'))).strip()
                # with col_s2:
                    vad = " ".join(list(st.multiselect("Vad:", ['biff', 'sås'], placeholder="biff...", label_visibility='collapsed', key=f'spec_food_select_noun_{key_char}_{x}'))).strip()
                with col_s2:
                    if same_select:
                        st.selectbox("Samma kost som:", same_select, key=f'same_as_select_{key_char}_{x}', placeholder="Choose...", index=None)
                    extra = str(st.text_input("Extra:", label_visibility='collapsed', placeholder="Fritext", key=f'spec_food_select_free_{key_char}_{x}')).strip()
                with col_s3:
                    save_special_select_btn =  st.form_submit_button("Spara")
            
            chosen_special_cont = st.empty()
            spec_food_result = chosen_special_cont.text_input(f"Vald kost till {e}:", value="; ".join(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]), key=f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}")
            
            print('##### list?')
            print(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])
            # print(food_string)
            if save_special_select_btn:
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e].append(" ".join([hur, vad, extra]).strip())
                #st.dataframe(pd.DataFrame(st.session_state["special_food"], index=range(len(st.session_state["special_food"]))).T)
                special_to_copy = st.session_state.get(f"same_as_select_{key_char}_{x}", False)
                same_food = []
                if special_to_copy:
                    same_food = st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][special_to_copy]
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e].extend(same_food)
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = sorted(list(filter(None, set(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]))))
                if st.session_state.get(f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}", False):
                    food_string = "; ".join(sorted(list(set(st.session_state[f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}"].strip().split("; ") + st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e]))))
                else:
                    food_string = "; ".join(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])
                
                st.session_state["sp_inp_key"] = str(uuid.uuid4())
                chosen_special_cont.empty()
                spec_food_result = chosen_special_cont.text_input(f"Vald kost till {e}:", value=food_string, key=f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}")


#            spec_food_result = st.text_input(f"Vald kost till {e}:", value=f'{"; ".join(food_string)}', key=f"special_food_result_{key_char}_{x}")
            if not spec_food_result:
                sf_result.error("... specialkost ej vald ...",)
            elif spec_ok:
                sf_result.empty()
            else:
                sf_result.warning("... urval av specialkost påbörjat ...")

            updd = st.button("Uppdatera", key=f"special_food_result_upd_{key_char}_{x}")
            if updd:
                st.success("Uppdaterad!")
                if st.session_state[f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}"] == "":
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = []
                else:
                    st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e] = sorted(list(filter(None, set(str(st.session_state[f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}"]).strip().split("; ")))))
                    #print(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])
                    st.session_state["sp_inp_key"] = str(uuid.uuid4())
                    
                    chosen_special_cont.empty()
                    chosen_special_cont.text_input(f"Vald kost till {e}:", value=f"{'; '.join(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"][e])}", key=f"special_food_result_{key_char}_{x}_{st.session_state['sp_inp_key']}")
                    
            st.divider()


def show_allerg_summary(summary_allerg, qkey):
        sum_df = pd.DataFrame({"entry": [f"{v} p. {k}" for k, v  in summary_allerg.items()]}, index=range(0, len(summary_allerg)))
    # sum_df_upd = show_df_with_checkboxes(sum_df, f"choose_allerg", "summary_allerg", True)
        sum_df_upd = show_editable_df(sum_df, f"choose_allerg", f"summary_allerg_{qkey}", no_filter=True, allow_delete=True)
        return sum_df_upd

def update_allergy_summary(daytime, meal_type, new_special, sum_df_upd):
    st.session_state.result_dict["meals"][daytime][meal_type]["amount_special"] = new_special
        # Check if allergy summary entry exists in special_food and delete those deleted here:
    if st.session_state.result_dict["meals"][daytime][meal_type].get("special_food"):
        for e in list(st.session_state.result_dict["meals"][daytime][meal_type]["special_food"].keys()):
            if e not in list(sum_df_upd.loc[:, "entry"]):
                st.session_state.result_dict["meals"][daytime][meal_type]["special_food"].pop(e)
#            for idx, entry in zip(list(sum_df_upd.index), list(sum_df_upd.loc[:, "entry"])):
    st.session_state.result_dict["meals"][daytime]["special"] = {idx: entry for idx, entry in zip(list(sum_df_upd.index), list(sum_df_upd.loc[:, "entry"]))}


def read_excel():
    st.title("Upload Excel and Read Specific Range")

# File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file:
        # Read the specific range A20:C20 (1-based index) from the first sheet
        df = pd.read_excel(uploaded_file, sheet_name=0, header=None, usecols="A:C", skiprows=1, nrows=10)

        # Optionally set column names
        df.columns = [f"Column {i+1}" for i in range(df.shape[1])]

        # Convert the row to a dictionary
        result_dict = df.iloc[0].to_dict()

        # Show as DataFrame
        st.write("Extracted Data:")
        st.dataframe(pd.DataFrame([result_dict]))

        # Show the dictionary (optional)
        st.write("As dictionary:")
        st.json(result_dict)

            # show_special_selection(f'{x}__')
            # show_special_selection(f'{x}___')

        #  xx = st.container()
            # col_s1, col_s2, col_s3 = st.columns(3)
            # col_s1.multiselect("Hur:", ['glutenfri', 'laktosfri', 'vegan'], key=f'spec_food_select_adj_{x}')
            # col_s2.multiselect("Vad:", ['biff', 'sås'], key=f'spec_food_select_noun_{x}')
            # col_s3.text_input("Extra:", key=f'spec_food_select_free_{x}')
        #    print(st.session_state["special_food"])
       # st.dataframe(st.session_state["special_food"])
  


            # chosen_items = sum_df_upd[sum_df_upd.loc[:, "choose"] == True]
            # for i in range(len(chosen_items)):
            #     #print(chosen_items.iloc[i]["entry"])
            #     if st.session_state.result_dict["meals"][daytime].get("special"):
            #         next_idx = max(list(st.session_state.result_dict["meals"][daytime]["special"].keys())) + 1
            #     else:
            #         next_idx = 0
            #         st.session_state.result_dict["meals"][daytime]["special"] = {}
            #     st.session_state.result_dict["meals"][daytime]["special"].update({next_idx: chosen_items.iloc[i]["entry"]})
    # with col_df_3:
    #     st.write("Min egen sammanfattning:")
    #     if st.session_state.result_dict["meals"][daytime].get("special"):
    #         sum_df_own = pd.DataFrame({"entry": [v for v in st.session_state.result_dict["meals"][daytime].get("special").values()]}, index=range(0, len(st.session_state.result_dict["meals"][daytime].get("special", None))))
    #         sum_df_own_upd = show_editable_df(sum_df_own, f"delete_allerg_own", "summary_allerg_own", no_filter=True, allow_delete=True)
    #         upd_allerg = st.button("Uppdatera")
    #         if upd_allerg:
    #             st.session_state.result_dict["meals"][daytime]["special"] = {idx: entry for idx, entry in zip(list(sum_df_own_upd.index), list(sum_df_own_upd.loc[:, "entry"]))}
    #             print(st.session_state.result_dict["meals"][daytime]["special"])
    #             print("###")
    #             print(sum_df_own_upd.loc[:, "entry"])
    #             print(sum_df_own_upd.index)


        # del_allerg = st.button("Ta bort")
        # if del_allerg:
        #     for idx in sum_df_own_upd[sum_df_own_upd.loc[:, "choose"] == True].index:
        #         print(sum_df_own_upd.iloc[idx])
        #         #st.session_state.result_dict["meals"][daytime]["special"].pop(idx)
        #         st.rerun()

            # chosen_items = sum_df_own_upd[sum_df_own_upd.loc[:, "choose"] == True]
            # for idx in range(len(chosen_items)):
            #     #print(chosen_items.iloc[i]["entry"])
            #     #next_idx = max(list(st.session_state.result_dict["meals"][daytime]["special"].keys())) + 1
            #     st.session_state.result_dict["meals"][daytime]["special"].update({next_idx: chosen_items.iloc[i]["entry"]})

