import airtable
import streamlit as st
import numpy as np
import time
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

np.random.seed(int(time.time()))

st.title("Backlog")

airtable = airtable.Airtable(AIRTABLE_BASE_ID, "tasks", AIRTABLE_API_KEY)
items = [item["fields"] for item in airtable.get_all()]

def update_current_choice_in_progress(item):
    record = airtable.search("Tema", item[0]["Tema"])
    airtable.update(record[0]["id"], {"Status": "In progress"})

def pick_at_random(list_of_items):
    in_progress = [item for item in list_of_items if item["Status"]=="In progress"]
    if len(in_progress) > 0:
        return in_progress
    else:
        # Now actually pick at random new task
        urgent_ones = [item for item in list_of_items if item["Prioriteta"]=="Nujno" and item["Status"]=="Todo"]
        medium_ones = [item for item in list_of_items if item["Prioriteta"]=="Hitro" and item["Status"]=="Todo"]
        standard_ones = [item for item in list_of_items if item["Prioriteta"]=="Redno" and item["Status"]=="Todo"]
        if len(urgent_ones) > 0:
            randomly_chosen = np.random.choice(urgent_ones, 1)
            update_current_choice_in_progress(randomly_chosen)
            return randomly_chosen
        elif len(medium_ones) > 0:
            randomly_chosen = np.random.choice(medium_ones, 1)
            update_current_choice_in_progress(randomly_chosen)
            return randomly_chosen
        elif len(standard_ones) > 0:
            randomly_chosen = np.random.choice(standard_ones, 1)
            update_current_choice_in_progress(randomly_chosen)
            return randomly_chosen
        else:
            return [{'Tema' : 'completed'}]
    


def get_currents(items):
    current_study, current_do, current_read = {}, {}, {}

    all_study = [item for item in items if item["Področje"]=="Učenje"]
    all_do = [item for item in items if item["Področje"]=="Delo"]
    all_read = [item for item in items if item["Področje"]=="Branje"]

    current_study = pick_at_random(all_study)
    current_do = pick_at_random(all_do)
    current_read = pick_at_random(all_read)

    return current_study, current_do, current_read

with st.expander("Status Quo", expanded=True):
    default_text = "Čestitke! Vse si izpolnil, kar si si zadal. Ti si pravi heroj!"
    naslovi = ["Kaj se moram naučiti ...", "Kaj moram narediti ...", "Kaj moram prebrati ..."]
    curr_study, curr_do, curr_read = get_currents(items=items)

    for category, naslov in zip([curr_study, curr_do, curr_read], naslovi):
        st.write(naslov)
        if category[0]["Tema"] == "completed":
            st.write(default_text)
        else:
            if st.checkbox(category[0]["Tema"]):
                record = airtable.search("Tema", category[0]["Tema"])
                airtable.update(record[0]["id"], {"Status": "Done"})
                st.balloons() 

with st.expander("Dodaj novo nalogo", expanded=True):
    tema = st.text_input(label="")
    col1, col2 = st.columns(2)

    # Področje
    področje = col1.radio("Področje", ["Učenje", "Delo", "Branje"])

    # Prioriteta
    prioriteta = col2.radio("Prioriteta", ["Redno", "Hitro", "Nujno"])

    if st.button("Dodaj!"):
        if tema != "" and tema not in [item["Tema"] for item in items]:
            airtable.insert({
                "Tema": tema,
                "Status": "Todo",
                "Področje": področje,
                "Prioriteta": prioriteta
            })

